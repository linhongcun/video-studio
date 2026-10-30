# MQ03 源码深度重制 · 审稿提纲与执行链

状态：提纲已获根代理方向认可，完整脚本待独立审稿；尚未TTS或制作动画。身份维持EP43/kafka-log-replay/原标题/旧封面。本轮固定Apache Kafka/Java客户端4.4.0，commit `1156b2752aaa28eafc0b4c4d387e63356793268d`。

本片唯一机制：**持久committed恢复值 → 新客户端内存position → Fetch请求起点 → 同一日志字节**。Broker日志文件、客户端内存、消费组持久恢复值各有明确所属，不能把数字画成一张无归属的表。一个E01（旁白称“事件一”）始终位于P0/offset0。本例开始已有committed=0，关闭自动提交，不暗称新组初始值默认0。

| 镜 | 观众跟随的动作与原因 | 实际执行依据（本期sources中的完整原文件） |
|---|---|---|
| 01–02 | 同一事件读过又出现，先建立日志/内存position/持久committed三份状态 | 固定示例条件；KafkaConsumer的日志位置与恢复语义另外由正文实现核对 |
| 03 | 请求起点0定位段与字节范围，读取只产生切片而不删除原文件 | LocalLog.java479选择`segments.floorSegment(startOffset)`，508调用segment.read；LogSegment.java439定位startOffset，461返回`log.slice(startPosition, fetchSize)`；FileRecords.java145–149构造同文件/channel范围视图 |
| 04 | 收到offset0后，下一次读取位置算成1并写回客户端 | CompletedFetch.java290：`nextFetchOffset = lastRecord.offset() + 1;`；FetchCollector.java178–185构造nextPosition并`subscriptions.position(tp, nextPosition)` |
| 05 | 当前position前进不自动提交committed，原字节也没消失 | 前两步各自更新的结构不同，固定enable.auto.commit=false；commit持久实现只作文章核对，正文不展开整套coordinator |
| 06 | 退出丢弃旧实例；新客户端缺position，查询committed | ClassicKafkaConsumer.java1205–1217先检查缺有效位置再`coordinator.initWithCommittedOffsetsIfNeeded(timer)`；ConsumerCoordinator.java947–956查询后refresh |
| 07 | 把查得的0建立FetchPosition，再真正装进新客户端 | ConsumerUtils.java202–210以`offsetAndMetadata.offset()`构造FetchPosition并seekUnvalidated；SubscriptionState.java1195–1205中seekValidated执行`this.position = position;`。正文直接展示这句实际赋值，不用API注释代替 |
| 08 | 下一次Fetch的起点直接取内存字段0 | AbstractFetch.java477–483把`position.offset`作为FetchRequest.PartitionData参数，而不是直接读取Broker committed或“记住上次读过” |
| 09 | Fetch0再次走同一文件读取范围，得到同ID/offset/内容的E01 | 回到03的实际read/slice链；教学模型验证返回的是同一不可变记录快照，非新生产一条 |
| 10 | 回到“已读E01、尚未提交”的共同状态，只改成提交1成功；恢复就装1 | 同一ConsumerUtils/SubscriptionState初始化与Fetch字段链；只改变持久恢复值，不改日志。不会返回offset0，不等于原记录被删 |
| 11 | 原封闭段清理后，logStart超过0；Fetch0已不合法，旧位置不能复原字节 | UnifiedLog.java2016–2030按段最大时间与保留条件选择删除，1853–1857/1942起按段删除；1646–1650在offset小于logStartOffset时抛OffsetOutOfRangeException。明确无分层存储、delete清理、满足高水位等前提，不讲自动offsetreset流程 |
| 12 | 回收三份状态及其因果 | 三段执行链复述，不追加新机制 |

正文省去稀疏索引算法、组协调器完整持久化流程、admin reset CLI与主动seek。文章可补LogSegment.java398–400的index.lookup→向前定位，以及seek仅修改当前读取位置而不自动提交恢复点；这些补充不抢正文主线。

关键代码只在对应动作出现：先用动画完成“0来自保存值并装入内存”的映射，再展示SubscriptionState实际赋值；Fetch片段只突出实际起点实参。源码名不代替中文因果解释，不把方法调用列表当深度。

证据身份：`sources/recovery-source-reuse.json`保留本会话较早官方GET的检索时间、完整SHA及本轮复读时间；没有冒称重新联网。Broker读取与保留实现为本轮新完整HTTPS GET，见`fresh-storage-source-evidence*.json`，保留两次错误路径404的真实记录以及固定commit目录解析后成功原文件。不把有限模型/源码实读写成真实Broker、CLI、磁盘性能或故障实验。
