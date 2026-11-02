# MQ05 consumer-replay-v2：同一条 E01 为什么又被读到

研究日期：2026-11-02，北京时间。状态：本轮新鲜 GET、定向实读和文件完整性核对已完成，供本修订文稿整合。本文只讨论 Kafka 读取位置、恢复位置与 Fetch 链；外部数据库 `+10` 属于应用示例，数据库实现与方案由本期其他研究负责。本轮没有运行 Kafka 实验，不把教学状态表当成实测。

本期按最新反馈，以 Kafka 重读的原因作为主要解释对象；不沿旧 MQ05 示例展开数据库唯一约束的并发或锁内部机制。

## 固定条件与下载身份

- Apache Kafka 及 Java clients **4.4.0**，commit **`1156b2752aaa28eafc0b4c4d387e63356793268d`**，`group.protocol=classic`。
- 示例只有一个源分区 P0，E01 位于 offset 0；关闭自动提交 `enable.auto.commit=false`，`max.poll.records=1`。A、接手的 B 使用同一个 `group.id`。开始时已存在并确认该组 P0 的 committed offset **0**，不是“没有已提交 offset”。
- A 拿到 E01 后，在外部数据库提交 `+10`，然后在 Kafka offset 提交之前 halt；不调用 producer 重新发送，不写新日志记录。B 获得 P0 后按该组已提交位置恢复。
- 前提是该日志的 E01@0 仍可读取，期间没有 retention/compaction 删除、日志截断或应用显式 seek。组接手的等待时间与再均衡过程不是本轮研究对象，不承诺 halt 后 B 立即得到分区。
- 全部源码来自本轮对官方 raw.githubusercontent.com 的 HTTPS GET，保留正常证书校验；没有复用旧修订文件、旧期日期或 verified 状态。逐文件 URL、状态、请求/接收 UTC 与北京时间、response headers、完整 SHA-256、字节数保存在 `sources/*.download.json`。
- [source-manifest.json](sources/source-manifest.json) 汇总 9 个必要源码文件及实际阅读行段；[source-integrity-check.json](sources/source-integrity-check.json) 记录 raw 字节/SHA、官方 Contents API 内容与连续引文核对结果。所有下载 HTTP 200。
- 官方版本指向证据：[4.4.0 ref](sources/kafka-4.4.0-tag.json) → annotated tag `9661b1ef7a0120e476399250b31d530792506787` → [tag object](sources/kafka-4.4.0-annotated-tag.json) 的 `object.sha` 为固定 commit。API 返回签名 `verified=false / unknown_key`；此处核对版本指向，没有宣称完成 GPG 签名验证。

## 已确认的因果

**A 的 position=1 只是本消费者下一次读取的位置；committed=0 才是这次接手恢复所使用的进度。数据库已经提交 `+10`，并不会自动把这个 Kafka committed offset 改成 1。B 从 committed 0 初始化自己的 position，再发送 Fetch offset 0，所以交付的是日志中原来的 E01@0。**

这里既没有 producer 再次发送，也没有给 E01 分配新日志 offset。新的 Java `ConsumerRecord` 对象不代表新的 Kafka 日志记录；它的 offset 来自响应记录原有的 `record.offset()`。

## 五个核心执行入口

下面五个入口足以支撑正文主线。其他必要短段用于补上委托、赋值和原记录偏移量的连接，不按文件数量展开新的机制。

