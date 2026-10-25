# D02 观察者模式：MQ实战修订调研

访问日期：**2026-10-25（北京时间）**。制作基线`9834e2cd84b1081f8ab41ade369cf46b8b6ddf62`；本次按用户最新反馈改写实际视频，将主要篇幅从手写订阅名单、取消订阅移到跨服务MQ发布订阅与消费。旧同进程版来源与制作结果仍由Git基线和`revisions/mq-practice/baseline/`追溯，不能把旧成片检查直接记为本轮通过。

问题：**订单状态改变后，怎样让摘要与变化记录各自响应？跨服务项目通常怎样实现，又要承担哪些交付与一致性问题？**

## 实际取得与阅读范围

来源由Tinyfish `fetch_content`取得公开正文。本编辑实际阅读以下正文或指定章节，未只采用其他代理摘要。没有阅读GoF书籍全文，没有用市场占比数据证明“所有项目都用MQ”。两份临时取回文件的身份如下，正文SHA按UTF-8原文计算：

- RabbitMQ与Outbox：`revisions/mq-practice/research-rabbitmq-outbox.json`，完整SHA-256 `cb742536cd64bc30d11861aed681ec729e51a6015195854217fb66baf7cfec68`，独立审稿代理取回，本编辑随后读取。
- Microsoft：`revisions/mq-practice/research-observer-pubsub.json`，完整SHA-256 `14f768fbc12a65ca5398ea67e225cbdb4c10fef45f1745958fb90559fde49215`，本编辑取回并读取。网页有通用授权提示，但本次工具实际返回公开正文及元数据；没有访问账户私有内容。

