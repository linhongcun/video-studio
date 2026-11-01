# MQ07 · 精简提纲与源码/状态对照

主问题：十二个消费者为什么仍不能让这条通知业务排空。主机制：分区列表形成→只按列表拉取→记录交还应用→受限串行通知成功后才记完成。流量账建立在这条执行链上，不单靠公式。

| 镜 | 因果目标 | 状态与来源 |
|---|---|---|
| 01 | 订单通知的未完成量随扩容仍增长，建立问题 | 业务示意，不冒充监控实测 |
| 02–03 | 先比较2→12的分配，成员顺序不是到达/老资格 | old-two-assignment→twelve-empty→rank-sorted；Range128–171、AbstractPartitionAssignor150–160 |
| 04–05 | 基础0余2，逐个放分区并移出候选，余10空 | quota-zero-two→assign-first→assign-second；Range249–250、280–289 |
| 06 | 稳定分配后共同起点，装本地列表，E01才进入业务跟踪 | installed-stable→first-four-arrived；SubscriptionState315–328/486–496；不抹旧在途 |
| 07 | E01从P0交给应用，position前进不记done | first-two-polled；AbstractFetch432/477–483、FetchCollector178–185、Classic679 |
| 08 | 本例按区串行等待通知API成功，才写业务完成 | notify-waiting→first-business-done；应用伪代码、非Kafka内部动作；每区1/s教学假设 |
| 09–10 | 跟同批事件逐步计数，进20完10，各剩5；业务未完成不是lag/留存数 | growth-tick-2…5；model逐事件深拷贝，不是benchmark |
| 11 | 只降流入至1/s且交替两区，min(可用,1)逐区排空 | lower-rate-start→drain-tick-1…10→after-clear-next-tick；最后只来1条只完成1 |
| 12 | 实例数不能自动扩张本例分区串行业务路径 | 概念回顾，不把片中模型升级为所有业务并发规则 |

图位：05分配完成2250、07已poll未业务完成3260、09五步积压4320、11十步排空5418；按最终6058帧声轨/真实board固定整数帧、frame/30秒与MDX seekTo。作者已实际查看对应PNG；正式MP4导图仍待根生产后检查。
