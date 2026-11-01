# 重试与死信：失败消息，为什么不能一直重试？

唯一问题：应用怎样给失败处理设定跨进程重启仍有效的有限预算，并在停止业务重试后保留可处置的事件。

固定Kafka4.4.0/Java客户端，commit `1156b2752aaa28eafc0b4c4d387e63356793268d`，classic、`enable.auto.commit=false`、`max.poll.records=1`；一个消费者、一个原分区P0，E01@0/order7042，后续E02@1，原记录在示例期间保留。逻辑handler固定notify。原已提交恢复位置0；原位置只用显式Map提交offset+1，禁止无参提交把未处理的后续记录算进去。

本片策略由应用实现，不是Kafka nack/requeue/DLX，也不建立自动延时Topic。应用保留已poll出的E01；pause只是本地分区交付门，期间owner线程持续短poll，业务与producer.send由受控executor执行；只有原commit成功才resume。失败分类、预算、deadline与DLQ调度全为应用状态。

预算是最多3个“持久化预留的调用名额”，包含首次；调用前先保存`totalStarted+1/IN_FLIGHT`，成功后才发起业务，因此在保存后/实际调用前退出也会消耗名额。状态以logicalHandler+eventId为键，额外校验原topic/partition/offset/payload hash，保留在同机同一state目录并用进程锁保护。只演进程退出/重启，不宣称断电耐久、目录丢失恢复、多机共享或再均衡完整生产协议。IN_FLIGHT恢复视为结果未知，仍消耗预算；业务需幂等。

同一事件展示临时恢复成功、预算耗尽、永久拒绝和DLQ目标失败；条件对照先reset共同状态。原记录始终留存。DLQ先成功metadata，再写本地confirmed，最后另commit原进度；这些边界有重复/未知窗口，不宣称原子或恰好一次。等待处置不等于业务成功。完整调用链、精确配置、文件保存协议、目标未知结果与外部副作用边界留文章。未完成的真实运行只记计划，有限模型输出不冒称Broker实测。

### 01 problem

旁白：同一个订单通知一直失败，应用就一直重试，后面的通知怎么办？跟着这个事件，看看怎样给重试设界限，也给失败留出口。
画面：错误对照：P0日志保留E01@0和E02@1；应用反复调用同一E01，E02等待。有限展示4次循环，不称真实程序无限实验。
出处：R1/R2；应用错误策略对照。

### 02 held-record

旁白：本例只有一个消费者和一个分区，一次取一条，关闭自动提交。应用保留已取到的事件，暂停后续交付；原记录还在日志里，同分区的后续事件也要等。
画面：建立P0/E01@0/E02@1；应用持有E01，原已提交恢复位置0。pause改本地paused flag，Fetch交付门关闭；不画退回Broker或自动重试。
出处：R1/R2；ClassicKafkaConsumer978–984、SubscriptionState1222–1253、FetchCollector125–143。

### 03 reserve

旁白：应用给同一通知业务、同一事件三个调用名额，包含第一次。调用前，先把已用次数加一、记为进行中并保存在本机；保存成功才调用。
画面：本地保留state目录，键notify/E01；journal reserved0→1/IN_FLIGHT，持久化完成后才业务调用；再返回temporary。目录锁/完整身份校验留文章。
出处：原创应用实现examples/Mq08Core.java；开始预留先保存。

### 04 deadline

旁白：第一次是临时不可用，应用记下下次尝试时间，暂时不再调用业务。等待时仍短间隔轮询Kafka；暂停挡住新交付，计时和重试由应用负责。
画面：记录BACKOFF/readyAtMs（画面称下次尝试时间），now<deadline门关闭，poll owner继续以维护成员活跃，不触发handler；E01由应用持有/E02等待。时间轴压缩并标示非实时，不无界sleep，不用普通Topic冒充延时。
出处：R1/R2；应用deadline门和worker持续poll。

### 05 crash-after-start

旁白：到时间且还有名额，应用先保存第二次预留，再开始调用。假设此时进程退出，第二个名额已经占用，业务是否完成却可能不知道。
画面：now达到deadline与reserved<3两条件成立；journal1→2/IN_FLIGHT保存后调用，再crash；业务结果标未知，绝不标已失败。
出处：原创应用与进程故障场景；同机state目录保留。

### 06 restart-journal

