# 《什么是分布式事务？》核心资料核验

访问日期：2026-10-24（北京时间）。本次通过可用网页检索工具实际打开官方正文，不以旧EP.21稿件、聊天记忆或搜索摘要充当引用。本文核验脚本与文章的技术主张，不代表配音、动态预演、成片或线上检查已经完成。

## 本期要回答什么

本期是现有[分布式事务方案详解](../../episodes/distributed-tx/article.mdx)的前置。先用同一笔订单建立“一个业务目标、独立提交边界、部分成功、结果未知、可恢复收尾”的认识，再让观众进入后续各方案。视频只首次引入本地事务、分布式事务、最终一致三个术语，不抢先列出全部协议缩写。

严格的数据库分布式事务通常关注跨参与资源的统一提交。业务开发中，Saga、可靠消息也常进入分布式事务的方案讨论，但各自提供的原子性、隔离与中间状态保证并不相同。本片用“跨独立提交边界的业务协作”引入这一问题，不宣称所有工程路线都是同一笔全局ACID事务。

## 实际阅读记录

| ID | 公开正文与实际阅读位置 | 用于本片的独立转述与边界 |
|---|---|---|
| R1 | [PostgreSQL当前事务教程](https://www.postgresql.org/docs/current/tutorial-transactions.html)，3.4 Transactions，正文原子性、BEGIN/COMMIT/ROLLBACK段落 | 多步操作要受同一笔事务管理，才有该事务的共同提交或撤销；同一个数据库里执行的两笔独立事务并不会自动合为一笔。脚本04–07只讨论事务型数据。 |
| R2 | [MySQL 8.4 XA Transactions](https://dev.mysql.com/doc/refman/8.4/en/xa.html)，全局事务、资源管理器、两阶段处理段落 | 统一协调可跨多个参与资源，各资源仍有自己的事务分支。17镜第一类思路据此绘制，不推导“所有数据库在同一毫秒可见”或所有方案具有相同全局隔离。 |
| R3 | [AWS：Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)，Retrying and side effects、Reducing client complexity、Late arriving requests | 没收到回复不等于没有执行；重试可能重复副作用。用同一操作标识识别重复，标识记录与业务效果需要共同原子保存；单凭相同参数推断重复不总正确。 |
| R4 | [AWS：Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)，Intent、Motivation、Issues and considerations、Using an outbox table | 本地写入与外发通知是不同操作，之间可出现故障空档；持久进度要与本地业务正确衔接。视频不展示Outbox实现，具体机制留方案详解。 |
| R5 | [AWS：Saga patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-patterns.html)，sequence of local transactions、continuation/compensation段落 | 各步本地提交后，需要依据结果决定向前恢复还是业务补偿；临时技术故障与永久业务拒绝不能用同一条“不断重试必成功”概括。支撑16、17镜。 |
| R6 | [Azure：Compensating Transaction](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)，Context and problem、Solution、Problems and considerations | 中间状态可见时，收尾规则依赖业务；补偿不是把数据库快照直接覆写回去。持久进度、可重复执行、失败恢复与必要的人工介入都要设计。支撑14–19镜的边界。 |
| R7 | [Azure：Retry](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry)，Solution、Retry strategies、Issues and considerations | 重试用于适合重试的临时故障，需有次数/间隔/终止策略；不适合重试的故障应走异常处理。本文不使用资料中的示例时延或吞吐数字。 |
| R8 | [Seata：What Is Seata?](https://seata.apache.org/docs/overview/what-is-seata/)，AT Overall mechanism、Read isolation | AT可在全局完成前本地提交，普通读的隔离与全局状态也要另看。这是“不同方案保证不同”的交叉核对，仅用于文章边界与深入片连接，不在前置片塞入产品模式术语。 |

以上均为访问时的当前官方文档正文；没有依据页脚推断原始发表年份。另实际阅读[AWS：Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)，页面标注2019-12-05，**仅参考**：用于交叉核对“timeout/failure不表示副作用必然没发生”；本片关键重试事实由R3、R7当前官方正文支持，不依赖该早期文章。

## 镜头到主张的映射

| 镜号 | 主张 | 依据 |
|---|---|---|
| 01–03 | 已记录订单不等于整个下单流程完成；示例成功规则同时约束订单和库存 | R4、R5支持多步业务可能局部成功；订单8124、商品7042、库存4买1和本例成功条件是明示教学设定，并非官方电商规则。 |
| 04–07 | 同一笔本地事务可共同提交或撤销受它管理的修改 | R1；画面须明确同笔事务，不把同库当成充分条件。 |
| 08–11 | 独立提交边界需要额外协调；本地回滚不能撤销另一边已提交操作 | R2、R5、R6；机器数量和微服务数量不是此处判断依据。 |
| 12–14 | 超时未知；重复扣减与盲目反向修改都可能制造错误 | R3、R6；4→3→2和未执行4→错误返还5是互斥教学分支，必须显式重置。 |
| 15–16 | 持久进度、可核验结果、重复无额外业务效果与不同失败收尾 | R3–R7；已处理标记与库存扣减共同本地提交，防并发重复；不能把进度表本身画成完整协议。 |
| 17–19 | 协调提交与逐步推进具有不同保证；最终一致需要工作中的恢复机制与业务规则 | R2、R5、R6、R8；不是互斥、穷尽的二分类，也不是“等一会儿就必成功”。 |
| 20 | 前置片认识问题，深入片比较机制与具体边界 | 教学编排，按用户本次要求；不是对外部资料的事实主张。 |

## 需要在动画和文章中拦截的误解

- “同库一定是同一事务”“跨两台机器才叫分布式事务”。依据实际事务控制边界判断；受支持的跨资源协议也可能将多个资源协调起来。
- “订单已经记录，所以整单已成功”。本例中须保持待确认，直到库存安排满足规则。
- “超时等于对方失败”“客户端取消等待等于服务端撤销”。没有证据不能据此判未执行。
- “再扣一次总能修好”“没回复就加回一件”。14镜明确这都是错误演示，数字分别重置为3和4后展示错误2、5。
- “有一张进度表就万无一失”。业务修改、操作标识、流程进度和恢复决定必须正确持久衔接；还有并发、迟到请求、重复执行、故障策略等实现责任。
- “最终一致意味着无限等待后一定成功”。需要可推进的恢复条件，业务拒绝可按规则失败收尾；不可恢复的外部故障可能要求告警和人工处理。
- “补偿就是普通数据库回滚”“所有方案都天然全局ACID”。各方案机制与适用边界由深入片分别解释，本片不提前作虚假统一保证。

## 配音前独立复核

独立教学技术代理已逐镜阅读20镜40句脚本，未发现配音阻断项。按其意见将15镜画面明确为“库存扣减与已处理标记在同一本地事务保存”，文章补充最终一致的恢复条件。09镜采用主任务建议，明确库存库回滚不能撤销另一边已提交订单。以上是稿件复核，实际成片检查另记。

## 导航修订的官方正文复读

2026-10-24，`flow-map-20261024/#199`保持原事实，另实际阅读PostgreSQL18的Transactions140–240行，以及MicrosoftDocs官方GitHub的Compensating Transaction、Retry实际include正文与Idempotent Consumer。完整URL、SHA及实际阅读范围见research-navigation.json。

PostgreSQL共同提交/撤销支持同笔范围；Retry的Idempotency段明确“服务已成功处理却没能发出回复，重发会产生重复效果”，约束图中的结果未知；Idempotent Consumer说明业务效果和去重标记共同原子保存及并发约束；Compensating Transaction说明持久进度、业务规则、不可逆步骤与失败恢复。图中上下是管理范围对照，部分成功/未知是问题示例，不把示例拼成一笔业务必经路径，也不将两类协作思路说成穷尽二分类。

本次AWS正文直连被网络隧道403阻断，未记为重新读到；超时与重复效果使用上述实际可读的官方GitHub正文独立核对。retry.yml本身只是包装，已继续打开retry-content.md，未把包装摘要当作正文。

## 片尾参考资料

2026-10-26整理存量片尾书目，保留上述2026-10-24技术实读及其原日期口径，不把本轮题名核对改写为重新技术调研。`references.json`采用`presentation: title-author`，5项分两页、每页最多4项且默认5秒；没有明确公开个人署名，使用PostgreSQL、Oracle / MySQL及Microsoft · Azure Architecture Center发布机构，不把维护账号推定为作者。

片尾清单编号独立于前文原研究编号：R1 Transactions对应04–07镜本地事务范围；R2 XA Transactions对应08–11及17镜跨资源协调；R3 Retry pattern对应12–16镜结果未知与有界重试；R4 Compensating Transaction pattern对应部分成功、业务补偿与恢复边界；R5 Idempotent Consumer pattern对应15–16镜业务效果与已处理标记共同原子保存、并发重复，以及非消息场景的适用边界。最后一项不能仅以Retry概括替代。

Azure题名与维护信息本轮从官方固定Github源补核；四份完整GET响应的字节数及SHA与`research-navigation.json`的24日快照记录完全相同，技术读日仍保留24日。Retry使用wrapper的`metadata.title`，其论点来自实际include正文；补偿与幂等使用正文H1完整题名并保留pattern后缀。原研究、导航的完整SHA/Git blob、逐论点原记录、26日元数据请求和署名判断见[本轮证据](../../docs/reference-endcards/batch-7/sources-distributed-tx-intro.json)，完整清单见[references.md](references.md)。未重新请求或声称本轮访问PostgreSQL/MySQL官网页面，也未将旧AWS复读403写成成功。
