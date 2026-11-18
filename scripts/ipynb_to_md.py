#!/usr/bin/env python
r"""
Notebook → 静态 Markdown 转换脚本

把你 src/content/notebooks/ 下的 .ipynb 转成可以直接放进
src/content/blog/ 的 .md 文件（代码 + 输出 + 图表）。

用法：
    python scripts/ipynb_to_md.py                      # 转换全部
    python scripts/ipynb_to_md.py 因子分析.ipynb         # 转换指定文件

前置：
    pip install nbformat nbconvert jinja2
    若 Notebook 用了 plotly，需额外：pip install plotly

⚠️ 本机有两套 Python（WorkBuddy 内置版 / Miniconda 版），
   依赖装在 WorkBuddy 内置版里。本脚本会自动用 scripts/which_python.py
   定位到正确的解释器重新执行，所以在任何终端调用都一致。
"""

import argparse
import base64
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# 若当前解释器不是本项目该用的那个，转交给正确的解释器
def ensure_correct_interpreter() -> None:
    """检测当前 Python 是否具备所需依赖；不具备则用正确解释器重启自己"""
    try:
        import importlib.util as util
        needed = ["nbformat", "nbconvert", "jinja2"]
        if all(util.find_spec(m) for m in needed):
            return
    except Exception:
        pass

    resolver = SCRIPT_DIR / "which_python.py"
    if not resolver.exists():
        return

    # 解析出目标解释器
    try:
        out = subprocess.run(
            [sys.executable, str(resolver), "--json"],
            capture_output=True, text=True, timeout=90,
        )
        import json
        info = json.loads(out.stdout.strip().splitlines()[-1])
        target = info["executable"]
    except Exception:
        return

    if Path(target).resolve() == Path(sys.executable).resolve():
        return

    # 用目标解释器重新执行自己
    print(f"[ipynb_to_md] 当前解释器缺少依赖，转交至：{target}")
    os.execv(target, [target, str(Path(__file__).resolve()), *sys.argv[1:]])


ensure_correct_interpreter()

try:
    import nbformat
    from nbconvert import HTMLExporter
except ImportError:
    print("缺少依赖，请先运行：")
    print(f'  "{sys.executable}" -m pip install nbformat nbconvert jinja2')
    sys.exit(1)

ROOT = PROJECT_ROOT
NB_DIR = ROOT / "src" / "content" / "notebooks"
OUT_DIR = ROOT / "src" / "content" / "blog"
# 图表输出目录：public/charts/ 会被原样拷贝到网站 /charts/ 路径
CHART_DIR = ROOT / "public" / "charts"


def sanitize_filename(stem: str) -> str:
    """把notebook 文件名转成安全的 slug"""
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", stem).strip("-").lower()
    return slug or "notebook"


def extract_title(nb) -> str:
    """从第一个 markdown cell 里抠出标题"""
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            for line in cell.source.splitlines():
                line = line.strip()
                if line.startswith("#"):
                    return line.lstrip("#").strip()
            if cell.source.strip():
                return cell.source.strip().splitlines()[0]
    return "未命名 Notebook"


def execute_notebook(nb_path: Path) -> bool:
    """
    执行 notebook，把输出写回文件。

    为什么需要这一步：notebook 文件里存的输出可能是空的（比如从别处拷来的
    骨架，或者从未执行过）。没有输出就没有图表、没有数值，文章是空的。
    这里用 nbclient 跑一遍，把真实的输出固化下来。

    前提：pip install nbclient ipykernel
    失败时返回 False，不阻断转换流程（会保留原有输出）。
    """
    try:
        import nbclient
        from nbclient import NotebookClient
    except ImportError:
        print("      (未安装 nbclient，跳过执行；如需自动执行请 pip install nbclient ipykernel)")
        return False

    # Windows 下 zmq 需要 Selector 事件循环，否则会刷 RuntimeWarning
    if sys.platform == "win32":
        try:
            import asyncio
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass

    try:
        # nbclient 0.11 的 NotebookClient 接受 Notebook 对象而非路径
        nb = nbformat.read(str(nb_path), as_version=4)

        # 把 scripts/ 加入 kernel 的 sys.path，这样 notebook 里可以直接
        # `import plot_config` 而不用写相对路径（kernel 的 cwd 不是 notebook 目录）
        pre_code = (
            "import sys\n"
            f"sys.path.insert(0, {str(SCRIPT_DIR)!r})\n"
            "sys.path.insert(0, %r)\n" % str(nb_path.parent)
        )
        # 插到第一个 cell 之前
        nb.cells.insert(0, nbformat.v4.new_code_cell(pre_code))

        client = NotebookClient(
            nb,
            timeout=300,
            kernel_name="python3",
            allow_errors=True,
        )
        client.execute()

        # 移除注入的前置 cell
        nb.cells.pop(0)

        # 把执行结果写回原文件，下次 --no-execute 也能用
        nbformat.write(nb, str(nb_path))
        print("      已执行 notebook，输出已固化")
        return True
    except Exception as e:
        print(f"      执行失败（保留原有输出）: {type(e).__name__}: {e}")
        return False


