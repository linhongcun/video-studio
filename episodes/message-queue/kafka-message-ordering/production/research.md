# MQ06 实现研究：日志有序以后，谁保持完成顺序

研究日期2026-10-30。制作基线f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3；root已从最新主干建立codex/mq05-07-implementation-20261030，初查工作区clean。本期独占kafka-message-ordering新目录，未改旧生产输入/共享实现/站点/git。

## 问题、业务规则与范围

订单7042的支付成功E01、退款成功E02已经按这个顺序发生。发送者只有一个，调用线程确定先完成E01发送、再发E02。下游只更新订单状态页投影，不重新执行扣款或退款；E01/E02是两个不同有效事件，不是重复投递。问题是同一日志按序交付后，异步任务为何仍可先写退款、后写支付。

正文机制不是一串“保序”结论，而是：同样的key字节读取内建取余规则→同分区双端批队列→leader从日志末分配offset→内部记录迭代/列表append→交给应用→应用是否等待前一条真实写入完成。单集不讲全部rebalancing、发送故障恢复或数据库版本仲裁。

固定Kafka/Java4.4.0 commit1156b2752aaa28eafc0b4c4d387e63356793268d。所有实际源码永久URL、字节SHA和访问时间在sources/download-manifest.json；完整原字节、NOTICE/LICENSE保存在本期sources/。具体已读执行段在sources/source-evidence.json，镜号/结构/条件/写入值/后果在implementation-map.json。视频4项原题采用源码实际class声明：BuiltInPartitioner、RecordAccumulator、CompletedFetch、KafkaConsumer，机构Apache Kafka，无个人作者推断。

## 选择的生产与消费条件

- Producer：StringSerializer/UTF8；key=字符串7042；没有显式partition或自定义partitioner，partitioner.ignore.keys=false。orders固定2分区，主线没有扩容。
- Producer：acks=all、enable.idempotence=true、max.in.flight.requests.per.connection=1；非事务；单调用线程先等E01发送成功再send E02。这里的严格条件便于隔离应用完成顺序，不声称所有生产配置都相同。
- Consumer：显式classic+Range，一个成员订阅orders，无group.instance.id/client.rack；enable.auto.commit=false；保留日志从0开始，只展开有两条数据的P0，P1为空。应用只用一个线程调用poll，再移交工作任务。
- 应用投影：处理任务的“完成”是将该事件状态真实写入状态投影，不是刚发起另一个异步请求。本例未加版本比较/状态转移拒绝规则，后完成的无条件写会覆盖先完成的值。

## 已实际读取的核心执行链

### 1. 相同key怎样选择同一分区

KafkaProducer1078-1111先序列化key/value，再调用partition、再accumulator.append。partition1556-1575先判显式partition、再自定义partitioner，只有serializedKey非null且没有ignore才走BuiltInPartitioner.partitionForKey。

StringSerializer33-57把默认编码字段设UTF8，serialize返回data.getBytes(encoding)。BuiltInPartitioner411-413真实return对序列化key字节murmur2→toPositive→对分区数取余。不是按订单号的语义、业务eventId或生产时间排序。

本期已用真实Kafka4.4.0 jar实际运行StringSerializer/Utils/BuiltInPartitioner：7042→37303432，murmur2=1934056876，正数相同，%2=0。所以P0是实际计算结果；同key只选同分区，不能替多个producer先定义外部业务因果。driver、stdout/stderr、Java版本与client jar SHA在experiments/，只称实际类运行，不称Broker实验。

### 2. 分区队列怎样接上日志位置

RecordAccumulator319-328按effectivePartition取得Deque并在锁内tryAppend。470-485先尝试末批；428-436新批createProducerBatch后addLast；后台924-980检查peekFirst、退避/可发条件后pollFirst取批。ProducerBatch166-170调用recordsBuilder.append；MemoryRecordsBuilder581-583按nextSequentialOffset追加（合批旁支，不要求所有示例每条一批）。

