# MQ01 Broker追加链：定向实现阅读

状态：本轮真实读取Apache Kafka 4.4.0固定提交的实现代码；没有启动Broker、真实Produce请求、文件持久性或性能实验。仅为MQ01重制提供机制依据，不展开ISR、副本故障、事务或重试支线。

固定提交：`1156b2752aaa28eafc0b4c4d387e63356793268d`。本目录9份源码均从官方固定提交raw路径新GET，HTTP状态、完整字节SHA、永久链接见`source-evidence.json`。文件保持原ASF头。原题文献/许可证和总tag身份由本期研究汇总记录，不推定Git提交者为作者。

## 选定最小路径与前提

选本例已通过授权/格式检查、非事务、新的非重复普通记录，目标分区P0；为了让正文编号原理对应最短实现分支，固定producer/topic目标压缩均为none、record format v2。前提满足时的调用链如下，不能把方法名字当作已经执行过的实测日志：

```text
KafkaApis.handleProduceRequest
  → ReplicaManager.handleProduceAppend
  → ReplicaManager.appendRecords
  → ReplicaManager.appendRecordsToLeader / appendToLocalLog
  → Partition.appendRecordsToLeader
  → UnifiedLog.appendAsLeader / append
  → LogValidator.validateMessagesAndAssignOffsets / assignOffsetsNonCompressed
  → LocalLog.append
  → active LogSegment.append
  → FileRecords.append
  → MemoryRecords.writeFullyTo(channel)
```

注意4.4.0的API入口实际调用`handleProduceAppend`，不是从KafkaApis直接调用`appendRecords`；非事务路径才进入下述省略事务验证的短链。

## 实际语句与稳定结构

1. **按目标主题/分区接收已编码记录。** `KafkaApis.scala`419–450遍历请求的topic/partition，427构造`TopicPartition(topicName, partition.index())`，442取得`MemoryRecords`，450把合法记录放入`authorizedRequestInfo`。548–557以`entriesPerPartition`交给ReplicaManager。
2. **由目标分区本地日志执行追加。** `ReplicaManager.scala`780–785非事务直接走postVerificationCallback；767–776调用appendRecords。653–662转appendRecordsToLeader，597–604转appendToLocalLog。1402–1416逐分区找到Partition并调用`partition.appendRecordsToLeader(records,...)`。`Partition.scala`1227–1240在本地leader日志分支调用`leaderLog.appendAsLeader`。这里不把minISR检查是否成功当成本期新证明；只固定前提满足。
3. **从这个分区的日志尾取下一编号。** `UnifiedLog.java`1150取得日志锁；1158实际赋值`offset = PrimitiveRef.ofLong(localLog.logEndOffset())`，1159记firstOffset，1175–1178调用LogValidator，1182记`lastOffset = offset.value - 1`。这解释编号来自当前分区日志状态，而非订单ID、业务完成数或整个集群的全局序号。
4. **按记录数推进编号并写到批次。** `LogValidator.java`147–153在无压缩且magic已匹配时调用`assignOffsetsNonCompressed`；237–255逐批/逐记录检查，252执行`offsetCounter.value++`，264执行`batch.setLastOffset(offsetCounter.value - 1)`。v2采用批次基准及记录相对offset表达，不应画成每条payload都包含一个由应用生成的绝对offset字段。
5. **追加后推进日志的下一位置。** `UnifiedLog.java`1269–1276对非重复批次调用`localLog.append(lastOffset,validRecords)`；`LocalLog.java`529–531先`segments.activeSegment().append(...)`，随后`updateLogEndOffset(lastOffset + 1)`。`LocalLog.java`304–305把逻辑endOffset、活跃段baseOffset、段字节位置组合成`LogOffsetMetadata`。
6. **真正写入日志文件通道。** `LogSegment.java`255取得追加前物理字节位置，260调用其`FileRecords`的`log.append(records)`；270–272在需要时更新offset/time索引。`FileRecords.java`195–202实际执行`int written = records.writeFullyTo(channel)`，随后`size.getAndAdd(written)`。`MemoryRecords.java`84–90循环`channel.write(buffer)`直到当前记录缓冲写完，并恢复buffer位置。

