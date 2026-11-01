# MQ03 · Kafka日志重放：消息读过了，为什么还能重读？

核验日期：2026-10-30（北京时间）。身份：公开官方资料实读与确定性教学模型，**未运行真实Kafka Broker、Java消费者、管理命令或日志清理实验**。本期为EP.43 / `kafka-log-replay`，选题[#311](https://github.com/linhongcun/video-studio/issues/311)，系列[#308](https://github.com/linhongcun/video-studio/issues/308)。开工基线`9e44109511cac1b0fb54d8aa9383b9d7dfe9074b`，分支`codex/mq03-20261030`。根AGENTS、现行流程、调研/图文规范及MQ02预检经验已读取：事件ID用可读前景色，完成标签不得早于实际读取结束，静态边界不代替动态检查。

## 唯一问题与主线

记录已经读过，为什么同一组恢复后或主动回退位置后还能再次读到？本片区分同一分区里的三个对象：保留日志、活跃实例的下一条读取位置、组已提交的下一条恢复位置。源记录始终留在日志，poll推进读取位置，应用处理后手动提交恢复位置；另一组进度独立；整组停止后通过CLI仅重置通知组的P0，再启动便能读取原记录。最后用旧封闭段已清理的反例说明保留边界。

本期不再长篇重复MQ02的组内分工与跨组订阅，但保留合法稳定分配：通知组三实例N1←P0、N2←P1、N3空闲；积分组S1←P0/P1。空闲N3仍是活跃组成员，CLI重置前也必须退出。组内实例多于分区不代表每实例都能同时拥有分区。

## 版本与本轮实读范围

固定Apache Kafka **4.4.0**。官方Git标签本轮重新GET，经tag对象解析确认提交`1156b2752aaa28eafc0b4c4d387e63356793268d`。原响应`sources/tag-4.4.0.json`、`sources/tag-object-4.4.0.json`。

通过现有代理与默认TLS验证，对固定commit官方raw源作新的完整HTTPS GET，文件、字节数、SHA见`sources/source-evidence.json`。随后直接阅读各原题frontmatter和相关机制/API/配置/工具实现段，不声称精读无关全文；未读取canonical `kafka.apache.org` HTML。配套文章保留版本文档链接、固定GitHub链接及本轮实际raw读取链接。

文档frontmatter与关联API、配置和命令说明未见明确个人作者署名，使用**Apache Kafka**机构署名，不从Git提交者推断作者；保留ASF原LICENSE与NOTICE。四项片尾原题均直接取frontmatter第2行，一页、无旁白5秒，仅显示原题与机构。

## R1 · Introduction

- 原始题名：**Introduction**；题名证据`sources/introduction.md`第2行。
- 作者/机构：未明确个人作者，Apache Kafka。
- 版本：Apache Kafka 4.4.0；原文未单列页面日期。
- 链接：https://kafka.apache.org/44/getting-started/introduction/
- 实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/getting-started/introduction.md
- 位置：Main Concepts and Terminology，第79–83行，重点第81行。
- 主张：消费不会移走或删除源记录；保留策略决定还能读取哪些记录。
- 连续原句：`Events in a topic can be read as often as needed-unlike traditional messaging systems, events are not deleted after consumption.`（第81行）
- 译文：主题中的事件可按需要反复读取；与传统消息系统不同，事件不会因为已消费就被删除。
- 用在：日志仍在、另一组读取、重放；片尾R1。
- 限制：不从消费不删除推出无限保留或任意历史可恢复。

## R2 · Design

- 原始题名：**Design**；题名证据`sources/design.md`第2行。
- 作者/机构：未明确个人作者，Apache Kafka。
- 版本：Apache Kafka 4.4.0；原文未单列页面日期。
- 链接：https://kafka.apache.org/44/design/design/
- 实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/design/design.md
- 位置：The Consumer / Consumer Position，第137/149–159行；Message Delivery Semantics，第197–202行。
- 主张：分区位置是下一条消息的offset，消费者可回退；读取、业务处理与保存恢复位置是不同动作。
- 连续原句：`This means that the position of a consumer in each partition is just a single integer, the offset of the next message to consume.`（第157行）
- 译文：消费者在每个分区中的位置只需一个整数，即下一条将要消费的消息的偏移量。
- 用在：0→1→2、手动提交恢复点、回退重放；片尾R2。
- 限制：offset不必在所有Kafka场景中连续；本例固定无事务/无压缩的两个连续记录。position推进不是业务完成证明，更不是业务与Kafka进度原子提交。

### 同版本KafkaConsumer API交叉检查

`sources/KafkaConsumer.java`第72–89行明确两种位置：position是下次poll返回记录的位置，随poll收到记录自动推进；committed是已安全保存、重启恢复使用的位置。第286–288行、1016–1025行明确提交的是下一条，而非刚处理完那条本身。

本例每次poll只返回一条，显式`max.poll.records=1`，依据`sources/ConsumerConfig.java`第95–99行；该参数不改变底层fetch行为，不宣称Broker每次只传一条。关闭`enable.auto.commit`，按当前已处理的分区提交下一条，不能用一次全局commit误提交其他未处理记录。

## R3 · Basic Kafka Operations

- 原始题名：**Basic Kafka Operations**；题名证据`sources/basic-kafka-operations.md`第2行。
- 作者/机构：未明确个人作者，Apache Kafka。
- 版本：Apache Kafka 4.4.0；原文未单列页面日期。
- 链接：https://kafka.apache.org/44/operations/basic-kafka-operations/
- 实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/operations/basic-kafka-operations.md
- 位置：Managing consumer groups，第238–259行。
- 主张：CLI重置前实例须inactive；dry-run预览，execute才执行，范围需限定组与主题/分区。
- 连续原句：`Also, first make sure that the consumer instances are inactive.`（第238行）
- 译文：也要先确认消费者实例处于非活跃状态。
- 用在：整组停止、预览与执行只改notify/P0、重启；片尾R3。
- 限制：文章中的命令是按官方语法写出的示例，未实际运行，不能将模型回执当作CLI终端记录。

### 工具源码交叉检查

- `sources/ConsumerGroupCommand.java`第631–659行：检查整个组的状态，Empty/Dead允许重置；其他状态报错。第669–681行：未带execute默认dry-run，execute调用`alterConsumerGroupOffsets`改变选定map；第945–950行转交主题/分区范围解析。
- `sources/GroupOffsetsResetter.java`第247–297行：接受`topic:partition[,partition]`，所以`--topic orders:0`仅选P0。第150–172行、300–305行：`--to-offset`请求超出当前可用范围会钳制，低于earliest则调整到earliest，不能假装成功回到已删除位置0。
- 本片示例使用`--group notify --topic orders:0 --to-offset 0`，先dry-run再execute；P1的提交位置2、积分组的所有位置不变。CLI重置改变committed，不是对一个仍在运行的实例调用seek；整组停用期间不显示仍有一个活跃读取position。

## R4 · Topic Configs

- 原始题名：**Topic Configs**；题名证据`sources/topic-configs.md`第2行。
- 作者/机构：未明确个人作者，Apache Kafka。
- 版本：Apache Kafka 4.4.0；原文未单列页面日期。
- 链接：https://kafka.apache.org/44/configuration/topic-configs/
- 实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/configuration/topic-configs.md
- 实际机制正文：wrapper指向生成配置；本轮直接读取同提交`sources/TopicConfig.java`的`SEGMENT_BYTES_DOC`第35–43行、`RETENTION_MS_DOC`第83–89行、`CLEANUP_POLICY_DOC`第200–206行，并查看第159–161行的文件删除延迟。
- 连续原文短引：`Retention and cleaning is always done a file at a time`（TopicConfig.java第36行）。这是原字词的连续短语，未拼接多条Java字符串或添加原文没有的标点。
- 译文：保留清理始终以文件为单位进行。
- 主张：旧日志段满足delete保留条件并实际完成清理后，已删除的旧记录不能靠回退offset重建。不是单条消息到时立刻删除，也不是等消费者全部读完才删除。
- 用在：最后的保留边界分支；片尾R4。
- 限制：本例本地日志、`remote.storage.enable=false`，不讨论分层存储的本地/远端保留差异。不能把封闭段的例子说成active segment永远不会清理；该版本retention满足也可能触发滚段。时间/大小策略、清理调度与文件删除延迟影响实际时点，本片只给出满足条件且清理已完成的状态，不承诺毫秒精度。

## 固定教学数据与模型

`model.py`生成同源`model.json`；本轮运行**137项断言通过**，真实输出`model-verification.json`。未启动Broker、客户端、CLI或文件删除。这是带完整状态快照和拒绝路径的可执行教学模型，专项结论只覆盖这个输入和明确规则。

| 分区 | offset0 | offset1 |
|---|---|---|
| P0 | E01 / 订单7042 | E03 / 订单7044 |
| P1 | E02 / 订单7043 | E04 / 订单7045 |

本例传统consumer group与稳定分配，`group.protocol=classic`；通知组N1负责P0、N2负责P1、N3为空闲活跃成员；积分组S1负责两个分区。P1两条记录在开头前均已处理并提交下一条位置2，两组P0的有效committed起始为0。后续只展开P0，P1始终保留在背景，其已提交位置不无故跳变。

主线快照：

1. notify poll E01：position=1，committed仍0，应用尚未处理；处理后再commit1。
2. notify poll E03：position=2，committed仍1；处理后再commit2。日志中E01/E03还在原处。
3. points独立poll/处理/commit P0的E01/E03，其committed0→1→2；notify不变。两组P1都保持2。
4. 停止notify的N1/N2/N3；组无活跃成员，运行态position记为null，committed仍P0=2/P1=2。
5. dry-run得到P0目标0但不修改；execute仅notify/P0的committed变0，P1和points完整状态不变。
6. 重启notify，N1由committed0恢复读取；再次读到同一E01/offset0、E03/offset1，不制造新eventId或搬走源记录。
7. 另一保留边界：旧封闭P0段[0,2)先满足保留条件，再完成整段清理；earliest=2、logEnd仍2，offset不重编号。若此后CLI请求0，会被钳制到2；当前日志没有旧两条可供返回。

模型的`groups.*.position`只汇总本例各分区当前拥有者的客户端内存读取位置，不是Broker持久保存的“组级读取位置”。仅剩idle N3活跃的拒绝测试用于抽象验证“只要有活跃成员就拒绝reset”，不声称它是正常协调后的稳定分配结果。

专项断言包括：>2实例仍每分区唯一归属、poll前进而commit不动、收到不等于处理、提交下一条、另一组不受影响、活跃组拒绝reset、仅剩idle成员也拒绝、dry-run无状态修改、合法reset分区范围、重启恢复点、重放同事件与offset、未满足条件拒绝清理、整段清理与P1保持、已删位置请求钳制及旧记录不可恢复。第三个通知实例不会凭空分到第三分区，也不能在reset前因空闲而被忽略。

只记录应用“处理过该事件”的观察，未运行积分/邮件等外部副作用；重放后处理观察中可以再次出现E01/E03，不宣称真实业务可安全重复或恰好一次。幂等与数据库事务另属MQ05，不在本期假定已解决。

## 编码前仍需独立完成的检查

来源预检、脚本/图文准确性、位置标签的实际字形可读性、poll/处理/提交分步与跨镜连续性、无字幕动态、配音时序、最终资料卡、实际成片、网站与线上完整SHA分别验收。模型或文档核验通过不代替真实媒体检查，也不预记用户认可。
