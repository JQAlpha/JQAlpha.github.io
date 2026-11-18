#!/usr/bin/env python
"""
Notebook → 静态 HTML 转换脚本

把你src/content/notebooks/ 下的 .ipynb 转成可以直接放进
src/content/blog/ 的 .md 文件（代码 + 输出 + 图表）。

用法：
    python scripts/ipynb_to_md.py                      # 转换全部
    python scripts/ipynb_to_md.py 因子分析.ipynb         # 转换指定文件

前置：
    pip install nbformat nbconvert jinja2
    若Notebook 用了 plotly，需额外：pip install plotly
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import nbformat
    from nbconvert import HTMLExporter, MarkdownExporter
except ImportError:
    print("缺少依赖，请先运行：pip install nbformat nbconvert jinja2")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "src" / "content" / "notebooks"
OUT_DIR = ROOT / "src" / "content" / "blog"


def sanitize_filename(stem: str) -> str:
    """把 notebook 文件名转成安全的 slug"""
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


def convert(nb_path: Path) -> Path | None:
    nb = nbformat.read(nb_path, as_version=4)

    # 1) 抽出输出为图片（matplotlib 等会产出 base64 PNG）
    html_exporter = HTMLExporter()
    html_exporter.template_name = "lab"
    body, _ = html_exporter.from_notebook_node(nb)

    # 2) 转成 markdown（代码块 + 文本输出）
    md_exporter = MarkdownExporter()
    md_body, _ = md_exporter.from_notebook_node(nb)

    title = extract_title(nb)
    slug = sanitize_filename(nb_path.stem)
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
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Notebook 转 Markdown")
    parser.add_argument("notebook", nargs="?", help="指定 notebook 文件名（可选）")
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
            convert(f)
        except Exception as e:
            print(f"  ✗ {f.name}: {e}")

    print("\n完成。产物已在 src/content/blog/ 下，push 后自动发布。")


if __name__ == "__main__":
    main()
