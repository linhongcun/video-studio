# message-queue / mq-intro · 参考资料

本轮实际读取与核验：2026-10-27（北京时间）。三项均为RabbitMQ官方资料，未见明确个人署名，视频片尾显示原题与机构。下列短引只用于文章与研究核对，不上视频资料卡。

固定源commit：`a284a068ab720672b40ceed40f3f151d9829fb70`。完整来源字节、真实题名、原句及上下文见 [核验记录](sources/evidence.json)。

## R1 · RabbitMQ tutorial - Work Queues

- 机构：RabbitMQ
- 版本：现行官方教程（Pika Python）· 2026-10-27核验
- 正式文档：<https://www.rabbitmq.com/tutorials/tutorial-two-python>
- 固定原文：<https://github.com/rabbitmq/rabbitmq-website/blob/a284a068ab720672b40ceed40f3f151d9829fb70/tutorials/tutorial-two-python.md>
- 原题位置：frontmatter title · source line 2
- 原文完整SHA-256：`cabb69419c24d03876e78504e064c3ad2a8df3242481e3065e7cc6c23964d211`

> Instead we schedule the task to be done later.

原文位置：What This Tutorial Focuses On · source line 48。

编者说明（不是原文引句）：
- 耗时任务可以编码为消息送入工作队列，交给后台worker稍后处理。
- 网页请求受理任务与后台完成任务是不同阶段，工作队列将耗时处理移出短暂的请求窗口。

## R2 · Queues

- 机构：RabbitMQ
- 版本：RabbitMQ 4.4 官方维护文档 · 2026-10-27核验
- 正式文档：<https://www.rabbitmq.com/docs/queues>
- 固定原文：<https://github.com/rabbitmq/rabbitmq-website/blob/a284a068ab720672b40ceed40f3f151d9829fb70/docs/queues.md>
- 原题位置：frontmatter title · source line 2
- 原文完整SHA-256：`70a81800b3df6e9e0295391a2fae37f67421af5b097d112e06a3ac9ba3087025`

> Durable queues will be recovered on node boot, including messages in them published as persistent.

原文位置：Durability · #durability · source line 272。

编者说明（不是原文引句）：
- 队列持久性与消息持久性分别配置；持久队列的重启恢复包含其中以persistent发布的消息，不能从任意入队动作推出已安全持久化。
- exclusive和auto-delete是与连接或消费者生命周期有关的不同队列属性；本片固定non-exclusive、non-auto-delete的durable quorum queue，不借临时订阅队列声称消费者离线时任务仍保留。
- 队列和消息可以配置TTL、队列可配置长度限制；待处理任务的保留有配置和资源边界，不是永久或无限保存。
- 队列中的ready消息与已投递未确认消息是不同状态；本片暂停场景固定在尚未投递之前，不能把处理线程暂停自动画成消息仍在ready。

## R3 · Consumer Acknowledgements and Publisher Confirms

- 机构：RabbitMQ
- 版本：RabbitMQ 4.4 官方维护文档 · 2026-10-27核验
- 正式文档：<https://www.rabbitmq.com/docs/confirms>
- 固定原文：<https://github.com/rabbitmq/rabbitmq-website/blob/a284a068ab720672b40ceed40f3f151d9829fb70/docs/confirms.md>
- 原题位置：frontmatter title · source line 2
- 原文完整SHA-256：`861abccf819fddcdaddd661255914d867d6ed511a9ff19311bfef73d0907b127`

> Positive acknowledgements simply instruct RabbitMQ to record a message as delivered and can be discarded.

原文位置：Consumer Acknowledgement Modes and Data Safety Considerations · #acknowledgement-modes · source line 146。

编者说明（不是原文引句）：
- Consumer ACK发往RabbitMQ，表示消费者承担本次投递的处理责任并允许Broker释放消息；不是向网页返回业务完成通知。
- 发布确认与消费者确认覆盖不同通信方向、彼此独立；本片只简要建立接力阶段，不把ACK或confirm等同于整条业务链完成。
- 本片固定手动ACK，并在业务操作完成后才确认；自动确认模式有不同的数据安全语义，不能把本例推广为所有消费模式。

## 核验范围

已完成：官方网页相关正文阅读、固定源全文读取、原题/机构/原句/上下文核对、保存字节与Git blob身份一致检查。未完成也不预记：运行RabbitMQ、性能测量、故障注入、配音听辨、成片和线上检查。新输入只属于本revision，不改写旧冻结或追认历史媒体。
