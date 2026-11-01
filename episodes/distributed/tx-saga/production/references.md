# tx-saga · 片尾参考资料

本轮清单整理／题名补核：2026-10-26。R1–R3技术实读日期沿用本片2026-10-24（北京时间）；R4是本片2026-10-26新增技术核验，不沿用其他视频的旧读身份。

title-author清单4项、一页5秒；无明确公开个人署名，使用Microsoft · Azure Architecture Center，不把Git或ms.author账号推定为作者。原AWS书目及正文完整保留，本次未选它们，也未根据笔记缺少byline替其填写机构作者。

本轮3次完整固定官方源GET；Saga wrapper/content用于补全题名和绑定正文快照，Idempotent Consumer用于新增技术读取。Compensating/Retry完整源文件独立复制并绑定batch7原请求身份，未重记为新GET。旧Saga技术记录没有原页完整hash，不把其他期的旧hash冒充本片24日原页hash。完整原研究Git/blob/SHA、请求状态/完整响应SHA、题名及逐论点证据见[本轮证据](../../docs/reference-endcards/batch-8/sources-tx-saga.json)。

## R1 · Saga distributed transactions pattern

- 发布机构：Microsoft · Azure Architecture Center
- 版本／技术实读日期：Azure Architecture Center · 实读2026-10-24
- 正式文档：[Saga distributed transactions pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)
- 官方固定原文：[saga.yml](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/dcf29659535a230ee4d73b812d49a6953b912430/docs/patterns/saga.yml)
- 实际include正文：[saga-content.md](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/dcf29659535a230ee4d73b812d49a6953b912430/docs/patterns/saga-content.md)
- 原研究记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-saga/research.md#L10)
- 原题定位：saga.yml · name（第15行）
- 题名元数据核对日期：2026-10-26
- 正文位置：Solution · Irreversible local database changes · Potential data anomalies in sagas

对应主张：

- 业务由先后提交的本地事务推进；已提交的前一步不能靠另一数据库的回滚撤销。
- Saga没有内建跨服务全局隔离，已提交的中间状态可能被其他操作看到；适用性须先符合业务规则。

## R2 · Compensating Transaction pattern

- 发布机构：Microsoft · Azure Architecture Center
- 版本／技术实读日期：Azure Architecture Center · 实读2026-10-24
- 正式文档：[Compensating Transaction pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
- 官方固定原文：[compensating-transaction.md](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/498e83a207cfd512b396489e95ed3f791b372364/docs/patterns/compensating-transaction.md)
- 原研究记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-saga/research.md#L11)
- 原题定位：compensating-transaction.md · H1（第11行）
- 题名元数据核对日期：2026-10-26
- 正文位置：Solution · Problems and considerations · When to use this pattern

对应主张：

- 对已经提交的操作，以新的业务动作补偿；补偿不能简单覆写旧快照，也不要求抹除已发生的历史。
- 补偿本身可能失败，需要持久进度、安全重复、监控告警及必要人工处理；并非所有动作都可逆。

## R3 · Retry pattern

- 发布机构：Microsoft · Azure Architecture Center
- 版本／技术实读日期：Azure Architecture Center · 实读2026-10-24
- 正式文档：[Retry pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry)
- 官方固定原文：[retry.yml](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/cb69919fc6c9ebe8c3e3c389020e29a0ede6c941/docs/patterns/retry.yml)
- 实际include正文：[retry-content.md](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/dcf29659535a230ee4d73b812d49a6953b912430/docs/patterns/retry-content.md)
- 原研究记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-saga/research.md#L12)
- 原题定位：retry.yml · metadata.title（第3行）
- 题名元数据核对日期：2026-10-26
- 正文位置：Retry strategies · Idempotency · When to use this pattern

对应主张：

- 对适合重试的临时故障采用有次数、间隔和终止出口的策略；长期故障与业务拒绝不能无条件重试。
- 重复操作应避免产生额外业务效果；未取得回复也不能证明前一次没有执行。

## R4 · Idempotent Consumer pattern

- 发布机构：Microsoft · Azure Architecture Center
- 版本／技术实读日期：Azure Architecture Center · 本片补充实读2026-10-26
- 正式文档：[Idempotent Consumer pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer)
- 官方固定原文：[idempotent-consumer.md](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/dcf29659535a230ee4d73b812d49a6953b912430/docs/patterns/idempotent-consumer.md)
- 原题定位：idempotent-consumer.md · H1（第12行）
- 题名元数据核对日期：2026-10-26
- 正文位置：Commit the processed key and the side effects atomically · Guard against concurrent duplicates · Idempotent processing beyond messaging

对应主张：

- 同一逻辑退款使用稳定标识；退款业务效果与已处理标记在同一事务保存，避免已退款而标记丢失导致重复退款。
- 并发重复需要数据存储层唯一约束或等价原子保护；稳定标识、原子标记等机制也适用于无消息代理的重复HTTP等操作。
