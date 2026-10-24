# EP10 公开资料实读记录

访问日期：2026-10-24（北京时间）。实际通过搜索服务打开官方正文并定位相关章节；不是只看摘要。公开文档当前显示RabbitMQ 4.4，片中不要求观众使用该产品，教学机制限定如下。

| 编号 | 官方正文 | 支持本片的主张 | 本片保留的边界 |
|---|---|---|---|
| R1 | [Work Queues](https://www.rabbitmq.com/tutorials/tutorial-two-python)，Work Queues / Message acknowledgment / Message durability | 耗时工作可作为任务消息交后台处理；处理完成后确认；持久化需队列与消息配合 | 例子不是全局严格FIFO；可靠保存不等于业务已完成 |
| R2 | [Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms)，Basics / Automatic Requeueing / When Will Published Messages Be Confirmed | 发布确认与处理确认属于不同通信方向；手动确认下连接关闭会重投未确认任务；持久消息进入持久队列的确认发生在保存后 | 发现断连需要时间；重投不代表新业务；路由失败和确认需共同处理 |
| R3 | [Reliability Guide](https://www.rabbitmq.com/docs/reliability)，Data Safety on Publisher/Consumer Side | 发送者、队列、消费者共同负责安全；不确定的确认可能造成重复，应让业务可安全重试 | 无恰好一次或永久不丢承诺；只有确认消息丢失与业务未做完要区分 |
| R4 | [Queue Length Limit](https://www.rabbitmq.com/docs/maxlength)，Overview / Overflow Behaviour | 积压有资源与策略边界；到达上限后的行为可配置 | 不能把队列当成无限缓存；某些策略会丢旧消息，某些拒绝新发布 |

片中教学设计：7042/7043/7044是无真实含义的业务编号；一次只处理一笔和三笔瞬时抵达仅用于看清状态，不是性能测试。画面中的移动时间经过放慢，不代表官方时延。

本轮相对旧片的内容修正：不再用“有队列就不会丢单”作绝对承诺。开头改问提交与完成的区别，把可靠保存、消费完成、确认丢失三个阶段分开。消费侧的记录仅表示队列维护的未确认状态，不是一笔新订单。
