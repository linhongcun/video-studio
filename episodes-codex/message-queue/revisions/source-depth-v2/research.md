# MQ01 · 从任务数据到分区日志，再到业务执行

2026-10-30（北京时间）。本轮保留EP10 / message-queue / 原题《订单已提交，为什么还没处理完？》及旧封面，独立制作目录为`episodes-codex/message-queue/revisions/source-depth-v2/`。基线`923305b49cea1b18d7fc7e4dd8ac70ad830bc673`，批次issue[#443](https://github.com/linhongcun/video-studio/issues/443)。旧制作源、takes、冻结、QA、发布媒体未被本目录改写；新npm依赖按复制的现行锁文件安装，不复用旧node_modules。

本期唯一问题是**存储任务与执行业务为什么能分开，因此已受理不等于已完成**。新稿13镜沿同一E01/订单7042：数据→UTF-8字节→生产者缓冲→Broker在P0末尾分配编号0并追加→日志下一编号1但消费者仍暂停→成功后回复已受理→消费者带读取位置0拉取→解码文本、解析字段、读取位置1→业务函数另执行保存完成→页面查询。Sender批次调度、提交恢复位点、副本选举与幂等去重留各自课程，不在这条链中展开。

## 身份、读法与本轮范围

固定Apache Kafka/Java客户端4.4.0、官方commit`1156b2752aaa28eafc0b4c4d387e63356793268d`。本轮对官方固定commit原始源重新完整HTTPS GET，保留原字节、链接和SHA，分别见`sources/client/source-evidence.json`与`sources/broker/source-evidence.json`。先读关键执行语句，再用API/文档/注释交叉核对；没有把Javadoc当执行实现，没有访问canonical HTML却宣称已读。

文档frontmatter与相关类声明未见明确个人署名，使用Apache Kafka机构，不推定Git提交者为作者；ASF原LICENSE/NOTICE保留。片尾两项原题为`Introduction`与`Design`，titleEvidence对应原frontmatter第2行。文章另用实际类标识`StringSerializer`、`FileRecords`、`CompletedFetch`作为源码引用题名，不另拟论文字样。

当前**源码事实已实读，有限教学模型已运行；尚无本目录真实Kafka Broker、Java客户端或通知服务实验**。根代理另组织的真实最小实验会有独立版本/拓扑/原始输出证据，未完成前不追认为本片实测。本文不预记音频、动态图、正式编码、网站或用户观看通过。

## 固定示例与配置

- 事件数据：`eventId=E01, orderId=7042, task=notify-order`。这些是应用定义的字段；Kafka不凭task字段自动运行通知函数。
- 网站将其JSON文本交给StringSerializer，显式UTF-8；消费者StringDeserializer解码回String，再由应用JSON解析字段。画面字节长度仅指该value，不冒充整条Kafka记录/批次大小。
- `orders`只有P0，producer显式指定P0，producer与topic目标压缩均none，格式v2，本例是已通过校验的合法新普通记录；非事务。编号来自分区末尾，不是业务eventId或字节地址；v2真实批次使用base offset和记录delta，不画成应用在payload写绝对offset。
- 单节点RF1/minISR1/currentISR1，`acks=all`，幂等true，retries=2147483647，max.in.flight=1；不作高可用/每条立即fsync或任意故障不丢保证。固定这些条件仅为给成功路径明确前提。
- 消费者classic组，`enable.auto.commit=false, max.poll.records=1`，本例开始有效读取位置0，源记录全程保留。提交offset及重启恢复另见MQ03，本片不靠提交进度解释通知完成。
- 网站策略：收到本例发送成功之后才回复任务已受理；页面另外查应用业务结果。消费者起初暂停，未发起本例读取/未执行业务；恢复后读取并由模拟通知业务函数处理。

## 关键执行结构、条件与更新

| 入口与结构 | 谁在什么条件下改什么 | 对应可见因果 |
|---|---|---|
| KafkaProducer.doSend，序列化后的key/value、本地RecordAccumulator | 先调用serializer得到byte[]，之后才append缓冲；后台再发送 | 04字段先变字节再暂存，不能从数据卡直接跳成已执行业务 |
| UnifiedLog当前分区logEndOffset、LogValidator计数 | 已校验非重复新记录进入选定分区，取当前末尾0，验证时推进offsetCounter并写批次编号 | 05本记录分配0；编号从本分区当前状态产生 |
| LocalLog活跃LogSegment/FileRecords | 先append当前段，随后更新logEndOffset为lastOffset+1；FileRecords经channel实际write字节 | 06记录存在，日志下一编号变1；业务还没运行 |
| AbstractFetch构建FetchRequest | 消费者恢复后，将本地position.offset=0装入分区请求 | 08只有明确从0拉取，才返回这条记录；原记录不会被拿走 |
| CompletedFetch解析记录、FetchCollector更新SubscriptionState | 反序列化后nextFetchOffset=record.offset+1，写客户端position，再poll返回记录 | 09解码与读取位置推进先发生；不是通知完成 |
| 本例应用业务状态（不是Kafka内置结构） | 应用接收到数据后显式调用通知模拟函数，成功后另存E01=completed | 10–12同一日志/读取位置保持，业务完成另变，页面查这处结果 |

## 真实最小执行链与永久定位

### producer：从字段到发送缓冲

`KafkaProducer.doSend`先序列化，再`RecordAccumulator.append`。执行位置：[KafkaProducer.java1080–1111](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/KafkaProducer.java#L1080-L1111)。[StringSerializer.java34–57](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/common/serialization/StringSerializer.java#L34-L57)设置UTF-8并实际`data.getBytes(encoding)`；不是只读“异步”定义。

正文只保留一个本地待发结构，不展开Deque/ProducerBatch/Sender drain及Future完成，避免同MQ04争主线。

### Broker：按分区末尾追加，不调用订单业务

完整本轮定向阅读见`sources/broker/notes.md`。最小链：KafkaApis.handleProduceRequest→ReplicaManager.handleProduceAppend→非事务append路径→Partition.appendRecordsToLeader→UnifiedLog.appendAsLeader→LogValidator分配编号→LocalLog.append→LogSegment.append→FileRecords.append→MemoryRecords.writeFullyTo(channel)。

- [KafkaApis.scala419–450](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/server/KafkaApis.scala#L419-L450)实际构造目标TopicPartition并取MemoryRecords；[542–557](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/server/KafkaApis.scala#L542-L557)交handleProduceAppend。
- [UnifiedLog.java1150–1182](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/storage/src/main/java/org/apache/kafka/storage/internals/log/UnifiedLog.java#L1150-L1182)：日志锁内从`localLog.logEndOffset()`取下一编号0，交验证器；[LogValidator.java237–264](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/storage/src/main/java/org/apache/kafka/storage/internals/log/LogValidator.java#L237-L264)无压缩分支实际逐记录`offsetCounter.value++`并setLastOffset。
- [LocalLog.java529–532](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/storage/src/main/java/org/apache/kafka/storage/internals/log/LocalLog.java#L529-L532)先append活跃段，再`updateLogEndOffset(lastOffset+1)`；[FileRecords.java195–209](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/common/record/internal/FileRecords.java#L195-L209)真正writeFullyTo(channel)，单独flush才force(true)；[MemoryRecords.java84–90](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/common/record/internal/MemoryRecords.java#L84-L90)循环channel.write。

这串执行处理记录、编号、字节与日志追加结果，未调用本例notify-order函数；不是声称Broker没有运行任何内部代码。存储条件与副本可见性分开，不从本地append直接推出所有acks成功前提或每条都fsync。

### consumer：指定位置取数、解码，再交应用

- [AbstractFetch.java477–484](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/AbstractFetch.java#L477-L484)在真正的FetchRequest.PartitionData中放入`position.offset`，本例为0。
- [StringDeserializer.java56–60](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/common/serialization/StringDeserializer.java#L56-L60)实际`new String(data,encoding)`，只还原字符串，不替应用JSON解析字段。
- [CompletedFetch.java269–290](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/CompletedFetch.java#L269-L290)解析、加入返回records并更新下一offset；[FetchCollector.java178–204](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchCollector.java#L178-L204)写SubscriptionState.position。
- [ClassicKafkaConsumer.java662–679](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L662-L679)随后poll把记录返回应用，应用业务尚未由这些赋值完成。

## 片尾与文章出处

R1 `Introduction`，机构Apache Kafka，4.4.0，核验2026-10-30；[原文](https://kafka.apache.org/44/getting-started/introduction/)，实际读固定源码frontmatter与Main Concepts第79–83行。短引为消费不删除记录的连续原句，原字词保存在sources/client/introduction.md。

R2 `Design`，机构Apache Kafka，4.4.0，核验2026-10-30；[原文](https://kafka.apache.org/44/design/design/)，实际读The Consumer与Consumer Position。短引“consumer works by issuing fetch requests”保持连续原文，保存在sources/client/design.md。

文档解释能力边界，实际实现原因由上述执行代码兑现；文章A1–A3分别引用序列化、文件追加与读取位置更新的原始语句。片尾只显示两项文档原题/机构，不堆源码行号或代码墙。

## 模型、条件对照和实际检查范围

`model.py`从同一应用JSON生成真实UTF-8值字节，再建立有限状态快照。34项检查已通过：先编码再缓冲；Broker从末尾0分配，追加后末尾1；业务暂停时记录仍存；网站必须等本例发送成功才接受；Fetch实际带0；解码和读取位置1不代表业务完成；应用另执行/存结果；页面另查；源日志跨读取和执行保持。模型只模拟被解释的状态，不仿真完整Kafka批次格式、文件物理大小或通知服务。

改变关键条件的模型对照：消费者保持暂停，则任务仍可存储、业务仍等待；改从位置1拉取，则已有位置0记录不在该次返回范围内。两者解释“数据存在”“读到了”和“做完了”是三个不同条件；后者仅专项验证，不另加正文分支。

最小真实Kafka实验由根代理另组织，只有实际完成并有独立原始记录才补充结果。不得用模型检查冒充Broker实测，也不得用来源/断言/静帧通过代替独立因果审与实际连续动画检查。

## 独立真实实验的引用边界

根代理另组织的官方4.4.0单节点RF1真实实验已完成，记录见`docs/archive/2026-10/mq-source-depth-remake/runtime/README.md`。其中run-20261030T120117.612545Z在消费者尚未创建时，Produce成功后物理日志dump已见E01；这支持“消费者未执行时记录可保存”。实际value只含eventId/orderId，P0还有E03，不含本片notify-order字段或真实通知处理；不得把影片业务完成状态当作已真实执行。该run消费组部分是static实验，另有dynamic补验，MQ01只引用其保存记录的窄范围，不把拓扑或输入差异隐藏。原始运行源、配置、整包SHA512与输出在独立runtime目录，不复制成动画模型输出。
