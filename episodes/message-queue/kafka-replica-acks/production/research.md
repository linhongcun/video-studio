# MQ15 · E01怎样从日志追加走到成功确认

本期只回答：Kafka返回发送成功时，同一E01在哪些数据副本上，Leader依据什么进度返回。先读实现再选叙事；API与注释只交叉核对，不能替代执行段。EP49 / #323，标题《Kafka 多副本确认：写入成功，到底哪些副本已经跟上？》。基线8769a592856fe2618e5daf3d84849bf4b052e22b，新制作实体目录，旧源码/ignored缓存/冻结不作当前依赖。

## 固定输入与适用范围

产品与Java客户端均Kafka4.4.0，固定commit1156b2752aaa28eafc0b4c4d387e63356793268d。P0单分区，RF3、min.insync.replicas=2，ELR feature level0、unclean.leader.election.enable=false；单producer、每分支单次单条E01/order7042，明确producer幂等false/retries0/inflight1，P0显式指定。当前是非事务写入，不把默认设置或其他分区/集群机器并入等待人数。完整假设与配置在example-config.json。

四个确认/名单分支各自从同样空日志与同一E01开始。稳定ISR内不改变成员，不包含进行中的扩大/缩小、也无额外近期追齐可加入候选；这是把HW取当前集合最小已知位置的适用前提。ISR成员允许短时尚未复制某条新记录，所以选定acks1确认窗口时，另两份仍在ISR但E01还没复制，并不自相矛盾。不宣称发生概率或固定等待时间。

## 真实来源身份与实读范围

sources/download-manifest.json记录16份本轮官方raw GET及16份固定commit GitHub Contents API原响应：URL、真实UTC访问时间、状态、字节数与SHA；API `.name`为真实文件原题，且base64内容与raw逐字节匹配。实际机构取官方Apache Kafka仓库与NOTICE；这些执行文件没有明确个人署名，不把Git提交者推定为作者。版本、访问日期与永久链接分别见references.json/article-sources.json。本轮日期为2026-11-01（北京时间）。

首次把DelayedProduce/Replica猜成旧Scala路径导致404，该检索失败保留sources/retrieval-attempt-01.json；从本commit tree与真实import定位到server Java包后重新GET，不能用猜测旧路径作版本依据。完整source文件下载不意味着逐行读完整产品，实际读到的执行/配置上下文列在sources/source-evidence.json（连续原文、精确行号与永久链接）。未用的整文件旁支不声称已审。

| 链上的结构/状态 | 实际读到的执行位置 | 本期因果与镜号 |
|---|---|---|
|Produce请求的acks|KafkaApis.scala401–419、546–559|请求参数传给ReplicaManager，03/05不是互不相干的“成功定义”|
|准入与Leader本地追加|Partition.scala1219–1243|仅acksall(-1)在ISR不足effectiveMinISR时先抛错；appendAsLeader在该检查之后，06/12|
|requiredOffset与等待结构|ReplicaManager.scala835–849、878–917、1356–1367|lastOffset+1；只有all且有成功追加才安装DelayedProduce，acks1不等待该复制条件，03/06/09|
|Follower日志与下次请求位置|ReplicaFetcherThread.scala111–150；AbstractFetcherThread.scala373–395|先append响应记录，再以lastOffset+1更新自己的Fetch状态；07不搬走Leader记录|
|Leader保存的Follower进度|Replica.java69–101；Partition.scala767–817、1280–1323|下一次Follower Fetch位置写入ReplicaState，随后评估HW；07/08实际LEO与Leader已知值分两列|
|共同进度与完成条件|Partition.scala947–1040|当前稳定集合最小已知末尾限制HW；本版underMinISR不推进HW；HW>=requiredOffset后还检查minISR，08/09/11|
|等待结束与响应|DelayedProduce.java110–119、140–195|未满足则保持pending；条件满足/错误后才完成并回调，09成功响应抵达网站后才标成功|
|clean选主资格|PartitionChangeBuilder.java254–322；ReplicationControlManager.java2095–2144|ELR关闭且unclean关闭，本例控制面从存活ISR的可用候选挑选；04/10只示意稳定结果，不画数据副本互投|
|契约与边界交叉核对|ProducerConfig.java131–150、370–378；TopicConfig.java218–232|all不是minISR数量多数票；ELR改变语义。幂等与acks耦合故本例显式关闭，避免隔离对照失效|
|刷盘是另一条件|UnifiedLog.java1268–1302、2250–2296；TopicConfig.java58–73|追加后的flush检查由flushInterval等配置独立触发，不从all推断每块盘每次fsync；13|

