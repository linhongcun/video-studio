# distributed-tx-intro · 片尾参考资料

本轮整理日期2026-10-26；技术实读日期沿用2026-10-24。原research使用北京时间，navigation快照使用UTC日期；均按原记录保存，不推断缺失的读取时刻。

采用title-author简表，5项分两页，每页最多4项、5秒；不上屏引文、日期、定位或提示。无可确认公开个人署名，使用文档发布机构，不把Git或ms.author维护账号当作者。

Azure完整题名依据26日固定官方源元数据；四份完整响应SHA/字节数与24日navigation完全一致。重试标题来自wrapper，技术论点对应其实际include正文。所有请求身份、完整SHA、原研究及导航Git blob/SHA见[本轮证据](../../docs/reference-endcards/batch-7/sources-distributed-tx-intro.json)；既有实读记录是本仓笔记，不是官网固定正文。

## R1 · Transactions

- 发布机构：PostgreSQL
- 版本／实读日期：PostgreSQL 18 Documentation · 实读2026-10-24
- 正式文档：[Transactions](https://www.postgresql.org/docs/18/tutorial-transactions.html)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/distributed-tx-intro/research.md#L15)
- 题名依据：既有实读记录 · 第15行的3.4 Transactions
- 正文位置：3.4 Transactions · 原子性、BEGIN / COMMIT / ROLLBACK

对应主张：

- 同一笔本地事务管理的事务型数据可共同提交或撤销；同库中的独立事务不会自动合为一笔。

## R2 · XA Transactions

- 发布机构：Oracle / MySQL
- 版本／实读日期：MySQL 8.4 Reference Manual · 实读2026-10-24
- 正式文档：[XA Transactions](https://dev.mysql.com/doc/refman/8.4/en/xa.html)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/distributed-tx-intro/research.md#L16)
- 题名依据：既有实读记录 · 第16行
- 正文位置：XA Transactions · 全局事务、资源管理器与两阶段处理

对应主张：

- 受支持的跨资源协调由各资源处理自己的事务分支；独立提交不会自动变成同一笔本地事务。
- 片中协调决定后落实提交是一类思路，不承诺所有方案都有相同全局隔离或同一毫秒可见。

## R3 · Retry pattern

- 发布机构：Microsoft · Azure Architecture Center
- 版本／实读日期：Azure Architecture Center · 实读2026-10-24
- 正式文档：[Retry pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/distributed-tx-intro/research-navigation.json#L34)
- 题名依据：retry.yml · metadata.title（第3行）
- 正文位置：Solution · Retry strategies · Idempotency · Issues and considerations
- 题名补核：2026-10-26；[官方固定版本](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/cb69919fc6c9ebe8c3e3c389020e29a0ede6c941/docs/patterns/retry.yml)

对应主张：

- 没有得到回复不能证明操作没有执行；无重复保护的重试可能重复产生业务效果。
- 对适合重试的临时故障安排次数、间隔与终止策略；永久故障或业务拒绝需要其他异常出口。

## R4 · Compensating Transaction pattern

- 发布机构：Microsoft · Azure Architecture Center
- 版本／实读日期：Azure Architecture Center · 实读2026-10-24
- 正式文档：[Compensating Transaction pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/distributed-tx-intro/research-navigation.json#L13)
- 题名依据：compensating-transaction.md · H1（第11行）
- 正文位置：Context and problem · Solution · Issues and considerations
- 题名补核：2026-10-26；[官方固定版本](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/498e83a207cfd512b396489e95ed3f791b372364/docs/patterns/compensating-transaction.md)

对应主张：

- 各本地步骤可能先提交并留下可见中间状态，恢复与失败收尾要遵守业务规则；补偿不是覆写旧快照。
- 流程需要持久进度、可恢复执行和必要的人工介入；最终一致不等于等待后必成功。

## R5 · Idempotent Consumer pattern

- 发布机构：Microsoft · Azure Architecture Center
- 版本／实读日期：Azure Architecture Center · 实读2026-10-24
- 正式文档：[Idempotent Consumer pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/656b525f533037f1c0dff6383c4afa69926e612c/episodes-codex/distributed-tx-intro/research-navigation.json#L27)
- 题名依据：idempotent-consumer.md · H1（第12行）
- 正文位置：Solution · Commit the processed key and the side effects atomically · Idempotent processing beyond messaging
- 题名补核：2026-10-26；[官方固定版本](https://raw.githubusercontent.com/MicrosoftDocs/architecture-center/dcf29659535a230ee4d73b812d49a6953b912430/docs/patterns/idempotent-consumer.md)

对应主张：

- 稳定的操作标识用于识别同一逻辑操作；已处理标记与业务效果共同原子保存，并处理并发重复。
- 此处机制可用于会重复到达的HTTP或其他操作，不把视频中的同步调用误写成已有消息队列协议。