| ID | 公开来源 | 本次实际阅读 | 采用主张与限定 |
|---|---|---|---|
| M1 | [Microsoft Observer design pattern](https://learn.microsoft.com/en-us/dotnet/standard/events/observer-design-pattern) | 概述、When to apply、角色清单、When to consider alternatives；不声称逐行审阅整段C#/VB机场代码 | 来源、观察者、订阅与通知职责；文档本身明确单应用简单通知可使用标准事件。接口与通知顺序属于具体实现，不定义所有语言或分布式消息系统 |
| M2 | [Azure Publisher-Subscriber pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/publisher-subscriber) | Context/problem、Solution、Problems/considerations、When to use及其不适用项 | 中间件向各订阅输出通道路由，已有产品优于从零构造；独立订阅、故障隔离、重复消息、事件契约、背压和最终一致性边界。不能把所有MQ产品当作同一套投递语义 |
| R1 | [RabbitMQ Publish/Subscribe](https://www.rabbitmq.com/tutorials/tutorial-three-python) | 全文，重点Exchanges、Temporary queues、Bindings及完整客户端 | 发布者→交换机→各绑定队列，一对多业务订阅与同队列竞争不同。**教程实际用exclusive临时队列和auto_ack=True**，无绑定可丢弃；这里只借用拓扑，不能照搬为离线可靠保留方案 |
| R2 | [RabbitMQ Work Queues](https://www.rabbitmq.com/tutorials/tutorial-two-python) | 全文，重点Round-robin、Message acknowledgment、Message durability | 一个业务队列多个worker分担；处理完成再确认；持久队列与持久消息配合，持久标记单独仍不够，较强交付需要发布确认；不把任务内容当成本例事件命令 |
| R3 | [Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms) | Are Publisher Confirms Related...、Consumer Acknowledgement Modes...、When Consumers Fail...、When Will Published Messages...、Publisher Confirms and Guaranteed Delivery | 发布确认与消费确认正交；手动确认下连接/通道关闭导致未确认投递重新入队，检测不可用需要时间；可重复投递。可路由持久消息进入持久队列后确认需落盘；**无法路由的消息也可能获发布确认**，不能把一个ACK当作业务送达证明 |
| R4 | [RabbitMQ Reliability Guide](https://www.rabbitmq.com/docs/reliability) | 全文 | 数据安全是broker、发布者和消费者共同责任；持久化、确认、连接恢复、路由检查、重投幂等、故障监控。普通等待超时不是本片重投触发条件，也不宣称绝对不丢或恰好一次业务效果 |
| O1 | [Transactional outbox — microservices.io](https://microservices.io/patterns/data/transactional-outbox.html) | 全文Context、Problem、Solution、Result context | 业务变更与待发事件在同一本地事务保存，再由relay发送；relay也可能重复发布，消费者仍需幂等。不是消费者ACK就补上数据库与发消息之间的原子性 |

Microsoft M1元数据`updated_at`为2026-06-02，M2为2026-06-03；`ms.date`与更新时间是不同字段，本文不混作同一发布日期。RabbitMQ使用本次动态文档，不沿用旧研究“4.4”版本断言。Outbox页面未标更新日，不以页脚推断日期。

正文UTF-8 SHA-256，顺序对应M1、M2、R1、R2、R3、R4、O1：

```text
M1 aea66f0646c714c5eded6ee1e1aa3cc329f4cab71003c2ea8ca76178878d6d57
M2 205f97029405f88777655b3e888c433f6357eb122151c57f6877d77490d1e1ff
R1 6d3490ac8fae6e6601d0339feba15eeccd83faee9232d9c719f6e72fa5fccec0
R2 1b9b6e5a8622f2c3b11860c6a493c21faccc705ace0aee731da2cf10c2dba5c0
R3 cda7a48c5878a98cb9bdc18f35fdea0e16f124d16a09e6b716097ec05a798893
R4 ab76e738a47874e1321027acddeb8bdd174f9a6f26b82c49cd0aed2db6cbedd3
O1 37541a9166191d6678d2404deecbe57bbb61a6209d3b9264e1740cab12cd1852
```

## 片中事实与例子映射

| 镜头 | 主张 | 依据和例子限制 |
|---|---|---|
| 01–02 | 来源变化，已登记接收者按共同约定各自响应 | M1；订单17、摘要、记录是自建功能例子，01不执行真实付款，02只是同进程原理 |
| 03–04 | 跨服务常借助消息中间件；一个业务订阅一条输出路径 | M2、R1；是部署与工程判断，不是行业占比。明确切换为RabbitMQ教学部署，不从商家界面推断真实架构 |
| 05 | 各消费自己的事件，业务完成再手动确认；契约不变时可增加订阅方 | R1–R4、M2；不是所有MQ统一用ACK删除，也不宣称新增订阅不需配置 |
| 06 | 记录离线时自身队列保留待处理，摘要继续处理 | M2、R2、R4；已建立且适当配置的持久队列、持久消息与确认路径，不能用R1临时队列代替 |
| 07 | 恢复消费；业务已成功、ACK未送达、断连检测后重投；同事件需要幂等 | R3、R4；同事件编号`e17-1`，订单号不是唯一事件键。幂等是效果定义，编号去重是本例方法，去重状态与业务效果需原子提交 |
| 08 | 数据库更新与发事件存在双写缺口；Outbox衔接；消费者结果可短暂滞后 | O1、M2；另一个边界示意，不接成07的同事件新故障；Outbox不能消除重复和全部一致性成本 |
| 09–10 | 同进程可用框架事件，跨服务可用MQ；学习思想与工程保证分别看 | M1 alternatives、M2 use/avoid；不说观察者模式无人使用，也不说所有跨服务任务都应引入MQ |

## 明确不作的保证

不承诺全局处理顺序、跨服务原子提交、绝对不丢、自动无限重试或恰好一次业务处理。消费者可能读到旧状态；最终收敛需发布/消费/重试/对账真正成功。共同契约变化、队列配置与新增订阅方的实现成本没有消失。

保留现有`demo-java/ObserverDemo.java`仅作同进程观察者原理对照，片尾静默5秒；旧程序中的取消订阅与发货行为可以在完整示例中复查，但本次不再占主要视频时长，也不将其运行结果当作RabbitMQ集成测试。媒体、配音、动态及实际站点结果由本轮制作检查另记。
