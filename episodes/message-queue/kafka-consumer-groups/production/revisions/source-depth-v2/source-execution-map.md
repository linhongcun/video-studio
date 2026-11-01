# MQ02：源码执行与画面因果映射

固定Apache Kafka4.4.0提交`1156b2752aaa28eafc0b4c4d387e63356793268d`。本轮从官方raw GitHub重新下载完整文件并直接阅读下列执行段，原文与SHA在`sources/download-manifest.json`。源码事实、画面模型与真实执行三层分开；真实Range与SubscriptionState运行已在`experiment/actual-execution.json`和`actual.stdout.txt`记录；新编译class实际加载位置已核对，不预记Broker或协议端到端实测。

| 镜 | 状态/问题 | 实际执行代码 | 条件与因果 |
|---|---|---|---|
| 04 | 同组订阅组成输入；谁算表 | Broker `GroupMetadataManager.classicGroupJoin` 6975–7010按request.groupId查组；完成join 7541–7563只给group leader完整members。客户端`AbstractCoordinator` 645–687读取isLeader分支。 | 明确classic新组，成功JoinGroup；组内leader是本轮承担计算的消费者，不等同Broker controller或分区leader，也不由Range排序第一决定。 |
| 05 | 分配者拿到成员订阅和分区元数据 | `ConsumerCoordinator.onLeaderElected`655–715反序列化每名成员订阅，`assignor.assign(metadata.fetch(), new GroupSubscription(subscriptions))`，随后序列化assignment。 | `skipAssignment=false`；所选策略Range；传入的是本组订阅集合，不是所有组的全局成员。 |
| 06 | 明确排序输入 | `AbstractPartitionAssignor.assign`74–92复制并按partition编号排序；`MemberInfo.compareTo`138–157无静态实例ID时按memberId；`RangeAssignor.TopicAssignmentState`239–250对members排序并算商和余数。 | `group.instance.id`不设、`client.rack`不设，避免静态成员/机架分支改变简化前提；N1/2/3是member-01/02/03的短名，不是client.id或启动顺序。 |
| 07 | q/r如何变成N1:P0、N2:P1、N3:[] | `RangeAssignor.assignPartitions`128–145先为所有成员创建空列表；`assignRanges`158–173顺序访问成员，按`maxAssignable`280–283取未分配分区；`onAssigned`285–289更新计数、递减余数、从unassigned移除。 | 2/3整数商0、余2。N1最多1个→P0，余1；N2最多1个→P1，余0；待分配为空时循环break，N3保持初始化的空列表。移走的是候选分区标识，不是Kafka日志记录。 |
| 08 | 算出的整表怎样变成每人的返回行 | `AbstractCoordinator.onLeaderElected`772–803把groupAssignment填入SyncGroupRequest；Broker`classicGroupSyncToClassicGroup`8294–8341只接受leader提交的整表，成功持久化后setAndPropagateAssignment；`setAndPropagateAssignment`7925–7935为每名member写自己的assignment；`propagateAssignment`7944–7964在各SyncGroupResponse内返回member.assignment。 | 本例成功同generation、经典组COMPLETING_REBALANCE→STABLE；不把本期成功路径扩大成全部重平衡/故障恢复流程。 |
| 09 | 返回列表在哪里安装 | `AbstractCoordinator`505–515在join future成功后调用onJoinComplete；`ConsumerCoordinator.onJoinComplete`379–465先反序列化assignment、校验订阅，然后`subscriptions.assignFromSubscribed(assignedPartitions)`；`SubscriptionState.assignFromSubscribed`315–330创建每分区状态map并`assignment.set`。 | 订阅未改变、结果与订阅相符。空列表也会被安装。这里改变消费者本地状态，不是逐条Broker推送名单。 |
| 09–10 | 归属列表为何限制正常客户端Fetch | `SubscriptionState.fetchablePartitions`486–497只枚举assignment；`isFetchableAndSubscribed`515–520与`TopicPartitionState.isFetchable`1251–1255要求已订阅、未暂停且有效位置；`AbstractFetch.prepareFetchRequests`420–488遍历unbuffered，取位置/目标节点，再`builder.add(partition, partitionData)`；`Fetcher.sendFetches`106–120发送这些请求。 | 本例有效position=0、未暂停、无待交付缓存、节点可用且无已有inflight Fetch。N1列表{P0}只形成P0请求；N3[]使请求集合为空。不能声称空闲成员完全不联网，也不能将正常客户端枚举规则当作Broker强制的安全授权。 |
| 11–12 | 新group为何仍能得到P0/P1 | 同上onLeaderElected只接收该group的members；Range本组输入[S1]算2/1=2、余0；本地安装{P0,P1}后分别Fetch。 | group.id不同，计算与恢复位置分别归组；示例从同一保留开头0读取。原记录未因另一组的Fetch或offset提交被删除。 |

源码永久链接均为`https://github.com/apache/kafka/blob/1156b2752aaa28eafc0b4c4d387e63356793268d/<sources/download-manifest中的upstreamPath>#L行号`。正文用具体名单、分区表、安装和请求动作兑现因果，不要求观众先读这些方法名。

## 关键条件对照

- 通知组输入成员数3、分区数2，归属为1/1/0；第二组只有1人时本组输入2/1，归属2。算法在两个group内分别运行，不做全局抢占。
- 另用真实Range执行验证将成员传入顺序打乱，结果仍按member.id排序；此为算法调用实验，不冒充Broker重平衡实测。
- 如果改为3分区/3成员，本策略得到1/1/1，第三个成员不再空闲。此分支用于内部对照与文章，不再挤进正文主线。
- 如果变更订阅、静态成员、机架或分配策略，需按实际策略重新判断，不沿用本例“前两位”的结果。