| 核心入口 | 实际执行与关键条件 | 对 E01 的含义 |
|---|---|---|
| `ClassicKafkaConsumer.poll / updateFetchPositions` | [647–700](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L647-L700) 在取记录前更新协调/位置，随后返回所收集记录；[1205–1226](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L1205-L1226) 发现没有全部有效 position 时，请 coordinator 初始化 committed offsets。 | 新 B 没有继承 A 进程中的 position=1；它要获取自己的起读位置。 |
| `ConsumerCoordinator.initWithCommittedOffsetsIfNeeded / fetchCommittedOffsets` | [947–1004](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L947-L1004) 取待初始化分区，发送/等待 OffsetFetch，成功取 map，再调 `refreshCommittedOffsets`；超时不伪造成功位置。 | coordinator 返回这组 P0 的 committed=0，不返回外部数据库是否已经 `+10`。 |
| `ConsumerUtils.refreshCommittedOffsets` | [192–218](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerUtils.java#L192-L218) 只对非 null、仍 assigned 的分区，把 `offsetAndMetadata.offset()` 写入新 `FetchPosition`，然后 `subscriptions.seekUnvalidated(tp, position)`。 | B 的 P0 position 由组提交值初始化为 0。leader epoch 等校验可能在可取数前进行；初始化不是不经条件立即读取。 |
| `AbstractFetch.prepareFetchRequests` | [420–484](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/AbstractFetch.java#L420-L484) 选 fetchable 且无缓冲的数据分区，获取其 position；有可用节点、无相应在途请求等条件满足后，构造 `FetchRequest.PartitionData(..., position.offset, ...)`。 | position=0 变成真实 Fetch 请求的起读 offset=0，不是重发一条生产消息。 |
| `FetchCollector.fetchRecords` | [149–186](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchCollector.java#L149-L186) 要求仍 assigned、fetchable，且 `nextFetchOffset == position.offset`；解析后如下一偏移量更大，写 `subscriptions.position(tp, nextPosition)`。 | A 第一次交付 E01@0 时先把自己的 position 改到 1；B 第二次交付同一日志记录时也会把自己的 position 改到 1。两次都不等于 Kafka committed offset 已改到 1。 |

## 最小真实恢复链与状态更新

### A 第一次读取：Fetch0 → E01@0 → position1

1. `ClassicKafkaConsumer.poll` [647–679](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L647-L679) 调 `pollForFetches`；[706–738](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L706-L738) 优先收集已有响应，必要时发送请求、网络 poll、再收集。
2. `Fetcher.java` 105–119 把 prepareFetchRequests 结果发送；183–204 的 `client.send(fetchTarget, request)` 为请求登记成功/失败回调。145–146 的 collectFetch 直接委托给 FetchCollector。
3. `FetchCollector.java` 91–135 用 `fetchConfig.maxPollRecords` 限制本次交付数量；此例为 1。它不保证 broker 只返回一条，也不意味着客户端没有预取缓冲。
4. [CompletedFetch.java 257–290](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/CompletedFetch.java#L257-L290) 把原记录解析、加入返回列表，然后执行 `nextFetchOffset = lastRecord.offset() + 1`。E01@0 使该值成为 1。
5. FetchCollector 178–186 将这个值写入 `SubscriptionState` 中该分区的本地 position。`SubscriptionState.java` 1208–1211 最终执行 `this.position = position`。ClassicKafkaConsumer 随后才在 679 返回应用记录。
6. `ClassicKafkaConsumer.position` [875–885](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L875-L885) 读取的正是该有效本地 `FetchPosition.offset`。此时 A position=1，组 committed offset 仍为预先保存的 0。

### 外部数据库提交后，A 在 Kafka commit 前停止

- 数据库 `+10` 并提交属于外部系统的操作，是本期应用输入。上面的 Fetch/position 代码不访问数据库，不会知道其提交结果，也没有据此产生 OffsetCommit。
- `enable.auto.commit=false` 是必要范围条件；[ConsumerCoordinator.java 1202–1209](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1202-L1209) 只有 `autoCommitEnabled` 才走定时自动提交。不能泛化说任何配置下 poll 都绝不触发提交。
- 本例明确在应用显式 Kafka commit 之前 halt，没有“请求已发送、仅响应丢失”的提交歧义，因此提交值维持 0。若故障窗口改成提交请求已在途，仅客户端报错不足以认定 coordinator 没有保存新 offset，需另设计和观察该实验。

### B 接手恢复：committed0 → position0 → Fetch0 → SAME E01@0

1. 新建的 `TopicPartitionState` 在 `SubscriptionState.java` 1029–1035 初始为 `INITIALIZING` 且 position=null。B 获得 P0 后，在没有有效本地位置时经 ClassicKafkaConsumer1205–1217 进入 coordinator 初始化。
2. ConsumerCoordinator947–955 取 `initializingPartitions` 并请求其 committed offsets；965–994 在网络完成后返回 `future.value()`。
3. [ConsumerCoordinator1481–1511](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1481-L1511) 构建的是 **OffsetFetch** 请求，1505 明确写入 `rebalanceConfig.groupId`。所以条件是 B 与 A 使用同组，并接手同一分区。
4. [ConsumerCoordinator1570–1596](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1570-L1596) 对非负 `partition.committedOffset()` 组装 `OffsetAndMetadata`，完成返回 map。本例拿到 0；若没有 committed offset，则 map 值为 null，随后走 reset 策略，那不是本片“已有 committed0”的场景。
5. ConsumerUtils192–210 把 0 装进 `FetchPosition` 并调 seekUnvalidated。`SubscriptionState.java` 445–446 委托到分区状态；[1195–1205](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/SubscriptionState.java#L1195-L1205) 写 position，清理 reset/backoff，再按需要校验 leader epoch；1139–1150 展示可能进入 AWAIT_VALIDATION，不能省略有效位置条件。
6. `AbstractFetch.java` 553–559 从 subscriptions 取 position；447–484 将 `position.offset=0` 放进 FetchRequest.PartitionData。Fetcher183–197 真正发送请求，并将响应交给 `handleFetchSuccess`。
7. [AbstractFetch.java 181–225](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/AbstractFetch.java#L181-L225) 从原请求 session data 读取 `requestData.fetchOffset`，以这个 0 建立响应的 CompletedFetch 并加入 FetchBuffer；不是从数据库进度猜起点。
8. `CompletedFetch.java` 85–99 将 `nextFetchOffset=fetchOffset`；[228–239](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/CompletedFetch.java#L228-L239) 选择 `record.offset() >= nextFetchOffset` 且非控制批次的记录；本例 E01@0 正好符合。控制记录和不可见事务批次等另有过滤，所以不把“Fetch0 总会返回 offset0”当成无条件定律。
9. [CompletedFetch.java 334–338](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/CompletedFetch.java#L334-L338) 构造交付对象时使用 `partition.topic(), partition.partition(), record.offset()`。在日志仍有 E01@0 的前提下，B 交付的是原记录的相同 topic/partition/offset，不是新追加记录。之后 B 的本地 position 同样推进到 1。

## 显式提交 next1：只改变 Kafka 的恢复进度

- [ClassicKafkaConsumer.java 752–765](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L752-L765) 对显式 map 调 `coordinator.commitOffsetsSync`，超时未确认成功抛异常。此例的目标是 `P0 → OffsetAndMetadata(1)`。
- [ConsumerCoordinator.java 1284–1304](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1284-L1304) 把 map 中的 offset 直接写入 `.setCommittedOffset(...)`；1337–1349 用 groupId 组装 **OffsetCommit** 并发给 coordinator。
- [ConsumerCoordinator.java 1146–1181](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L1146-L1181) 独立等待该请求；成功才返回 true，非可重试错误抛出，超时返回 false。1361–1375 检查分区响应，1465–1469 在无授权错误时完成其 Future。
- 这条代码链负责 Kafka 组的 offset 进度，不在同一操作中提交、撤销或验证外部数据库 `+10`。把它与数据库事务一同画成一个原子提交是不准确的。
- `1` 的意思是下一次应从 1 读，不是“已经消费的最后一条 offset=1”。当前干净示例 E01@0 的下一位置为 1；一般 offset 可能不连续，真实程序宜采用本次记录集给出的 nextOffsets/leader epoch，而不是把所有位置关系简化为任意 offset+1。

## 可用于正文的状态表（源码推导，非运行结果）

| 时刻 | A 的本地 position | B 的本地 position | 同组 P0 committed | 外部数据库 |
|---|---:|---:|---:|---|
| 演示准备好 | 0 | 尚未接手 | 0 | 示例初值 |
| A poll 交付 E01@0 | 1 | 尚未接手 | 0 | 尚未 `+10` |
| 外部 DB 事务提交 | 1 | 尚未接手 | 0 | 已 `+10` |
| A 在 Kafka commit 前 halt | 随 A 进程丢失 | 尚未恢复 | 0 | 仍为已提交结果 |
| B 读取 committed 并初始化 | 不适用 | 0 | 0 | 已 `+10` |
| B Fetch0 后 poll 又交付 E01@0 | 不适用 | 1 | 0 | 是否再 `+10` 由业务处理决定；Kafka 不替它判断 |
| 业务安全完成后显式提交 next1 成功 | 不适用 | 1 | 1 | 保留业务已确认结果 |

## 改变关键条件会怎样

- 若 A 在 halt 前已经确认 Kafka committed=1，B 的这次初始化会从 1 起读；本例的 E01@0 重读原因不成立。
- 若 B 用不同 groupId，它获取的是另一个组的提交状态，不能沿用“同组 committed0”的解释。
- 若根本没有已提交 offset，或 0 已超出有效日志范围，reset 策略/错误处理会参与，不能把 `auto.offset.reset=earliest` 当成本例必经恢复路径。
- 若开启自动提交，A 的位置可能被周期性保存，故障窗口与重读结果会改变；不能在不观察提交值的情况下保证 B 必定 Fetch0。
- Kafka 源码只支持进度分离与重读链；外部数据库是否执行一次、去重登记与 `+10` 是否同事务，需要对应数据库来源与应用实现，不能拿 Kafka 源码代证。

## API 契约交叉核对与资料候选

本轮另保存并实读官方 `KafkaConsumer.java`，作为实现之外的交叉证据：

- [73–89](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/KafkaConsumer.java#L73-L89)：offset 标识分区中的记录；position 随 poll 自动前移，committed position 用于进程恢复；offset 可能不连续。
- [250–256](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/KafkaConsumer.java#L250-L256)：明确讨论“数据库插入后、offset commit 前进程失败；接手进程从 last committed offset 消费并重复插入”的边界。
- [286–290](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/KafkaConsumer.java#L286-L290)：提交值应是应用下一条要读取的位置，可从 ConsumerRecords.nextOffsets 取得，并保留 leader epoch 元数据。
- [328–341](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/KafkaConsumer.java#L328-L341)：把消费结果与 offset 存到同一个外部系统、同一事务，是另一种需要应用自行管理 offset 的设计。它不是本例 Kafka commitSync 自动具有的能力；本期无需展开该替代方案。
- [1016–1029](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/KafkaConsumer.java#L1016-L1029)：显式 commit API 保存的是 Kafka offset，后续启动/再均衡后的 fetch 使用该进度，并说明同步成功、错误、超时边界。

机构统一用 **Apache Kafka**；未找到明确个人文档署名，不从维护账号、tagger、Git 提交者或版权声明推断个人作者。项目官方仓库身份保存在 [kafka-repository.json](sources/kafka-repository.json)。片尾可选下列 2–4 项，原题保留实际源码文件名，不翻译或自拟摘要：

| 原题 | 官方 API 题名证据 | 主要用途 |
|---|---|---|
| KafkaConsumer.java | [Contents API](sources/KafkaConsumer.github-contents.json) 的 `name/path/html_url` | position/committed 与外部数据库故障窗口 |
| ConsumerCoordinator.java | [Contents API](sources/ConsumerCoordinator.github-contents.json) 的 `name/path/html_url` | 读取同组 committed offset、显式提交 |
| AbstractFetch.java | [Contents API](sources/AbstractFetch.github-contents.json) 的 `name/path/html_url` | 恢复 position 如何成为 Fetch 请求 offset |
| FetchCollector.java | [Contents API](sources/FetchCollector.github-contents.json) 的 `name/path/html_url` | 返回记录前更新本地 position |

[quotation-candidates.json](sources/quotation-candidates.json) 保存上述四项的题名依据、永久定位、逐字连续原始片段和支持关系；这是来源候选数据，不是最终 references.json。Javadoc 原始摘录保留注释标记，未拼接或改写为另一段原文。片尾按 title-author 只显示真实题名与机构，完整原文和链接留在文章/研究记录。
