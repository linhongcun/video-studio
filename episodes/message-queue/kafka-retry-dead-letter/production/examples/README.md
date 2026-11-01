# MQ08：Kafka 重试与死信的可执行应用策略

固定 **Apache Kafka broker / Java client 4.4.0、`group.protocol=classic`**。Java 源码使用 Java 17 语法与 API；完整 JDK 17+ 可编译。此处的重试次数、分类、退避、journal 和 DLQ 都是应用代码的策略，不是 Kafka 自动提供的业务重试功能。

`Mq08Worker.java` 使用真实 Kafka consumer / producer；业务 handler 是有界、可配置的教学 fixture，只等待指定时间并返回 `temporary` / `permanent` / `success`，**不调用真实通知服务，也不伪称已发送真实通知**。`Mq08CoreTest.java` 只验证纯核心和本机进程恢复，不是 Kafka 实测。实际 broker、组位点、DLQ 记录和 JSONL 的实验记录由运行者另存。

## 文件和运行入口

| 文件 | 职责 |
| --- | --- |
| `Mq08Core.java` | 固定 3 个持久化开始预算、状态迁移、身份校验、独占锁、原子 journal |
| `Mq08Worker.java` | Kafka I/O、owner poll、后台 fixture / send、终态 Future 确认、独立原位点提交 |
| `Mq08CoreTest.java` | 纯 JDK 检查，含真实子 JVM 强制退出后恢复与互斥 |
| `run.sh` | 编译运行；不下载依赖，不引用旧制作目录 |

```bash
bash ./run.sh test-core
export KAFKA_HOME=/path/to/fresh/kafka_2.13-4.4.0
bash ./run.sh \
  --bootstrap 127.0.0.1:19092 \
  --topic mq08-orders --dlq mq08-orders-dlq --group mq08-case-success \
  --state-dir /tmp/mq08-state-success \
  --handler-outcomes temporary,temporary,success \
  --backoff-ms 400 --handler-delay-ms 250 --max-runtime-ms 60000
```

脚本默认把 class 写入 `/tmp/mq08-example-classes`，可用 `MQ08_CLASSES_DIR` 指定；日志 stdout 是 JSONL，Kafka 自身诊断写 stderr。完整 JDK 使用 `--release 17`；若环境只有带 `jdk.compiler` 的精简 JRE，脚本改用 `-source 17 -target 17`。后一方式不能独立验证 Java 17 的 API 链接兼容性，正式 Java 17 兼容性应在完整 JDK 17 上复核。worker 启动核验加载的 Kafka client 版本必须恰为 4.4.0。

## 输入与隔离合同

- 一个 worker、稳定不变的 `--group`、一个只含 **P0** 的输入 topic；`enable.auto.commit=false`、`max.poll.records=1`、`auto.offset.reset=earliest`、`allow.auto.create.topics=false`。
- 提前创建输入和正常实验的 DLQ topic。为观察缺失 DLQ 的真实失败，broker 配置 `auto.create.topics.enable=false`，故意不创建 `--dlq` 指定目标。producer 没有与 consumer 的 `allow.auto.create.topics` 等价的禁止自动创建开关，必须在 broker 上禁用。
- 每个独立实验用新的输入 topic、group、state-dir，避免历史记录或组进度污染。**同一实验的每次进程重启使用相同 group、state-dir、topic、DLQ、outcomes、退避与 handler-delay。不得删除 journal 来重置额度。**
- 向输入 P0 顺序写两条 UTF-8 value，第一条为 `{"eventId":"E01","orderId":7042}`，第二条为 `{"eventId":"E02","orderId":7043}`。均为教学数据。worker 的有限 fixture 严格接受上述字段顺序与 E01/7042（7042 也可写为 JSON 字符串），容许空白；不提供通用事件 JSON 解析器。
- key 可为任意字节或 null，journal 保存并核验；生产者分区路由必须保证两条都在 P0。单分区 topic 的 console producer 可直接顺序输入这两行。
- worker 只处理 E01，成功提交 E01 的 `offset+1` 后 resume 并在下一次 poll 前退出。E02 用于观察后续消息等待：等待期间应用只持有 E01，E02 不交给 handler，也不提前提交。Kafka 客户端可能已经预取 E02；这与向应用交付是两回事。

示例准备（仅正常目标）：

