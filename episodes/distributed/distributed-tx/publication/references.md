# distributed-tx 片尾参考资料

以下8项是本历史合集各章的核心精选资料，每项技术正文均沿用2026-10-24（北京时间）的实际阅读记录。题名、作者和机构分别依据原书目、已有固定官方存档或本轮必要的题名metadata补核；补核日期另记，不冒充技术正文重读。原文全部章节、脚注和18项来源记录继续保留，精选清单不替代完整依据；本片的历史归档与后续分集入口保持。

`title-author`：8项2页，每页最多4项、5秒；视频只有实际原题和明确作者或机构，日期、定位和链接留在文章/内部记录。

**[R1] XA Transactions**

Oracle / MySQL · MySQL 8.4 Reference Manual：[正式资料](https://dev.mysql.com/doc/refman/8.4/en/xa.html)；[本合集既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/distributed-tx/research.md#L23)。

支持范围：事务管理器与资源管理器通过XA协作，准备阶段与最终提交或回滚阶段分开。；2PC描述提交过程，XA提供协作接口；原子终决不自动推出跨库全局快照、同毫秒可见或全局串行化。

边界：准备态恢复、锁和连接生命周期的细节仍由原A2/A3/A4脚注补充；本精选条目不冒称整个MySQL手册所有章节都为同一页。；仅受控且支持相关接口的资源可参与，普通HTTP或邮件副作用不会因名称自动纳入。

内部定位：XA Transactions：全局事务；TM/RM；两阶段提交过程

**[R2] Seata AT mode**

Apache Seata · Seata AT开发原理文档 · 原技术实读2026-10-24：[正式资料](https://seata.apache.org/docs/dev/mode/at-mode/)；[本合集既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/distributed-tx/research.md#L28)。 [原题固定官方证据（2026-10-26）](https://github.com/apache/incubator-seata-website/blob/ae31c10be89d7cca4d3a7010f3875d30992731c8/i18n/en/docusaurus-plugin-content-docs/current/dev/mode/at-mode.md)。

支持范围：Seata AT将业务修改与undo_log同一本地事务提交，先释放本地锁；全局锁仍控制参与写入。；二阶段失败需校验数据后按日志补偿，普通SELECT不自动获得相同全局读隔离保护。

边界：本条特指Seata AT，不泛化为全部框架；支持数据库、SQL、代理及参与路径仍有条件。；不能盲目覆盖别人的合法写入，也不能自动撤销邮件、外部付款等任意副作用。

内部定位：Write isolation；Read isolation；Phase 1；Phase 2

**[R3] Seata TCC Mode**

Apache Seata · Seata TCC用户文档 · 原技术实读2026-10-24：[正式资料](https://seata.apache.org/docs/user/mode/tcc/)；[本合集既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/distributed-tx/research.md#L30)。 [原题固定官方证据（2026-10-26）](https://github.com/apache/incubator-seata-website/blob/ae31c10be89d7cca4d3a7010f3875d30992731c8/i18n/en/docusaurus-plugin-content-docs/current/user/mode/tcc.md)。

支持范围：业务提供检查预留、确认与取消，预留之后按决定择一确认或释放，不是三个操作顺次全做。；需要侵入业务资源设计，不能把一次查询或数据库通用回滚当作已持久预留。

边界：幂等、空回滚、悬挂和Try本地保存细节仍由原C2/C3及Fence脚注补充，未从视频或文章删除。；只引用公开Seata实现，不宣称Seata是唯一TCC方案或所有业务天然正确。

内部定位：Overview；Disadvantages；Try、Confirm、Cancel业务操作

**[R4] SEATA Saga Pattern**

Apache Seata · Seata Saga用户文档 · 原技术实读2026-10-24：[正式资料](https://seata.apache.org/docs/user/mode/saga/)；[本合集既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/distributed-tx/research.md#L33)。 [原题固定官方证据（2026-10-26）](https://github.com/apache/incubator-seata-website/blob/ae31c10be89d7cca4d3a7010f3875d30992731c8/i18n/en/docusaurus-plugin-content-docs/current/user/mode/saga.md)。

支持范围：参与者逐步提交本地事务，失败可发起业务补偿，不能把已提交效果说成从未发生。；没有天然跨整个流程的事务隔离，中间状态与业务并发需另行设计。

边界：此处是Seata公开Saga机制，不把它的组织方式当所有Saga唯一实现；原AWS变体脚注仍保留。；没有引用页面链接的1987论文为本片已读原文，也不为完整性追加历史理论来源。

内部定位：Overview；Dealing with Lack of Isolation

**[R5] Compensating Transaction pattern**

Microsoft · Azure Architecture Center · Azure Architecture Center · 原技术实读2026-10-24：[正式资料](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)；[本合集既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/distributed-tx/research.md#L36)。 [原题固定官方证据（2026-10-26）](https://github.com/MicrosoftDocs/architecture-center/blob/498e83a207cfd512b396489e95ed3f791b372364/docs/patterns/compensating-transaction.md)。

支持范围：补偿依赖业务语义，是已提交之后的新动作，不必抹掉历史、覆写旧快照或严格反向执行。；补偿本身也会失败，需要持久进度、可重试与幂等、监控及必要人工处理。

边界：ms.author和author维护账号不是公开个人署名；采用机构而不把账号猜成人名。；不能承诺所有外部动作可逆或补偿必然成功。

内部定位：Solution；Problems and considerations

**[R6] Transactional outbox pattern**

Amazon Web Services · AWS Prescriptive Guidance · 原技术实读2026-10-24：[正式资料](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)；[本合集既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/distributed-tx/research.md#L37)。 [既有原题书目记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/tx-outbox/article.mdx#L47)。

支持范围：业务行和待发事件在同库本地事务中一起保存，另行发送以衔接本地持久化和通知。；可能重复投递，消费端需要幂等；Outbox不把下游库存库纳入生产端同一原子事务。

边界：完整题名由既有24日Outbox原书目补充核对，不声称本轮GET了当前AWS H1或新技术正文。；发送恢复、消费处理及永久业务拒绝需要另外收尾；消息确认不等于库存业务已成功。

内部定位：Intent；Issues and considerations；Using an outbox table

**[R7] Transaction Message**

Apache RocketMQ · Apache RocketMQ事务消息文档 · 原技术实读2026-10-24：[正式资料](https://rocketmq.apache.org/docs/featureBehavior/04transactionmessage/)；[本合集既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/distributed-tx/research.md#L38)。 [原题固定官方证据（2026-10-26）](https://github.com/apache/rocketmq-site/blob/fd076ce3777a04f18bdc4ad7c6aff22ec031082b/i18n/en/docusaurus-plugin-content-docs/version-5.0/04-featureBehavior/04transactionmessage.md)。

支持范围：先保存暂不可投递的半消息，再执行本地事务，报告提交或取消；未知结果时回查生产端本地事务状态。；真实边界是本地事务与消息可投递性，不能自动保障消费端业务与上游共同成功。

边界：回查不是重做扣款，也不是询问下游库存结果；回查时限、次数和终止需遵守具体系统策略。；固定version5.0英文源仅补实际题名，不把metadata获取改写成当前部署配置或24日上游SHA证据。

内部定位：Working mechanism；Usage limits；Usage notes

**[R8] Handling duplicate messages using the Idempotent consumer pattern**

Chris Richardson（发布机构：microservices.io） · 2020-10-16 · 原作者公开文章：[正式资料](https://microservices.io/post/microservices/patterns/2020/10/16/idempotent-consumer.html)；[本合集既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/distributed-tx/research.md#L40)。 [既有原题与署名书目记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/tx-outbox/article.mdx#L49)。

支持范围：唯一处理标识与业务修改应在同一本地事务提交，重复请求由唯一约束等原子保护拦截。；只在内存查重、先查询再无保护更新，或把处理标识独立提交，都不足以保证重复消费不再扣库存。

边界：原作者Chris Richardson在本片旧研究及既有24日书目明确署名，未从Git账号推定。；仅用同一事件或业务操作身份去重，不把订单出现过当作屏蔽后续合法退款的条件。

内部定位：Tracking message IDs；PROCESSED_MESSAGE

内部证据：`docs/archive/2026-10/reference-endcards-batch-12/sources-distributed-tx.json`。全部技术日期仍24日；metadata日期与真正读取范围分别记录。