旁白：重启仍用原来的状态目录，读回已用两次和进行中状态。上次结果按未知处理，只剩一个名额；重调业务仍需幂等，不能重新领三次。
画面：进程B读取相同journal键/2/IN_FLIGHT，恢复为BACKOFF并设置下一时间；显示剩1。旁注预留写成但调用未开始也会占名额；不承诺精确3次实际调用。
出处：原创应用恢复分支；结果未知需幂等。

### 07 temporary-success

旁白：先看服务恢复：到下一尝试时间，第三个名额保存成功，再调用原事件。业务返回成功，应用另行提交原分区的下一位置一，成功后再放行后续事件。
画面：reserved2→3保存→handler success→BUSINESS_DONE→独立commit P0:1成功→resume；E02才可交付。原日志E01/E02仍在。
出处：应用成功分支；R4原进度提交。

### 08 budget-exhausted

旁白：回到已用两个名额、第三次尚未开始的相同状态，只改成服务仍失败。第三次也失败，已用次数达到三，判断便挡住第四次调用，转为等待处置。
画面：显式reset共同recover-ready-two，不复活成功现场；预留3/临时失败→DLQ_PENDING，尝试4的调用门关闭。
出处：原创条件对照；预算耗尽。

### 09 permanent-reject

旁白：如果一开始就是明确的永久业务拒绝，不必用完三个名额。回到未尝试的起点，第一次返回永久拒绝，应用直接转为等待处置。
画面：reset原E01已持有/0次/commit0；先预留1，再fixture永久拒绝→DLQ_PENDING，剩余2不调用。分类由应用业务规则决定，不将任意异常判永久。
出处：原创应用错误分类；永久拒绝。

### 10 dlq-envelope

旁白：应用把原事件、来源位置、已用次数和失败原因整理成死信记录。死信只是另一个普通主题，保存问题供后续检查，不代表通知业务成功。
画面：明确切回已耗3次的耗尽路径；显示DLQ envelope原E01+source orders/P0@0+reserved3+reason；业务状态“未获成功确认”。无自动修复/自动回放箭头。
出处：原创应用DLQ envelope；R3生产者能力。

### 11 dlq-confirm

旁白：发出死信后，先等这次发送的最终结果，调用返回不等于写成。只有取得成功的分区和位置，才记住转存已经确认；此时原消费位置仍是零。
画面：producer send返回Future pending，DLQ日志追加E01@0后成功metadata，journal DLQ_CONFIRMED；原commit0保持。acks=all/RF1实验范围，不展开副本。
出处：R3；Sender/ProducerBatch/FutureRecordMetadata链。

### 12 commit-source

旁白：接着再单独提交原记录的下一位置一，成功后才恢复后续交付。死信发送和原位置提交，是先后两件事，不是一次原子提交。
画面：DLQ_CONFIRMED且原commit0→offset request in-flight→success原1/journal COMMITTED→resume P0；E02出现可处理。死信不等于原业务完成。
出处：R4；应用独立commit阶段。

### 13 dlq-unavailable

旁白：再回到发送死信前，只把目标改成不可用。如果发送最终报错，应用保留等待处置和原位置零，停止这个流程，不能假装已经转存或跳过去。
画面：reset耗尽/DLQ_PENDING/原0/目标空；真实最终发送失败→pending/terminal error，不能由短get超时判断最终失败。目标日志有无不据异常一概断定；E02仍受阻。
出处：R3；目标失败分支和失败可能结果未知边界。

### 14 double-boundary

旁白：还有一个空隙：死信已经写成，本机没来得及记住结果，原位置也没提交。重启后原事件仍会再来，应用可能再写一份死信；同一事件也可能占两个位置。
画面：reset发送前；DLQ E01@0确认→在本地DLQ_CONFIRMED保存前crash→原commit0/journalpending→restart重读E01→新应用send→DLQ E01@1；保留两条原身份相同的记录。另小注若本地已记确认则可直接补原commit，但仍非原子/跨机保证。
出处：原创崩溃窗口；R3/R4为独立确认边界，不宣称exactly-once。

### 15 recap

旁白：有限重试由保存的预算和到期判断控制，进程重启也不随意清零。确认死信后还要确认原位置，待处置不等于业务成功；修复后的回放仍要防重复。
画面：收回稀疏分支：到期且有余额→保存名额→调用；业务成功直接原commit；临时失败且余名额返回等待门；永久拒绝或预算满才待处置→确认DLQ→另commit原进度；公共日志和状态不伪造恢复为成功现场。IT小村·原创。
出处：应用策略回收；来源边界。