def _clean_stream_output(text: str) -> str:
    """
    清理 stdout 里的噪音：
    - UserWarning / RuntimeWarning 等告警行（matplotlib 字体警告会刷屏几十行）
    - 空行
    保留真正的程序输出。
    """
    lines = text.splitlines()
    cleaned = []
    in_warning = False

    for line in lines:
        stripped = line.strip()

        # 警告块起始：...Warning: xxx
        if re.search(r"^\S*(Warning|Error)\s*:", stripped) or re.match(
            r"^[A-Za-z_]*Warning:", stripped
        ):
            in_warning = True
            continue

        # 警告块的续行（缩进的 traceback / 提示）
        if in_warning:
            if stripped == "" or line.startswith((" ", "\t")):
                # 续行可能是 traceback，保留有价值的部分
                if "Error" in stripped and ":" in stripped:
                    cleaned.append(stripped)
                continue
            in_warning = False

        if stripped:
            cleaned.append(stripped)

    return "\n".join(cleaned)


def extract_outputs(nb, slug: str) -> tuple[str, list[str]]:
    """
    逐 cell 渲染成 Markdown：代码块 + 输出（文本输出转代码块，图片输出存成文件）。

    nbconvert 的 MarkdownExporter 会丢弃图片输出，所以这里手写一遍，
    把matplotlib 产出的 base64 PNG 落盘到 public/charts/ 并改成 md 引用。

    返回 (markdown 正文, 图片文件列表)
    """
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    parts: list[str] = []
    images: list[str] = []
    img_index = 0

    for cell in nb.cells:
        # Markdown cell —— 直接作为正文
        if cell.cell_type == "markdown":
            parts.append(cell.source.rstrip())
            continue

        # Code cell —— 代码块 + 输出
        if cell.cell_type != "code":
            continue

        source = cell.source.rstrip()
        if source:
            parts.append(f"```python\n{source}\n```")

        for output in cell.get("outputs", []):
            otype = output.get("output_type")

            # 文本输出（stdout / stderr）
            if otype == "stream":
                text = output.get("text", "")
                if text:
                    cleaned = _clean_stream_output(text)
                    if cleaned:
                        parts.append(f"```\n{cleaned}\n```")

            # 错误输出
            elif otype == "error":
                ename = output.get("ename", "Error")
                evalue = output.get("evalue", "")
                tb = "\n".join(output.get("traceback", [])[:6])
                parts.append(f"```\n{ename}: {evalue}\n{tb}\n```")

            # 图片输出（matplotlib 默认 PNG base64）
            elif otype in ("display_data", "execute_result"):
                data = output.get("data", {})
                png = data.get("image/png")
                if png:
                    img_index += 1
                    filename = f"{slug}-fig{img_index}.png"
                    (CHART_DIR / filename).write_bytes(base64.b64decode(png))
                    images.append(filename)
                    alt = f"{slug} 图表 {img_index}"
                    parts.append(f"![{alt}](/charts/{filename})")
                else:
                    plain = data.get("text/plain")
                    if plain:
                        parts.append(f"```\n{plain.rstrip()}\n```")

    return "\n\n".join(p for p in parts if p.strip()), images


def convert(nb_path: Path, do_execute: bool = True) -> Path | None:
    # 先执行一遍，确保有真实输出
    if do_execute:
        execute_notebook(nb_path)

    nb = nbformat.read(nb_path, as_version=4)

    slug = sanitize_filename(nb_path.stem)
    md_body, images = extract_outputs(nb, slug)

    title = extract_title(nb)
    date = nb.metadata.get("date") or "2026-01-01"
    tags = nb.metadata.get("tags", [])
    description = nb.metadata.get("description", title)

    front = [
        "---",
        f"title: '{title}'",
        f"description: '{description}'",
        f"pubDate: {date}",
    ]
    if tags:
        tag_str = ", ".join(f"'{t}'" for t in tags)
        front.append(f"tags: [{tag_str}]")
    front.append("---")
    front.append("")

    md = "\n".join(front) + md_body + "\n"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{slug}.md"
    out_path.write_text(md, encoding="utf-8")

    print(f"  ✓ {nb_path.name}  ->  {out_path.relative_to(ROOT)}")
    if images:
        print(f"      图表 {len(images)} 张 -> public/charts/ ({', '.join(images)})")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Notebook 转 Markdown")
    parser.add_argument("notebook", nargs="?", help="指定 notebook 文件名（可选）")
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="跳过执行，直接转换已保存的输出",
    )
    args = parser.parse_args()

    if not NB_DIR.exists():
        print(f"目录不存在：{NB_DIR}")
        print("请把 .ipynb 放进该目录后重试。")
        sys.exit(1)

    if args.notebook:
        target = NB_DIR / args.notebook
        if not target.exists():
            print(f"文件不存在：{target}")
            sys.exit(1)
        files = [target]
    else:
        files = sorted(NB_DIR.glob("*.ipynb"))

    if not files:
        print(f"{NB_DIR} 下没有 .ipynb 文件")
        sys.exit(0)

    print(f"转换 {len(files)} 个 notebook：")
    for f in files:
        try:
            convert(f, do_execute=not args.no_execute)
        except Exception as e:
            print(f"  ✗ {f.name}: {type(e).__name__}: {e}")

    print("\n完成。产物已在 src/content/blog/ 下，push 后自动发布。")


if __name__ == "__main__":
    main()
