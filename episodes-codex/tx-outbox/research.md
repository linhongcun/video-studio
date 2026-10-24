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