```bash
"$KAFKA_HOME/bin/kafka-topics.sh" --bootstrap-server 127.0.0.1:19092 \
  --create --topic mq08-orders --partitions 1 --replication-factor 1
"$KAFKA_HOME/bin/kafka-topics.sh" --bootstrap-server 127.0.0.1:19092 \
  --create --topic mq08-orders-dlq --partitions 1 --replication-factor 1
printf '%s\n' '{"eventId":"E01","orderId":7042}' '{"eventId":"E02","orderId":7043}' |
  "$KAFKA_HOME/bin/kafka-console-producer.sh" --bootstrap-server 127.0.0.1:19092 --topic mq08-orders
```

## 状态、预算与 owner 线程

```text
READY -> IN_FLIGHT -> BUSINESS_DONE -> 原offset+1提交成功 -> COMMITTED
            |
            +-- temporary且仍有预算 -> BACKOFF -> IN_FLIGHT
            +-- permanent / 预算耗尽 -> DLQ_PENDING
                                           |
                                Future终态成功且metadata已取得
                                           v
                                     DLQ_CONFIRMED
                                           |
                                 原offset+1提交成功 -> COMMITTED
```

1. poll 得 E01 后立刻 pause P0，应用保存该 `ConsumerRecord`。唯一 consumer owner 线程持续调用 `poll(Duration.ofMillis(50))`；退避、handler 执行和 DLQ 等待期间都继续 poll。50ms 是 poll 的等待上限参数，不是操作系统调度或真实调用间隔的硬保证。
2. 每次调用 handler 前，先把 `IN_FLIGHT` 与 `totalStarted+1` 持久化，再提交到单线程 handler executor。持久化失败则退出，绝不能调用。上限 **3 个持久化开始预算，包含首次**，不是“3 次额外重试”，也不能保证崩溃场景确实调用了 3 次。
3. `temporary` 在还有预算时写入固定 400ms 教学退避期限；到期直接用应用仍持有的 E01 再调用，无须 resume 或让 Kafka 重新交付。`permanent` 立即进入 DLQ。第 3 个开始预算之后仍临时失败就进 DLQ，不再调用第 4 次。
4. handler outcomes 按**持久化的 totalStarted**选择；列表耗尽后重复最后一项。示例 `temporary,temporary,success` 会在第 3 个开始预算返回成功；`temporary` 会三次临时失败，`permanent` 会首次拒绝。重启不会把列表游标重置为首次。
5. 重启发现 `IN_FLIGHT` 时，上一调用结果未知，该开始预算仍已耗用。若仍有预算，持久化新的 BACKOFF 后再调用；预算耗尽则进 DLQ。崩溃可能发生在登记开始与实际调用之间，也可能发生在真实业务副作用成功与成功登记之间。实际业务必须以 **`logicalHandler=notify` + `eventId=E01`，即 `notify:E01`** 实现幂等；本地 journal 不能证明业务副作用是否完成。

## 本地 journal 合同

`worker.lock` 的操作系统文件锁贯穿 worker 生命周期，同一 state-dir 的第二进程无法进入。`journal.properties` 是唯一状态快照；写入同目录临时文件后 `FileChannel.force(true)`，`ATOMIC_MOVE + REPLACE_EXISTING` 替换，再 force 目录。原子移动不支持时直接失败，不偷偷降级。

journal 校验原 topic、P0、offset、eventId、原始 value 的 SHA-256、logicalHandler，并核验原 key、group、DLQ 与策略参数。保存原 key/value 的 Base64；不得把同目录借给另一事件、另一组或另一实验。`NULL` 表示原 key 为 null，空 key 则保存为空 Base64，两者可区分。

边界是**同机、本地 Linux 文件系统、保留同一目录的进程退出/重启**。未做断电实验，不宣称磁盘/硬件故障保证；目录迁移、丢失、删除或多机并发不在保证内。该 journal 也不是可直接替代数据库事务、Outbox、分布式幂等或 Kafka 事务的生产通用方案。

启动先读取 Kafka 的组提交进度。若 journal 已是 `BUSINESS_DONE` / `DLQ_CONFIRMED`，且 Kafka committed 已经达到原 `offset+1`，说明提交成功而 COMMITTED 登记可能没落盘：直接补 COMMITTED 后停止，**不先 poll E02**。若尚未提交，则分配 P0 后 seek 原 offset，重新取得 E01 核验身份，再只补提交；业务和已确认 DLQ 都不重做。COMMITTED journal 遇到 Kafka 进度人为回退则拒绝启动，要求另建独立实验。

## DLQ 确认与提交是两步

