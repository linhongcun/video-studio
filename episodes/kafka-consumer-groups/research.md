# MQ02：多个消费者，分工处理，还是每人一份？

核验日期：2026-10-30（北京时间）。状态：核心官方出处已重新读取，确定性教学模型已运行；未进行真实Kafka Broker/客户端实验。制作基线为最新`origin/main`的`68d2d2dbea525f08fce8a10441b77bec243d9ca7`，独立制作目录`episodes-codex/kafka-consumer-groups/`。选题见[#310](https://github.com/linhongcun/video-studio/issues/310)，系列见[#308](https://github.com/linhongcun/video-studio/issues/308)。

本片只回答一个问题：两个业务都需要每条订单事件时，消费组该怎样划分，组内再加实例又改变什么？因果链为同组错误→独立组各读完整集合→通知组内部扩实例分工。各情景均从同一保留日志、同一起始位置重新对照，不将情景重置画成同一业务先遗漏再补救。

## 版本、读法和证据身份

- 固定Apache Kafka 4.4.0。官方Git标签本轮重新GET，经tag对象解析至提交`1156b2752aaa28eafc0b4c4d387e63356793268d`；原响应见`sources/tag-4.4.0.json`与`sources/tag-object-4.4.0.json`。
- 本轮通过配置代理、默认TLS校验，对该固定提交的官方raw GitHub路径作完整HTTPS GET，原字节和SHA见`sources/source-evidence.json`。随后实际读取原题、相关机制/API/配置段；未声称完整精读无关章节。没有访问canonical `kafka.apache.org` HTML，不把版本文档链接误记为HTML已读取。
- 本文与`references.json`两项片尾文献均取官方文档frontmatter第2行的原题。原文frontmatter与相关声明无公开个人署名，保留Apache Kafka机构署名，不根据Git提交者推定作者。ASF原License、Notice一并保存。
- 只保留两项片尾资料：`Introduction`、`Design`。同版本`KafkaConsumer.java`与`ConsumerConfig.java`作为交叉检查证据，不增加无关片尾卡。两项均为本轮实际使用的来源，绝非只供拓展。

## R1 · Introduction

- 机构：Apache Kafka；无明确个人作者，机构署名依据如上。
- 原始题名：**Introduction**，题名证据`sources/introduction.md` frontmatter第2行。
- 版本：Apache Kafka 4.4.0；原文未单列页面发布日期，版本身份由官方tag和固定提交核对。
- 文档链接：https://kafka.apache.org/44/getting-started/introduction/
- 实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/getting-started/introduction.md
- 读取位置：Main Concepts and Terminology，第69–89行，重点第79/81/83行。
- 支持主张：生产者写入事件，消费者订阅读取；Topic被分区；同一日志允许再次读取，消费不删除记录，保留时间由配置控制。
- 连续原句（第81行）：`Events in a topic can be read as often as needed-unlike traditional messaging systems, events are not deleted after consumption.`
- 译文：一个主题内的事件可按需要反复读取；与传统消息系统不同，事件不会因为已经消费就被删除。
- 用在：Topic/分区建立、独立组遍历同一日志；文章的保留边界。片尾入选R1。
- 边界：不将“消费不删除”推成永久保留，不承诺新组自动取得全部历史。生产者选分区规则本片直接指定，不由示例事件ID推断哈希分区结果。不引用文中“常见副本数”等与本片无关信息。

## R2 · Design

- 机构：Apache Kafka；无明确个人作者。
- 原始题名：**Design**，题名证据`sources/design.md` frontmatter第2行。
- 版本：Apache Kafka 4.4.0，原文未单列页面发布日期。
- 文档链接：https://kafka.apache.org/44/design/design/
- 实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/design/design.md
- 读取位置：The Consumer / Consumer Position，第137/149–159行；The Share Consumer，第246–257行。
- 支持主张：传统消费组内，分区是稳定分配的分工单位；同一分区在一个组内由一个实例读取。本片对照多个独立组与同组多实例，不讲Share Groups。
- 连续原句（第157行）：`Our topic is divided into a set of totally ordered partitions, each of which is consumed by exactly one consumer within each subscribing consumer group at any given time.`
- 译文：主题分成多个全序分区；每个分区在每个订阅消费组内，在任一时刻由一个消费者消费。
- 用在：同组错误分工、不同组完整订阅、通知组扩实例三个情景；片尾入选R2。
- 边界：这是本例传统consumer group在稳定分配状态的规则，不能套用到Share Groups。所选协议固定为`classic`，并不声称只有classic协议才有传统组的分区独占。跨分区不建立总顺序。

## 同版本API与配置交叉检查

### KafkaConsumer.java

实读固定链接：https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/KafkaConsumer.java

本地证据`sources/KafkaConsumer.java`：

- 第94–105行，Consumer Groups and Topic Subscriptions：共享同一`group.id`的实例属于同组，按分区在组成员间分配；每分区分给组内一个消费者。
- 第115–123行：一组是由多个进程组成的逻辑订阅者，可有多个独立组读取同一Topic而不复制存储数据；队列式分工和发布订阅式完整订阅可用不同组组织方式表达。
- 第107–113行说明成员变化会发生重新分配。本片只呈现重分配后的稳定结果，不模拟重新分配时序、停顿或保证零中断。
- 第129–131行，手动`assign`会关闭动态分配和组协调。本例使用`subscribe`语义，不能把手动分区分派冒充真实协调器实验。

连续原文：`Conceptually you can think of a consumer group as being a single logical subscriber that happens to be made up of multiple processes.`（第115–116行，跨注释行的换行不是新增词；文章如使用该段应从原文按原字词引出，不拼接未相邻语句。）

### ConsumerConfig.java 与配置原题

配置文档原题为`Consumer and Share Consumer Configs`（`sources/consumer-configs.md`第2行）。该文档主体是生成页include入口，实际配置说明直接核验同提交`sources/ConsumerConfig.java`，不把wrapper当作已读取生成HTML正文。

- 第120–123行：`group.protocol`明确支持`classic`与`consumer`；本例显式固定`classic`，不依赖默认值暗造结论。
- 第182–190行：只有组没有初始位置或旧位置不存在时才使用`auto.offset.reset`；`earliest`选择当前最早可用位置。它不覆盖一个正常有效的既有提交位置，也不恢复已被保留策略删除的历史。
- 本例每情景从无已提交位置的新组开始；四条记录在示例全程仍保留，最早位置恰为0，所以earliest可读到全部四条。实际部署已有组不能仅改earliest就假定重放。

## 固定教学输入与专项验证

完整同源数据为`model.json`，生成与断言入口为`python3 episodes-codex/kafka-consumer-groups/model.py`。输出`model-verification.json`，本轮运行38项断言通过。属于可执行的有限教学模型，未运行真实Broker或Java消费者，不能写成Kafka实测。

固定`orders` Topic有P0/P1两分区。每条记录只在源日志保留一份；去向动画表示读取到实例，不能搬走源记录。分区显式选定，offset仅在本分区内有效：

| 分区 | offset 0 | offset 1 |
|---|---|---|
| P0 | E01 / 订单7042 | E03 / 订单7044 |
| P1 | E02 / 订单7043 | E04 / 订单7045 |

每种情景完整重置至这份输入与各分区位置0。动画可以按某个跨分区顺序演示，但该顺序仅为观看安排，没有Kafka全局顺序保证。

| 情景 | 组 | 实例与分区归属 | 收到集合 |
|---|---|---|---|
| wrong-shared | shop | 通知N1←P0；积分S1←P1 | N1={E01,E03}；S1={E02,E04}，各业务都缺一半 |
| separate-groups | notify | 通知N1←P0、P1 | N1={E01,E02,E03,E04} |
| separate-groups | points | 积分S1←P0、P1 | S1={E01,E02,E03,E04} |
| scale-notify | notify | 通知N1←P0；通知N2←P1 | 两实例各2条，组内合计完整4条 |
| scale-notify | points | 积分S1←P0、P1 | 仍完整4条，与上一情景完全相同 |

本例订阅所有分区，采用一组合法的稳定分配结果，不实现或预言某个assignor的具体结果。交换N1与N2分区不改变结论。组内不能出现两个实例同时独占同一分区，不画成逐条随机争抢。

模型固定传统Java KafkaConsumer 4.4.0语义、`group.protocol=classic`、`enable.auto.commit=false`、各组均订阅orders；新组无已提交位置且`auto.offset.reset=earliest`。示例设`cleanup.policy=delete`、`retention.ms=604800000`、`retention.bytes=-1`，并显式假设全部记录尚在保留窗口内；不是永久保留或容量建议。未产生业务数据库/邮件副作用，`received`是收到集合，不是业务成功或恰好一次。

专项检查覆盖：四条事件身份唯一、分区内offset/读取次序、每个情景同起点、每组内每分区唯一归属、每组完整集合、各实例仅收到本分区记录、错误情景的业务缺失、独立组的完整集合、扩实例后的2+2而非4+4、积分组不变，以及无效重复分区归属的拒绝规则。片中图义、布局动态、音频、实际编码与网页还需单独验收；模型通过不替代这些检查。

## 不展开的支线

本片不解释offset提交细节与重放（MQ03）、发送确认（MQ04）、消费幂等（MQ05）、保序链路（MQ06）、积压指标（MQ07）、失败处置（MQ08）或副本确认（MQ15）。也不承诺组间同时读到、业务成功、故障零丢失、无限保留或恰好一次。