## 数字怎样对应同一条记录

空日志next/LEO为0；本次E01追加的offset0，写完后的next为1。等待目标requiredOffset=lastOffset+1=1。HW采用exclusive上界：HW0尚未涵盖E01@0，HW1涵盖offset<1的本条。教学里Leader已知[1,1,0]时，minISR2已经通过准入，但集合仍3，HW只能0；第三份真实写完还不等于Leader已经获知，下一次Fetch(1)到达并更新ReplicaState之后共同进度才可推进1。

这是固定稳定集合的推导，不把通用HW公式绝对化。实现还考虑maximalISR及近期追齐、满足加入资格的副本；ISR中途变化可产生追加后错误，正文没有模拟这套完整过渡。

## 单Broker故障的精确含义

acks1分支选定合法调度：只Leader有E01，另两份仍ISR却尚未复制；Producer成功之后停止Leader，控制面可让存活ISR副本clean接管，新主日志没有这条记录。原主离线盘的E01字节可以仍存在，因此不写成“全世界三份字节都消失”。若原主重入后的截断/恢复是另一条路径，本文不展开。

all3分支从新的同起点独立执行完整复制与确认；在进度收敛的注入点只停一个Broker，两个存活ISR副本各有E01，可clean接管保留记录。模型刻意选成功后后续Fetch已传播HW的稳定故障点，不把这个后续传播说成Producer成功所必需的额外条件，也不逐帧模拟KRaft控制器投票或新Leader初始化协议。没有推导多盘同时损坏、全部副本离线或不可恢复灾难的保证。

## 错误边界

稳定ISR1/min2、正常非事务all请求，前置检查会在append调用之前拒绝。本片第12镜只说“这次无追加”；本轮实际ISR1发送前后各副本物理LEO均0，且官方快照无记录；该特定结果见runtime-cross-evidence.json。不能把NotEnoughReplicasAfterAppend、总发送超时或响应丢失一律画成空日志。

Partition.checkEnoughReplicasReachOffset在HW达到所需位置后，如有效集合不足minISR会返回NOT_ENOUGH_REPLICAS_AFTER_APPEND；这说明错误名与发生阶段需分开。acks1可以绕过此all准入检查，但本版4.4的maybeIncrementLeaderHW在underMinISR时不前进，不能画成只剩Leader也自动把HW推到LEO。

## 有限模型与真实运行的分工

model.py生成39个教学快照与有限不变量检查，结果在model-verification.json。状态分别保留物理records/next、Leader已知进度、HW、准入、等待、响应在途与Producer最终结果；成功后故障不改写已经得到的确认历史。它不是Broker实验、全协议实现或受众理解研究。

deploy_diagnosis/mq15_runtime在公共本批runtime目录负责真实三节点运行，计划通过CLIENT/REPLICATION/CONTROLLER独立listener与透明Fetch门控隔离数据复制和控制quorum，分别验证ISR3正常、ISR3单慢副本仍等、ISR2成功、ISR1追加前拒绝、acks1/acksall单Leader故障结果。本轮最终runtime已实际通过七类分支，39态教学模型之外另有33份物理日志快照经官方DumpLogSegments成功解码、21个实际批次CRC通过。runtime-cross-evidence.json保存原路径→本地逐字节SHA映射、真实B1/2/3角色与每项观察；完整本地输入/原始观察/官方后验回执在examples/actual-runtime。第一次whole-JVM暂停导致观察超时的失败、后一次officialdump因快照非数字basename失败均在公共A保留；后者以同SHA数字名快照解码闭合，不重跑Broker或改写原false回执。实际三listener门控没有暂停控制quorum。实验没有证明时延benchmark、fsync/断电、多盘损毁或教学中每个内部指令时点；模型与实际运行范围继续分开。

## 制作与当前闸门

完整初稿13镜26句759汉字，script/plan/pronunciation与逐镜执行映射已在本目录。共享prep真实识别###编号+英文slug、每镜一旁白行；初稿格式风险已在任何prep之前修正，保留旧稿及canonical不变证明于qa-self/editorial-format，不伪称发生过丢句takes。root独占声音、封面与正式冻结/编码；当前未TTS、未冻结、未正式编码。

新Remotion只复制当前保留工程的生产基础源码/lock，fresh npm ci记录dependency-install.json；不使用仓外旧缓存、旧声轨/QA/输出/冻结。正文与资料沿不可变style-v1/同色title-author入口，正式渲染真实limitedBT709；需冻结实际当前shared和本轮新证据，不能继承迁移前旧清单。