## 至少三个可用于正文的执行变化

- 日志原来下一位置是0，`offsetCounter`从该分区的0开始；一条合法新记录进入批次后，计数变1，批次最后编号为0。
- `activeSegment.append`把包含记录的已编码字节接到当前日志段末尾；源记录此后在日志中存在，不等于业务动作已执行。
- `updateLogEndOffset(lastOffset+1)`把下一可追加位置改为1；下一条新记录据此取1。逻辑编号和文件字节长度分别保存，不能把offset画成字节地址。
- `FileRecords.append`的`written`是真正文件通道写出的字节数量，`size`随之增加；这是存储动作，不是“订单处理完成”状态写入。

## 直接永久定位

- 接收目标分区及MemoryRecords：[KafkaApis.scala419–450](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/server/KafkaApis.scala#L419-L450)
- 进入handleProduceAppend：[KafkaApis.scala542–557](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/server/KafkaApis.scala#L542-L557)
- 非事务短路径：[ReplicaManager.scala755–785](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/server/ReplicaManager.scala#L755-L785)
- 逐分区转交：[ReplicaManager.scala1402–1416](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/server/ReplicaManager.scala#L1402-L1416)
- 分区调用leader日志：[Partition.scala1227–1240](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/core/src/main/scala/kafka/cluster/Partition.scala#L1227-L1240)
- 从logEndOffset分配：[UnifiedLog.java1150–1182](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/storage/src/main/java/org/apache/kafka/storage/internals/log/UnifiedLog.java#L1150-L1182)
- 逐记录增量与批次编号：[LogValidator.java237–264](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/storage/src/main/java/org/apache/kafka/storage/internals/log/LogValidator.java#L237-L264)
- 调用实际追加：[UnifiedLog.java1269–1277](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/storage/src/main/java/org/apache/kafka/storage/internals/log/UnifiedLog.java#L1269-L1277)
- 活跃段与下一位置：[LocalLog.java529–532](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/storage/src/main/java/org/apache/kafka/storage/internals/log/LocalLog.java#L529-L532)
- 日志段写FileRecords：[LogSegment.java250–272](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java#L250-L272)
- 文件通道追加与单独flush：[FileRecords.java195–209](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/common/record/internal/FileRecords.java#L195-L209)
- 最终写循环：[MemoryRecords.java84–90](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/common/record/internal/MemoryRecords.java#L84-L90)

## 正文可保留与不可扩大之处

正文可用“按分区保存的追加日志”解释存储：Broker收到客户端已编码的记录，沿选定分区日志尾分配编号，把记录批次字节接到日志段末尾，再推进下一位置。让这一串真实状态变化参与动画；函数全名和索引维护留图文，避免堆方法名代替原理。

这条追加路径传递的是记录、日志与追加结果，不包含本例订单业务函数；记录存在与业务完成必须分开。不能因FileRecords写入就宣布业务已执行，也不能因Producer/HTTP回复就把通知处理状态自动改完成。业务仍由后续消费者的应用代码执行，需结合本期consumer链展示。

重要边界：

- 此处文件通道append不等于每条立即fsync。`FileRecords.flush`208–209另行调用`channel.force(true)`；本片不能把append画成单条写盘后永久不会丢，也不研究操作系统PageCache/性能。
- 日志本地追加与客户端成功回执、ISR确认/可见性是不同边界。这里只提供追加执行依据，确认仍沿本期固定配置，不从这几行源码推出所有故障保证。
- 编号限定分区与本例普通新记录。幂等重复批次可能返回既有offset（UnifiedLog1261–1268），压缩/事务/清理情景也不能据此泛化为所有offset永远无间隔；本片不展开这些支线。
- 文件按记录批次与日志段存储，不是“一条消息一个文件”；offset不等于业务eventId、消费进度或物理字节地址。
- 此文件与source-evidence只证明实读范围和来源身份，不是运行日志，不预记动画、最终成片或真实Broker实验已通过。
