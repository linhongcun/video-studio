新增 MQ05–MQ07 三期实现机制短片及配套图文，延续同一事件的连续推导：

- EP45 / MQ05 · [消费幂等：已经处理过，为什么还会再来一遍？](https://linhongcun.github.io/video-studio/episodes/kafka-consumer-idempotency/)（3分08秒）：唯一约束如何仲裁并发插入，RETURNING 如何决定是否执行积分增量，去重登记为何要和业务写入共用本地事务。
- EP46 / MQ06 · [消息保序：订单已退款，为什么又变回已支付？](https://linhongcun.github.io/video-studio/episodes/kafka-message-ordering/)（2分51秒）：同 Key 路由、分区日志、客户端交付怎样衔接，以及应用异步完成为何仍会打乱订单状态。
- EP47 / MQ07 · [消息积压：加了十台消费者，为什么还越排越长？](https://linhongcun.github.io/video-studio/episodes/kafka-message-backlog/)（3分27秒）：两分区、十二同组成员如何形成分工，poll 返回为何不等于通知完成，怎样按分区推导积压与排空。

固定 Kafka 4.4.0 源码；消费幂等另核 PostgreSQL 18.0。源码原文、121 项真实最小运行断言与教学模型分别留证，不把有限运行扩大为吞吐测试。三片共 80 句旁白、12 幅从正式成片提取的正文图，均含实际资料片尾。资料、动态、声音信号及成片独立复核与本地网页检查通过后发布；线上完整资产和原生播放器将在 Release 后 Pages 部署成功后复核。未作逐字 ASR、全片人工语义听辨、物理手机或学习效果实验。

仅 GitHub 与本站，未进行外部平台投稿。原有四期视频与历史冻结输入保持。

Refs #313, #314, #315.
