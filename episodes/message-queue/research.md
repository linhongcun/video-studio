# Kafka MQ01 入门：本轮官方来源核验

核验日期：2026-10-28（北京时间）。固定版本：Apache Kafka 4.4.0，官方tag解引用commit `1156b2752aaa28eafc0b4c4d387e63356793268d`。本轮实际完整GET官方GitHub固定源，未访问canonical kafka.apache.org HTML，未做真实Broker实验。原字节、SHA与连续引文见source-evidence.json。

范围：仅支撑约两分钟入门的同一订单7042从提交受理、分区日志保存、后台读取处理、业务结果保存、消费进度提交到页面查询结果；复制确认、失败重试、幂等和Exactly Once各自后续展开。

## 核心资料与片尾

### R1 · Introduction

- 机构：Apache Kafka；原文无明确个人署名，不从提交者推定作者。
- 版本：4.4.0；页面日期未单独核验，访问日期为本轮固定源读取日期。
- 原题证据：frontmatter line2，原文件introduction.md。
- 公开文档链接：https://kafka.apache.org/44/getting-started/introduction/
- 固定原文：https://raw.githubusercontent.com/apache/kafka/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/getting-started/introduction.md
- 论点：生产者向topic的某分区追加事件，消费者读取并处理。；消费后不删除记录，记录保留受topic配置约束。；顺序保证限定同一分区。
- 连续原句：Events in a topic can be read as often as needed-unlike traditional messaging systems, events are not deleted after consumption.
- 定位：introduction.md · line 81
- 片尾：入选，按真实原题与机构显示；不显示引文、版本或定位。

### R2 · Design

- 机构：Apache Kafka；原文无明确个人署名，不从提交者推定作者。
- 版本：4.4.0；页面日期未单独核验，访问日期为本轮固定源读取日期。
- 原题证据：frontmatter line2，原文件design.md。
- 公开文档链接：https://kafka.apache.org/44/design/design/
- 固定原文：https://raw.githubusercontent.com/apache/kafka/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/design/design.md
- 论点：消费者按分区记录下一条消息的位置。；本例先处理再保存进度，失败窗口可能重读，不保证任意业务恰好一次。
- 连续原句：It can read the messages, process the messages, and finally save its position. In this case there is a possibility that the consumer process crashes after processing messages but before saving its position.
- 定位：design.md · line 200
- 片尾：入选，按真实原题与机构显示；不显示引文、版本或定位。

### R3 · Producer Configs

- 机构：Apache Kafka；原文无明确个人署名，不从提交者推定作者。
- 版本：4.4.0；页面日期未单独核验，访问日期为本轮固定源读取日期。
- 原题证据：frontmatter line2，原文件producer-configs.md。
- 公开文档链接：https://kafka.apache.org/44/configuration/producer-configs/
- 固定原文：https://raw.githubusercontent.com/apache/kafka/1156b2752aaa28eafc0b4c4d387e63356793268d/docs/configuration/producer-configs.md
- 论点：acks控制生产者完成写入请求所需的确认，不表示下游业务处理完成。；acks=all等待当前ISR；最少ISR条件另受topic配置约束。
- 连续原句：The number of acknowledgments the producer requires the leader to have received before considering a request complete.
- 定位：ProducerConfig.java · line 133
- 片尾：入选，按真实原题与机构显示；不显示引文、版本或定位。

Producer Configs的原题来自同commit文档wrapper。wrapper引用生成的producer_config.html；实际acks说明由同commit ProducerConfig.java的ACKS_DOC提供，本轮直接读该原文（包括被引用的一句）。不将未访问的HTML冒称本轮已访问。

## 图文补充来源

A1 `KafkaConsumer.java` 为官方源文件的真实文件名，不用推测生成JavaDoc页的标题。源码286行明确提交下一条应用将读取的offset；72–89区分拉取位置与提交恢复位置；250–256解释业务操作后commit及其中的重读窗口。图文可用article-sources-candidate.json的连续完整短引。

TopicConfig.java219–231核验min.insync.replicas与acks=all配合。topic-configs.md真实标题为Topic Configs；细节留研究/图文，不为增加条目在片尾强加。

## 脚本与机制边界

- ProducerConfig ACKS_DOC133–147: acks=all waits current ISR; no promise all configured replicas always caught up. TopicConfig219–231 additionally requires min.insync.replicas threshold. Illustrative RF3/minISR2 is a selected configuration, not universal default. Acks is not fsync or a never-loss guarantee.
- KafkaConsumer72–89 distinguishes poll/read position from committed recovery position. Manual Offset Control213–289 supports processing before commit and next-message offset. Processing offset0 then committing1 is valid in a chosen contiguous example, not a claim offsets are always consecutive.
- KafkaConsumer135–148 requires poll for group liveness. API408–410 pause/resume controls fetching assigned partitions in future poll calls. Pausing assigned partition does not mean stopping poll indefinitely without rebalance risk.
- Introduction81: records are not deleted on consumption. Select cleanup.policy=delete and finite retention for teaching. Deletion works by retention/segments, not an exact per-record second timer; no infinite retention promise.
- Introduction83 orders events within a topic-partition; no global FIFO over all partitions.
- Website accepted status, stored business results and webpage querying results are teaching application design. Do not attribute business status/query API to Kafka. Commit is progress metadata, neither page notification nor atomic commit with arbitrary external business DB.
- Input count minus finished-business count is original illustrative arithmetic, not measured Kafka throughput or automatically equal to logEndOffset−committedOffset.

## 建议固定教学前提

- 一个教学topic的一个分区，记录offset0/1/2对应示例订单7042/7043/7044；本例数据连续，不推断所有offset永远连续。
- 生产者acks=all，topic复制因子3/min.insync.replicas2并满足ISR条件；只以正常写入确认建立“已接住任务”，不用“永久不丢失/所有副本已同步/已fsync”等绝对词。
- 消费者关闭自动提交，读到0后先把业务结果保存成功，再手动提交下一位置1；本例不将外部结果存储与Kafka位点说成一个事务。
- 若需演示暂停，暂停已分配分区拉取并继续poll维持活跃；或只表明“尚未读取”，不承诺停止poll仍不会重平衡。
- 记录消费后留在日志，按有限保留策略清理；commit不删除记录，也不通知网页。网页经网站服务查询业务结果，是本教学应用明确选择。
- 短时排空/持续输入2完成1为原创教学计数，不是Kafka吞吐基准。待完成业务数量、消费者commit lag和磁盘保留条数不要混为一个值。
