"""
Matplotlib 中文字体与绘图样式配置

在Notebook 里先 `import sys; sys.path.insert(0, '../scripts')` 再
`import plot_config as pc; pc.apply()`，或直接：

    import sys
    sys.path.insert(0, '../scripts')
    import plot_config
    plot_config.apply()

中文图表三件套：
1. 字体       —— 默认 DejaVu Sans 不含中文，标题会变成方块
2. 负号       —— 中文字体下负号会显示为方块，需设 axes.unicode_minus=False
3. 样式一致性 —— 与网站配色一致

配色沿用站点设计变量（src/styles/global.css）：
  --color-accent: #2563eb
  深色模式强调色：#7c3aed
"""

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# 与网站一致的调色板（对比度经过校验，黑白打印也能分辨）
PALETTE = [
    "#2563eb",  # 主色蓝
    "#7c3aed",  # 紫
    "#0891b2",  # 青
    "#059669",  # 绿
    "#d97706",  # 橙
    "#dc2626",  # 红
    "#db2777",  # 粉
    "#4f46e5",  # 靛
    "#65a30d",  # 黄绿
    "#ea580c",  # 深橙
]

# 按优先级尝试的中文字体
CJK_FONT_CANDIDATES = [
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "Microsoft JhengHei",
    "DengXian",
    "FangSong",
    "KaiTi",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
]


def find_cjk_font() -> str | None:
    """在系统已安装字体中找出可用的中文字体"""
    available = {f.name for f in fm.fontManager.ttflist}
    for name in CJK_FONT_CANDIDATES:
        if name in available:
            return name
    # 兜底：按名称包含关键词匹配
    for f in fm.fontManager.ttflist:
        n = f.name
        if any(k in n for k in ("YaHei", "SimHei", "SimSun", "Yahei", "Hei", "Song", "Kai")):
            return n
    return None


def apply(style: str = "default") -> str:
    """
    应用中文字体与配色。返回实际使用的字体名。

    在Notebook 中调用一次即可，之后所有 plt 调用都会生效。
    """
    font = find_cjk_font()

    if font:
        matplotlib.rcParams["font.sans-serif"] = [font] + CJK_FONT_CANDIDATES
        print(f"[plot_config] 中文字体: {font}")
    else:
        matplotlib.rcParams["font.sans-serif"] = CJK_FONT_CANDIDATES
        print("[plot_config] 未找到中文字体，图表中文可能显示为方块")
        print("            可安装：pip install matplotlib 并确认系统有微软雅黑")

    # 中文字体下负号会变方块
    matplotlib.rcParams["axes.unicode_minus"] = False

    # 配色
    matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(color=PALETTE)

    # 基础样式
    matplotlib.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.edgecolor": "#cbd5e1",
        "axes.labelcolor": "#334155",
        "axes.titlecolor": "#0f172a",
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#e2e8f0",
        "grid.linewidth": 0.8,
        "text.color": "#334155",
        "xtick.color": "#64748b",
        "ytick.color": "#64748b",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 13,
        "legend.fontsize": 10,
        "figure.dpi": 110,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
        "font.size": 11,
        "lines.linewidth": 2,
        "lines.markersize": 5,
    })

    return font or ""


def dark_theme() -> None:
    """深色背景样式（与网站深色模式一致）"""
    matplotlib.rcParams.update({
        "figure.facecolor": "#0b1120",
        "axes.facecolor": "#0b1120",
        "savefig.facecolor": "#0b1120",
        "axes.edgecolor": "#334155",
        "axes.labelcolor": "#e2e8f0",
        "axes.titlecolor": "#e2e8f0",
        "grid.color": "#1e293b",
        "text.color": "#e2e8f0",
        "xtick.color": "#94a3b8",
        "ytick.color": "#94a3b8",
    })


if __name__ == "__main__":
    f = apply()
    print(f"[plot_config] 字体解析完成: {f or '未找到中文字体'}")
