# MQ06 · 订单状态为什么倒退

唯一主机制：同一订单的外部先后已确定 → 相同key字节选同一分区 → 分区队列/日志按发送先后追加 → 客户端逐条收集成同分区列表 → 应用调度决定状态写入的完成先后。

先用订单7042页面从已退款回到已支付的问题，再说明E01是已发生的支付、E02是已发生的退款；下游任务只更新页面状态投影，不再执行钱款动作。这是两个不同有效事件，不能通过去重删除其中一个。

14镜四段：

1. 01–03：业务目标、两条输入与写入/交付/完成三段定位。来源已经先支付后退款，单producer单调用线程先完成E01发送再send E02。
2. 04–06：同key7042 → UTF8字节37 30 34 32 → murmur2正数1934056876 % 2=0 → P0批次队列尾进头出 → P0的E01@0/E02@1。P1为空，分区数固定2。实际Java内建类计算已运行，不猜P0。
3. 07–08：CompletedFetch的内部记录迭代器逐条取出并records.add到列表尾；FetchCollector结束本次收集后安装position，再作为ConsumerRecords交给应用。只演列表，不把内部扫描位点0→1→2误画成SubscriptionState.position逐条变化。应用同步完成时，页面已支付→已退款。
4. 09–14：明确相同日志和起始页面reset，只改应用调度。先到的支付任务在写入前等待，后到的退款先完成，支付随后覆盖为已支付。再同输入reset并按订单串行，上一条实际写完才放行下一条；其他订单可独立并行。同key无法替多个producer先确定外部业务先后。回收原问题。

正文不展开murmur内部位运算、完整rebalance、恢复/提交、Broker副本协议或重试序号协议。关键短代码若使用，只展示hash实际余数规则和“提交任务≠等待业务写完”的教学差异，画面承担主要因果。

固定Kafka/Java4.4.0 commit1156b2752aaa28eafc0b4c4d387e63356793268d；显式classic+Range单成员，非事务；StringSerializer UTF8、无显式分区/无自定义partitioner、不ignore key、分区数稳定2；producer幂等true/acksall/max.in.flight1且主线无故障。配置不会被描述成Kafka全部默认。

来源阅读和执行映射见research.md/implementation-map.json。有限模型与真实Java key-route计算分别留证；Broker/latch真实小实验由本批运行代理负责，未回传前不写已通过。无片长硬限制，当前约三分钟的内容量。
