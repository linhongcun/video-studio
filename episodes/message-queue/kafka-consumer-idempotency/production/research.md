# MQ05：消费幂等的实现依据

基线`f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3`；首次本期调研2026-10-30。Kafka/Java4.4.0固定commit `1156b2752aaa28eafc0b4c4d387e63356793268d`；PostgreSQL18.0固定commit `3d6a828938a5fa0444275d3d2f67b64ec3199eb7`。机构分别为Apache Kafka和PostgreSQL Global Development Group；原始源码文件头/固定commit GitHub路径作为题名依据，不把提交者或维护账号推定为个人作者。

本轮真实GET、响应时间/状态/URL/全文SHA分别在`sources/kafka/source-evidence.json`和`sources/postgresql/retrievals.json`，原文件完整保留。只定向实读相关执行范围，不把完整下载说成逐行读完全部代码。PG细节与26段精确连续原文在`sources/postgresql/source-evidence.json`及`notes.md`。本文、源码事实、`model.json`有限模型和独立runtime实验是不同证据；本期模型已执行，独立代理完成的真实Broker/数据库实验范围及本代理实际阅读输出见文末，不把它们混成同一身份。

## 固定问题与输入

订单7042的事件E01要给账户17加10分。Kafka主题orders/P0只有E01@offset0，初始已提交的下一恢复位置为0；原日志在示例期间保留。classic组协议、`enable.auto.commit=false`、`max.poll.records=1`、group.id=`points`；这里只在该条完成后显式提交P0的下一位置1，不提前提交后续未完成记录。

PostgreSQL为Read Committed、普通非分区两表、无触发器/规则/RLS。`processed_events(logical_consumer text NOT NULL,event_id text NOT NULL,PRIMARY KEY(logical_consumer,event_id))`为立即不可延迟主键；键固定`('points','E01')`。`account_points(account_id bigint PRIMARY KEY,points int NOT NULL)`已有账户17/0分。两个处理任务是同逻辑业务的重叠应用尝试，不代表稳定classic组同一分区存在两个拥有者。逻辑身份不是进程ID，也不自动随进程重启或发布版本改变。

## Kafka：为什么业务做完还会重来

