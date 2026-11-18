# 数据工作区

本目录存放分析过程产生的数据与中间产物，**不进入 Git 版本库**（见 `.gitignore`）。

## 目录规范

```
data/
├─ YYYY/MM/DD/              按日期分层
│  ├─ market-data/          行情原始数据
│  ├─ research-notes/       研究过程记录（假设、结论、待验证项）
│  └─ charts/               图表中间产物（CSV / JSON 形式的数据）
├─ raw/                     未整理的原始数据（下载即存）
└─ processed/               清洗、去重、标准化后的数据
```

日期一律用 `YYYY/MM/DD`。例如 2026 年 11 月 19 日 → `data/2026/11/19/`。

## 命名约定

| 类型 | 格式 | 示例 |
|---|---|---|
| 文件名 | `<主题>-<频率>-<日期>-<时间>.<ext>` | `market-index-daily-20261118-1530.csv` |
| 日期 | `YYYYMMDD` 或 `YYYY-MM-DD` | `20261118` |
| 时间 | `HHMM`（24 小时制） | `1530` |
| 板块 | 英文小写 + 短横线 | `market-data`、`factor-performance` |

## static/ 目录

`static/` 是最终静态产出，结构与 `data/` 一致（`YYYY/MM/DD/<板块>/`），
另外有 `static/exports/` 存放对外导出的文件（CSV / Excel / PDF）。

发布到网站时，把需要公开的文件从 `data/` 或 `static/` 复制到 `public/` 下对应的位置，
`public/` 里的内容会原样拷贝到网站根路径。

## 当前已有

| 日期 | 板块 | 内容 |
|---|---|---|
| 2026/11/19 | market-data | 上证指数、深证成指 2026-11-18 盘后快照（通达信） |
