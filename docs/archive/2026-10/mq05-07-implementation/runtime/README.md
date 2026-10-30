# MQ05–MQ07真实最小运行

本目录独立于上一批runtime与视频制作目录。用户授权的新批实验已在2026-10-30实际执行；三个run均通过，合计121项实际打印断言。源码事实、这些受限运行、教学模型与最终媒体审查各自保留范围。没有启动真实支付退款、积分外部服务、三副本故障或吞吐benchmark。

| 实验 | 真实结果 | 独立运行证据 |
|---|---|---|
| MQ05 / EP45 | DB提交后、Kafka位置仍0时真实终止；不去重重读同一E01积分10→20；唯一键与业务同事务后重读仍10，再独立commit1 | [89项断言](runs/mq05-20261030T152318.187770Z/assertion-summary.json) |
| MQ06 / EP46 | key UTF8 `7042`实际落P0@0/@1；同一日志输入，串行完成最终REFUNDED，受控异步反转最终PAID | [12项断言](runs/mq06-20261030T153232.189835Z/assertion-summary.json) |
| MQ07 / EP47 | classic Range两分区，2→12动态成员稳定且安装一致后仅2非空/10空；poll与业务完成另计 | [20项断言](runs/mq07-20261030T153232.191596Z/assertion-summary.json) |

各run保存本次实际编译的Java源码、脚本、配置、参数命令、原stdout/stderr、物理Kafka日志dump、断言、清理结果与文件SHA。`runtime-files-sha256.json`是当前证据身份索引，不是视频冻结清单，不授权正式编码。

## 版本与运行边界

- Kafka/Java客户端4.4.0。原官方分发包SHA512重新计算一致，重用目录191个bin/libs文件逐个比对归档原字节；每次run再次检查。复用被明确标记，不冒充新的Kafka分发GET。原分发证据路径与字节未改。
- PostgreSQL18.0源码来自官方`REL_18_0`所指提交`3d6a828938a5fa0444275d3d2f67b64ec3199eb7`；本轮GitHub API/tag与codeload均实际读取。压缩包SHA256为`b90e598761827cee3477a6159653914a7fbf02602767ea7122762fa59611513a`。Java21实际编译/运行；PG仅在用户临时目录构建，关闭可选ICU/readline/zlib，不改核心事务源码。
- PostgreSQL JDBC42.7.8由官方Maven命名空间经正常TLS下载；仓中SHA512/SHA256路径404，实际提供的SHA1核验相同，另锁完整本地SHA256。没有宣称存在更强的仓库checksum。
- 所有Broker/PG只监听127.0.0.1，RF1、minISR1。PG本地临时cluster使用trust认证。它们是隔离实验配置，不是生产部署建议。每次run结束仅停止本次拥有的进程组，实际业务数据目录已清理；源码、构建产物与原日志保留。
- 本轮fresh环境状态为running/connected、observations_current=true、HTTP policy enforced。沿继承proxy与CA，未打印secret、未绕过策略或TLS。没有使用Docker。

## MQ05：重读与本地事务

固定一条`E01/order7042/account17/delta10`，逻辑消费者`points`，`auto.commit=false/max.poll.records=1`，classic+Range。Kafka真实日志只有P0@0这一条；业务变化来自同一条日志记录的再次读取。

[schema.sql](schema.sql)创建`processed_events(logical_consumer,event_id)`复合主键和`account_points(account_id,points)`。积分初始`(17,0)`。成功的`INSERT ... ON CONFLICT DO NOTHING RETURNING event_id`才执行`UPDATE+10`，并检查恰好影响1行；二者同一个本地COMMIT。Kafka下一位置1在数据库COMMIT之后独立提交，未形成跨系统原子事务。

[Mq05Probe.java](Mq05Probe.java)通过独立Java进程的`Runtime.halt(23/24)`实际终止处理者。日志先记录DB COMMIT已可由其他连接看到积分10、Kafka committed仍0，再终止进程；随后新消费者实际重读相同P0@0。23/24是预期的真实非零终止码，没有将它们写成正常退出0。原输出分别见`naive-crash/replay.stdout.txt`与`dedup-crash/replay.stdout.txt`。

