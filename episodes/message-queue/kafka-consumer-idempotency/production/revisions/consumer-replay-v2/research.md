# MQ05 消费幂等：同一条 Kafka 记录为何再次处理

本轮日期2026-11-02（北京时间），开工主干基线01cd181caf24d4a8ce846c0eb8faeeab8f0054e2，分支codex/mq05-consumer-replay-20261102。新修订issue #454，原#313为首发历史。本期保留EP45、slug、原标题、首发v0.97.0与既有封面；只写新consumer-replay-v2，不修改旧制作/发布/冻结/证据。

## 本轮教学重点

问题是“只生产一条记录，消费者为何可能在数据库已完成后再处理一次”，而不是唯一索引怎样仲裁并发。前九镜沿E01展示Kafka读取/恢复链，第10镜用提前提交作反例，最后两镜以简单本地事务业务键收尾。前九镜旁白569/805字，70.68%；这是编辑范围指标，真实声音完成后仍要检查时长占比和动作可读性，不预记学习效果。

最新用户反馈优先于旧MQ05研究示例中“PG并发为主”的范围。Kafka前提与实现进入正文：同一记录身份、当前客户端position、组持久committed、恢复赋值、Fetch实参、返回原offset，以及外部DB提交不改变Kafka进度。数据库唯一索引页锁、等待和RETURNING机制不作为正文原理段；文章只解释足以安全实现简单保护方案的本地事务/主键/插入返回条件。

## 固定版本与输入

- Apache Kafka4.4.0、Java客户端，commit1156b2752aaa28eafc0b4c4d387e63356793268d。官方tag和annotated tag指向、源码原始字节、Contents API题名及官方仓库机构证据均为本轮新GET，见sources/source-manifest.json。tag API的签名验证状态不是本次完成GPG验证的声明。
- PostgreSQL18.0固定commit3d6a828938a5fa0444275d3d2f67b64ec3199eb7；本轮新GET的REL_18_0直接指向这个commit。仅实读本地事务、主键与INSERT返回规则，见sources/postgres-source-review.json；不借Kafka源码证明数据库原子性。
- group.id=points、group.protocol=classic、enable.auto.commit=false、max.poll.records=1。单分区P0，同组拥有者A随后B；故障时A已退出，B获得分区后才继续。示例不规定交接需要多少时间，不演两个稳定同组拥有者并发读同P0。
- 唯一事件E01/order7042/account17/delta10，orders/P0/offset0，生产发送一次、实际日志记录一条，logStart0/logEnd1。演示期间记录保留可读，不压缩/清理/截断。
- 账户17初始0；组P0初始恢复值由实测准备程序Admin.alterConsumerGroupOffsets显式设置0，再向Broker查询确认，不是“无有效提交值时earliest回退”。消费者业务后的提交1才使用commitSync；两者API不混称。auto.offset.reset仅为另一条条件分支，不用它解释本例重复。
- halt发生在外部DBCOMMIT成功之后、应用尚未调用Kafka提交1之前，因而不存在“Kafka提交请求已发送但回复丢失”的结果歧义。本例消费者手动显式提交下一位置1，不能用无参提交把未处理的未来记录进度算入。

## 已实读的最小执行链

完整永久定位与执行段见source-chain-notes.md；本作者又实际读取了下列关键原文，未仅凭Javadoc或助手结论起稿。

| 结构/执行代码 | 读取或更新 | 同一E01的因果 | 正文 |
|---|---|---|---|
| CompletedFetch257–290，FetchCollector149–186，ClassicKafkaConsumer647–679 | 响应原offset0→nextFetchOffset1→SubscriptionState.position1→poll返回 | 第一次取到记录后，A的下一读取位置先变1；这条链不提交外部DB或Kafka组恢复值 | 03–04 |
| ConsumerCoordinator的OffsetCommit请求1284–1304/1337–1349 | 显式Map内offset写入请求；独立网络操作 | DB自己的COMMIT不走这条链；本例halt前未调用它，所以组仍0 | 04–06 |
| ClassicKafkaConsumer1205–1217，ConsumerCoordinator947–995/1481–1511/1570–1596 | 新客户端无有效position→查询同组committed→收到0 | B不是继承A的内存1，而是读取组保存的0；OffsetFetch有groupId | 07 |
| ConsumerUtils192–210，SubscriptionState1195–1205 | 非null且仍assigned→FetchPosition(committed.offset)→seekUnvalidated | 收到0与安装本地position0分为两步；必要位置/leader校验条件仍成立后才fetch | 07 |
| AbstractFetch420–484，Fetcher183–197 | fetchable/无缓冲/节点可用等条件满足，将position.offset放到FetchRequest.PartitionData | B的本地0实际变成请求读取起点0，不是屏幕标签或生产重发 | 08 |
| AbstractFetch181–225，CompletedFetch228–239/334–338 | 以原请求fetchOffset建CompletedFetch；交付对象采用record.offset | 日志尚有E01@0时返回原topic/partition/offset，新的Java对象不是新日志 | 08–09 |

