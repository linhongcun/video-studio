# Outbox单机制短片：资料核验

访问日期2026-10-24（北京时间）。实际打开并阅读以下官方/原作者正文，不使用旧稿或搜索摘要代替核验；全文均为独立转述，无长引文。

| 来源 | 实际阅读位置 | 本期取用与边界 |
|---|---|---|
| [AWS Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | Intent、Issues and considerations、Using an outbox table、示例独立发送程序 | 01–07：业务与待发事件共同本地保存，独立转发，仅发布已提交记录；回滚不应发消息。未照搬其中任何特定队列的“恰好一次”宣称。 |
| [Chris Richardson Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html) | Solution、Participants、Result context | 08–09：relay在发送后、记录完成前中断可重发；需要消费者处理重复。模式正文未给原始发表年，按当前原作者正文引用，不从页脚推断年龄。 |
| [AWS Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | Retrying and side effects、Reducing client complexity | 10–12：同一请求身份和业务效果需正确原子衔接；仅看相同参数或内存查询不充分。 |
| [Chris Richardson Idempotent Consumer](https://microservices.io/post/microservices/patterns/2020/10/16/idempotent-consumer.html) | Why duplicate messages、Tracking IDs、PROCESSED_MESSAGE | 10–12：处理标识应有唯一约束，并与业务修改同一本地事务；提交后确认消息。2020-10-16原作者文章，未早于2020。 |

## 逐镜核验

- 01：双写空档导致订单已保存、通知未发，是故障示例设定。
- 02–05：订单与待办共同提交/共同回滚；不等于数据库和队列同一原子提交。
- 06–09：独立发送、等队列确认后记录发送结果，发送成功与标记完成之间仍可出故障；同一通知身份重发。
- 10–12：消费本地事务将库存扣减和唯一已处理标记共同保存；失败不留下半套结果，重复不再扣。唯一约束是并发保护责任，不把先查后扣的普通查询当充分方案。
- 13–14：最终业务收敛仍依赖消息持久性、发送与消费恢复。永久业务拒绝须按规则结束，Outbox本身不包办业务补偿，也不提供跨库全局隔离。

商品7042库存4买1、订单8124、事件E8124为明示教学设定，不是官方性能数据或真实业务记录。本集不同时解释CDC、RocketMQ半消息、TCC或Saga，也不宣称这是唯一可靠消息实现。

## 片尾参考资料清单（2026-10-26整理，沿用2026-10-24访问）

本期选择旧记录中明确归属于Chris Richardson的两篇资料，presentation为title-author，只显示英文文献名和明确作者，每页最多4项、默认5秒。原稿机制、导航、所有实际技术阅读记录与AWS佐证保留。

旧完整research基线`61d3b984a594578a67bc34aa374cccd0326cd9d6`，Git blob`0986a194beed12659bbcfb57dd52847c3ec27a5e`，SHA-256`46d4971b74525c7e0f87bb496cc9b9143584b7a41a91f3fe5535366b6f19dc5f`（2687字节）；旧完整article Git blob`5397917b4840a533ac2b27bf9f9a391761be020f`，SHA-256`0878d922eeda4386c5047e6f92b741ea742816dd218814ba9b94a5b8f31a3f59`（4441字节）。[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/tx-outbox/research.md)和[原研究逐字归档](../../docs/reference-endcards/batch-8/tx-outbox-evidence/prior-research-61d3b984.md)仅标识本仓阅读记录，不是官方正文固定快照。

R1题名Transactional outbox与Chris Richardson署名逐字取自旧article.mdx第48行，并与本research第8行归属记录交叉；R2完整原标题Handling duplicate messages using the Idempotent consumer pattern与署名逐字取自旧article第49行，并与research第10行交叉。日期均保留2026-10-24，不冒充26日新的公开byline、完整H1或正文读取；不从Git贡献者猜作者，不凭印象给旧题加Pattern:。

| 片尾编号 | 既有实读书目英文文献名 | 明确作者 | 旧题名/署名记录 |
| --- | --- | --- | --- |
| R1 | [Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html) | Chris Richardson | article第48行 |
| R2 | [Handling duplicate messages using the Idempotent consumer pattern](https://microservices.io/post/microservices/patterns/2020/10/16/idempotent-consumer.html) | Chris Richardson | article第49行 |


原逐镜与边界记录、旧书目字节和核对范围见[sources-tx-outbox.json](../../docs/reference-endcards/batch-8/sources-tx-outbox.json)。本轮GitHub仓库候选404及搜索没有取得可信原作者正文，不能当题名/作者新证据；遵守现行网络策略，未请求未授权原站或绕过代理。原研究和article完整前缀及4脚注保留。

本条只记录资料整理；没有官方完整旧响应SHA，不将本仓研究SHA替代。未改媒体/冻结/共享码，也不预记编码、声音/审片或发布通过。
