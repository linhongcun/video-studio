# EP.21 入门：什么是分布式事务？

依据：storyboard.json 95e91c6c；covers.json 40f10a4a。冻结副本由 root 的 freeze.py 产出，以 source-sha256.json 为准。
script 2e98b2b8 / voice 86b9bd79 / words 285f4761，5155 帧，20镜。画布1920×1080；所有局部帧从本镜0起算。

## 本版相对上一冻结的变化

首次新增前置视频，无上一冻结。全片重新制作；现有方案详解视频不重渲。预演05/07中央状态曾遮挡边界标签，现改y263；06状态移到中心空隙y493，17决定状态y263。源文件和实际预演须复核后才冻结。06/09失败X移到x1630右侧空白；17工作流未执行状态改为本步待处理；18成功落点与待恢复分支各有对应顶部说明。

## 相对方案详解的变化

不展示五种方案缩写和比较矩阵。只保留订单8124、商品7042、初始库存4买1；业务不同分支明确重置。三术语04本地事务、10分布式事务、18最终一致，各在声学cue后显示；导航一律白话，不抢先显示术语。所有画面canvas，不用浏览器、DevTools、假窗口或实物比喻。

## 0. 画面类型与时序

| 镜 | 页型 | frame | 绝对起点 | 帧数 |
|---|---|---|---:|---:|
| 01 | hook | canvas | 0 | 246 |
| 02 | business-goal | canvas | 246 | 236 |
| 03 | scope | canvas | 482 | 256 |
| 04 | local-intro | canvas | 738 | 241 |
| 05 | local-commit | canvas | 979 | 227 |
| 06 | local-rollback | canvas | 1206 | 226 |
| 07 | local-boundary | canvas | 1432 | 226 |
| 08 | split-boundaries | canvas | 1658 | 226 |
| 09 | partial-success | canvas | 1884 | 233 |
| 10 | distributed-intro | canvas | 2117 | 297 |
| 11 | not-machine-count | canvas | 2414 | 237 |
| 12 | timeout | canvas | 2651 | 297 |
| 13 | two-possibilities | canvas | 2948 | 242 |
| 14 | unsafe-retry | canvas | 3190 | 272 |
| 15 | durable-progress | canvas | 3462 | 251 |
| 16 | safe-retry | canvas | 3713 | 270 |
| 17 | decision-or-workflow | canvas | 3983 | 279 |
| 18 | eventual-consistency | canvas | 4262 | 280 |
| 19 | business-boundaries | canvas | 4542 | 290 |
| 20 | bridge | canvas | 4832 | 323 |

## 1. 页型与状态帧

无browser镜。每镜由Main.tsx的visualType选择。布局由本期程序组件绘制；状态时机统一从冻结cueFrames.sentences经motion.ts的at/events计算，不另推测内部逐字起音。预演脚本直接import该events函数，采样事件前后相邻帧。

- 镜05 local-commit：150帧 joint-local-commit。
- 镜06 local-rollback：62帧 stock-failed；170帧 pending-order-discarded。
- 镜08 split-boundaries：126帧 independent-boundaries。
- 镜09 partial-success：29帧 order-local-committed；74帧 stock-failed；167帧 stock-local-rolled-back。
- 镜12 timeout：59帧 remote-stock-committed；107帧 reply-lost；167帧 caller-timeout-unknown。
- 镜13 two-possibilities：73帧 switch-to-already-executed-possibility。
- 镜14 unsafe-retry：99帧 wrong-double-decrement；151帧 reset-to-never-executed-branch；220帧 wrong-reverse-increment。
- 镜15 durable-progress：75帧 stock-and-progress-local-commit；158帧 process-interrupted-record-survives；202帧 recovery-checks-record。
- 镜16 safe-retry：89帧 duplicate-recognized-stock-unchanged；156帧 separate-business-rejection-branch。
- 镜17 decision-or-workflow：51帧 durable-shared-decision；75帧 first-participant-applies；99帧 second-participant-applies；124帧 switch-to-workflow-illustration；161帧 workflow-first-step-complete；221帧 workflow-second-step-complete。
- 镜18 eventual-consistency：96帧 recovery-converges；141帧 rewind-to-stalled-recovery-branch；188帧 recovery-pauses-business-pending。

## 2. 页外角标与叠字

- 顶部左：[100,54]“分布式 · 概念入门”，字号24。五章白话导航[100,98]，字号21。
- 顶部右：[1700,54]“IT小村”，字号25；示例说明中心[1650,103]，字号19。
- 主标题：[130,190]，字号46。三术语标题的appear严格读取cueFrames.labels；所有其他首次术语不出现于更早导航。
- 字幕带：[130,925,1660,至少100]，字号40，逐句读取冻结subtitles，不加快语音。
- 片尾“IT小村 · 原创”中心[960,885]，字号23。
- 不使用strike或波纹。

## 3. 计数与同步

镜05 joint-local-commit同一帧确认订单记录与库存4→3；镜15 stock-and-progress-local-commit同一帧把库存4→3与8124-扣库存已完成标记共同保存。镜12实际库存3后回执丢失，调用方仅显示结果未知；镜16重复操作号抵达后仍3。镜14明确错误示范，分支B的3→2与重置分支A的4→5不是同一次业务顺序执行。镜18第二分支可靠推进暂停后仍库存4/整单待确认，不自动成功。

## 4. 封面

封面主标题“什么是 / 分布式事务？”，副标题“订单已记录，库存却没变”。所有数字标示“示例”。16:9画布1920×1080，内容x130..1790；4:3画布1440×1080，全部内容x315..1125、最末文字底904，小于bottom15Y918；3:4画布1080×1440，内容x110..970。poster.jpg取3:4 JPEG。封面没有COPYFIT回退。

## 5. 方框加文字镜、讨论题与衔接

boxShots=[]，全部以具体订单记录、库存和操作路径为主体，事务边界表示实际语义。讨论题：请求超时后，能否直接认定远端没有执行？第20镜引导现有“分布式事务，几种方案到底怎么选？”，不说下期见。

## 只给人看、渲染时忽略的字段

scriptVisual、direction、timing说明、cueOnset、资产说明由读者复核；渲染实际使用visualType、from、durationInFrames、cueFrames和subtitles。source-sha256与本说明承担追溯，不替代实际动画/音轨检查。
