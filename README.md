# video-studio · IT小村工作室

IT小村工作室的互联网开发技术科普短视频项目。一条主线讲清楚一个问题，画面不用比喻。视频用代码生成（[Remotion](https://www.remotion.dev/)），每期配一篇图文文章。

做片的人从 [AGENTS.md](AGENTS.md) 进入，规范以 [docs/RULES.md](docs/RULES.md) 为准，步骤以 [docs/pipeline.md](docs/pipeline.md) 为准。

- 线上站点：https://linhongcun.github.io/video-studio/
- 发布平台：抖音（头条同步）、B站、微信视频号，以及本站。不发快手，不发 X。2026-10-16 的「发抖音、B站、快手」已废止，见 [docs/RULES.md](docs/RULES.md)。已上线 `meta.json` 里残留的快手链接是历史记录。
- 站点功能：按系列浏览（浏览器与网络 / 后台缓存 / 扛住高峰 / 数据库 / 分布式）、站内搜索（Pagefind）、[更新日志](https://linhongcun.github.io/video-studio/changelog/)（构建时读取 GitHub Releases，发 Release 后自动重新部署）
- 订阅：[RSS](https://linhongcun.github.io/video-studio/rss.xml) · [站点地图](https://linhongcun.github.io/video-studio/sitemap-index.xml)
- 成片：每期 `episodes/<slug>/video.mp4`，各版本变更见 [Releases](https://github.com/linhongcun/video-studio/releases)

## 已上线剧集

剧集信息来自各期的 `episodes/<slug>/meta.json`（`draft: false`）。期号按 2026-10-21 新排期（[#91](https://github.com/linhongcun/video-studio/issues/91)）：EP.01–15 已重制；EP.16–21 目前是旧版（`meta.json` 写 `"legacy": true`，站点显示「旧版，重制中」），重制版上线时去掉；原 EP.16 隔离级别（`db-isolation`）已下架（`draft: true`，源文件保留）。第 9 至 14 期演示网页已改为深色页身（v0.45.0）；EP.15 索引在 v0.45.1 更新为订单表查找动画，均只更新站点，不重发平台。

系列默认暂停。2026-10-24 用户单独授权 EP.15 索引重制，并在观看成片后批准合并、部署 GitHub 站点；其他新期与平台新发尚未恢复。状态以 [docs/RULES.md](docs/RULES.md) 的 STATUS 为准。

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

完整清单在 [docs/pipeline.md](docs/pipeline.md)。顺序是：调研 → `script.md` / `article.mdx` / `pronunciation.md` → `storyboard.json` / `covers.json` → 配音冻结 → Deming 预检 → 渲染 → Nolan 与 Deming 审成片 → 村长批准上线 → 站点与三个平台。

「先讲比喻，再给术语」已废止。配音用冰糖，成片 −16 LUFS。不要再按「每句 −21 LUFS」或「渲染器一律追加 2 秒片尾」操作，这两句和现行脚本不一致，说明见 [docs/render.md](docs/render.md)。

## 目录结构

```
AGENTS.md                 给 coding agent 的入口
docs/                     RULES、pipeline、knoll-props.template.md、examples/knoll-props.degradation.md
episodes-codex/db-index/  EP.15 索引重制工程、配音与公开资料
episodes-codex/_template/ 开新期的说明（其他期仍暂停）
episodes/
  <slug>/                 站点内容。每期一个目录
    meta.json             期号、标题、简介、标签、publishedAt、series（site/src/content/series.json）、updatedAt、platforms（站点渲染 bilibili / douyin；不再新写 kuaishou）、draft、legacy
    script.md             旁白稿
    article.mdx           站点文章
    pronunciation.md      读音表
    storyboard.json       分镜
    covers.json           重制期封面（本期 Remotion 经 @covers 读取）
    words.json            词级时间与配音 SHA-256（重制期）
    video.mp4             成片
    cover-16x9.jpg 等     平台封面
    remotion/             本期 Remotion 工程
  _shared/
    branding/             水印规范 spec.json（重制期 Main.tsx 未挂 ChannelBranding）
    cover/                旧的共享封面工程（没有顶层 cover 节点的期不要用）
    music/                mix_bgm.py 与 Wallpaper
    theme/pageTheme.ts    演示页身 pageBg / pageInk
    tts/                  mimo_say.py（冰糖）
    onset_rule.py         起音规则（EP.06 起）。期目录不要另存一份
site/                     Astro 站点（GitHub Pages）
covers/cover-spec.json    仅共享封面工程使用的期
```

## 本地开发与渲染

站点（`site/`，Astro）：

```sh
cd site && npm ci
npm run dev       # 本地预览（会先把各期视频、封面复制到站点）
npm run build     # 构建到 site/dist
npm run preview   # 预览构建结果
```

重制期渲染（`episodes/degradation/remotion/package.json` 没有 `typecheck` 和 `still`）：

```sh
cd episodes/degradation/remotion && npm ci
npm run render      # out/voice.mp4，再混 BGM 得到 ../video.mp4
```

封面、静帧和共享封面工程的适用条件见 [docs/render.md](docs/render.md)。现行 4:3 安全区是 x 315..1125、y < 918，且不得出现 `COPYFIT`。以前写的「16:9 在 x280–1640、y>900 不放字；3:4 的 y<144 与 y>1224」不再作为闸门。

共享封面命令只用于分镜顶层有 `cover`，或 slug 在 `covers/cover-spec.json` 中的期：

```sh
cd episodes/_shared/cover && npm ci
npm run covers -- <slug>
```

`degradation` 两种都不是，不要对它运行 `npm run covers`。

## 版本规则

- 版本号用三段式 `主.次.修订`，记在 `site/package.json`，每次发布打同名 tag 并发 Release。
- 只改内容（文字修订、重配、重渲等）升修订号（patch），例如 v0.25.0 → v0.25.1。
- 新增一期、新功能或站点改动升次版本号（minor），例如 v0.25.1 → v0.26.0。
- 村长只批准最终上线。脚本和分镜在团队内定稿。见 [AGENTS.md](AGENTS.md)。

## 署名

背景音乐（原文见 [CREDITS.md](CREDITS.md)）：

"Wallpaper" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
http://creativecommons.org/licenses/by/4.0/

配音、动画等其他署名见 [CREDITS.md](CREDITS.md)。
