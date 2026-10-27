# 站点交互问题修复

日期：2026-10-28（北京时间）。基线：`7b1fcc2846a8532db6245ef16d9994bd1c709e92`。本轮只调整站点，未重制视频或改写制作冻结输入。

## 范围

- #386、#387、#389：单集顶部与文末提供标明 GitHub 的脚本、分镜和源码入口，脚本/分镜另有原始文件入口。链接固定到构建该页面的完整提交 SHA，文件与页面使用同一发布树；不把此 SHA 宣称为原始视频编码提交。
- #388：站点播放器默认显示中文字幕。
- #390、#394：明确系列目录序号是观看顺序，EP 是沿用的历史发布编号，跨系列可能重复；引用以标题和页面链接为准。工程算法标签统一 EA01/EA02/EA03，不重写历史媒体或内容时间。
- #391：学习页顶部固定系列直达目录，可直接进入独立系列页。
- #392、#393：更新日志展示读者摘要及可点击的课程/素材列表，最近五版展开，旧版按月折叠，完整内部记录保留 GitHub Release 入口。提取时使用纯文本和限定的 HTTPS 链接，不直接注入 Release HTML。
- #395：中文 404 页沿用站点导航和主题，提供首页、学习系列、全部内容及带查询词的搜索。
- #396：内容卡片仅显示一个北京时间日期，统一 `YYYY-MM-DD`；单集详情继续保留完整时间和版本。
- #398：历史分布式事务合集保留“系统原理 › 分布式”面包屑，继续排除在现行课程导航之外。

## 验证

本地全站构建通过，包含日期、参考资料、文章、资源复制、Astro 与 Pagefind。日期与学习路径的构建产物检查通过，文章检查器测试 13 项通过；更新日志提取的针对性测试另见脚本。

本环境 Node 抓取 Release 需使用 `NODE_USE_ENV_PROXY=1` 沿用环境代理。已确认抓取成功后的日志页包含 100 个版本，无原样 Markdown 链接和 SHA/冻结记录；初次降级外链的构建不作为日志页面验收。

`preservation-baseline.json` 与 `preservation-check.json` 记录 49 个视频和 49 张海报的完整 SHA-256，以及 49 份内容时间与身份字段。全部保持一致。浏览器检查和上线结果分别记录于同目录的实际回执。

`browser-check.json` 记录本地 Chromium 的 84 项检查，覆盖 1440/390 视口及深浅主题。字幕轨实际载入并开启、素材入口、目录跳转、日志折叠与 404 搜索均通过；40 张工作区截图中选存 8 张代表截图。简单本地服务器不支持范围请求，此结果不声称已经验证生产媒体传输。

可复核命令：

```sh
NODE_USE_ENV_PROXY=1 npm --prefix site run build
node site/scripts/check-episode-dates.mjs --built
node site/scripts/check-learning-path.mjs --complete --built
npm --prefix site run test:articles
npm --prefix site run test:releases
python3 episodes/_shared/tests/secret_scan.py
```

## 上线结果

[PR #399](https://github.com/linhongcun/video-studio/pull/399) 已合并，发布 [v0.82.0](https://github.com/linhongcun/video-studio/releases/tag/v0.82.0)。初次 Pages `40604223382` 及 Release 后 Pages `40604271523` 均成功，实际发布提交为 `ac31f8431fe49a64f05e87e44a037de4e9af0cfd`。Release 后再次确认线上版本、素材提交与更新日志正常。

`online-verification.json` 核对全部 49 个单集页面和字幕、98 份线上媒体完整 SHA-256，以及原始文件、卡片、系列目录和真实多层错误路径的中文 404。`online-browser-check.json` 记录桌面浅色及手机深色的 32 项实际浏览器检查；中文字幕默认显示、实际播放及跳转到 30 秒通过，观察到 4 次真实 HTTP 206 范围响应，无已知能力限制。浏览器使用原生 CA 校验和环境代理，不绕过 TLS。

12 个 issue 均已以 `completed` 关闭，状态快照见 `completed-issues.json`；发布回执见 `publication.json`。本次仅 GitHub 站点上线，未重发外平台。
