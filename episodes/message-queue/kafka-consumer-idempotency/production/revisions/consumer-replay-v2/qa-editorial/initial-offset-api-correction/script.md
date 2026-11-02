# 消费幂等：已经处理过，为什么还会再来一遍？

唯一问题：生产者只追加一条记录，为什么消费者重启后仍可能把同一业务做两次。Kafka恢复链占正文前九镜，数据库只用简单业务键与同一本地事务承接解法，不讲索引锁或并发仲裁内部。

固定Apache Kafka4.4.0 Java客户端/commit1156b2752aaa28eafc0b4c4d387e63356793268d，group.protocol=classic，enable.auto.commit=false，max.poll.records=1；同一组points只有A随后B一个稳定拥有者。唯一记录E01/order7042/account17/+10，orders/P0/offset0。原记录在本例保留，开始前显式commitSync({P0:0})建立持久恢复值0；auto.offset.reset=earliest仅在无有效提交值时作回退，不是本例重读原因。账户初始0，受控进程退出发生在外部数据库COMMIT成功之后、Kafka offset1提交之前。数据库与Kafka是两个提交边界。

画面把三处状态分开：Kafka原日志/组恢复值，当前消费者内存position，外部数据库已提交积分/业务键。A退出清除内存位置，B先查询已提交值、收到0，再安装本地position0，随后Fetch请求携带0，取得的ConsumerRecord仍是原offset0。没有producer重发、新日志追加或记录搬走。数据库内未提交值不冒充已完成效果。

第10镜先完整reset到a-polled/DB0/无业务键/组0再改变提交顺序；第11镜也从这个相同起点reset，先演登记points:E01与积分+10同事务提交，再退出/恢复，不能在第09镜已20分或无标记10分的现场凭空补业务键。第12镜以日志1条、业务尝试2次、积分效果1次回收标题。生产者幂等与acks不覆盖外部DB，Kafka事务的适用范围、唯一约束与外部副作用只进文章，不扩正文支线。

### 01 problem

旁白：订单七零四二只发出一条积分事件，账户已经加了十分，重启后为什么又加一次？沿着同一条记录，看看消费者究竟从哪里继续。
画面：原日志只有E01@P0offset0，账户17已10，问题指向同一身份的再次处理；不提前显示20已完成。随后显式回到首次读取前的教学起点。
出处：R1；应用受控故障问题。

### 02 one-record

旁白：生产者只把这条事件写入一次，零号位置保存着订单和加分内容。消费者读取记录不会把它从日志里取走；只要仍在保留范围内，它还能再次被读取。
画面：唯一E01/order7042/account17/+10固定在orders/P0/offset0，producerSendCount=appendCount=1全程不变。起点组已保存0、DB0，不把保留说成永久保存。
出处：R1；同一保留日志的读取契约。

### 03 first-poll

旁白：消费者甲从零开始请求，拿到的就是这条零号记录。客户端随即把内存里的下一读取位置推进到一，表示下一次往后读。
画面：Aposition0→Fetch参数0→响应E01@0→FetchCollector写position1→poll返回。offset是分区内记录位置，不是字节地址。
出处：A1/A2；FetchCollector、CompletedFetch实际执行代码。

### 04 two-positions

旁白：但这个一只是甲的内存读取进度，不是已经保存的重启起点。Kafka另外保存同组的已提交位置，本例仍是零，只有提交进度才会改变它。
画面：A内存position1与Kafka组points committed0分别高亮；不画Broker持有A的position。此刻应用未调用offset1提交，下一读取与恢复值都表示下一条位置。
出处：R1；客户端position推进和offset commit彼此独立。

### 05 database-commit

旁白：甲把事件交给积分业务，数据库给账户加十分，并成功提交。数据库已经完成了自己的事务，可Kafka的恢复位置还没提交，仍然是零。
画面：DB本地事务open先暂存+10，COMMIT后已提交积分0→10；Kafka组0保持，不由DBCOMMIT触发Kafka提交。
出处：R1/R4；两个提交边界与教学例子。

### 06 crash-gap

旁白：就在数据库提交之后、Kafka进度提交之前，假设甲进程退出。甲内存中的一消失了，留下的是日志里的原记录、数据库的十分，以及Kafka保存的零。
画面：A先退出并释放拥有者身份，position/returned清空；logE01@0、DB10、committed0都保留。B尚未出现，不画两位稳定同组拥有者。
出处：R1；受控进程故障窗口，不是Broker崩溃。

### 07 restore-offset

旁白：接手的消费者乙没有甲的内存位置，它先向Kafka查询这个组保存的进度。拿到零后，客户端把零装进乙自己的读取位置，作为恢复起点。
画面：B拥有P0后position尚空；OffsetFetch(group=points,P0)请求→收到committed0但position仍空→ConsumerUtils构造FetchPosition(0)/seekUnvalidated安装position0，三步分开。
出处：R2；ConsumerCoordinator与ConsumerUtils实际恢复路径。

### 08 fetch-same-record

旁白：接下来生成读取请求时，客户端把这个零填进请求，要求从零开始取。返回的仍是原来的事件和零号位置，并没有生产者第二次发送，也没有新写一条消息。
画面：AbstractFetch从Bposition0构造FetchRequest.PartitionData(fetchOffset=0)，原日志同一E01@0响应，ConsumerRecord.offset仍0；Bposition推进1。日志不移动、不新增。
出处：R3/A2；请求实参与返回原始offset。

### 09 repeated-effect

旁白：如果积分业务见到事件就加十分，这次又会执行一次，积分变成二十分。重复的是对同一条记录的业务处理，不是Kafka日志里多了一条记录。
画面：B业务尝试第2次，DB事务暂存20→COMMIT后已提交20；组仍0，日志只有一条，区分读取次数与业务调用数。
出处：R1；无防护应用反例。

### 10 commit-too-early

旁白：能不能先提交Kafka进度，再去加分：回到尚未加分时，先把恢复位置提交成一，接着进程退出。乙就会从一开始，越过还没加分的零号记录；提前提交把重复风险换成了漏处理风险。
画面：明确reset到a-polled/DB0/无key/组0；commitSync显式P0:1成功后A退出，B查询1→安装1→Fetch1返回空，DB仍0。原E01@0还在日志，只是恢复起点越过它，不称记录已丢失。
出处：R1；提交顺序改变的应用反例。

### 11 bind-business-key

旁白：再回到第一次加分之前，应用给积分业务和这条事件一个稳定的业务键。在同一个数据库事务里，登记这个键和加十分一起提交；然后即使在Kafka提交前退出，乙仍会按零重读。
画面：reset同a-polled/DB0/组0。业务键points:E01不含进程A/B；同DB事务暂存key与+10→一起COMMIT变DB10/key在→A退出→B恢复0/Fetch0/poll同E01。不展开唯一索引锁、RETURNING或并发图。
出处：R4/A3；简单同事务应用设计，Kafka恢复仍同一链。

### 12 idempotent-effect

旁白：乙发现这个业务键已经处理过，就跳过加分，积分仍是十分，再把Kafka进度提交成一。日志一条、业务尝试两次、效果一次，这就是消费幂等要守住的关系。
画面：B业务尝试2查到已提交points:E01→skip，DB10/key保持；显式P0:1提交成功→组恢复值1。日志一条、业务尝试2、效果1从当前模型值收回，不暗示所有消费者都必然重复。
出处：R1/R4/A3；应用去重边界。