KafkaConsumer.java73–89交叉核对position与committed的API含义；250–256直接讨论外部数据库写成后、Kafka提交前故障导致接手者重新读取。实际执行代码仍是正文恢复因果的依据，API说明不代替执行阅读。

## 关键条件与反例

主路径：log1/组0/DB0→A Fetch0/poll推进position1→业务尝试1/DB+10COMMIT→A halt清内存→B查询同组0→安装position0→Fetch0返回同E01@0→无防护业务尝试2/DBCOMMIT20。数据不是被退回或再生产，而是恢复起点仍位于原记录之前。

提前提交反例先完整reset到a-polled：log仍1、Aposition1、组0、DB0、无标记。只改变顺序，先Kafka提交1再在DB处理前halt。B恢复1/Fetch1为空，DB0；原offset0仍保留，漏的是业务效果而非日志记录被删除。这个分支之后再次reset同一个起点，不能在DB20或未标记的DB10现场凭空增加去重标记。

正确保护分支：首次业务前建立稳定键points:E01；主键登记与账户+10同一个本地DB事务，COMMIT后DB10/key在，Kafka仍0；再演同窗口halt/B恢复0/Fetch0。第二次业务尝试发现已提交key则skip，DB10保持，成功后另Kafka提交1。日志1条、业务尝试2、效果1来自模型独立计数，不把poll次数当作业务调用次数。

数据库方案范围：主键(logical_handler,event_id)，不使用进程名/版本号；本次INSERT实际登记成功才UPDATE积分且要求恰好一行。任一步失败则回滚整段；DO NOTHING冲突不返回旧行作为“本次插入成功”。只保护本地同库积分，不泛化到发邮件/外部扣款/HTTP副作用。应用伪代码明确原创，不冒充Kafka源码。

## 来源身份与精确原文

片尾references.json四项：R1 KafkaConsumer.java（Apache Kafka），R2 ConsumerUtils.java（Apache Kafka），R3 AbstractFetch.java（Apache Kafka），R4 Transactions（PostgreSQL Global Development Group）。原题来自官方源码文件名/Contents API或SGML的实际title，个人署名未明确所以省略author；不把tagger/维护账号/Git提交者当作者。title-author每页最多4项、默认5秒，视频不显示摘录/版本/链接。

文章独有A1 FetchCollector.java、A2 CompletedFetch.java、A3 Primary Keys、A4 INSERT、A5 KafkaConsumer.java的另一段position契约、A6 KafkaProducer.java的生产幂等/事务边界。每项quotation是保存原文里的连续精确字节，不拼接、不改成概括；Javadoc标记原样留在摘录中。A3/A4/R4只用数据库已实读合同，不宣称本轮读取了唯一索引实现。

KafkaProducer.java165–199与750–805实读支持边界：producer retries的判重与原子发送Kafka分区是生产者能力，sendOffsetsToTransaction用于Kafka消费-转换-生产；它没有参加本例外部DBCOMMIT。不能把enable.idempotence/acks或“Kafka支持事务”说成外部业务自动恰好一次。KafkaConsumer328–341另介绍把结果和offset放同一外部系统事务的设计，不是本例commitSync自动做到的事。

## 三种证据与当前状态

