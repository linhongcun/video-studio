# video-studio · IT小村工作室

IT小村工作室的互联网开发技术与算法科普短视频项目。一条主线讲清楚一个问题，画面不用比喻。视频用代码生成（[Remotion](https://www.remotion.dev/)），每期配一篇图文文章。

做片的人从 [AGENTS.md](AGENTS.md) 进入，规范以 [docs/RULES.md](docs/RULES.md) 为准，步骤以 [docs/pipeline.md](docs/pipeline.md) 为准。手册、经验、策划和历史记录统一从[文档索引](docs/README.md)查找。

- 线上站点：https://linhongcun.github.io/video-studio/
- 发布平台：抖音（头条同步）、B站、微信视频号，以及本站。默认不发快手（STATUS 中逐次明确授权除外），不发 X。小红书由村长自己发，运营和 Codex 默认不发（STATUS 中逐次明确授权除外）。2026-10-16 的「发抖音、B站、快手」已废止，见 [docs/RULES.md](docs/RULES.md)。已上线 `meta.json` 里残留的快手链接是历史记录。
- 站点功能：按系列浏览（计算机网络 / Redis / 高并发、高可用、高性能 / MySQL / 分布式 / Agent 开发 / LeetCode · 算法可视化 / 设计模式 / 趣味推理 / 工程算法 / 消息队列）、站内搜索（Pagefind）、[更新日志](https://linhongcun.github.io/video-studio/changelog/)（构建时读取 GitHub Releases，发 Release 后自动重新部署）
- 订阅：[RSS](https://linhongcun.github.io/video-studio/rss.xml) · [站点地图](https://linhongcun.github.io/video-studio/sitemap-index.xml)
- 成片：每期 `episodes/<slug>/video.mp4`，各版本变更见 [Releases](https://github.com/linhongcun/video-studio/releases)

<!-- batch-12-publication-archive:start -->
固定原47期参考资料补齐已完成，该批48期发布视频均已补齐原题与作者/机构附录；新期默认生成并继续核验。真实发布与检查范围见[完成归档](docs/archive/2026-10/reference-endcards-batch-12/README.md)，固定存量与新增视频分别见[清单](docs/reference-endcards/inventory.json)。
<!-- batch-12-publication-archive:end -->

## 已上线剧集

剧集信息来自各期的 `episodes/<slug>/meta.json`。当前制作入口由 `sourcePath` 指向 `episodes-codex/`；EP.01–21 已完成重制，完整版本记录见 [Releases](https://github.com/linhongcun/video-studio/releases) 和 [制作记忆](docs/production-memory.md)。已下架的隔离级别旧片和被替代工程已从工作树清理，仍可通过 Git 历史恢复，详见 [清理记录](docs/archive/2026-10/repository-cleanup.md)。

GitHub 主干、Release 和站点沿用用户持续授权，完成制作与检查后自主发布；平台新发另行授权。状态以 [docs/RULES.md](docs/RULES.md) 的 STATUS 为准。

| 期 | 系列 | 标题 | 站点 | 上线日期 |
|---|---|---|---|---|
| 1 | 计算机网络 | 浏览器输入网址后发生了什么？ | [http-request](https://linhongcun.github.io/video-studio/episodes/http-request/) | 2026-10-12 |
| 2 | 计算机网络 | HTTPS 为什么安全？ | [https](https://linhongcun.github.io/video-studio/episodes/https/) | 2026-10-12 |
| 3 | 计算机网络 | 输入网址后，怎么找到服务器？ | [dns](https://linhongcun.github.io/video-studio/episodes/dns/) | 2026-10-12 |
| 4 | 计算机网络 | 网站怎么记住你已经登录？ | [cookie-session](https://linhongcun.github.io/video-studio/episodes/cookie-session/) | 2026-10-12 |
| 5 | 计算机网络 | 网站离你那么远，为什么还这么快？ | [cdn](https://linhongcun.github.io/video-studio/episodes/cdn/) | 2026-10-12 |
| 6 | 计算机网络 | 一台服务器忙不过来，怎么办？ | [load-balancing](https://linhongcun.github.io/video-studio/episodes/load-balancing/) | 2026-10-12 |
| 7 | 计算机网络 | 同一个网页，第二次打开为什么快这么多？ | [browser-cache](https://linhongcun.github.io/video-studio/episodes/browser-cache/) | 2026-10-12 |
| 8 | Redis 系列 | 数据库明明有数据，为什么还要再存一份？ | [server-cache](https://linhongcun.github.io/video-studio/episodes/server-cache/) | 2026-10-13 |
| 9 | Redis 系列 | 后台改了价格，页面怎么还是旧的？ | [cache-consistency](https://linhongcun.github.io/video-studio/episodes/cache-consistency/) | 2026-10-16 |
| 10 | 消息队列 | 订单已提交，为什么还没处理完？ | [message-queue](https://linhongcun.github.io/video-studio/episodes/message-queue/) | 2026-10-13 |
| 11 | 高并发、高可用、高性能 | 抢票时，为什么总提示系统繁忙？ | [rate-limit](https://linhongcun.github.io/video-studio/episodes/rate-limit/) | 2026-10-13 |
| 12 | 高并发、高可用、高性能 | 手一抖点了两次支付，为什么只扣一次钱？ | [idempotency](https://linhongcun.github.io/video-studio/episodes/idempotency/) | 2026-10-13 |
| 13 | 高并发、高可用、高性能 | 一个服务出故障，为什么整个网站没跟着崩？ | [circuit-breaker](https://linhongcun.github.io/video-studio/episodes/circuit-breaker/) | 2026-10-14 |
| 14 | 高并发、高可用、高性能 | 搜索页和结算页，为什么两个价不一样？ | [degradation](https://linhongcun.github.io/video-studio/episodes/degradation/) | 2026-10-13 |
| 15 | MySQL | 加个索引，为啥就快了？ | [db-index](https://linhongcun.github.io/video-studio/episodes/db-index/) | 2026-10-14 |
| 16 | MySQL | 扣了钱，对方没到账？ | [db-transaction](https://linhongcun.github.io/video-studio/episodes/db-transaction/) | 2026-10-14 |
| 17 | MySQL | 两个人抢最后一件货，听谁的？ | [db-lock](https://linhongcun.github.io/video-studio/episodes/db-lock/) | 2026-10-15 |
| 18 | MySQL | 刚改的昵称，怎么又变回去了？ | [db-replication](https://linhongcun.github.io/video-studio/episodes/db-replication/) | 2026-10-15 |
| 19 | 分布式 | 订单太多，一个数据库装不下怎么办？ | [db-sharding](https://linhongcun.github.io/video-studio/episodes/db-sharding/) | 2026-10-15 |
| 20 | 分布式 | 分布式 ID：两个订单，怎么撞成同一个号了？ | [global-id](https://linhongcun.github.io/video-studio/episodes/global-id/) | 2026-10-15 |
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

## 工程算法

从扩容、故障和容量约束等真实系统问题出发，研究算法解决了什么、怎样工作，以及维护成本和适用边界。首批选题见[系列总览 #294](https://github.com/linhongcun/video-studio/issues/294)，首期为[EA01 一致性哈希](https://linhongcun.github.io/video-studio/episodes/consistent-hashing/)，约3分21秒（含5秒参考资料卡）；[制作与检查](episodes-codex/consistent-hashing/README.md)保留同一组十键的取余/哈希环对比、虚拟位置与迁移边界。第二期为[布隆过滤器](https://linhongcun.github.io/video-studio/episodes/bloom-filter/)，约3分16秒（含5秒原题资料卡）；用同一位数组解释安全排除、误判、共享位删除风险和同步前提，[制作与检查](episodes-codex/bloom-filter/README.md)分别保留来源、动态、成片与网站证据。其余选题待后续安排，候选不作为已上线内容。

## 消息队列

独立系列从任务提交、排队到处理完成讲一条消息怎样接力，与其他系列并列，可以独立观看。首期为[EP.10《订单已提交，为什么还没处理完？》](https://linhongcun.github.io/video-studio/episodes/message-queue/)，约2分08秒（含5秒参考资料卡）；系列页见[消息队列](https://linhongcun.github.io/video-studio/series/message-queue/)。制作入口见[本期工程](episodes-codex/message-queue/revisions/kafka-intro/message-queue/README.md)。第二期[MQ02 / EP.42《多个消费者：分工处理，还是每人一份？》](https://linhongcun.github.io/video-studio/episodes/kafka-consumer-groups/)约2分钟，用同一批订单事件对照独立消费组与组内分工；[本期制作与检查](episodes-codex/kafka-consumer-groups/README.md)。

## 高并发、高可用、高性能

[独立系列](https://linhongcun.github.io/video-studio/series/peak/)从限流、幂等、熔断与降级四期出发，理解高峰流量、重复请求和服务故障的处理过程与边界。全站采用“系列 → 视频”两层结构，首页并列展示系列，系列目录直接列视频，不再保留“系统原理”中间分组。原`peak`目录与EP.11–14链接、内容时间和媒体保持。布局、兼容与验证见[本轮记录](docs/archive/2026-10/flat-learning-series/README.md)。

## 计算机网络

[计算机网络独立系列](https://linhongcun.github.io/video-studio/series/request/)以现有7篇Web通信入门内容为范围，从浏览器请求出发，讲解HTTP、HTTPS、DNS、登录态、CDN、负载均衡与浏览器缓存。EP.01–07沿原顺序独立学习，不再作为系统原理的章节或前后课；限流、幂等、熔断与降级归入“高并发、高可用、高性能”独立系列；服务端缓存与缓存一致性归入Redis应用场景。原`request`系列ID、URL、EP编号、文章、媒体与内容时间保留，分类与发布状态见[本轮记录](docs/archive/2026-10/network-standalone-series/README.md)。

## MySQL

[MySQL独立系列](https://linhongcun.github.io/video-studio/series/database/)以MySQL 8.4为背景，从InnoDB索引、事务与锁，到MySQL单主异步复制，后续持续扩充MySQL工作原理与设计取舍；具体存储引擎、复制模式和适用条件按单集说明。现有[EP.15 索引](https://linhongcun.github.io/video-studio/episodes/db-index/)、[EP.16 事务](https://linhongcun.github.io/video-studio/episodes/db-transaction/)、[EP.17 锁](https://linhongcun.github.io/video-studio/episodes/db-lock/)与[EP.18 主从复制](https://linhongcun.github.io/video-studio/episodes/db-replication/)归入这一独立系列，不再作为系统原理的章节或前后课。原期号、URL与首发身份保留，系列目录只展示实际已发布内容。

## 分布式

[分布式独立系列](https://linhongcun.github.io/video-studio/series/distributed/)从分库分表、分布式 ID，进入事务入门与2PC、TCC、Saga、Outbox四种实现，共7篇已发布内容。系列内沿原学习顺序衔接，不再作为系统原理的章节或前后课；限流、幂等、熔断与降级归入“高并发、高可用、高性能”独立系列；后台缓存两课归入Redis应用场景。原URL、EP编号、内容时间与媒体保留，历史事务合集继续只供回看。分类与发布状态见[本轮记录](docs/archive/2026-10/distributed-standalone-series/README.md)。

## Redis

[Redis系列](https://linhongcun.github.io/video-studio/series/redis/)从应用场景到内部机制：EP.08《数据库明明有数据，为什么还要再存一份？》讲商品查询缓存，EP.09《后台改了价格，页面怎么还是旧的？》讲商品价格更新与缓存一致性，EP.40继续讲跳表。两条缓存视频作为应用场景独立展示，原题名、期号、URL、内容时间与媒体保持；旧`/series/cache/`入口转到Redis目录。它们讲应用管理的服务端缓存流程，以Redis共享缓存为实现示例，不将通用缓存流程改称Redis命令实战。

## 制作流程

完整清单在 [docs/pipeline.md](docs/pipeline.md)。顺序是：调研 → `script.md` / `article.mdx` / `pronunciation.md` → `storyboard.json` / `covers.json` → 配音冻结 → Deming 预检 → 渲染 → Nolan 与 Deming 审成片 → 按持续授权合并、Release、部署 GitHub 站点 → 线上文件核验；三个平台另行授权。

「先讲比喻，再给术语」已废止。配音用冰糖，成片 −16 LUFS。不要再按「每句 −21 LUFS」或「渲染器一律追加 2 秒片尾」操作，这两句和现行脚本不一致，说明见 [docs/render.md](docs/render.md)。

## 目录结构

```
AGENTS.md                   项目入口
docs/                      规范、手册、经验与现行策划；入口 README.md
   archive/                 已完成记录与保留原路径的历史证据索引
episodes-codex/
   <slug>/                  当前制作工程，以 meta.json.sourcePath 为准
     remotion/              动画、逐期封面与渲染命令
     voice/、voice.wav      配音原稿和选定素材
     source-sha256.json     冻结输入清单
   _shared/                 句级装配、冻结、编码检查与流程导航
   _template/               新期入口
episodes/
   <slug>/                  站点发布内容：meta、文章、分镜、字幕、MP4、JPG
   _shared/                 共享配音、起音、混音、主题和有效回归样本
site/                      Astro 站点（GitHub Pages）
```

发布目录不另存旧动画工程、WAV 或 PNG 原稿；幕后源码链接由 `meta.json.sourcePath` 指向制作工程。用户已要求删除A01/EP.22与A02/EP.28两期Agent试片，相关发布内容与制作工程退出当前目录；原`agent-intro-v2/`拼接依赖不再保留。旧工程可通过Git历史追溯，当前范围与发布验证见[撤下记录](docs/archive/2026-10/agent-video-retirement.md)。后续概念研究题库继续保留。

## 本地开发与渲染

站点（`site/`，Astro）：

```sh
cd site && npm ci
npm run dev       # 本地预览（会先把各期视频、封面复制到站点）
npm run build     # 构建到 site/dist
npm run preview   # 预览构建结果
```

制作与渲染从当前期的 `episodes-codex/<slug>/README.md` 进入。例如：

```sh
cd episodes-codex/degradation/remotion && npm ci
npm run render
npm run covers
```

WAV、PNG 等制作原稿留在制作工程；站点使用检查通过的 MP4 与 JPG。冻结、封面和静帧检查见 [docs/render.md](docs/render.md)。

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
