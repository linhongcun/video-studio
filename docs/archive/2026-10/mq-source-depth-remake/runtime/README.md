# MQ源码深入重制：最小真实Kafka验证

日期：2026-10-30（UTC）。状态：**真实运行通过**。完整首轮运行：[run-20261030T120117.612545Z](runs/run-20261030T120117.612545Z/)；与MQ02无静态成员条件对应的后续动态组运行：[run-20261030T120411.068260Z](runs/run-20261030T120411.068260Z/)。首轮组实验使用静态实例身份，不能作为影片无静态配置的完全实证；后续只重跑producer种子与动态组，不重跑position。这是MQ01–MQ03核心机制的窄范围运行证据，不是成片质量检查或用户观看认可，也没有运行MQ04未知响应故障、三副本确认或业务副作用实验。

## 环境与输入身份

- 官方Apache Kafka 4.4.0二进制包`kafka_2.13-4.4.0.tgz`，135,295,923字节。
- 原下载URL：https://archive.apache.org/dist/kafka/4.4.0/kafka_2.13-4.4.0.tgz
- 官方校验URL：https://archive.apache.org/dist/kafka/4.4.0/kafka_2.13-4.4.0.tgz.sha512
- 原校验字节：[官方sha512](kafka_2.13-4.4.0.tgz.sha512)。官方文本使用8位十六进制分组与换行；核对时仅去掉文件名冒号后的空白，未修改原文件。完整实际SHA512：`f5ceba8a265ab6bb2d68362b1f6859a95e15d60ef92ba83b43fdf065b557dc18e98d6383c15b9977320e25b3a2c8b6f11decb17b0fa6c0f163423793a0eb95cb`。
- [下载与验证回执](distribution-verification.json)保存读取日期、HTTP HEAD、16个官方host分段GET的实际Content-Range与整包核对结果。初始单流下载过慢，停止的仅为本次下载进程；随后通过同官方域Range请求重组，全量SHA512匹配后才解压运行。未换镜像或绕过代理。
- Java21.0.12.1，包含`jdk.compiler`。系统没有`javac`可执行文件，实际用`java com.sun.tools.javac.Main`与Java源文件启动模式；不安装或修改系统Java。
- 真正运行的客户端报告`kafkaClientVersion=4.4.0`、`kafkaClientCommit=1156b2752aaa28ea`，与本轮固定源码提交前缀一致；服务端CLI版本及整包校验独立记录。
- 隔离本地单KRaft节点，`127.0.0.1:19092`为Broker、`127.0.0.1:19093`为controller，RF1/minISR1；日志与metadata均位于本任务`/tmp/mq-source-depth-runtime/`，堆256–512MiB。不用Docker，不改系统配置或既有服务。

## 本轮真实观察

源代码：[KafkaDepthProbe.java](KafkaDepthProbe.java)，实际服务配置：[server.properties](server.properties)。成功run内另保存当次输入副本，避免后续工具改动追认旧输出。

| 部分 | 真实观察 | 证据 |
|---|---|---|
| 生产确认与处理分开 | E01已获P0/offset0成功metadata；尚未构造任何消费者时Admin观察P0日志末端为1 | [producer原始stdout](runs/run-20261030T120117.612545Z/producer.stdout.txt) |
| 实际日志字节 | 启动任何消费者之前直接运行官方dump-log工具，P0文件存在E01@0与E03@1，magic2、无压缩、CRC有效 | [物理日志原始stdout](runs/run-20261030T120117.612545Z/physical-log-before-consumers.stdout.txt) |
| 组内分工 | 两分区、三个classic动态成员、RangeAssignor；无group.instance.id，按Admin真实member.id排序核对P0/P1/空，组内每分区唯一归属 | [动态groups原始stdout](runs/run-20261030T120411.068260Z/groups.stdout.txt) |
| 组间独立 | points的单成员S1自己获得P0/P1；稳定后才开放读取，两组各实际收到E01/E02/E03/E04 | 同上，保留每次poll的partition/offset/eventId |
| poll与committed分开 | progress组手动assign P0，max.poll.records=1，auto commit关闭；读E01后position=1但committed=0 | [position原始stdout](runs/run-20261030T120117.612545Z/position.stdout.txt) |
| 重开恢复 | 关闭前一个consumer，不提交1；新consumer首次恢复position0并再次读E01@0 | 同上 |
| 显式提交下一条 | commitSync(P0=1)后关闭；另一个新consumer恢复position1，读取E03@1，此时position2/committed1 | 同上 |

完整首轮**29个运行断言通过**：producer7、静态groups12、position10，见[首轮机器汇总](runs/run-20261030T120117.612545Z/assertion-summary.json)。补充动态组轮**21个断言通过**：producer种子7、动态groups14，见[动态组机器汇总](runs/run-20261030T120411.068260Z/assertion-summary.json)；增加断言确认所有实例均无group.instance.id，并按照真实member.id排序验证Range分工，不把client.id显示名当作排序规则。这些断言由真实API返回值、实际分配和实际poll结果决定，原始stdout/stderr未经编辑。物理日志dump发生在groups命令之前，命令顺序与起止时间见[首轮commands.json](runs/run-20261030T120117.612545Z/commands.json)与[动态组commands.json](runs/run-20261030T120411.068260Z/commands.json)。

