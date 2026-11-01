# MQ08研究与执行映射

本轮任务：EP48/MQ08/#316，2026-11-01。基线8769a592856fe2618e5daf3d84849bf4b052e22b，分支codex/mq08-15-implementation-20261101。制作路径episodes/message-queue/kafka-retry-dead-letter/production；发布稿由根负责。未借旧episodes-codex缓存、冻结许可或verified记录。已读现行AGENTS/RULES/研究/流程/图文/声画、L060/S023和制作记忆。

## 一个问题和必要实现

同一E01持续失败，应用怎样用保留在同机目录的预算阻止无界调用，并在退出业务重试后保留问题记录。核心是应用持久化阶段、次数和到期时间的状态机，不是Kafka nack/requeue/DLX/延时队列。Kafka执行仅解释取回、pause门、持续poll以及两个独立确认边界。

固定Java/Broker4.4.0 commit1156b2752aaa28eafc0b4c4d387e63356793268d、classic、单原分区/P0、单消费者、manual commit、单次交付1。示例E01/order7042@0、E02/order7043@1，原已提交恢复值0。notify:E01稳定逻辑身份，最多3个持久化开始预算含首次；本地目录不随进程变化，单实例锁。保存后未实际调用也耗额度；IN_FLIGHT恢复结果未知。业务副作用需幂等；只演进程恢复，不宣称断电耐久、多机共享或完整再均衡算法。

## 实际官方实读

[source-chain-notes.md](source-chain-notes.md)记录定向读取的实际代码、关键结构/条件/状态变化及精确永久行号。[sources/source-manifest.json](sources/source-manifest.json)与逐文件download元数据保存本轮HTTP200 GET、URL、时间、字节和SHA。tag/annotated tag原始响应核对4.4.0指向固定commit；未认领GPG签名验证。额外两份本轮GET ConsumerConfig.java/ProducerConfig.java及各自download.json核对具体配置；未拷贝旧来源。片尾原题取官方Contents API实际name/path，机构为Apache Kafka项目，无个人文献署名。

已实读而非仅引用Javadoc：ClassicKafkaConsumer647–705、978–997；SubscriptionState1222–1253；FetchCollector91–186；ConsumerCoordinator1041–1132及OffsetCommit请求1284–1304；KafkaProducer1108–1154；Sender结果分支与ProducerBatch/FutureRecordMetadata完成链。4条连续原文在references.json，与保存原始字节逐字核验。source notes保留sync API交叉核对，但实际worker是commitAsync显式Map+成功回调，不把sync写成runtime动作。

## 正文执行映射

| 镜 | 对象/结构保存什么 | 条件与动作，为什么得到该结果 | 依据 |
|---|---|---|---|
|01–02|原日志E01/E02；应用持有E01；paused flag|paused挡住新交付，已交付E01不退回/不自动重试；同分区后续等待|R1/R2实际执行|
|03–04|notify:E01、totalStarted、phase、readyAtMs|到期且有余额→先保存IN_FLIGHT和+1→才调用；临时失败设下一时间，owner继续poll|Mq08Core.begin/classify，Worker owner/executor|
|05–06|同目录journal，已用2/IN_FLIGHT|进程退出不退还名额；恢复按未知，deadline后只剩一次|Core.recoverInFlight；进程窗口|
|07–08|共同第三次之前状态|success走BUSINESS_DONE→原commit；temporary且3已用走DLQ_PENDING，拒第四次|Core分类与Worker异步提交|
|09|相同未尝试起点|permanent首调直接pending，不用完3|Core分类|
|10–12|DLQ envelope/Future/metadata；原offset request|send返回尚未确认；成功metadata→保存confirmed→原commitAsync成功回调才结束|R3/R4实际链+Worker|
|13|同一pending/原0，改变目标可用性|最终发送错误保留pending/不提交，异常不一概推出空日志|Worker目标失败；Producer真实边界|
|14|同一pending，ACK到journal的空隙|先写成却没记住，重启可能新send，在DLQ多一个offset|应用窗口+R3/R4独立请求|
|15|预算/时间门/确认边界|回收到期且有余额→保存→调用，待处置不是业务成功|同源模型及应用|

## 三类证据的界线

