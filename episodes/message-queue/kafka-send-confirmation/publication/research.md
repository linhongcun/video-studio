# MQ04 发送确认的实现研究

核验日期：2026-10-30（北京时间）。本轮目录source-depth-v2，从主干923305b49cea1b18d7fc7e4dd8ac70ad830bc673开始；保留EP44、原标题与slug。固定Apache Kafka/Java 4.4.0，官方tag再次解析到`1156b2752aaa28eafc0b4c4d387e63356793268d`。本轮重新GET官方固定提交源字节，SHA/URL/时间见`sources/fetch-evidence.json`；原始错误路径的404仅作发现记录，正确internal/MemoryRecordsBuilder.java已另行读取，不把404计作有效来源。

## 一个问题、一条执行链

网站发送订单7042的通知事件E01。调用返回、Kafka写入、发送方取得成功结果和下游业务完成不是同一个状态。本片要解释：E01进入什么结构，Sender为何仍记着它，哪个回应最终完成同一个结果对象；回应缺失时，Broker怎样识别原批次而不是靠业务eventId去重。

19处实际执行路径、连续摘录、永久行号和完整文件SHA见`implementation-map.json`。API契约与Javadoc仅交叉核对；缓冲、在途、Broker重复分支与状态更新的主张均实际读执行代码。

## 入口、分区批次与同一个Future

- `KafkaProducer.doSend`1065–1076先处理元数据可用性，1080–1092进行序列化，1095–1111选择分区并append。1122–1126可唤醒Sender后直接返回append所得future，没有等待Broker成功回应。同步编码错误由1147–1150抛出，发生在accumulator之前；它不代表整个调用绝无元数据网络访问。
- `RecordAccumulator`319–328按有效分区取Deque，尝试附到末批；428–436创建ProducerBatch、将记录加入批、入队并返回记录Future。`ProducerBatch`166–183把记录Future连到共享的ProduceRequestResult及batchIndex，并把回调一同保存。不是每次请求都另建一个不相干的结果对象。
- `RecordAccumulator`924–982从分区队首出批，只有还没有序号的批次才将producerId/epoch/本分区sequence写到批中，并递增下一序号；已有序号的重试批不改身份。`ProducerBatch`518–519和`MemoryRecordsBuilder`316–326把这些字段写入记录构造状态。身份在首次发出之前已经存在，视频第10镜仅展开查看。

## Sender、在途与回应完成

`Sender.sendProducerData`380–453先检查可发送条件与目标连接，再drain、addToInflightBatches和构造请求；`inFlightBatches`219–223按分区保留等待回应的批次。`sendProduceRequest`896–947为这一次请求保存recordsByPartition映射，回应callback捕获这张映射，因此不是仅凭分区从所有在途批里任意找一个。

正常响应经691–763走到同一个`batch.complete`。`ProducerBatch`281–342先用CAS固定一次终态，再设置元数据、调用该批记录的回调，最后`produceFuture.done()`释放Future.get等待。视频聚焦同一次完成事件，不把Future与callback画成两次确认，也不宣称Future.get先于回调返回。实际代码顺序与未展开的回调细节保留在本文；本例排除应用回调抛错/阻塞等旁支。

## Broker究竟比较什么

本例A为非事务生产者，示例producerId501/epoch0；一记录一批，P0序号范围0..0。Broker收到新的有效批次，`UnifiedLog`1255–1280先分析生产者状态，若无重复、且规则校验通过才`localLog.append`，随后更新ProducerStateManager。`ProducerAppendInfo`223–232保存本批代次、序号范围及对应offset，StateManager384–395更新已有entry或加入新producerId。

重传原批时，`UnifiedLog`1411–1420用batch.producerId定位这个分区的已存entry；`ProducerStateEntry`128–136要求epoch一致，并匹配保存的完整firstSeq/lastSeq范围。命中时`UnifiedLog`1261–1268返回原批的first/last offset与时间，完全跳过1276的append。动画不能先增加logEnd再回滚；本例任何重复阶段的日志都仍只有E01@0。

代码没有读取业务eventId或key来作这一判断。A关闭后新建非事务生产者B，本例取得新producerId902，epoch0/初始序号0；A的旧entry不是B的已处理清单。未命中重复仍需`ProducerAppendInfo`156–193的代次/序号校验，不能把“未命中”概括为无条件追加。有效B发送在本例追加E01@1，两个记录eventId相同，但属于两次应用发送。

此状态不是永久业务去重表：StateEntry88–103仅保存近期五批元数据，变更epoch会清空旧批元数据。本例单记录、单批、max.in.flight=1，重传时原批元数据仍保留；缓存淘汰、状态过期、PID恢复、事务和完整乱序处理不塞入正文。

## 回应缺失与总发送超时

本例先让记录被Broker追加且满足固定acks条件，再让原请求及其自动重试的成功回应在总期限内都没有被客户端处理。这是明确的教学故障条件，不是现场Broker或网络故障注入。

`Sender`185–216收集达到delivery期限的在途批，362–375以Kafka TimeoutException完成失败；并非Future.get短等待超时。`ProducerBatch`287–313只准首个终态完成结果，迟到成功不翻转已失败F1。失败不能撤销远端已追加的记录；应用只凭失败无法推断是否已写入。此后应用重新发送还要面对业务去重问题，生产幂等不替下游保证恰好一次。

## 固定条件

orders/P0，一记录一批；非事务、不设transactional.id；acks=all、enable.idempotence=true、retries=2147483647、max.in.flight.requests.per.connection=1、linger.ms=0；request.timeout.ms=45000、delivery.timeout.ms=120000、max.block.ms=60000；RF3/minISR2/当前ISR3且条件稳定。本片使用本例满足条件的写入成功，不展开MQ15副本确认算法，不说全部副本刷盘或任意故障零丢失。等待被压缩并明确标非实时时长，数字为教学设置而非性能测量。

## 实际执行与教学模型分开

- `experiments/run-probe.py`使用Java21编译**未修改**的官方ProducerStateEntry.java和BatchMetadata.java，链接官方kafka-clients4.4.0中的RecordBatch接口。明确的动态代理fixture只供应producerEpoch/baseSequence/lastSequence字段；15项差异条件通过，包括同代次/完整范围命中并复用旧offset、改代次或范围不命中、近期五批保留等，实际来源SHA与输出见`experiments/result.json`。这是两个原类的源码级单元执行，不是序列化记录、ProducerStateManager、Broker追加/网络或acks运行实验。
- `model.py`是有限教学状态机，仅驱动画面；82项结构与状态断言通过。它保存分区队列、Sender在途、请求上下文映射、F1/新F2、日志与Broker近期生产者状态。每个快照深拷贝；重复分支不增长日志，B成功不改旧F1失败。有限模型的输出不冒充Kafka终端或真实集群日志。
- 声音、真实配音时序、动态中间态、成片与站点另行验收，不预记用户认可。原始源码是Apache官方机构维护材料，未见本轮所用文件明确公开个人署名，视频显示原始类符号与Apache Kafka。

## 来源与片尾

`references.json`选KafkaProducer、RecordAccumulator、Sender、UnifiedLog四项原始类标识，原题证据为实际class声明，完整固定链接及原字节URL均在文章。`article-sources.json`另给ProducerStateEntry、ProducerBatch、ProducerAppendInfo逐字短引。所有摘录只在文章/研究，视频片尾仅原题/机构，每页最多4项、5秒。
