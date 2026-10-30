# MQ03 · 为什么旧位置能读回同一记录：实现研究

本轮复读日期：2026-10-30（北京时间）。身份保留EP43、kafka-log-replay、原标题《Kafka日志重放：消息读过了，为什么还能重读？》；基线923305b49cea1b18d7fc7e4dd8ac70ad830bc673。固定Apache Kafka与Java客户端4.4.0，commit1156b2752aaa28eafc0b4c4d387e63356793268d；传统classic消费协议、分配与leader/epoch校验成功且稳定。

本次实际工作为官方执行源码实读与有限教学模型，本修订作者未运行Kafka Broker、Java消费者、协调器持久化、日志格式实现、真实磁盘/网络/故障或retention调度实验；根代理另行完成隔离位置实验，范围与原始记录在文末单列，不扩大为本片全部状态实测。模型中的payload SHA只用于识别同一教学载荷，不是Kafka实际文件编码或生产测量。

## 原文、题名与复读身份

恢复链原文件来自本会话/tmp/mq05-depth-research/kafka早些时候的完整官方GET，本轮复制前逐文件核对其原SHA，随后复读相关实现；原检索时间与本轮复读时间分别保存在sources/recovery-source-reuse.json，未冒称重新GET。Broker日志读取与保留实现本轮从固定commit重新完整HTTPS GET，使用继承代理和默认TLS校验，原文件/URL/状态/SHA见sources/fresh-storage-source-evidence*.json。两条已失效的Scala/FileRecords旧路径404仍保留，之后由固定commit Git树解析正确Java路径，未把404说成来源成功。

本片片尾采用四个**实际源码文件名**作为原题，不自拟“恢复机制”等标题：ConsumerUtils.java、SubscriptionState.java、LogSegment.java、UnifiedLog.java。GitHub固定commit contents API实际name/path响应与原文件关联存于sources/code-title-evidence.json；这是源代码文件的原始身份，不声称它们是另有题名的技术文章。无明确个人署名，机构使用Apache Kafka；未从Git提交者推定作者。版本与访问日期及完整源码链接留在研究/文章，不上片尾资料列表。

## 一条执行主线

| 状态/条件 | 关键实现与实际执行语句 | 对应镜头 |
|---|---|---|
| Fetch请求带分区的当前读取位置 | AbstractFetch.java477–483将position.offset传给FetchRequest.PartitionData | 03概念、08具体参数 |
| Broker按offset定位日志段 | LocalLog.java479的segments.floorSegment(startOffset)，508调用segment.read | 03、09 |
| 日志段按起点定位文件范围并返回 | LogSegment.java398–400 index.lookup→searchForOffsetFromPosition；439 translateOffset；461 log.slice(startPosition,fetchSize) | 03、09；索引算法留文章 |
| slice没有消费/删除原文件 | FileRecords.java145–149以同一file/channel和起止位置创建FileRecords视图 | 03、09 |
| 记录返回推进的是客户端内存位置 | CompletedFetch.java290 nextFetchOffset=lastRecord.offset()+1；FetchCollector.java178–185新FetchPosition并subscriptions.position | 04–05 |
| 新实例缺位置，先初始化保存值 | ClassicKafkaConsumer.java1205–1217；ConsumerCoordinator.java947–956 initWithCommittedOffsetsIfNeeded→refreshCommittedOffsets | 06 |
| 从已提交值建立新位置并真正赋值 | ConsumerUtils.java202–210构造FetchPosition(offsetAndMetadata.offset(),...)并seekUnvalidated；SubscriptionState.java1195–1205经seekValidated执行this.position=position，再进行校验 | 07 |
| 恢复后的内存字段决定下一Fetch | AbstractFetch.java477–483的position.offset实参 | 08–09 |
| 修改committed为1仅改变重启起点 | 同一初始化/赋值/请求链，原日志字节不变；是独立反例，不把同一进程重复赋成不同结局 | 10 |
| 已删除旧段不再是合法读取范围 | UnifiedLog.java2016–2030按保留条件选段，1853–1857/1942起按段删除；1646–1650若offset<logStartOffset抛越界 | 11 |

R1 ConsumerUtils.java的连续实际片段见references.json quotation（205–210）；支持“以保存值构造新客户端位置并进入seek路径”，不支持保存值自动等于业务成功。R2 SubscriptionState.java1195–1205保存实际赋值及校验链；条件是该分区仍归当前客户端、初始化与必要验证成功。R3 LogSegment.java458–462为真正文件切片返回；FileRecords同文件/channel构造补足未删除原因。R4 UnifiedLog.java1646–1650支持过期位置越界；保留按段、最大时间及高水位等条件由2016段与deletableSegments实现核对，不能从一句retention.ms推出到秒即删单条。

## 固定示例与反例

同一命名事件E01/order7042位于orders/P0的offset0，旁白称“事件一”。单记录、无压缩的批次便于看清记录和字节范围，不把文件切片画成实际Kafka二进制格式。消费组notify、一个已分配P0的消费者，enable.auto.commit=false、max.poll.records=1、无事务。开始已有有效持久committed=0，明确为本例已保存的值，不声称无初始位点默认0。日志记录在整个恢复演示期间保留且可读。

客户端C1的position初始0。读取E01的响应到达后，解析/返回记录令下一位置变1；不发生commit，committed仍0。C1退出使其整个内存状态消失，C2起初position不存在；查询保存值0，构造FetchPosition，再执行赋值，成功初始化/验证后下一请求字段为0。重读返回同ID、offset、内容与教学payload SHA，未生成第二条日志记录。

committed1反例从“C1刚读完、position1、committed0”的共同状态明确重置，只增加退出前commit1成功的条件；C3恢复position1，Fetch1不会返回offset0的E01，日志仍含E01。持久记录是group/topic/partition的下一恢复位置，不是业务状态。该持久事实交叉核对本会话OffsetMetadataManager提交/回放与CoordinatorRuntime追加路径，但正文不展开整套组协调器。

保留反例明确另看日志范围条件：先存在装E01的旧封闭段与新的活动段，cleanup.policy=delete，分层存储关闭，旧段满足相应时间/容量、高水位等可删除前提。清理移除整个旧段、推进日志起点到1，再Fetch0越界；无论position或committed还保存0，都不能复原已不存在的字节。本片不演reset策略或offset过期后自动跳转。

## 画面必须兑现的实现因果

仅两处正文代码小窗：07实际this.position=position赋值；08Fetch的position.offset实参。03文件切片、04offset+1用字节/数值动作表达，完整片段留文章。三容器所有者明确，持久committed先回到新客户端对象再写内存，Fetch箭头从当前position出发，不能从持久值直接跳到日志。只出现模型快照和实际源码节选，不展示伪终端输出或虚构Broker测量。


## 根代理隔离位置实验的有限交叉验证

本轮Kafka 4.4.0/RF1真实实验原始stdout位于docs/archive/2026-10/mq-source-depth-remake/runtime/runs/run-20261030T120117.612545Z/position.stdout.txt。根代理已实际读取并确认结果：显式assign(P0)隔离读取/提交/重开，初始committed0，poll offset0后position1/committed0；close/reopen又读0；commit1后reopen读后续E03@1。该观察支持位置分离与恢复读取执行链，不验证影片业务、日志文件切片格式、retention调度或动态组重平衡。正式文章链接该原始记录，教学模型仍保留自身输入与101有限断言身份。