1. 源码事实：上述本轮官方固定commit原始GET和执行路径。
2. 有限教学模型：build_model.py/model.json，106项断言、41快照；虚拟毫秒、选择结果和状态反例，不是Kafka/文件系统模拟器或真实通知。包含第三次成功/失败共同reset、永久拒绝、目标错误也可能已有DLQ、保存后未调用也消耗预算、confirmed恢复不重复发等。
3. 可执行真实应用：examples/五文件。业务handler是有界可控返回fixture，不是实际通知；纯Java核心/子JVM检查与Kafka组位点/DLQ真实运行分别留证。独立runtime由deploy_diagnosis执行，作者已读实际结果后追加下节，保留源码/模型/真实运行的独立身份。

## 配置核对及边界

ConsumerConfig652–663：max.poll.records限制poll返回，max.poll.interval.ms默认300000。本例明确auto commit false、classic、earliest仅无有效恢复位置、session6000/heartbeat1000、api timeout2000。短poll参数50ms不是实际间隔硬保证。consumer与所有方法只有owner线程；业务fixture/send用单独executor。

ProducerConfig174–185 delivery timeout范围、429 retries默认Integer.MAX_VALUE、KafkaProducer配置校验维持delivery>=request+linger。本例acksall/idempotencetrue/max.block2000/delivery3000/request1000/linger0，属有限隔离实验参数。客户端网络retry不算业务尝试，也不把新进程新send按eventId合并。原commit使用显式P0:offset+1，避免提交尚未业务处理的后续记录。

本机journal保存采用force+atomic replace+directory force，未测硬件断电；时间以epoch毫秒比较，时钟调整影响等待长短；重启不清预算。锁和身份校验仅保护同机同目录单事件。多消费者/再均衡/多分区/并发业务/目录丢失须另行设计，不扩本片承诺。DLQ确认、journal、原提交都非原子，unknown窗口要求业务/处置端幂等。

## 文章与图位

article.mdx四章可独立阅读，R1–R4就近SourceQuote原文。根接受最终声轨6018帧后，4图按真实board定为2212/3114/4354/5525整数帧，seconds=frame/30，MDX seekTo同步九位小数。作者已实际打开对应源预演原图；最终JPEG仍待正式成片按整数帧抽取与独立核验，不预认图像验收。文章中的完整Java程序为原创应用，不拿自写代码冒充Kafka执行代码。正式freeze/render/TTS由根阶段闸门控制，作者不自行运行。

## 独立真实运行结果（实际输出复核后追加）

独立run为`docs/archive/2026-11/mq08-15-implementation/runtime/runs/mq08-20261101T092105.198110Z/`，report.json SHA `dd06c78fef4ece9320440325e17e5410f632855e56fb3204f91e0aaf84039555`。实际Kafka4.4.0/commit1156b2752aaa28ea、单节点RF1/ISR[1]、classic，8case/15个worker子JVM/6次halt86，151断言全通过；代码Worker SHA与D当前a1ea6e69…相同。根和独立执行者保留原始文件索引/编译失败旧源/修正后快照，作者复核范围见qa-editorial/runtime-author-review.json。

实际：temporary两次后success消耗1/2/3、原commit1、DLQ0；permanent首次与三次temporary耗尽分别DLQ1且确认在原commit前；缺失DLQ最终producer失败保留pending/原0，修复目标后同目录重启不再调用handler，成功转存/commit。三次after-begin halt每次在handler前，所以确实预留1/2/3却零次handler，第四进程耗尽转DLQ，证明保守预留而非三次通知。业务fixture返回success后、写journal前halt，重启按未知并用下一个名额再调用。DLQ ACK到journal前halt→旧原0/DLQ1，重启再send得到offset1、两份payload完全相同、最后原commit1；confirmed journal到原commit前halt→重启不再send/handler，只补原commit，DLQ保持1。原日志E01/E02始终两条。

独立运行刻意用backoff500ms、handler700ms来观察owner在BACKOFF/IN_FLIGHT持续poll；模型是虚拟时间400ms，不把两者时长冒称相同。真实辅助E02 value的orderId是7042，示意/README辅助E02是7043；E02从未交给handler，核心E01/order7042相同，这个输入差异不影响已验证机制，不隐藏为完全同一fixture。业务结果仍是模拟返回，不是通知服务真的成功；没有断电/多机/副本故障或E02业务实验。Broker及独立临时数据已由执行者清理，历史证据保留。