1. [`FetchCollector.java`178–185](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchCollector.java#L178-L185)在返回poll记录前，创建nextPosition并执行`subscriptions.position(tp,nextPosition)`。这段执行代码不查询积分数据库；position1不代表积分已提交。
2. [`ClassicKafkaConsumer.java`752–765](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java#L752-L765)将应用显式给出的offset map交给`coordinator.commitOffsetsSync`。无参数版本747–748取`subscriptions.allConsumed()`，而[`SubscriptionState.java`797–804](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/SubscriptionState.java#L797-L804)取客户端position，不是业务成功记录；本片选择处理该单条成功之后再提交明确的下一位置。
3. [`GroupCoordinatorRecordHelpers.java`470–491](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/GroupCoordinatorRecordHelpers.java#L470-L491)构造group/topic/partition键和offset值的内部恢复记录。这是Kafka状态，和业务数据库的事务不是同一个提交。
4. [`ConsumerCoordinator.java`947–955](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerCoordinator.java#L947-L955)查询committed后调用refreshCommittedOffsets；[`ConsumerUtils.java`192–210](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/internals/ConsumerUtils.java#L192-L210)以保存值创建FetchPosition并seek安装。本例DB10已提交而Kafka保存0时，重启仍可取回E01@0；不假设数据库事务会顺便提交Kafka。
5. R1的[`KafkaConsumer.java`250–256/286](https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/clients/src/main/java/org/apache/kafka/clients/consumer/KafkaConsumer.java#L250-L286)只是上述执行链的API交叉核对，准确说明DB插入与offset提交间失败和下一位置语义。正文只用它建立重来前提，不重讲完整Kafka恢复机制。

## PostgreSQL：普通查询为何不能认领资格

两个RC普通SELECT都未见已提交登记，只说明各自查询时的可见数据，不对不存在的行取得排他处理资格。若随后各自把积分单独提交，再补唯一登记，后来的冲突不能撤销以前独立提交的加分。此反例不声称“同一事务中先SELECT、再唯一INSERT并在失败时正确回滚”必然重复。

真正执行入口是`ExecInsert`，而非应用先查的结果：

- [`nodeModifyTable.c`1121–1139](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/executor/nodeModifyTable.c#L1121-L1139)先做非决定性冲突预检查；该预检查没有保持锁，仍可能与后来插入竞争。
- [`execIndexing.c`781–819](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/executor/execIndexing.c#L781-L819)使用DirtySnapshot扫描包括尚不可见的潜在冲突行，因此普通SELECT空与唯一检查遇到T1未决登记可以同时成立。
- R4的[`nbtinsert.c`187–211](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/access/nbtree/nbtinsert.c#L187-L211)说明检查到插入的候选叶页写锁保护并调用`_bt_check_unique`。相同键的并发插入者不能各自独立完成“未见→插入”的判断。等待事务时释放内部页锁再重新搜索，不把它画成整段业务事务占住一整页。
- 本期ON CONFLICT采用投机插入：`nodeModifyTable.c`1183–1227建立候选堆行、执行索引插入/检查、按specConflict确认或撤回，冲突则回vlock重试；`execIndexing.c`426–436/501–513选择UNIQUE_CHECK_PARTIAL并把潜在冲突带回executor。不能直接用普通INSERT的unique violation路径冒充DO NOTHING，也不能宣称物理索引永不暂存重复候选项。

## 未决冲突：等待结束之后再判断

R3的[`execIndexing.c`862–890](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/executor/execIndexing.c#L862-L890)从DirtySnapshot读取相关XID；投机状态先等token，否则`XactLockTableWait`等事务，之后`goto retry`重新扫描。发现尚未提交的同键不是立即永久重复，也不是立即允许第二次加分。

本例时序固定：T1已成功插入键并暂存+10、尚未提交，T2尝试同键等待。T1若COMMIT，T2重查发现有效键；若T1ROLLBACK，已回滚插入不阻挡T2，T2可成为本次成功登记者。`heapam_visibility.c`832–860为DirtySnapshot返回未决xmin/token、过滤已回滚插入。这里只固定RC；更高隔离级别可能出现序列化失败，不能泛化成全部隔离级别固定返回0/1。

R2的[`nodeModifyTable.c`1164–1179](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/executor/nodeModifyTable.c#L1164-L1179)在DO NOTHING冲突分支直接`return NULL`；成功INSERT才在1332–1333调用`ExecProcessReturning`。因此`RETURNING event_id`只在本次确实插入新登记行时返回E01，不会返回那条已有登记。应用必须按这个结果决定是否UPDATE；不能因为SQL没报错就无条件加分。

## 同一本地事务为什么一起生效

`heapam.c`2282–2291把新登记行xmin设为当前XID，3768–3778给UPDATE的积分新版本记相同事务XID。`xact.c`2359–2389记录事务提交并从运行数组移除；可见性代码按事务状态和读取快照决定新版本能否看见，不是每张表分别COMMIT。

回滚时`xact.c`1843–1851把XID树记为aborted；`heapam_visibility.c`1063–1087/1129–1137排除未提交新版本、保留被回滚更新的旧积分版本。教学图只表示登记和增量均未成为有效结果，不声称ROLLBACK立即擦除文件字节。投机插入候选的撤回与整个业务事务回滚也不混为同一步。

积分UPDATE必须恰好修改一个目标账户行。返回新登记后若账户不存在或业务异常，应用回滚整笔事务，不能吞错误然后只提交处理标记。反过来，登记先单独COMMIT后故障，会留下有效标记/积分0，重试跳过造成漏处理。这解释为什么唯一键与正确事务范围两者缺一不可。

## 来源与引用登记

R1–R4在`references.json`，title-author附录仅显示真实文件原题和机构。A1–A5在`article-sources.json`，提供额外执行原文。所有引句保持连续原文、缩进/注释，不添加省略或拼接；中文supports是编者解释，不冒充来源原句。Kafka源码原题由本轮固定commit GitHub contents name/path字段核对；PG由原文件头和官方仓库路径核对。实际读取日期2026-10-30（Asia/Shanghai），精确UTC GET时刻以各原始证据JSON为准。

## 模型与后续实验边界

`python3 build_model.py`本轮实际运行，90项有限状态/负向检查、33快照通过。模型抽象了有效键仲裁、RETURNING门槛、已提交结果和同事务结局，不模拟PostgreSQL投机物理元组、B树页、WAL或Kafka完整协调协议。它不作为真实数据库实现已执行的证明。

去重保存期、稳定事件身份和逻辑业务作用域是方案前提；删标记后重放、不同业务共用错键或同事件换ID都可能改变保证。

## 本轮真实运行的有限支持

独立执行者`/root/deploy_diagnosis`完成Kafka4.4.0单节点RF1与固定tag构建的PostgreSQL18.0运行，目录为`docs/archive/2026-10/mq05-07-implementation/runtime/runs/mq05-20261030T152318.187770Z/`。本代理实际打开并读了`assertion-summary.json`、`result.json`、`naive-crash/replay.stdout.txt`、`dedup-crash/replay.stdout.txt`、`db-concurrency.stdout.txt`与`physical-log.stdout.txt`，没有重跑这些进程。该次89项实际断言通过，运行后仅其自有进程/临时数据已清理。

- 无去重：worker实际halt(exit23)前，DB已提交10且Kafka committed仍0；新worker从同E01/P0@0读回，DB到20，再另一步提交Kafka1。
- 有去重：worker实际halt(exit24)前，DB10/登记1且Kafka仍0；重读时INSERT返回0行、UPDATE0行，结果仍10/登记1，再提交Kafka1。
- PostgreSQL两个连接实际竞争同键；`pg_stat_activity`记录B为Lock/transactionid等待，`pg_blocking_pids`包含A。A COMMIT后B返回0不更新；从相同初态改A ROLLBACK后B返回E01并+10。两组最后都是10/登记1；不是仅凭固定sleep推测存在等待。
- 目标账户缺失、UPDATE0行以及int溢出SQLState22003都会使应用回滚，无有效登记残留，之后有效尝试仍可取得键。物理Kafka日志dump仅E01@0，载荷为eventId/orderId/accountId/delta。

实验为隔离运行使用`mq05-orders`和带runId的Kafka组名；教学图简写为orders/points。SQL逻辑身份始终是`points`，账户17、增量10、orderId字符串`"7042"`与E01相同。有限模型的orderId类型已对齐实际载荷，画面业务编号不变。

这次运行不测试副本容错、吞吐、外部服务副作用、更高隔离级别，也不证明DB与Kafka原子提交或稳定同组双拥有者。先查询且先独立提交积分的竞态、标记先单独提交的漏处理反例目前作为源码支持的有限模型演示，不把89项断言说成所有分支都已在真实数据库实测；文章的Psycopg3函数是同语义应用示例，实际worker用Java/JDBC，不把它称作本轮运行的原始程序。原始Java、SQL、运行依赖及输出SHA在runtime目录可追溯。
