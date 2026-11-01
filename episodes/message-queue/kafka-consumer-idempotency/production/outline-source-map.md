# MQ05：一条事件，两个提交边界，一个数据库仲裁机制

基线`f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3`；分支`codex/mq05-07-implementation-20261030`。根已同步最新主干并确认clean，本代理实读现行AGENTS、RULES、pipeline、research-template、article-style及S023/L060。只写新D，不改既有媒体/旧生产输入/共享工具，不提交。EP45 / MQ05 / issue313。

## 观众最后能解释什么

同一E01可在DB积分成功而Kafka恢复值尚旧时重来。“先查没处理过”没有认领处理资格。真正的并发仲裁由唯一索引检查/插入与未决事务等待后重检完成；应用只在本次INSERT返回新登记行时加分。登记与加分同一本地事务决定共同提交/回滚，Kafka进度之后单独保存。

## 固定对象

- 事件E01/order7042/account17/delta10，Kafka P0@0，初始committed0，手动提交且单条poll，日志保留。
- PostgreSQL18.0 Read Committed；`processed_events(logical_consumer,event_id)`立即非延迟、NOT NULL主键，键`('points','E01')`。
- `account_points`账户17初始0。T1/T2是DB处理尝试，不是稳定同组同时拥有P0的两个消费者。
- 未提交暂存+10与公共已提交积分分栏；事务内部短锁与跨事务结局等待分开，RETURNING ∅不等于返回旧行。

## 四章与主线

1. `problem` 重来与重复不是同一个问题（01–03）：DB先成功、Kafka进度未成功→同E01重来→无判断则20。
2. `claim` 查询为什么不能认领（04–06）：共同0/空重置，两次查询都空；各自先提交积分再补标记已太迟；改用逻辑身份+事件的共同唯一键。
3. `arbitrate` 等待后怎样决定谁能加分（07–10）：T1本次INSERT返回E01才暂存加分；T2同键等待；T1提交后T2重检返回空并跳过；DB成功后再Kafka进度。
4. `atomic` 提交与回滚为什么要绑在一起（11–14）：共同未决态重置，只改T1回滚，T2随后完成；再从0/空演标记先提交的漏处理反例；回收正确同事务机制与本地范围。

## 执行代码与正文动作

| 标识 | 最小真实路径 | 正文兑现 |
|---|---|---|
| K1 | FetchCollector178–185更新SubscriptionState.position | poll得到E01后客户端下一位置1，不等待积分成功 |
| K2 | ClassicKafkaConsumer752–765显式Map提交；GroupCoordinatorRecordHelpers470–491构造group/topic/partition/offset恢复记录 | DB已提交10与Kafka仍保存0是两件事 |
| K3 | ConsumerCoordinator947–955→ConsumerUtils192–210 | 重启查询committed0并安装读取位置0 |
| K4 | KafkaConsumer250–256/286 API交叉核对 | 手动提交仍存在DB先成功/offset未提交窗口，提交下一位置 |
| P1 | nodeModifyTable1121–1139无锁预检查→execIndexing781–890 DirtySnapshot和等待/重扫 | 普通查询没见到不等于没有未决冲突；T2必须等后重查 |
| P2 | nbtinsert187–203/574–579短内部锁保护检查到插入；ON CONFLICT partial潜在冲突返回executor重试 | 两个并发登记不会都凭同一次空观察完成认领，不能把内部锁画成整段等待时一直持有 |
| P3 | nodeModifyTable1164–1179冲突DO NOTHING直接returnNULL；1183–1227投机完成/撤回和重试；1332–1333成功才RETURNING | 只有本次成功登记返回E01才加分，冲突返回空时跳过 |
| P4 | heapam插入/UPDATE新版本同XID；xact提交/回滚状态；heapam_visibility按XID与快照可见性 | 同一本地事务两项一起生效或不生效，回滚不等于物理立即擦除 |

正文不巡览方法名。索引数据结构、未决状态与应用门槛的动作承担原理；精确原句、完整链、投机候选及隔离级别旁支在research和article保留。主片并发结果先是官方实现约束的有限模型，实际实验输出待独立runtime产生后限定引用，不抢先标实测。

## 先提交编辑审稿

来源实读/raw证据、脚本及其旁白SHA、可运行有限模型、独立文章与来源引用先交根和mq_qa。文章图位先按镜头目标定义，声音测得后才填写准确整数frame/seconds并启用Figure，不使用虚构时序。未通过独立编辑不得TTS；本代理不freeze、不正式编码、不接站点或git。
