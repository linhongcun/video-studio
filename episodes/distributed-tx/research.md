# EP.21 核心资料核验

访问日期：2026-10-24（北京时间）。实际阅读正文后写作，不以issue、旧稿或搜索摘要代替公开来源。片中不展开产品配置和软件版本，不借用旧版四方案并列。

|ID|公开原始资料|已核验主张|本片使用与边界|
|---|---|---|---|
|R1|[AWS Prescriptive Guidance: Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)|业务行与outbox事件在同一数据库事务写入；提交后另行读取发送；可能重复，消费者须幂等|04—07。待发记录不是内存纸条；订单本地事务不直接修改远端库存|
|R2|[RabbitMQ Reliability Guide](https://www.rabbitmq.com/docs/reliability)|网络断连可能需要重新发送；发布确认/消费确认有不同含义；确认丢失会导致重复，消费端须按幂等处理|06、10—11。消息已被代理接受不等于库存业务已完成，不宣称无限必达|
|R3|[Amazon SQS at-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html)|标准队列可能再次交付同一条消息；应用应使重复处理没有额外不良影响|10—11。仅支持重复可能性，不把所有队列都概括为完全相同保证|
|R4|[Azure Architecture Center: Compensating Transaction](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)|跨步骤中间状态可暂时不一致；失败恢复需业务化补偿，可能告警人工介入；补偿也可能失败|12—13。不把最终一致写成不论永久故障/缺货都自动成功|
|R5|[Chris Richardson: Idempotent Consumer, 2020-10-16](https://microservices.io/post/microservices/patterns/2020/10/16/idempotent-consumer.html)|在处理消息的数据库事务中记录消息ID并更新业务状态，以唯一性检查拦截重复；事务失败不留下半份处理状态|08—11。处理标记与扣减必须同库存库事务；记录保留与唯一约束是必要实现条件|

订单8124、通知E8124、商品库存4→3均为教学设计。仅演示同一条库存扣减通知，去重键应包含消息ID或业务操作标识，不能用泛化“订单处理过”吞掉后续退款/调整等合法操作。未做吞吐、延迟或真实商城压测；动画时间不是服务延迟指标。正常路径假设库存足够、服务恢复、重试与持久化机制正确，异常路径明确转交后续处理。

画面里的订单“已记录”不等于完整业务成交确认。本片修复的是已提交订单的通知不可恢复地漏发、以及重复通知多扣库存的问题；缺货、永久失败和业务取消仍需设计完成/失败状态和补偿。2PC、TCC、Saga、XA等只在片外说明其属于其他设计方向，不并列讲解。
