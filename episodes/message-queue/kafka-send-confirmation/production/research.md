# MQ04 · Kafka发送确认：消息发出后，怎样才算发送成功？

核验日期：2026-10-30（北京时间）。EP.44 / `kafka-send-confirmation`，稳定题库MQ04，选题[#312](https://github.com/linhongcun/video-studio/issues/312)，系列[#308](https://github.com/linhongcun/video-studio/issues/308)。开工基线`2c54aa7c5f4e3236500728d3078b356d06625099`，制作分支`codex/mq04-20261030`。已读现行AGENTS、调研/图文/制作流程、教训、成功经验与制作记忆。事件ID需实际前景色可读，结果不得早于动作；本期三路径先总览、再聚焦，共同初始状态明确重置。

**实际范围：官方固定版本原文/源码实读，可执行有限教学模型及测试。没有启动真实Kafka Broker/Java Producer，没有网络故障注入、真实序列化器运行或业务副作用实验。** 下列故障路径是本期选择的合法教学条件，不冒充实测日志；模拟状态与官方支持依据分开。

## 唯一问题与叙事

send调用返回、发送最终成功和发送最终超时，分别能证明什么？沿订单7042的通知事件E01，固定发送方观察、Kafka日志实际、下游业务三列。成功分支展示send返回Future与成功RecordMetadata分开，成功仍不代表通知已处理；从共同空日志起点重置，未知分支改变响应条件，已追加却最终delivery timeout；本批次自动retry不新增记录，关闭旧producer后应用新实例send同eventId则可新增offset1；最后回共同起点，以send内同步序列化失败说明本条确定未发。

不用短暂断网直接代替最终异常，不用`Future.get(timeout)`停止等待冒充producer投递结果；不展开MQ15副本条件或MQ05业务去重实现。

## 版本、原题、署名及实读证据

固定Apache Kafka与Java客户端**4.4.0**。本轮重新GET官方Git标签及tag对象，确认固定提交`1156b2752aaa28eafc0b4c4d387e63356793268d`，原响应在`sources/tag-4.4.0.json`及`sources/tag-object-4.4.0.json`。

通过配置代理、默认TLS校验，重新完整GET该固定commit的官方raw源。文件原字节、URL、HTTP状态、SHA与行数保存于`sources/source-evidence.json`。实际阅读文档frontmatter及相关机制/API/config/内部完成路径，未声称完整精读无关章节，未访问canonical `kafka.apache.org` HTML。片尾两项原题取各自frontmatter第2行；文档及关联声明未见明确个人作者署名，使用Apache Kafka机构署名，不从Git提交者推定作者。ASF原LICENSE与NOTICE原字节保留。

## R1 · Design

- 原始题名：**Design**；题名证据`sources/design.md`第2行。
- 机构：Apache Kafka；未明确个人作者。
- 版本：Apache Kafka 4.4.0；原文未单列页面发布日期。
- 链接：https://kafka.apache.org/44/design/design/
- 实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/design/design.md
- 实读位置：Message Delivery Semantics，第191–202行，生产侧未知结果及消费处理边界。
- 连续原句（第191行）：`If a producer attempts to publish a message and experiences a network error, it cannot be sure if this error happened before or after the message was committed.`
- 译文：生产者尝试发布消息而遇到网络错误时，无法确定错误发生在消息提交之前还是之后。
- 支持主张：发送侧没有成功结果不能普遍推出Broker未追加。日志确认与消费者业务是不同职责；本期精确的最终delivery超时、应用重发和同步序列化路径还由同commit API/内部源码交叉核对，见下文。
- 用在：01冲突、06–09未知/重试/应用重发，文章未知结果；片尾R1。
- 限制：原句是网络错误的一般边界，不能单靠这句话声称任意TimeoutException均已写入。本片实际日志“已有E01”是教学全知观察，不是应用从超时异常推得。

## R2 · Producer Configs

- 原始题名：**Producer Configs**；题名证据`sources/producer-configs.md`第2行。
- 机构：Apache Kafka；未明确个人作者。
- 版本：Apache Kafka 4.4.0；原文未单列页面发布日期。
- 链接：https://kafka.apache.org/44/configuration/producer-configs/
- 实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/configuration/producer-configs.md
- wrapper是生成配置入口，具体配置说明实际读取同commit`sources/ProducerConfig.java`；没有把wrapper当作已读取完整生成HTML。
- 连续原句（ProducerConfig.java第133行）：`The number of acknowledgments the producer requires the leader to have received before considering a request complete.`
- 译文：生产者要求Leader收到多少确认，才把一次请求视为完成。
- 支持主张：acks定义本次生产请求的确认前提；delivery总期限和retries定义可重试过程边界；幂等的acks、retries、max.in.flight条件须同时满足。
- 用在：03–05正常证据、07–08自动retry与总期限，文章完整配置；片尾R2。
- 限制：成功回执不是下游通知已完成的证据。acks=all不是任意配置副本全都已刷入永久介质，也不是等够minISR个即返回；本片不展开副本算法或故障承诺。

## 发送API与最终结果的精确路径

### 1. send返回Future与成功结果

`sources/KafkaProducer.java`第923–951行：send通常在记录加入本地缓冲后返回Future，后台进行发送；成功RecordMetadata提供topic/partition/offset/timestamp。元数据或本地缓冲不足可能让调用阻塞，不能把异步理解为保证立即返回。Future返回时也可能已经完成，本例只选择返回时仍pending的合法调度，不把pending当API恒定保证。

`sources/RecordMetadata.java`第108–119行明确topic/partition字段；正常分支acks=all，成功offset为本例P0/0。acks=0的offset=-1等其他配置不在本片；不从“任意非空metadata对象”推出成功，须检查异常/成功状态。

Future与callback是观察同一发送完成结果的两种方式，不是生产端和业务端的两套确认。`ProducerBatch.java`第316–342行把结果交给future与callback；失败callback的metadata不能笼统假定恒为null，`KafkaProducer.AppendCallbacks`第1676–1682行可能构造无有效offset的metadata，本片只显示“没有有效成功RecordMetadata”，不显示伪成功offset。

### 2. 终态delivery timeout，但Broker实际已成功

**直接源码证据：**`sources/ProducerBatch.java`第263–273行原注释明确：在途批次可能在收到响应前过期，终态为FAILED，但Broker侧可能已经成功；第294–303行用最终状态CAS保持原失败，不把迟到成功改回成功。

本例的故障条件为：原批次已在Broker追加E01@P0/0并满足本例acks要求；在delivery截止之前，原批次和其自动重试的所有可使客户端成功的Produce响应均未被客户端处理。不是一次TCP断开就立刻判最终失败，也不要求Broker没接到请求。

`sources/Sender.java`第185–216行枚举已到delivery期限的未完成在途批次，第428–433行对在途和缓冲过期批次执行失败；第362–375行创建`org.apache.kafka.common.errors.TimeoutException`，错误文字明确可能尚未发送，也可能尚未收到响应。第835–862行完成批次异常，网络请求可能之后才完成，不能凭此抹去已追加事实。

`sources/FutureRecordMetadata.java`第94–99行：无超时参数的`get()`通过`ExecutionException`包装发送失败，cause为上述Kafka TimeoutException。callback观察的是Kafka TimeoutException本身。它与`get(long, TimeUnit)`第69–79行短等待产生的`java.util.concurrent.TimeoutException`不是一回事；本期不使用后者来表示producer最终失败。

### 3. 自动retry与应用重新send

`sources/KafkaProducer.java`第165–182行：producer幂等约束内部retry，明确不负责应用级re-send去重，并建议异常后关闭producer、核查最后结果。`ProducerConfig.java`第307–318行：内部retry受retries和delivery总期限共同约束。

本例打开幂等，自动retry继续使用producer会话A及同一batch序列身份；Broker日志仍是一条E01@0。模型只展开一次代表性自动retry，其余等待/可能的retry省略，不声称重现完整线程调度、网络连接或所有序列状态。

最终失败后关闭旧producer A。为了展示盲目业务重发风险，应用使用新producer B，再次send同一eventId E01；这有新的应用发送身份和producer会话，能在offset1追加另一条E01。新会话batch序列也可从0开始，身份不等于旧会话的0；producer不以eventId或key作为业务去重键。这个对照不是自动重试制造了重复，也不是推荐超时后直接重发。

### 4. 确定的本地序列化失败

本例选择自定义事件序列化器，对无效内容同步抛`org.apache.kafka.common.errors.SerializationException`。`KafkaProducer.java`第1080–1092行的序列化先于第1110–1111行`accumulator.append`，该异常沿第1147–1150行同步抛出；它不是先返回Future后异步callback。

因此这条记录未加入本地待发送缓冲、未发送这条Produce记录，日志保持为空。第1065–1074行的元数据获取在序列化前，故不能扩大为“整个调用从未有任何网络访问”。此确定失败只用于本例已固定的错误路径，不把所有异常都归成明确未写入。

## 固定配置与适用前提

| 范围 | 本例值 |
|---|---|
| Kafka / Java客户端 | 4.4.0，固定commit如上 |
| Topic / 分区 | orders / P0，只有一个分区，显式指定P0 |
| 复制条件 | RF3，min.insync.replicas=2，当前ISR3，条件稳定且满足 |
| acks / 生产幂等 | all / enable.idempotence=true |
| retries / max.in.flight | 2147483647 / 1 |
| request.timeout.ms | 45000 |
| delivery.timeout.ms | 120000 |
| linger.ms / max.block.ms | 0 / 60000 |
| retry.backoff.ms / retry.backoff.max.ms | 100 / 1000 |
| replica.lag.time.max.ms | 30000 |
| 事务 | 不设置transactional.id，非事务发送 |

`ProducerConfig.java`第175–182行要求delivery至少为request+linger；本例120000≥45000+0。第169–171行建议request高于replica.lag.time.max.ms，本例45000>30000。幂等要求acks=all、retries>0、max.in.flight≤5，本例显式满足，不依赖冲突默认项。`KafkaProducer.java`第628–648行实际检查delivery配置。各数字是固定教学条件，不是性能测量、容量建议或回执精确到时承诺；视频省略长等待并明确非实时时长。

同commit`sources/TopicConfig.java`第218–227行核对minISR与acksall：当前ISR3时全3个都需确认，即使minISR2也不是够2个就返回。本片只用“满足本例要求的确认条件”标注，不画副本轨道、不扩大为任意故障零丢失。

## 有限教学模型与验证

`python3 episodes-codex/kafka-send-confirmation/model.py`生成`model.json`与`model-verification.json`；本轮运行**76项断言通过**。它不运行Kafka或Java插件，也不声称验证真实网络重试、Broker序列去重、最终TimeoutException发生概率。

模型三分支从相同空日志、同一E01/订单7042和下游待处理状态重置。发送方观察`producer.senderObservedResult`与实际日志`log.records`分开；每条记录保留eventId、partition、offset、应用发送ID、producer会话、batch序列。`attempts`保存原发送的失败终态，新的B发送成功不会改写A的Future。

覆盖：正常Future返回并非确认；先追加再处理成功响应；成功metadata定位原记录而业务仍待处理；请求超时可retry而不立即终态；幂等自动retry不新增记录；delivery失败仍可已有记录；关闭A后B新应用send同eventId追加@1；同步序列化throw无Future/Produce；迟到响应不得改写原failed；同样的最终timeout观察也可对应没有追加的反例。因此应用不能仅凭错误推定已写入或未写入。

动态动画、文字运动包络、音频、实际编码、资料卡和网站上线须分别检查。官方源码与模型通过不替代真实媒体复核，不预记用户认可；本片不运行下游通知或积分副作用，也不保证业务恰好一次。

## 文章独有精确引用与预定图位

`article-sources.json`另收A1 `KafkaProducer`与A2 `ProducerBatch`，题名使用原始Java类声明的文档标识，机构Apache Kafka，非自拟论文题名；原始固定源码链接及实读证据随JSON保存。A1直接引用同会话幂等边界；A2直接引用在途批次先失败、Broker可能成功的原注释。A2跨Javadoc物理行的内容由`sources/javadoc-excerpts.json`程序提取，仅去除Java注释行前缀、列表标记和源代码物理换行，字词、顺序、大小写和标点保持；原装饰文本、行号和原文件SHA一并保存。两项已通过共享`validateArticleSource`精确证据检查，不增加视频资料页行数。

实际分镜已就绪后，按动画作者确认的每镜稳定尾部预定04/08/09/10四图，整数帧及秒数见`article-figure-plan.json`，Figure已在编码前启用。这里只冻结图位，不声称已从正式媒体抽图或看图验收；成片后root按这四个整数帧生成图片并核验图义。
