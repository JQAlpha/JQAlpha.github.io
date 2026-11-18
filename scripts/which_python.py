#!/usr/bin/env python
r"""
Python 解释器解析器—— 为本项目定位"该用哪个 Python"。

## 为什么需要这个脚本

这台机器上有两套 Python：

| 解释器 | 路径 | 说明 |
|---|---|---|
| WorkBuddy 内置 | `C:\Users\LAPTOP-Gary\.workbuddy\binaries\python\versions\3.13.12\python.exe` | 本项目的数据分析栈装在这里 |
| Miniconda base | `C:\Apps_Dev\Tools\miniconda3\python.exe` | 系统 PATH 里的默认解释器，只有 pandas/numpy |

**在 Git Bash 里 `python` 指向 WorkBuddy 版，在 Windows Terminal / PowerShell 里
`python` 指向 Miniconda 版。** 同一个命令在两个终端跑出不同结果，
`python scripts/ipynb_to_md.py` 会在后者报 `ModuleNotFoundError: nbformat`。

所以本项目的脚本不直接调 `python`，而是通过本解析器拿到正确解释器。

## 用法

    python scripts/which_python.py          # 打印本项目应使用的解释器
    python scripts/which_python.py --check  # 校验解释器与依赖完整性
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 候选解释器，按优先级排列
CANDIDATES = [
    PROJECT_ROOT / "tools" / "python" / "python.exe",
    Path.home() / ".workbuddy" / "binaries" / "python" / "versions" / "3.13.12" / "python.exe",
    Path(r"C:\Apps_Dev\Tools\miniconda3\python.exe"),
]

# 本项目的数据分析栈必须齐备
REQUIRED = ["pandas", "numpy", "matplotlib", "plotly", "nbformat", "nbconvert", "jinja2"]

MIN_VERSION = (3, 11)


def version_of(exe: Path) -> tuple:
    """返回 (major, minor)，失败返回 (0, 0)"""
    try:
        out = subprocess.run(
            [str(exe), "-c", "import sys;print('%d.%d' % sys.version_info[:2])"],
            capture_output=True, text=True, timeout=30,
        )
        major, minor = out.stdout.strip().split(".")[:2]
        return int(major), int(minor)
    except Exception:
        return (0, 0)


def missing_packages(exe: Path) -> list:
    """返回缺失的包列表"""
    code = (
        "import importlib.util as u;"
        f"miss=[m for m in {REQUIRED!r} if not u.find_spec(m)];"
        "print(','.join(miss))"
    )
    try:
        out = subprocess.run(
            [str(exe), "-c", code], capture_output=True, text=True, timeout=60
        )
        raw = out.stdout.strip()
        return [p for p in raw.split(",") if p]
    except Exception:
        return list(REQUIRED)


def resolve():
    """按优先级找第一个满足版本与依赖的解释器"""
    fallback = None
    for exe in CANDIDATES:
        if not exe.exists():
            continue
        ver = version_of(exe)
        if ver < MIN_VERSION:
            continue
        if fallback is None:
            fallback = (exe, ver)
        if not missing_packages(exe):
            return exe, ver, []
    if fallback:
        return fallback[0], fallback[1], missing_packages(fallback[0])
    return None, (0, 0), list(REQUIRED)


def main():
    exe, ver, missing = resolve()

    if exe is None:
        print("[which_python] 找不到可用的 Python 解释器", file=sys.stderr)
        print(f"  最低要求: Python {MIN_VERSION[0]}.{MIN_VERSION[1]}+", file=sys.stderr)
        for c in CANDIDATES:
            print(f"  已尝试: {c} ({'存在' if c.exists() else '不存在'})", file=sys.stderr)
        sys.exit(1)

    print(f"解释器: {exe}")
    print(f"版本  : {ver[0]}.{ver[1]}")
    print(f"依赖  : {'全部齐备' if not missing else '缺失 ' + ', '.join(missing)}")

    if "--check" in sys.argv:
        if missing:
            print(f"\n请用以下命令补装：\n  \"{exe}\" -m pip install {' '.join(missing)}")
            sys.exit(1)
        print("\n环境完整，可以正常使用。")

    if "--json" in sys.argv:
        print(json.dumps({
            "executable": str(exe),
            "version": f"{ver[0]}.{ver[1]}",
            "missing": missing,
        }, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
