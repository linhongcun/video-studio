# 归档与历史任务索引

这里收录已完成轮次的工作记录、旧草案和检查证据；现行手册与持续工作入口见[文档首页](../README.md)。单期的当前工程以 `episodes/<slug>/meta.json.sourcePath` 为准，历史记录里的“当前”“待完成”只描述当时阶段，阅读时结合该记录末尾的实际发布结果。

2026-10-26 整理时，将下表 13 份独立记录移入 `2026-10/`，保持文件名。JSON 回执逐字节保留，Markdown 仅调整链接；原始帧数、SHA、检查结论与发布事实不变。旧 upstream、startup 及发布回执中的路径保留当时写法，可用下表查新位置。

- [2026-10-28 · 系列两层布局与高并发、高可用、高性能](2026-10/flat-learning-series/README.md)：系列直接对应视频，平级卡片与旧入口兼容；实际状态见记录。

- [2026-10-28 · 后台缓存归入Redis应用场景](2026-10/redis-cache-scenarios/README.md)：商品查询缓存、价格更新与一致性归入Redis，旧入口兼容；实际状态见记录。

- [2026-10-31 · 平台周报反馈接入制作流程（#449）](2026-10/platform-feedback-449/README.md)：单周观察与假设分开，补首2秒/标题检查及分平台复盘；实际效果待后续数据。

## 已迁移记录

下表旧位置均相对于仓库根目录。

| 旧位置 | 归档位置 |
| --- | --- |
| `docs/agent-video-retirement.md` | [Agent 两期撤下记录](2026-10/agent-video-retirement.md) |
| `docs/agent-video-retirement.json` | [撤下核验回执](2026-10/agent-video-retirement.json) |
| `docs/cdn-map-terms-revision.md` | [CDN 地图与术语返工](2026-10/cdn-map-terms-revision.md) |
| `docs/codex-remake-ep01-14.md` | [EP.01–14 Codex 重制](2026-10/codex-remake-ep01-14.md) |
| `docs/design-pattern-product-scene-java.md` | [设计模式流程调整与旧备选](2026-10/design-pattern-product-scene-java.md) |
| `docs/episode-date-versions.md` | [视频日期与版本功能交付](2026-10/episode-date-versions.md) |
| `docs/flow-navigation-audit.md` | [旧片全局与局部定位扫描](2026-10/flow-navigation-audit.md) |
| `docs/leetcode-platform-republish-20261025.json` | [三题平台重发回执](2026-10/leetcode-platform-republish-20261025.json) |
| `docs/mysql-database-identity.md` | [数据库身份标记调整](2026-10/mysql-database-identity.md) |
| `docs/repository-cleanup.md` | [旧工程清理记录](2026-10/repository-cleanup.md) |
| `docs/repository-cleanup-online.json` | [旧工程清理线上核验](2026-10/repository-cleanup-online.json) |
| `docs/site-learning-redesign.md` | [学习站改版交付](2026-10/site-learning-redesign.md) |
| `docs/strategy-platform-publish-20261025.json` | [策略模式平台发布回执](2026-10/strategy-platform-publish-20261025.json) |

平台回执只记录当次结果，不能代替当前作品状态或新的发片授权。

## 新期制作记录

- [MQ05–MQ07实现机制短片](2026-10/mq05-07-implementation/README.md) — EP45–47已随v0.97.0交付；固定源码、121项真实运行与660声明、31完整GET、线上226动作/66严格PTS及图审通过，三issue completed，MQ现7/9。

- [MQ01–MQ04实现原理重制](2026-10/mq-source-depth-remake/README.md)：四期补足源码实现因果，v0.96.1已上线；完整媒体与原生线上核验通过，#443已completed关闭。

- [2026-10-30 · Kafka MQ04 发送确认](2026-10/kafka-send-confirmation/README.md)：调用返回、成功结果与最终未知分支；EP44/v0.96.0，线上完整媒体与播放器核验通过，#312已关闭，MQ进度4/9。
- [2026-10-30 · Kafka MQ03 日志重放](2026-10/kafka-log-replay/README.md)：读取与恢复位置、停组回退和保留边界；EP43/v0.95.0，制作、Pages及线上完整媒体/播放器核验通过。
- [2026-10-30 · Kafka MQ02 消费组](2026-10/kafka-consumer-groups/README.md)：同组按分区分工、不同业务独立订阅；EP42/v0.93.0，制作、Pages及线上完整媒体/播放器核验通过。
- [2026-10-29 · 高并发、高可用、高性能四期正文延续封面](2026-10/peak-video-style/README.md)：EP.11–14深青蓝/亮青/暖黄正文与资料页，原机制、完整声音和时序保持；实际状态见记录。
- [2026-10-29 · 高并发、高可用、高性能四期封面统一](2026-10/peak-cover-style/README.md)：深青蓝/亮青/暖黄、真实EP与四种机制图，原媒体和冻结保留；实际状态见记录。
- [2026-10-28 · LC547从二维数组进入题目](2026-10/number-of-provinces-matrix-first/README.md)：先读isConnected并逐格建立城市连线，再解释省份与进入解法；旧源、统一封面与有效后段保留，实际状态见记录。
- [2026-10-28 · Redis缓存两期封面与正文统一](2026-10/redis-cache-style/README.md)：EP.08/09延续跳表冷银灰/Redis红，保留应用流程、完整原声与时序，实际状态见记录。

- [2026-10-28 · Redis正文延续封面](2026-10/redis-video-style/README.md)：EP.40冷银灰/Redis红正文与资料页、原层高分支和声音保持；实际状态见记录。
- [2026-10-28 · 计算机网络独立系列](2026-10/network-standalone-series/README.md)：现有Web通信7篇独立为学习方向，系统原理保留缓存与流量治理；实际检查与发布状态见记录。
- [2026-10-28 · 分布式独立系列](2026-10/distributed-standalone-series/README.md)：现有7篇独立为学习方向，系统原理保留网络、缓存与流量治理；实际检查与发布状态见记录。
- [2026-10-28 · LeetCode十一期正文延续封面](2026-10/leetcode-video-style/README.md)：深蓝/暖金/青色正文、完整Python和资料页、原音轨时序保真；状态见记录。

- [2026-10-28 · Redis系列封面统一](2026-10/redis-cover-style/README.md)：冷银灰/Redis红、真实EP与跳表定位图，旧媒体和冻结保留；实际状态见记录。
- [2026-10-28 · Kafka系列统一与MQ01重制](2026-10/kafka-series-style/README.md)：规划收敛Kafka、MQ01日志/消费位点新片与同色封面，旧输入保护；真实发布状态见记录。
- [2026-10-28 · MySQL四期正文与系列范围统一](2026-10/mysql-video-style/README.md)：EP15–18墨绿正文、MySQL 8.4范围、三比例封面与独立音轨保真；状态见记录。

- [2026-10-28 · 深浅主题与可读性修复](2026-10/site-theme-fixes/README.md)：#401–405 的首屏、插图边框、文字对比、封面图标和搜索高亮。
- [2026-10-28 · 站点交互问题修复](2026-10/site-interaction-fixes/README.md)：#386–396、#398 的导航、素材、字幕、编号、日志、404 与卡片日期修复及检查。
- [2026-10-28 · 设计模式3期封面统一](2026-10/design-pattern-cover-style/README.md)：暖砂/靛蓝、D编号和职责图，三比例独立模板与媒体保真；发布状态见记录。
- [2026-10-27 · 数据库4期封面统一](2026-10/database-cover-style/README.md)：基于最新独立数据库系列，统一墨绿模板与三比例，保留原媒体和派生文章；发布状态见记录。
- [2026-10-27 · 趣味推理5期封面统一](2026-10/puzzles-cover-style/README.md)：独立紫色模板、三比例检查与原媒体保真；状态以本轮发布记录为准。
- [2026-10-27 · LeetCode 11期封面统一](2026-10/leetcode-cover-style/README.md)：三比例模板、逐图与站点验收、旧媒体与冻结输入保真；发布状态见本轮记录。
- [2026-10-27 · LC547省份数量](2026-10/number-of-provinces/README.md)：城市相连场景、并查集推导及实际交付检查，状态以记录中的发布回执为准。

## 保留原路径的历史记录

下列目录包含冻结输入、原文证据、历史检查工具或相对路径引用，保留原位置。这里将它们统一归入历史检索；目录仍存在不表示任务仍未完成，也不表示其中的脚本是新片默认入口。

| 已完成轮次 | 记录与证据 |
| --- | --- |
| EP.01–14 重制、全局导航扫描 | [重制证据](../codex-remake-ep01-14/)、[导航扫描证据](../flow-navigation-audit/) |
| HTTP 技术深度、CDN 地图术语 | [HTTP 修订](../http-request-depth/README.md)、[CDN 证据](../cdn-map-terms/) |
| LeetCode 题意与方法推导 | [题意修订证据](../leetcode-problem-first/)、[推导修订](../leetcode-derivation-20261025/README.md) |
| LeetCode 批次制作 | [首批](../leetcode-batch-20261025/README.md)、[后续批次](../leetcode-batch-next/README.md) |
| 楼梯、每日温度场景与栈入门 | [楼梯场景](../climbing-stairs-scene/README.md)、[栈入门](../daily-temperatures-stack-primer/README.md)、[单调栈开头](../daily-monostack-opening/README.md)、[先推导后命名](../daily-derive/README.md) |
| 岛屿数量首发与四向边界解释 | [首发](../number-of-islands/README.md)、[边界修订](../number-of-islands-boundaries/README.md) |
| 设计模式讲解流程 | [两期流程调整](../pattern-flow-ui-java/README.md)；旧候选保留于该目录的 `candidates/` |
| 观察者模式两轮修订 | [MQ 实践轮次](../observer-mq-practice/README.md)、[恢复模式主线轮次](../observer-pattern-first/README.md) |
| 数据库与中间件身份 | [MySQL 证据](../mysql-database-identity/)、[中间件标记](../middleware-identity/README.md) |
| 事务入门产品交互试点 | [交付记录](../product-scene-intro/README.md) |
| 学习站改版、平台合集整理 | [站点证据](../site-learning-redesign/)、[四平台合集](../collections-20261025/README.md) |
| 配套图文统一与原文交互 | [图文统一](../article-unification/README.md)、[按需查看原文](../citation-interaction/README.md) |
| 网站品牌图标 | [代码小村图标](../brand-icon-20261026/README.md) |
| 策略模式旧讲稿草案 | [新手理解路径复盘](../strategy-beginner-reference.md)；旧冻结脚本仍引用此路径 |
| 分布式事务拆片与导航复核 | [拆片教学复核](../transaction-split-editorial-review.md)、[分支导航复核](../transaction-branch-navigation-review.md)；来源清单引用其原文与完整 SHA，同前缀 JSON 证据一并原位保留 |

网站背景的本地检查另见[深夜小村背景记录](../village-site-background-20261026/README.md)，发布与线上核验状态以该记录中的实际回执为准。

## 参考资料补齐的已完成批次

原47期存量参考资料补齐已全部完成，截至v0.77.2的48期发布视频均有附录；新片继续默认生成并核验参考资料。完整范围与实际发布状态见[存量清单](../reference-endcards/inventory.json)。以下入口记录各批次完成证据；被制作工程和冻结清单引用的文件保持原路径。

| 批次 | 后续样式修订 |
| --- | --- |
| [1](../reference-endcards/batch-1/README.md) · [2](../reference-endcards/batch-2/README.md) · [3](../reference-endcards/batch-3/README.md) · [4](../reference-endcards/batch-4/README.md) · [5](../reference-endcards/batch-5/README.md) · [6](../reference-endcards/batch-6/README.md) · [7](../reference-endcards/batch-7/README.md) · [8](../reference-endcards/batch-8/README.md) · [9](../reference-endcards/batch-9/README.md) · [10](../reference-endcards/batch-10/README.md) · [11](2026-10/reference-endcards-batch-11/README.md) · [12](2026-10/reference-endcards-batch-12/README.md) | [原题核对](../reference-endcards/original-titles/README.md) · [原题与署名列表](../reference-endcards/title-author/README.md) |

后续文档的存放、收尾与迁移要求见[文档维护规范](../RULES.md#文档维护)。

- [趣味推理正文与封面视觉统一（2026-10-28）](2026-10/puzzles-video-style/README.md)：P01–P05紫色正文、独立冻结及实际制作检查。
