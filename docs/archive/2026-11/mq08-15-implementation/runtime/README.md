# MQ08 / MQ15 真实运行证据

本目录只保存这批新建实验的代码、配置、官方依赖身份、原始输出及有限结论。没有运行或覆盖旧批脚本，没有修改生产稿、配音、动画、冻结输入、站点或 Git。实际 Kafka 运行、应用 fixture、源码审读与教学模型分别记录。

官方 Kafka 4.4.0 分发在本轮重新下载，135,295,923 字节，官方 SHA512 核验通过；客户端和实际 Broker 日志对应 commit `1156b2752aaa28ea`，固定完整源码 commit 为 `1156b2752aaa28eafc0b4c4d387e63356793268d`。原 checksum、下载元数据和 191 项分发文件身份见 `dependencies/`。网络沿继承的代理与 CA，TLS 核验开启；未使用 Docker 或绕过网络策略。Java 21 的 `jdk.compiler` 模块可直接编译，没有额外安装 JDK。

## MQ08

入口为 [结果汇总](mq08-runtime-summary.json) 和 [实际运行报告](runs/mq08-20261101T092105.198110Z/report.json)。8 个独立案例、15 个 Worker 子 JVM、6 次真实 `Runtime.halt(86)`，151 项断言通过；该 run 的 153 个源快照、命令、日志、journal 及结果文件已逐项重新核对 SHA。

真实单 Broker、单 P0、classic、手动提交、每次最多取一条。各案例先写入 E01@0 与 E02@1，并明确设置 committed0。作者 Worker 的固定字节快照被编译到本 runtime，未运行会在制作目录写 classes 的包装脚本。业务调用是有限模拟结果和延时；不是实际通知 HTTP 服务。

已覆盖临时失败两次后成功、永久拒绝、三次预算耗尽、目标 DLQ 不存在时确认失败且原 committed 不前进，以及同 journal 修复重启。等待 handler、backoff 和 DLQ 时，暂停该分区而 owner 仍实际 poll。

跨进程证据分别展示：

- 调用前已落盘的三次预算预留不会因重启归零。该案例的三次 halt 都在真正调用前，所以保守消耗了预算，但不能称为已发送三次真实通知。
- handler fixture 返回成功但尚未落 journal，重启会在剩余预算内再次调用。
- DLQ Future 已确认、journal 尚未登记时崩溃，原 committed0；重启实际增加第二条相同 DLQ payload，然后提交1。
- journal 已登记 DLQ 确认、原位置尚未提交时崩溃，重启不再调用 handler 或再发 DLQ，最后提交1。

E02 是阻塞哨兵：Worker 完成 E01、恢复分区后明确停在下一次 poll 前，本实验没有真正执行 E02 的业务处理。journal 是同一个本地 volume 的持久文件和互斥锁，不是分布式全局存储或跨 Kafka 事务。原始 AppInfoParser 包路径编译失败、旧源及作者单行修正边界保留在 `failures/compile-01/` 和初版 `mq08-source-snapshot/`。

## MQ15

入口为 [证据说明](mq15/README.md) 和 [最终派生验收报告](mq15/runs/20261101T092613950298Z/post-validation/report.json)。7 个真实分支、34 项运行断言通过。三个隔离 combined broker/controller 使用独立 CLIENT、REPLICATION、CONTROLLER listener；复制门控保持客户端与控制器通道可用。实际 RF3、minISR2、ELR 官方输出明确为0、unclean 关闭；producer 幂等关闭、retries0、在途上限1及具体超时均留实际配置。

已观察健康 acks1/all、第三副本仍在 ISR3 时两份 LEO1 而 HW0/Future 仍 pending、ISR2 all 成功、ISR1 all 前置拒绝且未追加，以及 leader 故障后的 clean 接管。all 已确认的 E01 在新 leader 上保留；acks1 的确定门控分支只有旧 leader 有 E01，杀死它后 clean 新 leader 无 E01，旧离线文件仍有该记录。这里的“丢失”指当前可服务日志缺少记录，不称离线旧文件已被抹除。

物理 LEO 来自各副本实际批次文件；HW 来自显式 read_uncommitted 的消费者 endOffsets，执行链原字节和永久行号见 [源码核对](hw-source-evidence/chain-audit.json)。33 份空/非空快照经相同字节的合法数字文件名副本，用官方 DumpLogSegments 复核；21 批 CRC 有效。

首轮整 JVM 暂停导致观测 Admin 请求打到暂停节点而超时，原失败 run 保留。完成实际分支后的原 run 仍 `pass:false`，因为最后官方 dump 不接受 `node1-0.log` 这个快照文件名；失败输出未改。最终派生报告仅用 SHA 和逐字节完全相同的快照换合法数字文件名，关闭这项工具核验缺口，没有重跑 Broker 掩盖失败。具体边界见 MQ15 README。

## 核验与清理

运行 `python3 verify_records.py` 只读取本目录、核 SHA 和真实/派生回执，不联网、不启动服务、不写文件。`runtime-files-sha256.json` 是证据身份索引，不是视频冻结清单。

MQ08 Broker、MQ15 三 Broker 与代理均已停止，仅删除了各自标记的临时业务数据；原始日志、配置、快照和失败记录保留。MQ15 12 个隔离端口再次核为关闭，进程清理记录在其子目录。依赖包保留在本机临时缓存，便于作者编译；没有清理其他人的服务。

这些是有限的本地进程和复制通道故障实验，不是断电、磁盘持久性、吞吐 benchmark、任意生产故障保证、外部通知 exactly-once、独立代码审读、动画/配音或最终媒体验收。