1. **源码事实：**本轮固定版本官方GET、实际关键行阅读、完整SHA、原题/机构/精确连续原文；不是只访问链接或核标题。源下载证据保留HTTP状态和UTC/北京时间，未绕TLS、未把旧日期改成本轮。
2. **有限模型：**build_model.py纯标准库生成36全量状态、94检查，通过日志不变、单owner、halt无position、恢复收到值后才安装、Fetch实参、完整reset、20/0/10三结局。它不启动Broker/数据库，不声称时延、磁盘恢复或并发实测。
3. **实际运行：**本轮独立执行者新run为docs/archive/2026-11/mq05-consumer-replay/runtime/runs/recovery-20261102T065614.804079Z，report.json SHA382286a24fa2eaf6956b0955f21a9395c39e7acbdc5df917ba16e595a6937ad2，三个分支91项真实断言全部通过。作者已实际读取该报告、准备/甲/乙关键stdout、物理日志dump、依赖/版本/命令记录与探针代码，不仅引用pass字段；不是作者重新运行。2026-10-30旧89项/无防护20/去重10仍为历史；旧批121项是多期汇总，都不计本轮新断言数。

### 本轮实际运行的范围与对应

实际Java21.0.12.1、Kafka客户端4.4.0/commit1156b2752aaa28ea、PostgreSQL18.0固定源码构建；Broker单节点RF1/ISR1、classic/manual commit/maxPoll1。每个分支新空topic/group/schema、账户17初始0、无登记；实际组名points-分支-运行ID、主题名mq05-分支-运行ID用于隔离，与片中简写points/orders含义一致，不把字面名说成完全相同。

每分支一次producer.send，enable.idempotence=true/acks=all/retries3/max.in.flight1；Broker物理dump均只有P0offset0/E01，logStart0/LEO1，故无防护20不是生产重复导致。准备阶段用Admin显式设置组0并查询确认，A通过subscribe加入，赋值回调调用position触发实际恢复，不显式seek；A的进程halt86退出后才启动B。B实际NetworkClient DEBUG请求体分别见证unsafe fetchOffset0、safe fetchOffset0、early fetchOffset1，topicUUID与Admin查得身份一致，不从应用标签猜网络请求。

- unsafe：A实际poll取得原E01@0，position1/committed0；外连接确认DB10后halt86；B同组恢复0/Fetch0又取得完全相同key/value/P0@0，第二次DBCOMMIT20后commitSync1。
- early-commit：A先确认Kafka1、DB仍0再halt；B恢复1、Fetch1连续有限空poll，businessExecutions0，DB0；物理offset0仍保留。未称“数据库记录被Kafka删除”。
- safe：从新空DB0/无标记开始，A同事务登记(points,E01)与+10/更新一行，外连接确认10+一标记后halt、Kafka0；B同组恢复0/Fetch0，INSERT返回空/UPDATE0行，外部DB仍10/一标记，再commitSync1。没有同时两个稳定Kafka拥有者，也没有本轮PG并发争锁实验。

完整源码Mq05ReplayProbe.java SHA3828e759e492b09682f5f26fc12a6bec7b41b8f7e6c3dccedf0fc053b86448d0、commands.json和三个物理日志副本随run保存。实际探针在B完成后还commit1收尾，教学无防护第09镜停在DB20/组0来展示空隙；这是明确的展示截点不同，不声称模型演完探针全部收尾。报告确认自有Broker/PG停止、三个端口已关闭、自有临时数据清理；真实原始日志/物理副本仍保留。

失败候选保留：最初producer幂等true但retries0被构造校验拒绝；后续AbstractFetch DEBUG不含完整Fetch参数，不能充实参见证。新run改retries3与NetworkClient DEBUG之后才闭合三分支，不删除早期失败、不把所有尝试称pass。运行仅有限进程故障与本地数据库，非断电、性能、多机、外部服务或普遍exactly-once证明。

## 图文与后续闸门

article.mdx四章独立解释因果，引用按R/A就近分布；4幅配图全部采用新consumer-replay-*文件名，保留旧publication图URL/字节。article-figure-plan当前frame/seconds=null，不编造时间；根最终声音/真实board后定整数frame与frame/30秒，并在正式编码前启用Figure/冻结，成片后再抽JPEG实际看图。

整稿严格12个“### NN english-slug”标题，每镜一条旁白且两句；独立编辑审批确切整稿/无分隔旁白SHA之后，根唯一执行TTS。作者不写Main/package/thin wrappers/voice/board/covers/freeze或发布目录。动画由独立制作角色读取同源model/plan，真实声音未产生前只明确placeholder预演，不把其当正式时序或动态通过。
