# video-studio · IT小村工作室

IT小村工作室的互联网开发技术科普短视频项目：用生活里的比喻（驿站、快递、排队、记账……），把后端和分布式系统的知识讲清楚。视频全部用代码生成（[Remotion](https://www.remotion.dev/)），每期配一篇图文文章。

- 线上站点：https://linhongcun.github.io/video-studio/
- 发布平台：抖音、B站、快手（小红书暂停）
- 站点功能：按系列浏览（浏览器与网络 / 后台缓存 / 扛住高峰 / 数据库 / 分布式）、站内搜索（Pagefind）、[更新日志](https://linhongcun.github.io/video-studio/changelog/)（构建时读取 GitHub Releases，发 Release 后自动重新部署）
- 订阅：[RSS](https://linhongcun.github.io/video-studio/rss.xml) · [站点地图](https://linhongcun.github.io/video-studio/sitemap-index.xml)
- 成片：每期 `episodes/<slug>/video.mp4`，各版本变更见 [Releases](https://github.com/linhongcun/video-studio/releases)

## 已上线剧集

剧集信息来自各期的 `episodes/<slug>/meta.json`（`draft: false`）。期号按 2026-10-21 新排期（[#91](https://github.com/linhongcun/video-studio/issues/91)）：EP.01–14 已重制；EP.15–21 目前是旧版（`meta.json` 写 `"legacy": true`，站点显示「旧版，重制中」），重制版上线时去掉；原 EP.16 隔离级别（`db-isolation`）已下架（`draft: true`，源文件保留）。

| 期 | 系列 | 标题 | 站点 | 上线日期 |
|---|---|---|---|---|
| 1 | 浏览器与网络 | 浏览器输入网址后发生了什么？ | [http-request](https://linhongcun.github.io/video-studio/episodes/http-request/) | 2026-10-12 |
| 2 | 浏览器与网络 | HTTPS 为什么安全？ | [https](https://linhongcun.github.io/video-studio/episodes/https/) | 2026-10-12 |
| 3 | 浏览器与网络 | 输入网址后，怎么找到服务器？ | [dns](https://linhongcun.github.io/video-studio/episodes/dns/) | 2026-10-12 |
| 4 | 浏览器与网络 | 网站怎么记住你已经登录？ | [cookie-session](https://linhongcun.github.io/video-studio/episodes/cookie-session/) | 2026-10-12 |
| 5 | 浏览器与网络 | 网站离你那么远，为什么还这么快？ | [cdn](https://linhongcun.github.io/video-studio/episodes/cdn/) | 2026-10-12 |
| 6 | 浏览器与网络 | 一台服务器忙不过来，怎么办？ | [load-balancing](https://linhongcun.github.io/video-studio/episodes/load-balancing/) | 2026-10-12 |
| 7 | 浏览器与网络 | 同一个网页，第二次打开为什么快这么多？ | [browser-cache](https://linhongcun.github.io/video-studio/episodes/browser-cache/) | 2026-10-12 |
| 8 | 后台缓存 | 数据库明明有数据，为什么还要再存一份？ | [server-cache](https://linhongcun.github.io/video-studio/episodes/server-cache/) | 2026-10-13 |
| 9 | 后台缓存 | 后台改了价格，页面怎么还是旧的？ | [cache-consistency](https://linhongcun.github.io/video-studio/episodes/cache-consistency/) | 2026-10-16 |
| 10 | 扛住高峰 | 双十一下单那么多，为什么不丢单？ | [message-queue](https://linhongcun.github.io/video-studio/episodes/message-queue/) | 2026-10-13 |
| 11 | 扛住高峰 | 抢票那一刻，为什么总提示系统繁忙？ | [rate-limit](https://linhongcun.github.io/video-studio/episodes/rate-limit/) | 2026-10-13 |
| 12 | 扛住高峰 | 手一抖点了两次支付，为什么只扣一次钱？ | [idempotency](https://linhongcun.github.io/video-studio/episodes/idempotency/) | 2026-10-13 |
| 13 | 扛住高峰 | 一个服务出故障，为什么整个网站没跟着崩？ | [circuit-breaker](https://linhongcun.github.io/video-studio/episodes/circuit-breaker/) | 2026-10-14 |
| 14 | 扛住高峰 | 搜索页和结算页，为什么两个价不一样？ | [degradation](https://linhongcun.github.io/video-studio/episodes/degradation/) | 2026-10-13 |
| 15 | 数据库 | 加个索引，为啥就快了？（旧版，重制中） | [db-index](https://linhongcun.github.io/video-studio/episodes/db-index/) | 2026-10-14 |
| 16 | 数据库 | 扣了钱，对方没到账？（旧版，重制中） | [db-transaction](https://linhongcun.github.io/video-studio/episodes/db-transaction/) | 2026-10-14 |
| 17 | 数据库 | 两个人抢同一件货，听谁的？（旧版，重制中） | [db-lock](https://linhongcun.github.io/video-studio/episodes/db-lock/) | 2026-10-15 |
| 18 | 数据库 | 刚改的昵称，怎么又变回去了？（旧版，重制中） | [db-replication](https://linhongcun.github.io/video-studio/episodes/db-replication/) | 2026-10-15 |
| 19 | 分布式 | 大促一到，下单怎么就卡住了？（旧版，重制中） | [db-sharding](https://linhongcun.github.io/video-studio/episodes/db-sharding/) | 2026-10-15 |
| 20 | 分布式 | 两个订单，怎么撞成同一个号了？（旧版，重制中） | [global-id](https://linhongcun.github.io/video-studio/episodes/global-id/) | 2026-10-15 |
| 21 | 分布式 | 两个库，怎么一起成功或一起失败？（旧版，重制中） | [distributed-tx](https://linhongcun.github.io/video-studio/episodes/distributed-tx/) | 2026-10-16 |

## 制作流程

1. **选题调研**：确定问题和生活场景，事实带来源和日期（优先用 2020 年以后的资料）。
2. **脚本分镜**：`script.md`（旁白）、`article.mdx`（文章）、`pronunciation.md`（多音字和英文读法）、`storyboard.json` / `shotlist.md`（镜头、元素、字幕、推镜、章节卡）。先讲比喻，再给术语。
3. **配音**：Xiaomi MiMo TTS（`mimo-v2.5-tts`，音色「冰糖」）逐句合成，每句 −21 LUFS；逐句 ASR 和多音字核对；第一期为 edge-tts。
4. **Remotion 渲染**：按分镜插入停顿，渲染画面；`mix_bgm.py` 铺 Wallpaper 背景音乐（比人声低 12 dB），母带 −16 LUFS、真峰值 ≤ −1 dBTP；渲染器自动追加 2 秒「IT小村 · 原创」片尾。
5. **审核**：自检帧数、响度、音画同步、术语标签显示时长（≥63 帧）；团队审片，村长批准。
6. **上线发布**：`meta.json` 改为 `draft: false`，开 PR 合并到 `main`，GitHub Pages 自动部署站点；打 tag 发 Release；再发布到抖音、B站、快手。

## 目录结构

```
episodes/
  <slug>/                 每期一个目录
    meta.json             期号、标题、简介、标签、上线日期 publishedAt、系列 series（site/src/content/series.json）、更新日期 updatedAt（可选）、平台链接 platforms（B站/抖音/快手，未知留空）、draft、legacy（未重制的旧期，可选）
    script.md             旁白稿
    article.mdx           站点文章
    pronunciation.md      读音表
    storyboard.json       分镜（Remotion 渲染的输入）
    timing.json           配音时间 → 镜头时长
    video.mp4             成片
    cover-16x9.jpg 等     平台封面
    assets/               本期 SVG 素材
    remotion/             本期 Remotion 工程
  _shared/
    branding/             水印与片尾（ChannelBranding、spec.json）
    cover/                封面模板（Remotion Still）
    music/                背景音乐与混音脚本 mix_bgm.py
    tts/                  TTS 工具
  tts_timing.py           配音合成与计时
site/                     Astro 站点（GitHub Pages）
covers/                   封面配置
docs/                     截图等文档资料
CREDITS.md                音乐、配音等署名
```

## 本地开发与渲染

站点（`site/`，Astro）：

```sh
cd site && npm ci
npm run dev       # 本地预览（会先把各期视频、封面复制到站点）
npm run build     # 构建到 site/dist
npm run preview   # 预览构建结果
```

单期渲染（以 `episodes/<slug>/remotion/` 为例，脚本以各期 package.json 为准）：

```sh
cd episodes/<slug>/remotion && npm ci
npm run typecheck   # 同步 SVG 素材并做类型检查
npm run still       # 出静帧
npm run render      # 渲染 out/voice.mp4（--bundle-cache=false），再混 BGM 输出 ../video.mp4
```

## 平台封面（专用封面，非截帧）

模板在 `episodes/_shared/cover/`（Remotion Still：Cover169 1920×1080、Cover43 1440×1080 = 16:9 居中裁切、Cover34 1080×1440）。版式和文字来自 `episodes/<slug>/storyboard.json` 的 `cover` 节点（没有则用 `covers/cover-spec.json[slug]`）。

```sh
cd episodes/_shared/cover && npm ci   # 首次
npm run covers -- <slug>              # 输出 episodes/<slug>/cover-16x9.jpg、cover-4x3.jpg、cover-3x4.jpg（JPG ≤2MB）
npm run covers -- <slug> --out <dir> --only Cover34   # 可选：换输出目录 / 只出某个尺寸
```

安全区：16:9 内容在 x280–1640（B站 4:3 预览裁两边），y>900 不放字；3:4 顶部 y<144、底部 y>1224 不放字。

## 版本规则

- 版本号用三段式 `主.次.修订`，记在 `site/package.json`，每次发布打同名 tag 并发 Release。
- 只改内容（文字修订、重配、重渲等）升修订号（patch），例如 v0.25.0 → v0.25.1。
- 新增一期、新功能或站点改动升次版本号（minor），例如 v0.25.1 → v0.26.0。
- 上线和发布前都必须经村长批准。

## 署名

背景音乐（原文见 [CREDITS.md](CREDITS.md)）：

"Wallpaper" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
http://creativecommons.org/licenses/by/4.0/

配音、动画等其他署名见 [CREDITS.md](CREDITS.md)。
