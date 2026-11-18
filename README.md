# jqalpha.com

个人主页与数据分析文章站点。

- 框架：Astro 7（静态输出）
- 样式：Tailwind CSS 4
- 部署：GitHub Pages（GitHub Actions）
- 域名：https://jqalpha.com

## 本地开发

需要 Node ≥ 22.23.4。

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # 产出到 dist/
npm run preview    # 本地预览构建产物
```

## 写一篇新文章

在 `src/content/blog/` 下新建 `.md` 文件，frontmatter 如下：

```yaml
---
title: '文章标题'
description: '一句话摘要，用于列表页和 SEO'
pubDate: 2026-11-19
tags: ['量化研究', '数据分析']
featured: false
---
```

push 到 `main` 分支后，GitHub Actions 会自动构建并发布到 https://jqalpha.com。

## 目录结构

```
src/
├─ components/      Header、PostCard 等组件
├─ content/blog/    文章 Markdown
├─ layouts/         BaseLayout
├─ pages/           路由页面
├─ styles/          全局样式与设计变量
└─ content.config.ts  内容集合 schema
```

## 关于颜色与主题

设计变量集中在 `src/styles/global.css` 的 `:root` 中，同时定义了亮色与暗色两套。
改配色只需要改那里，不要在组件里写死颜色。
