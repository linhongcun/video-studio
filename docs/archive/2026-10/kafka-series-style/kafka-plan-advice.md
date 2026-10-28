# Kafka系列范围调整建议

日期：2026-10-28（北京时间），代码基线d7a5d768。按根代理传达的本轮最新用户指导：MQ统一Kafka，并同步重制现有MQ01再更换封面。原RabbitMQ机制小图仅为已撤回候选，留work追溯，不安装、不转作Kafka。

保留9个稳定题库号MQ01–08与MQ15；MQ15仍是推荐第9个，不能改号。仅MQ01本轮开始Kafka重制，其他8期仍未开工。14个取消题不恢复为储备。本任务未改动issue，原issue JSON和SHA保留；权威资料由kafka_research专责补齐，本建议不冒充已完成官方来源核验。

## 规划哪些需要改写

| 稳定号 | Kafka调整 |
|---|---|
| MQ01 | 网站服务写Kafka、producer确认后回复受理；消费者处理并提交进度，日志留存不随消费移除；页面独立查询业务结果。 |
| MQ02 | RabbitMQ Exchange/fanout/多个独立队列整体改为Topic、不同consumer group各读一份、同组实例按分区分工。只讲收到归属，必要前提片内建立。 |
| MQ03 | 已是Kafka，重心放日志留存、已提交位置和回退重放；减少与MQ02重复的组间/组内介绍。 |
| MQ04 | RabbitMQ Publisher Confirm/mandatory/return整体改为Kafka send/Future/回调、producer配置和未知结果；副本确认深度留MQ15。 |
| MQ05 | 业务已提交但Kafka进度尚未commit导致重读；本地去重记录与业务修改同事务，Kafka offset另一步提交。 |
| MQ06 | 原Kafka保序框架可保留，复核生产顺序、固定分区数/同Key路由及业务串行完成条件。 |
| MQ07 | 原Kafka传统消费组并行上限可保留，分清日志留存、消费lag、客户端在途和业务未完成数。 |
| MQ08 | RabbitMQ nack/requeue、delivery-count、DLX改为应用控制的有限重试与死信Topic；不能冒称Kafka自带同等Broker命令、调度或转发原子性。 |
| MQ15 | 原Kafka ISR/acks/minISR框架可保留，继续固定ELR/unclean前提，不重编号；与MQ04分别回答生产端证据和副本故障边界。 |

详细候选范围、禁画点及证据方向见series-plan-kafka.json。保留issue原题用于追溯，未来标题与范围须在各期开工前按新Kafka方向定稿。

## MQ01直接影响脚本/分镜的六点

1. 同一7042保持日志记录身份。建议先只展示“已提交位置”，不画完整poll读位置；读取位置会在poll后前进，不能错误等到业务完成才移动“读取位置”。已提交位置表示恢复入口/下一条位置，不是业务数据库的完成标记。
2. 受理回复来自网站服务在收到配置范围内的producer成功证据后做出的应用响应，Kafka不会直接向页面发“订单完成”。producer确认不包含消费业务完成。
3. 消费者暂停发生在尚未取到7042前；恢复后可读取并完成业务。消费与提交进度都不删除日志，7042原记录在该示例保留条件下继续可见。
4. 业务结果先保存，再提交消费进度可减少未处理就跳过的风险，但数据库业务写入与Kafka offset提交不是同一本地事务；入门不展开故障窗口，不能宣称两步天然原子或“仅一次”。
5. 页面仍通过网站服务查询业务结果；不用offset提交、producer确认或Broker信号直接冒充页面完成状态。
6. 高峰示例计数改用“业务未完成任务数”。即便业务排空，Kafka日志留存条数仍可能不减少；不要把日志长度、lag或已经poll数量直接画成未完成数。短时输入停止而业务逐步完成可排空的是业务积压，不是删除Kafka日志。

## 文件与来源协作

series-plan-kafka.json可作为新版共享模板的规划输入，但未来8期不是当前发布封面catalog的实际条目。本次早先成功取得官方apache/kafka的4.4.0 annotated tag ref（tag对象9661b1ef7a0120e476399250b31d530792506787），原JSON在kafka-sources/tag-4.4.0.json，已告知kafka_research继续固定commit并核对权威原文；未重复拉取文档。