- producer 使用 `acks=all`、`enable.idempotence=true`、`max.block.ms=2000`、`delivery.timeout.ms=3000`、`request.timeout.ms=1000`、`linger.ms=0`。`acks=all` 的实际复制条件仍由实验集群副本及 ISR 配置决定。
- 一个进程对一条 pending E01 只调用 **一次应用 `send`**。它在独立单线程 executor 上执行，防止元数据等待阻塞 consumer owner。Kafka producer 客户端自行重试与业务 handler 的开始预算无关；应用没有 DLQ 无限重发循环。
- owner 先以 `isDone()` 检查 send 调用是否结束，再取得 Kafka 返回的 delivery Future；继续 poll，只有 delivery `isDone()` 后才 `get()`。不存在把 `get(短超时)` 的等待超时误当作发送终态失败的问题。
- 取得终态成功 `RecordMetadata` 后先记录 `DLQ_CONFIRMED`，随后独立 `commitAsync` 原 P0 的 `offset+1`。commit callback 由 owner 的 poll 驱动；提交成功才落 COMMITTED 并 resume。
- 同步 `send` 抛错或 delivery Future 终态失败，保留 `DLQ_PENDING`，退出码 1，不提交原位点。重启同目录可以再尝试一次 send；先前发送结果未知或 ACK 已到但确认尚未落 journal 时，DLQ **可能重复**。
- DLQ payload 包含事件 E01/7042、logicalHandler、幂等键、原 topic/P0/offset、totalStarted、reason、原 key/value Base64。DLQ 的 Kafka key 是 `notify:E01`；key 本身不会使 Kafka 自动去重。

`enable.idempotence=true` 不能把本地 journal、DLQ 写入与原位点提交合成一个原子操作，也不能消除新进程新一次 send 的重复。保留同目录 journal 可以在 `DLQ_CONFIRMED` 后跳过重复发送，**减少而不消除**重复窗口。DLQ 的消费者或重放流程也需按业务幂等键处理重复。

## CLI 与崩溃实验

必填 `--bootstrap --topic --dlq --group --state-dir`。可选：

| 参数 | 默认 / 范围 |
| --- | --- |
| `--handler-outcomes` | `temporary,temporary,success`；1–3 项，合法值 temporary/permanent/success |
| `--backoff-ms` | 400；0–60000，教学配置，不是官方推荐值 |
| `--handler-delay-ms` | 250；0–10000，有界 fixture 等待 |
| `--max-runtime-ms` | 60000；1–600000；到时保留状态并非零退出 |
| `--crash-at` | none，或下表一个钩子；实验专用 `Runtime.halt(86)` |

| 钩子 | 已持久化 / 恢复预期 |
| --- | --- |
| `after-begin` | IN_FLIGHT 已占一个预算，实际 handler 尚未调用；重启等退避后使用下一个预算 |
| `after-handler-success-before-journal` | fixture 已返回 success，journal 仍 IN_FLIGHT；恢复按未知结果处理，实际业务必须幂等 |
| `after-dlq-ack-before-journal` | 真实 send Future 已成功，journal 仍 DLQ_PENDING；重启可能产生第二条 DLQ，原进度未提交 |
| `after-dlq-journal-before-commit` | DLQ_CONFIRMED 已落盘，原进度未提交；重启跳过 send，只补原位点提交 |

第一次指定钩子运行，收到 `crash_hook` JSONL 和退出码 86；恢复运行时去掉 `--crash-at`，其余身份与策略参数保持一致。不去掉钩子则新进程再次到达同一位置会再次 halt。

应核验的独立路径：两次 temporary 后 success；三次 temporary 后 DLQ；首次 permanent 直接 DLQ；after-begin 多进程预算累计；两个 DLQ 确认窗口；缺失 DLQ 的真实终态失败与原进度不动；同目录第二进程被锁拒绝。对每条路径保留输入、CLI、进程退出码、原 group committed、实际 DLQ key/value/offset 与 JSONL。前 44 项核心检查已在本地 Java 21.0.12.1 的 compiler 模块编译执行通过；它们不代替这些 Kafka 路径的运行证据。

关键 JSONL 事件：`config`、`journal_lock_acquired`、每次 `poll`、`journal_persist`、`attempt_start`、`handler_invoked`、`classification`、`dlq_application_send`、`dlq_future_confirm` / `dlq_future_failure`、`original_commit_start` / `original_commit`、`partition_resumed`、`crash_hook`、`fatal`。每行含 UTC timestamp、PID 和 thread，便于核对重启前后预算、owner 线程与暂停期间的 poll。
