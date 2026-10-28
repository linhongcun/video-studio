# 归档与历史任务索引

这里收录已完成轮次的工作记录、旧草案和检查证据；现行手册与持续工作入口见[文档首页](../README.md)。单期的当前工程以 `episodes/<slug>/meta.json.sourcePath` 为准，历史记录里的“当前”“待完成”只描述当时阶段，阅读时结合该记录末尾的实际发布结果。

2026-10-26 整理时，将下表 13 份独立记录移入 `2026-10/`，保持文件名。JSON 回执逐字节保留，Markdown 仅调整链接；原始帧数、SHA、检查结论与发布事实不变。旧 upstream、startup 及发布回执中的路径保留当时写法，可用下表查新位置。

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
