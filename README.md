# video-studio · IT小村工作室

IT小村工作室的互联网开发技术与算法科普短视频项目。一条主线讲清楚一个问题，画面不用比喻。视频用代码生成（[Remotion](https://www.remotion.dev/)），每期配一篇图文文章。

做片的人从 [AGENTS.md](AGENTS.md) 进入，规范以 [docs/RULES.md](docs/RULES.md) 为准，步骤以 [docs/pipeline.md](docs/pipeline.md) 为准。

- 线上站点：https://linhongcun.github.io/video-studio/
- 发布平台：抖音（头条同步）、B站、微信视频号，以及本站。不发快手，不发 X。2026-10-16 的「发抖音、B站、快手」已废止，见 [docs/RULES.md](docs/RULES.md)。已上线 `meta.json` 里残留的快手链接是历史记录。
- 站点功能：按系列浏览（浏览器与网络 / 后台缓存 / 扛住高峰 / 数据库 / 分布式 / LeetCode · 算法可视化 / Agent 开发 / 设计模式 / 趣味推理）、站内搜索（Pagefind）、[更新日志](https://linhongcun.github.io/video-studio/changelog/)（构建时读取 GitHub Releases，发 Release 后自动重新部署）
- 订阅：[RSS](https://linhongcun.github.io/video-studio/rss.xml) · [站点地图](https://linhongcun.github.io/video-studio/sitemap-index.xml)
- 成片：每期 `episodes/<slug>/video.mp4`，各版本变更见 [Releases](https://github.com/linhongcun/video-studio/releases)

## 已上线剧集

剧集信息来自各期的 `episodes/<slug>/meta.json`（`draft: false`）。期号按 2026-10-21 新排期（[#91](https://github.com/linhongcun/video-studio/issues/91)）：EP.01–21 已重制；原 EP.16 隔离级别（`db-isolation`）已下架（`draft: true`，源文件保留）。第 9 至 14 期演示网页已改为深色页身（v0.45.0）；EP.15 索引在 v0.45.1 更新为订单表查找动画；EP.16 事务在 v0.45.2 更新为逐步展示修改、提交和回滚的动画；EP.17 锁在 v0.45.3 更新为加锁读取、等待后重新检查库存的动画。v0.45.4 重制 EP.18–21，分别用昵称复制、按用户分片、号码字段与持久待办事件展示主从复制、分库分表、全局 ID 和跨服务一致性。以上均只更新站点，不重发平台。

2026-10-24 用户批准 EP.17 合并及 GitHub 站点发布，并持续授权后续视频制作和质量检查完成后自主合并、上线，有反馈再修正发布，不再逐次等待确认。该授权适用于 GitHub 主干、Release 和本站；平台新发仍需单独授权。状态以 [docs/RULES.md](docs/RULES.md) 的 STATUS 为准。

v0.48.0 已将 EP.01–14 的上一轮 Cursor 重制版全部替换为本轮 Codex 版：160镜、320句新配音，逐期重写脚本与主体动画，补齐章节导航和字幕。制作与检查见[本轮批次记录](docs/codex-remake-ep01-14.md)，当前源码由各期 `sourcePath` 指向 `episodes-codex/`。只上本站，历史平台投稿保留。

v0.50.3 更新 EP.05 CDN：在地图上演示临近边缘节点取图，并结合动作介绍CDN、边缘节点和回源；修订与实际检查见[本次记录](docs/cdn-map-terms-revision.md)。

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
| 10 | 扛住高峰 | 订单已提交，为什么还没处理完？ | [message-queue](https://linhongcun.github.io/video-studio/episodes/message-queue/) | 2026-10-13 |
| 11 | 扛住高峰 | 抢票时，为什么总提示系统繁忙？ | [rate-limit](https://linhongcun.github.io/video-studio/episodes/rate-limit/) | 2026-10-13 |
| 12 | 扛住高峰 | 手一抖点了两次支付，为什么只扣一次钱？ | [idempotency](https://linhongcun.github.io/video-studio/episodes/idempotency/) | 2026-10-13 |
| 13 | 扛住高峰 | 一个服务出故障，为什么整个网站没跟着崩？ | [circuit-breaker](https://linhongcun.github.io/video-studio/episodes/circuit-breaker/) | 2026-10-14 |
| 14 | 扛住高峰 | 搜索页和结算页，为什么两个价不一样？ | [degradation](https://linhongcun.github.io/video-studio/episodes/degradation/) | 2026-10-13 |
| 15 | 数据库 | 加个索引，为啥就快了？ | [db-index](https://linhongcun.github.io/video-studio/episodes/db-index/) | 2026-10-14 |
| 16 | 数据库 | 扣了钱，对方没到账？ | [db-transaction](https://linhongcun.github.io/video-studio/episodes/db-transaction/) | 2026-10-14 |
| 17 | 数据库 | 两个人抢最后一件货，听谁的？ | [db-lock](https://linhongcun.github.io/video-studio/episodes/db-lock/) | 2026-10-15 |
| 18 | 数据库 | 刚改的昵称，怎么又变回去了？ | [db-replication](https://linhongcun.github.io/video-studio/episodes/db-replication/) | 2026-10-15 |
| 19 | 分布式 | 订单太多，一个数据库装不下怎么办？ | [db-sharding](https://linhongcun.github.io/video-studio/episodes/db-sharding/) | 2026-10-15 |
| 20 | 分布式 | 两个订单，怎么撞成同一个号了？ | [global-id](https://linhongcun.github.io/video-studio/episodes/global-id/) | 2026-10-15 |
| 21 · 入门 | 分布式 | 什么是分布式事务？ | [distributed-tx-intro](https://linhongcun.github.io/video-studio/episodes/distributed-tx-intro/) | 2026-10-24 |
| 21 · 2PC | 分布式 | 两阶段提交，两个库怎么共同确认？ | [tx-2pc](https://linhongcun.github.io/video-studio/episodes/tx-2pc/) | 2026-10-24 |
| 21 · TCC | 分布式 | TCC：先预留，再确认 | [tx-tcc](https://linhongcun.github.io/video-studio/episodes/tx-tcc/) | 2026-10-24 |
| 21 · Saga | 分布式 | Saga：扣款成功，缺货了怎么办？ | [tx-saga](https://linhongcun.github.io/video-studio/episodes/tx-saga/) | 2026-10-24 |
| 21 · 可靠消息 | 分布式 | 可靠消息：Outbox怎样把通知送出去？ | [tx-outbox](https://linhongcun.github.io/video-studio/episodes/tx-outbox/) | 2026-10-24 |

EP.21按最新观看反馈改为“概念入门 → 两阶段提交 → TCC → Saga → 可靠消息（Outbox）”。每个实现独立短片，用一个示例逐步展示成功、失败和适用边界。实际时长与完整检查见各片制作入口；本批版本v0.47.0。

原约6分29秒[多方案合集](https://linhongcun.github.io/video-studio/episodes/distributed-tx/)保留历史页面与媒体，从推荐学习路径和搜索移出，页面提供独立短片入口。旧制作冻结输入不改；不能将原有机器/抽帧检查当作用户已认可合集教学效果。最新反馈和复盘见[教训L012](docs/lessons-learned.md)。

## 设计模式

独立系列每种模式制作一期，围绕“为什么需要、解决什么、什么时候值得用”展开，按具体内容选择图文、代码与动态表达。首期为[EP.23 · D01《策略模式：结算怎样换一种算价办法？》](https://linhongcun.github.io/video-studio/episodes/strategy-pattern/)，约2分27秒；同一100元订单展示稳定流程与变化策略，围绕共同约定、外侧选择、委托和独立维护解释设计思想；具体语言实现放在配套文章可选附录。制作与检查见[本期工程](episodes-codex/strategy-pattern/README.md)，选题池见[23种模式总览 #161](https://github.com/linhongcun/video-studio/issues/161)。

## LeetCode · 算法可视化

独立算法系列使用题号展示，不要求先看网络或分布式课程。首期为[LC.11《盛最多水的容器：为什么每次都移动短边？》](https://linhongcun.github.io/video-studio/episodes/container-most-water/)，22镜、约3分38秒，用同一组竖线讲清面积、整组排除依据和双指针扫描。完整Python实现与证明放配套文章，制作入口见[本期工程](episodes-codex/container-most-water/README.md)。本期只上站点。

## 趣味推理

独立系列从经典智力题出发，先交代完整题意，再用连续动画呈现每次比较、排除和信息变化。首期为[P01《25匹马赛跑：怎样用7场找出前三名？》](https://linhongcun.github.io/video-studio/episodes/horse-racing/)，18镜、约3分31秒；用同一组赛果展示“三匹确定更快”的排除见证，配套文章补充任意六场自适应策略的严格下界。制作与实际检查见[本期工程](episodes-codex/horse-racing/README.md)，后续选题见[首批10题总览 #204](https://github.com/linhongcun/video-studio/issues/204)。

## 制作流程

完整清单在 [docs/pipeline.md](docs/pipeline.md)。顺序是：调研 → `script.md` / `article.mdx` / `pronunciation.md` → `storyboard.json` / `covers.json` → 配音冻结 → Deming 预检 → 渲染 → Nolan 与 Deming 审成片 → 按持续授权合并、Release、部署 GitHub 站点 → 线上文件核验；三个平台另行授权。

「先讲比喻，再给术语」已废止。配音用冰糖，成片 −16 LUFS。不要再按「每句 −21 LUFS」或「渲染器一律追加 2 秒片尾」操作，这两句和现行脚本不一致，说明见 [docs/render.md](docs/render.md)。

## 目录结构

```
AGENTS.md                 给 coding agent 的入口
docs/                     RULES、pipeline、knoll-props.template.md、examples/knoll-props.degradation.md
episodes-codex/db-index/  EP.15 索引重制工程、配音与公开资料
episodes-codex/_template/ 开新期的说明（按当前选题和授权推进）
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
- 脚本、分镜和成片按质量流程核验；GitHub 站点沿用用户持续授权自主发布，平台发布另行授权。见 [AGENTS.md](AGENTS.md)。

## 署名

背景音乐（原文见 [CREDITS.md](CREDITS.md)）：

"Wallpaper" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
http://creativecommons.org/licenses/by/4.0/

配音、动画等其他署名见 [CREDITS.md](CREDITS.md)。
