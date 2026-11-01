# MQ08：有限重试与死信的源码边界

研究日期：2026-11-01，北京时间。实际状态：本轮已新鲜下载并定向阅读下列执行代码；没有把旧期来源、实验或 verified 状态复制到本期。本记录不宣称已运行 Kafka 实验。

**实际应用API修正（源码包成稿时）：** 本期 `examples/Mq08Worker.java`实际采用显式offset map的`commitAsync`并持续poll，只有成功回调后才记COMMITTED/resume；下表的commitSync段只是同步API对照，不是运行API。对应执行链为ClassicKafkaConsumer异步入口→ConsumerCoordinator1047–1100→doCommitOffsetsAsync1103–1132：独立sendOffsetCommitRequest，成功/失败入completedOffsetCommits，1041–1051由poll路径调用completion.invoke。R4最终摘录绑定实际异步链；下文所有“等提交成功”均指等待该成功回调，不把方法返回当成功。

## 固定范围与公开证据

- 产品/Java 客户端：Apache Kafka 4.4.0，commit `1156b2752aaa28eafc0b4c4d387e63356793268d`。
- 消费者协议：`group.protocol=classic`；一名消费者、单个源分区 P0；`enable.auto.commit=false`；`max.poll.records=1`。DLQ 生产者显式 `acks=all`，本期不用 Kafka 事务。
- 版本不是依据目录名推定：本轮官方 GitHub API 的 `refs/tags/4.4.0` 返回 annotated tag `9661b1ef7a0120e476399250b31d530792506787`；该 tag 的 `object.sha` 指向上述 commit。原始响应见 [tag](sources/kafka-4.4.0-tag.json)、[annotated tag](sources/kafka-4.4.0-annotated-tag.json)。GitHub 返回签名 `verified=false, reason=unknown_key`；此处仅核对版本指向，不宣称完成 GPG 签名验证。
- [source-manifest.json](sources/source-manifest.json) 汇总每份实际 raw GET 的 URL、时间、HTTP 状态、字节数与 SHA-256；每份原始文件旁的 `*.download.json` 另保存响应 headers。全部源码请求 HTTP 200，TLS 校验保持启用。没有下载全仓，也没有沿无关机制遍历。
- 研究主链集中于六个核心文件：`ClassicKafkaConsumer.java`、`SubscriptionState.java`、`FetchCollector.java`、`ConsumerCoordinator.java`、`KafkaProducer.java`、`Sender.java`。其余文件只补齐委托、Future/批次完成和 API 契约的必要短段，不将它们扩展成第二套教学主线。

永久链接均固定上述 commit；下面的行号直接对应本轮保存的原始 Java 文件。

## 一条 E01 的最小执行链

设干净示例日志中 E01 位于 P0 的 offset `k`，下一条为 `k+1`。`3` 是应用示例的总尝试预算，包含首次；不是 Kafka 默认参数。

