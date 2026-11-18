# github-pages

个人主页与数据分析文章站点，线上地址 **https://jqalpha.com**。

- 框架：Astro 7（静态输出）+ Tailwind CSS 4
- 部署：GitHub Pages（GitHub Actions 自动构建）
- 仓库：`JQAlpha/JQAlpha.github.io`（public）

---

## 目录结构

```
github-pages/
├─ .github/workflows/deploy.yml   CI：push → 构建 → 部署
├─ src/                           站点源码
│  ├─ components/                 Header / PostCard / Chart 组件
│  ├─ content/blog/               文章（.md / .mdx）
│  ├─ content/notebooks/          Notebook 源文件
│  ├─ layouts/                    BaseLayout
│  ├─ pages/                      路由页面
│  ├─ styles/global.css           配色 / 字号 / 深浅色变量
│  └─ content.config.ts           文章 frontmatter schema
├─ public/                        原样拷贝到网站根目录
│  ├─ avatar.svg  favicon.svg  og.png  robots.txt
├─ scripts/
│  ├─ astro.mjs                   Node 版本适配启动器
│  └─ ipynb_to_md.py              Notebook → Markdown
├─ tools/node22/                  便携版 Node 22.23.5（不入版本库）
├─ data/                          数据工作区
│  ├─ YYYY/MM/DD/                 按日期分层的原始与中间数据
│  │  ├─ market-data/             行情原始数据
│  │  ├─ research-notes/          研究过程记录
│  │  └─ charts/                  图表中间产物
│  ├─ raw/                        未整理的原始数据
│  └─ processed/                  清洗后的数据
├─ static/                        静态产出
│  ├─ YYYY/MM/DD/                 按日期 + 板块分层的产出
│  │  ├─ market-data/
│  │  ├─ research-notes/
│  │  └─ charts/
│  └─ exports/                    导出文件（CSV / Excel / PDF）
├─ docs/
│  ├─ customization-guide.md      ★ 站点定制指南（改页面看这里）
│  ├─ material-checklist.md       素材准备清单
│  └─ push-site.bat               一键构建 + 提交 + 推送
└─ astro.config.mjs               站点配置（域名、插件）
```

### 静态文件命名规范

所有产出文件按 **日期 / 时间 / 板块 / 次级板块** 分层，目录名见名知意：

```
static/2026/11/19/charts/                # 年 / 月 / 日 / 板块
    ├── market-index-daily-20261118-1530.png
    └── factor-performance-2026-11-18.csv
```

日期用 `YYYY/MM/DD` 或 `YYYYMMDD`，时间用 `HHMM`（24 小时制），板块用英文短横线命名。
例：`20261118-1530` 表示 2026 年 11 月 18 日 15:30。

---

## 常用命令

```bash
npm run dev       # 本地开发，http://localhost:4321
npm run build     # 构建到 dist/
npm run preview   # 预览构建产物
npm run check     # 类型与配置检查
```

> 本机系统 Node 是 22.22.2，Astro 7 要求 ≥ 22.23.4。
> `npm run` 系列已接好适配层，会自动使用 `tools/node22` 里的便携版。
> 升级系统 Node 后会自动切回，无需改配置。

**发布**：

```bash
git add -A
git commit -m "描述"
git push
```

或直接跑 `docs/push-site.bat`（会先本地构建校验再推送）。

---

## 定制入口速查

| 想改什么 | 改哪里 |
|---|---|
| 配色、深浅色 | `src/styles/global.css` 的 `:root` |
| 导航菜单 | `src/components/Header.astro` 的 `nav` 数组 |
| 首页内容 | `src/pages/index.astro` |
| 项目列表 | `src/pages/projects.astro` 的 `projects` 数组 |
| 关于页 | `src/pages/about.astro`（正文 + `facts` 数组） |
| 文章字段定义 | `src/content.config.ts` |
| 站点域名 / 插件 | `astro.config.mjs` |
| 分享卡片图 | `public/og.png`（1200×630） |

详细说明见 **`docs/customization-guide.md`**。

---

## 写文章

在 `src/content/blog/` 新建 `.md`（纯文字）或 `.mdx`（需要交互图表）文件：

```yaml
---
title: '文章标题'
description: '一句话摘要，用于列表页和 SEO'
pubDate: 2026-11-19
tags: ['量化研究', '数据分析']
draft: false
---
```

push 到 `main` 后自动发布，约 1-2 分钟生效。

---

## 数据来源

站内文章数据来自已连接的金融数据连接器：

- **通达信**：实时行情、K 线、F10 财务数据、板块成分、股东研究、资金流向
- **同花顺**：A 股财务三表、估值、题材概念

Python 数据栈已装齐：pandas / numpy / matplotlib / plotly / nbformat / nbconvert / papermill / scipy / statsmodels。

---

## 依赖与安全

- `npm audit` 保持 **0 漏洞**，通过 `package.json` 的 `overrides` 锁定安全版本
- CI 使用 Node 24，本地用 `tools/node22`（22.23.5）
- 仓库必须为 **public**（GitHub Free 计划下私有仓库无法启用 Pages）