输入四事件：P0含E01/订单7042与E03/订单7044，offset分别0/1；P1含E02/订单7043与E04/订单7045，offset分别0/1。producer使用显式分区、StringSerializer、acks=all、幂等开启、max.in.flight=1、retries=3、request timeout10s、delivery timeout60s、linger0、无压缩。consumer使用classic、RangeAssignor、手动提交、max.poll.records=1；所有显式配置由程序直接输出到原始日志。

## 边界

- 探针没有通知发送、积分修改、数据库或其他业务handler。证明的是确认/日志存在可以发生在任何消费者启动前，不能声称测量了某个真实业务系统的“待处理”状态或业务恰好一次。
- 最新动态组分配部分是实际classic `subscribe`与真实Coordinator/RangeAssignor运行，未设置group.instance.id，不是手工编排分配；首轮静态成员结果单独保留其身份，不能追认为无静态成员实验。为隔离稳定状态，每次分配回调先pause，Admin确认两组Stable后才resume读取。只证明这次有限稳定运行，不是重平衡、故障或任意拓扑保证。
- position/commit部分显式使用`assign(P0)`，因此它验证客户端读取位置、手动提交与重开恢复，**不验证动态组重平衡恢复**。同一部分的`group.id=progress`用于保存/取得committed位置。
- RF1单节点不支持三副本/ISR故障承诺；本实验acks=all在RF1前提下，不替代制作模型中的RF3条件。
- 没有拦截成功响应、触发delivery最终超时、测量自动重试去重或重发风险。MQ04仍由固定源码与教学模型单独核验，不把本实验写成MQ04复杂故障实测。
- 文件dump显示记录批次实际存在，不意味着每条消息都已执行独立fsync或在任意故障下不丢失。本轮未跑磁盘故障或性能测试。
- 相同事件ID的读取观察不是业务去重测试。历史保留、日志清理、offset管理命令重置也没有在本轮实测。

## 可复现步骤

要求本地19092/19093空闲、Java21及jdk.compiler、可访问官方archive.apache.org，继承环境代理与CA信任：

```bash
python3 docs/archive/2026-10/mq-source-depth-remake/runtime/download_distribution.py
python3 docs/archive/2026-10/mq-source-depth-remake/runtime/run_runtime.py
```

下载脚本重新取得官方校验、按官方同域字节段下载并验证全包；运行脚本再次核对整包SHA512，提取分发后启动自有Broker进程组。每次新建独立`runs/run-时间/`，保存源/配置副本、原始stdout/stderr、命令、结果、数据段SHA和文件清单，不覆盖旧运行。

运行结束只停止本脚本启动的Broker进程组，并移除本任务`data/metadata`目录。[首轮cleanup.json](runs/run-20261030T120117.612545Z/cleanup.json)与[动态组cleanup.json](runs/run-20261030T120411.068260Z/cleanup.json)确认Broker已停止、数据目录已移除；结束后19092/19093均无监听。二进制包与libs缓存仍在`/tmp/mq-source-depth-runtime/`供本轮其他代理只读复用，未留下运行服务。

## 保留的失败与输入修正

首轮[run-20261030T120018.496549Z](runs/run-20261030T120018.496549Z/)已成功启动Broker，但Java探针编译失败：4.4.0把`AppInfoParser`放在`org.apache.kafka.common.utils.internals`，初稿误用旧包路径。原编译stderr、初稿源及清理结果保留，没有数据观察或通过回执。修正import后先独立编译通过，再在全新空数据目录重跑；成功结果只属于第二轮源输入。

[compiler-check.json](compiler-check.json)与对应原始stdout/stderr保留修后实际编译结果；`com.sun.tools.javac.Main`的编译classpath使用实际jar完整列表，因为直接传通配符给该入口不会像Java launcher的classpath那样展开。该编译检查不冒充Broker实验。

## 动态成员补验的输入差异

首轮为便于固定显示名对应，向notify的N1/N2/N3及points的S1设置了group.instance.id。根审读指出这与本轮MQ02正文选择的动态成员范围不同，因而保留原通过输出，另用新空Broker数据和相同四事件补验。后续探针移除这四个实例的group.instance.id，直接读取Admin的实际consumerId/member.id并按该值排序断言Range归属；client.id只用于显示，未作为比较器。最新源为动态组版本，执行`run_runtime.py --groups-only`可重现本次补验范围；原静态源码仍在首轮run内，字节不变。

补验未更改此前position实验的源输入或输出，未将未重跑的部分重贴为新run。两轮都清理本次自有Broker与数据。