| 步骤 | 实际代码、条件与状态更新 | 本期因果 |
|---|---|---|
| 1. poll 进入 | [ClassicKafkaConsumer 647–679](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L647-L679) 更新协调/位置，再 `pollForFetches`。该方法 [706–738](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L706-L738) 先收集缓冲，没有结果再发请求、网络 poll、再次收集。`Fetcher.collectFetch` 145–146 直接委托给 `fetchCollector.collectFetch(fetchBuffer)`。 | poll 是取回与维护消费者状态的入口，不是业务 handler 的自动重试入口。 |
| 2. 一次至多交出一条 | [FetchCollector 91–135](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchCollector.java#L91-L135) 从 `fetchConfig.maxPollRecords` 得到本次剩余数量，逐次减去实际返回数。 | `max.poll.records=1` 限制单次交付数量，不代表 broker 一次只取一条，也不代表客户端不存在预取缓冲。 |
| 3. 交付前 position 已前移 | [FetchCollector 149–186](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchCollector.java#L149-L186) 要求分区仍 assigned、fetchable，且 `nextFetchOffset==position.offset`。取记录后若下一偏移量变大，就构造 `FetchPosition` 并写入 `subscriptions.position`。ClassicKafkaConsumer 668–679 随后才把记录交给应用。 | 在此干净连续示例中，应用拿到 E01 时 position 已是 `k+1`，但手动 committed offset 仍是先前值。position 不是业务成功标志。一般日志可能有 offset 空洞或被跳过的记录，不能把所有 position 都机械写成“最后交付 offset+1”。 |
| 4. 应用暂停 P0 | [ClassicKafkaConsumer 978–997](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L978-L997) 只调用 subscriptions pause/resume。[SubscriptionState 1222–1253](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/SubscriptionState.java#L1222-L1253) 的 pause 仅 `paused=true`，resume 仅 `paused=false`，`isFetchable` 要求 `!paused` 以及有效位置、无待撤销/回调状态。 | pause 不调用 seek，不回滚 position，不记重试次数，不启动定时器，也不再次调用 handler。 |
| 5. 等待时继续 poll | [FetchCollector 125–143](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchCollector.java#L125-L143) 将暂停分区尚未交付的 `CompletedFetch` 加入临时队列，最后放回缓冲；不耗尽这些记录。Classic 的 poll 仍进入 coordinator；[ConsumerCoordinator 513–578](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L513-L578) 在自动分配时更新 heartbeat poll 时间并维护组。 | 应用保留已拿到的 E01；后续已预取记录由客户端按暂停状态挡住。暂停期间持续短 poll，deadline 到了由应用再调用所保留 E01 的 handler。为这次本地重试无需 resume；处理完成/提交成功后再 resume 获取后续记录。 |
| 6. 关闭自动提交 | [ConsumerCoordinator 1202–1209](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1202-L1209) 只有 `autoCommitEnabled` 才会定时异步提交。`SubscriptionState.allConsumed` 797–804 从有效 position 组装 offset map。 | 必须 `enable.auto.commit=false`，避免等待/重试中的持续 poll 把已经前移的 position 当成可自动提交的进度。应用显式提交已完成记录的目标 offset。 |
| 7. 尝试耗尽后发 DLQ | [KafkaProducer 1040–1043、1108–1154](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/KafkaProducer.java#L1108-L1154) send 经 doSend 将记录 append 到 accumulator，返回 `result.future`；API 异常可包装为失败 Future，其他异常可能直接抛出。 | 仅 `send()` 返回，仍不能声称 DLQ 写入已确认。应用进入等待发送结果状态，保持源记录未提交。 |
| 8. 等 DLQ 发送结果 | [Sender 671–734](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/internals/Sender.java#L671-L734) 根据 ProduceResponse error 选择传输 retry、失败或完成；[757–763](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/internals/Sender.java#L757-L763) 在成功路径调用 batch.complete。 | Producer 内部网络/协议重试与本期“业务 handler 最多三次”是不同预算。DLQ send 的重试不能重新执行已耗尽的业务 handler。 |
| 9. 再提交源进度 | [ClassicKafkaConsumer 752–770](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L752-L770) 将显式 offset map 复制交给 coordinator，未成功且超时抛 TimeoutException。[ConsumerCoordinator 1146–1181](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1146-L1181) 独立发送 OffsetCommit、等待、检查成功，非可重试错误抛出。 | DLQ 确认后，实际Worker发起 `commitAsync({P0: OffsetAndMetadata(k+1)}, callback)`；持续poll，只有成功回调才能结束该源记录。同步路径在此只作API交叉核对。DLQ 确认与源 offset 提交是两个独立完成边界。 |

## DLQ Future 的真实完成链（有界补读）

1. `RecordAccumulator.java` 429–436 为新批次建立 `ProducerBatch`，`batch.tryAppend` 返回 `FutureRecordMetadata`，把批次放进分区 deque 并登记 incomplete；已有批次的相同连接在 470–482。
2. [ProducerBatch 166–183](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/internals/ProducerBatch.java#L166-L183) 创建共享本批次 `ProduceRequestResult` 的逐记录 Future，并保存 callback/future thunk。
3. Sender 的成功路径见上表；最终失败经 [Sender 835–844](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/internals/Sender.java#L835-L844) 调 `batch.completeExceptionally`。`ProducerBatch` 240–259 把成功/异常交给同一个 done；281–295 用 CAS 确定最终状态。
4. [ProducerBatch 316–342](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/internals/ProducerBatch.java#L316-L342) 先 `produceFuture.set(baseOffset, logAppendTime, recordExceptions)`，按成功或错误触发 callback，最后 `produceFuture.done()`。
5. [ProduceRequestResult 69–82、109–120](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/internals/ProduceRequestResult.java#L69-L82) 先保存结果，再 countdown latch；等待方法等待同一个 latch。
6. [FutureRecordMetadata 61–99](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/internals/FutureRecordMetadata.java#L61-L99) 的 get 等待 latch，读取按 batchIndex 的错误，错误则抛 ExecutionException，否则返回 RecordMetadata；带 timeout 的等待超时只抛 TimeoutException。KafkaProducer 1607–1627 还覆盖发送前 API 错误的 FutureFailure。

本期应显式 `acks=all`；[Sender 653–656](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/producer/internals/Sender.java#L653-L656) 说明 `acks=0` 没有响应也会走完成，不能笼统说“任意 Future 成功都表示收到了 broker 确认”。本记录不展开 acks/ISR 的 broker 复制实现。

为保持暂停期间 poll，应用宜保存 pending Future，在单线程循环内检查完成，再取结果；或只做足够短的有界等待。不要在消费者线程上进行可能超过 `max.poll.interval.ms` 的无限期业务调用、sleep 或 send().get()。源码只证明 poll 的消费者维护路径，不证明任意 handler 时长都安全。

## 应用自定义状态与准确性边界

以下属于本期设计与推导，不是 Kafka 自带的重试、nack、requeue 或延迟队列：

- 应用保留 `ConsumerRecord E01`，键建议 `(topic, partition, offset)`，不把客户端暂停缓冲中的后续记录画成应用待重试的 E01。
- 本地 durable journal 保存 attempt start 数、当前阶段与下一次 deadline；每次调用 handler 前先持久化本次 START，成功后才调用 handler。三次预算包含首次。崩溃若发生在 START 持久化后、handler 真正进入前，也消耗预算；可保证的是至多三次获准的业务开始，不保证三次完成调用。
- deadline 由应用时钟/调度判断；pause 自身没有定时恢复语义。等待时 poll，不自动发起 handler；到期后应用调用所保留 E01，直到成功或预算耗尽。
- KafkaConsumer API 的“下一交付位置”与“已提交恢复位置”在原始文件 73–90 可交叉核对；实现依据仍为上面的 FetchCollector 写 position 和 ConsumerCoordinator OffsetCommit 两条实际链。恢复需要应用 journal 和 Kafka committed offset 一起决定阶段；单靠进程内变量不能跨崩溃保持三次预算。
- `commitSync` 的请求直接使用传入 offset：[ConsumerCoordinator 1284–1304](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1284-L1304) 将 `offsetAndMetadata.offset()` 写入请求；[1361–1375、1465–1469](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1361-L1375) 检查分区响应并完成 Future。这里没有把 send 和 commit 合为原子操作。
- 发送失败/本地 Future 等待超时不能推出“DLQ 一定没有记录”；服务端成功而响应未到客户端是可能的。本例不能宣称无重复 DLQ。DLQ 成功后、源 commit 前崩溃也留有重复窗口；本地 journal 的 DLQ_CONFIRMED 阶段可帮助当前实现恢复，但它与 Kafka 发送/提交仍不是跨系统原子事务。
- pause/resume 仅修改本消费者的分区状态；不删除 Kafka 原日志记录，也不把原记录移动到 DLQ。DLQ 是应用另外发送的新记录。原日志仍受其独立 retention/compaction 策略约束，不能说永久保留。本轮读取链没有触发日志删除请求；若文章要展开 retention/compaction 细节，须另做对应来源研究。
- `SubscriptionState.java` 69–70 明示 assignment 变化会丢失 pause 与 consumed position；本期限定单 P0 的稳定演示，不把暂停状态或本地 journal 扩张成跨消费者再均衡保证。

## 改变关键条件后的预期（源码推导，尚非本轮实测）

| 改变条件 | 能从实现推出的结果 |
|---|---|
| 等待时不 pause，仍持续 poll | position 可前移并交出后续源记录；应用必须处理额外 in-flight 记录。仅 `max.poll.records=1` 不能提供单记录全程阻塞。 |
| pause 后期待 Kafka 自动重新给出 E01 | pause/resume 不回滚 position；已交付 E01 不会因为 pause 被重新放回 FetchBuffer。应用必须保留并重调 E01，或另行显式 seek/恢复；本例采用前者。 |
| 开启自动提交 | poll 中的 autoCommit 分支可提交已前移 position，使业务尚未完成的 E01 被越过。 |
| 只调用 send 就提交源进度 | send 返回的仍可是不成功的 Future；DLQ 后续失败时源记录可能已被跳过。 |
| DLQ Future 成功，但原位点commit成功回调未获确认 | DLQ 已达到其发送完成边界；源 committed offset 尚未获成功确认。应保留阶段、继续 poll，并按已确认 DLQ 状态恢复提交，不能重新花业务尝试预算。 |
| journal 不落盘，进程重启 | Kafka 只知道 committed offset；应用的 attempts/deadline/DLQ 阶段会丢失，三次总预算不成立。 |

## 片尾资料候选与连续原文

建议片尾从以下四份中选 2–4 项。实际原题采用官方源码文件名，不自拟论文题名；机构记 Apache Kafka，未见明确文档个人署名，不从 Git tagger、提交者或维护账号推定作者。

| 原题 | GitHub 官方 API 题名证据 | 适用论点 |
|---|---|---|
| ClassicKafkaConsumer.java | [Contents API 响应](sources/ClassicKafkaConsumer.github-contents.json) 的 `name/path/html_url` | poll、pause/resume、显式 commit 入口 |
| FetchCollector.java | [Contents API 响应](sources/FetchCollector.github-contents.json) 的 `name/path/html_url` | 暂停过滤、交付前推进 position |
| ConsumerCoordinator.java | [Contents API 响应](sources/ConsumerCoordinator.github-contents.json) 的 `name/path/html_url` | 独立 OffsetCommit 请求与成功/错误条件 |
| KafkaProducer.java | [Contents API 响应](sources/KafkaProducer.github-contents.json) 的 `name/path/html_url` | send 返回 Future，不等于发送成功 |

仓库身份的官方 API 响应为 [kafka-repository.json](sources/kafka-repository.json)；这里只据 Apache Kafka 项目仓库归属记录机构，不将版权方当作文献个人作者。四份候选的逐字连续源码摘录、永久定位、题名证据路径已整理为 [quotation-candidates.json](sources/quotation-candidates.json)，可用于文章/研究原文核验；它不是最终 references.json，也没有追认任何媒体已核验。片尾采用 title-author，只显示真实原题与机构，摘录、版本、链接、定位保留在文章与本记录。
