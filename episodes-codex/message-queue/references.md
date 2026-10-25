# message-queue · 参考资料

本轮实际读取与核验：2026-10-26（北京时间）。两份原文来自RabbitMQ官方公开仓库，均完整GET成功；原题与连续完整原句照录，不以内部supports概括代替。

实际HTTP状态、SHA-256、题名、原句及关键上下文：[核验记录](../../docs/reference-endcards/batch-4/sources-message-queue.json)。正式站点本轮受限的事实留在此记录，不改写旧访问历史。

## R1 · Consumer Acknowledgements and Publisher Confirms

- 机构：RabbitMQ
- 版本：官方维护文档 · 2026-10-26核验
- 正式文档：<https://www.rabbitmq.com/docs/confirms>
- 固定原文：<https://github.com/rabbitmq/rabbitmq-website/blob/29cb9ecf131223ad9b7faf61921ac3683008f722/docs/confirms.md>
- 原题位置：frontmatter title · line 2
- 正文完整SHA-256：`861abccf819fddcdaddd661255914d867d6ed511a9ff19311bfef73d0907b127`

> The two features, however, are entirely orthogonal and unaware of each other.

原文位置：The Basics · #relation；原文件行号72–72。

内部论点对应（制作解释，不是原文引句）：

- 发送者发布确认和消费者处理确认覆盖不同通信方向；发布确认不能证明后续业务已经完成
- 本片先可靠保存的前提是正确路由、持久消息与持久队列及发布确认配置；不能把任意confirm当作保存或业务成功
- 采用手动确认时，投递所在channel或connection关闭会使尚未确认的消息重新入队；发现断连需要时间

## R2 · Reliability Guide

- 机构：RabbitMQ
- 版本：官方维护文档 · 2026-10-26核验
- 正式文档：<https://www.rabbitmq.com/docs/reliability>
- 固定原文：<https://github.com/rabbitmq/rabbitmq-website/blob/29cb9ecf131223ad9b7faf61921ac3683008f722/docs/reliability.md>
- 原题位置：frontmatter title · line 2
- 正文完整SHA-256：`25d54e926d450a8676a93ba6282f4eb8456ab60db3242ac6333f14871d3e07e4`

> Therefore consumer applications will need to perform deduplication or handle incoming messages in an idempotent manner.

原文位置：Data Safety on the Publisher Side；原文件行号178–179。

内部论点对应（制作解释，不是原文引句）：

- 消费者应在完成所需业务操作后再确认；确认意味着接收方承担该消息的责任
- 确认未到达会产生不确定性与重复投递风险；消息重来不意味着新订单或业务必然未完成，程序需按业务规则去重或幂等处理
- 消息安全需要发送者、broker及消费者共同负责，不能据有消息队列就声称exactly-once或永久不丢

## 可靠性边界

保存回执与业务处理回执必须分开。本例可靠保存以目标队列、持久性和确认配置正确为前提；无法路由的消息也可能获得confirm。手动确认下断连触发重入队，重投仍可能对应已成功的业务，需以业务标识等机制保证安全重复处理。本片没有exactly-once、无限容量或永久不丢承诺。