UnifiedLog1150-1182在日志锁内从localLog.logEndOffset构造offset计数器，并调用LogValidator.validateMessagesAndAssignOffsets；本例无压缩路径230-264逐条offsetCounter++，最后设置batch的lastOffset；UnifiedLog1269-1278在非重复分支localLog.append，LocalLog529-532段追加后将log end设lastOffset+1。新的空P0先E01@0、后E02@1，原记录随后始终保留。

这里单producer、确定send先后与同partition是关键前提；日志offset记真实追加先后，不对业务时间戳做重排序。发送幂等/重试配置与应用调度是两个不同责任层。

### 3. 客户端怎样形成按序列表

CompletedFetch187-243顺着batches/records迭代器往后取，跳过范围外/控制/中止事务等不属于本例的记录。269-290建立ArrayList，在循环中nextFetchedRecord→parseRecord→records.add(record)，再更新内部nextFetchOffset=lastRecord.offset()+1。

必须区分内部扫描与客户端当前位置：FetchCollector163-185检查匹配的下一fetch起点，先调用整次fetchRecords，随后才安装SubscriptionState.position；ClassicKafkaConsumer648-681再将fetch.records包装成ConsumerRecords返回。ConsumerRecords76-92保存并按分区返回List。本例收集两条后，内部扫描0→1→2，而客户端position由外层最终0→2，视频只演列表依次append，不用中间position1混淆两层状态。

07这处在独立源码初审时纠正过，记录qa/editorial-source-correction.json。它是稿/模型阶段纠偏，没有真实失败帧或take，不追认为动态事故。

### 4. 应用为何能把完成顺序反过来

KafkaConsumer519-538的“Decouple Consumption and Processing”说明，先交给处理线程的数据可因线程执行时机而较晚处理；不是Kafka承诺替应用同步完成。完整连续引文只移除JavaDoc行前缀、CON列表标记与换行，原始三行及归一化方法一并保存在source-evidence.json，未删词或另造句。

模型中应用仍按E01、E02提交任务，却用受控屏障把E01停在真实写入前。E02写REFUNDED完成后释放E01，后者再写PAID。每个写入都与事件targetStatus一致，日志与交付保持E01/E02；反过来的是completionOrder。正确对照重新固定相同日志/起始页面，让7042的任务队列一次只放行一个，等实际写完才放行下一条，最终REFUNDED。

## 证据分层与当前状态

1. 固定源码：21个新下载原始文件968,089字节（含license/NOTICE），URL/sha在download-manifest，不使用旧期中文材料代替本轮实读。
2. 实际类运行：key-route-result.json，真实4.4.0内建路由结果P0，无Broker/网络send/消费调度结论。
3. 有限教学模型：model.py→model.json，校验分区offset、相同保留日志、交付顺序、内部扫描/外层position区别、投影写入与完成顺序、两个reset、串行单活跃任务等。模型断言通过不是实测或易懂程度证明。
4. 真实Broker和latch实验：本批/root/deploy_diagnosis已运行通过12项断言，本期experiments/runtime-mq06保存其完整原字节快照，runtime-snapshot.json保存原路径→本地SHA。真实metadata为P0@0/@1，classicRange按序poll，物理log保留两条；同一真实记录列表从相同PENDING投影出发，串行完成E01/E02最终REFUNDED、受控并发完成E02/E01最终PAID。实际max.poll.records=1，合并两次poll的真实列表后比较应用调度；片中07选择合法的两条一次收集作为实现教学，不冒充这份runtime的单次poll轨迹。应用实跑是Java AtomicReference/线程/latch，不是真支付退款、数据库或性能实验。
5. 编辑/声音/动画：新稿14镜28句；先交root与独立mq_qa审稿，未经放行不TTS。正文4Figure先按shot/model完成态规划；实际音轨装配后、编码前才写最终整数帧和seekTo。

## 边界

同key分区映射依赖序列化、partitioner分支和分区数；本例对3取余会从P0变P1，扩容不能继续套固定同分区前提。多个producer只在日志中形成实际写入先后，不能凭同key定义业务先后。幂等处理同批重传并不帮两个有效业务事件排应用完成顺序。并发业务完成后的安全提交与失败重投另有责任链，本片不展开。