两个竞争任务是**两个数据库任务**，并非两个稳定classic成员同时拥有同一分区。A持未提交登记与积分10时，B执行同键INSERT，实际`pg_stat_activity`显示`Lock/transactionid`、`pg_blocking_pids`指向A。只有A的决策改变：COMMIT后B返回0不加分；ROLLBACK后B返回E01并加分。两支最终都只有一个标记和积分10。外部连接在A未决时看到积分0/标记0，避免把未提交登记画成已提交事实。

目标账户不存在时UPDATE返回0，整笔事务回滚、标记不保留；另用真实int溢出SQLState22003验证UPDATE执行错误也回滚标记与积分。它们不代表已经覆盖任意业务失败或未知网络提交结果。

## MQ06：日志顺序与应用完成顺序

[Mq06Probe.java](Mq06Probe.java)用空的`orders`两分区、一个producer和一个调用线程，等待E01(PAID)发送确认后才调用E02(REFUNDED)。StringSerializer的UTF8 key为`7042`；实际metadata和单成员classic+Range的poll均是P0@0、P0@1，P1为空。分区结果来自实际返回值，没有预猜后追认。

两个应用对照都使用这次真正poll所得的同一记录列表，投影各自从PENDING开始。串行完成E01→E02，最终REFUNDED；实际双线程与CountDownLatch让支付任务启动但写入前等待，退款先写后才释放支付，完成E02→E01，最终PAID。没有以sleep人为猜测顺序。Broker末端始终P0=2/P1=0，日志未被应用调度更改。

业务部分是实际Java AtomicReference状态投影与任务调度，未运行支付、退款资金操作或数据库。两个对照没有重新Produce，亦不声称对不同分区、多个producer或任意应用调度保证全局完成顺序。

## MQ07：分区所有权上限与完成指标

[Mq07Probe.java](Mq07Probe.java)先在空主题启动2个动态classic Range成员，再新增10个。Admin实际观察Stable且成员数12，与各成员poll线程的本地assignment安装结果一致后，才检查两分区排他且完整的归属：2个非空、10个空。没有用仅线程已启动或subscribe调用成功代替分配完成。

本run最初original-A/B分别拥有P0/P1；新增后实际added-03/04获得分区，original-A/B均为空。完整memberId/clientId/分区列表保存在`observations.json`。这只是本次真实归属，不把成员标签或加入顺序当作固定所有权保证。

业务门控另用一个独立单成员classic组，先前12个成员已经关闭。真实poll到两个分区各一条后，两个Java处理步骤停在latch：polled2/completed0、position各1、committed各0。释放后实际完成2，再各commit1。这能展示poll与处理完成不同，不能推断12成员的业务吞吐。所有每秒速率、容量或清空时长若用于教学，仍须明确是假设值。

## 复现与保留失败

新复现先复制本目录的脚本到新的批次证据目录，避免覆盖现有`dependencies`索引；各实验run本身以UTC时间唯一命名。脚本需在同一仓库树内以找到AGENTS与原官方Kafka分发证据。示例顺序为`prepare_dependencies.py`、`prepare_toolchain.py`、`build_postgres.py`、`run_mq05.py`、`run_kafka_probe.py mq06`、`run_kafka_probe.py mq07`。仅Java21/compiler模块、GCC/make/perl和允许的官方HTTP源必需，不依赖sudo/管理员安装。

失败边界保留：当前Python无requests的首次准备失败；默认APT快照域的实际策略403与无candidate；原Maven强checksum路径404；首次PG构建缺m4；module方式javac的通配符classpath解析失败。APT退出0但无有效索引被判为失败。后续只在策略明确允许的官方当前Debian源读取签名元数据并用户目录解包bison/flex/m4，沿原proxy/CA，不访问被拒快照、不改系统源或安装系统包。最终PG完整构建、编译和三个真实run的成功有独立原输出，不以源码检查追认失败尝试成功。

这些记录只覆盖本目录运行，不改任何旧runtime、生产/共享输入、站点或git；没有TTS、冻结或正式视频渲染。
