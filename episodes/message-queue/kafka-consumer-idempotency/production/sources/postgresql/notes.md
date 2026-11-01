# PostgreSQL 18.0：MQ05 消费幂等的执行依据

固定仓库 `postgres/postgres`，commit `3d6a828938a5fa0444275d3d2f67b64ec3199eb7`。本轮真实 HTTPS GET 与时间、状态码、源 URL、字节 SHA、文件原题证据保存在 `retrievals.json`。`configure.ac:20` 自报18.0。只定向读核心执行范围；文件已完整保存不代表逐行读完全部无关分支。本任务没有启动或实测数据库，下面并发结果是源码推导；root/deploy_diagnosis 的独立真实实验需另查实际回执。

本轮以云运行环境技能核对网络策略，保留注入代理与TLS校验；未读取或输出凭证。没有改旧片、共享目录或提交。

## 固定示例及边界

```sql
CREATE TABLE processed_events (
  logical_consumer text NOT NULL,
  event_id text NOT NULL,
  PRIMARY KEY (logical_consumer, event_id)
);
CREATE TABLE account_points (
  account_id bigint PRIMARY KEY,
  points int NOT NULL
);
INSERT INTO account_points VALUES (17, 0);

BEGIN ISOLATION LEVEL READ COMMITTED;
INSERT INTO processed_events VALUES ('points', 'E01')
ON CONFLICT (logical_consumer, event_id) DO NOTHING
RETURNING event_id;
-- 应用必须检查本次RETURNING结果；仅返回一行时执行下面UPDATE。
UPDATE account_points SET points = points + 10 WHERE account_id = 17;
COMMIT;
```

注释描述应用条件分支，不能把这段顺序SQL原样无条件执行后声称具备幂等。E01为同一业务事件（orderId7042、accountId17、delta10）；`points`是稳定逻辑消费身份。两个字段都NOT NULL，主键默认为立即、不可延迟的唯一索引。没有触发器、规则、RLS或分区；积分账户已存在，应用检查UPDATE确实更新一行，异常则回滚整个事务，不能吞掉错误后提交标记。本例登记表不删键，事件身份不变；保留时长和身份规则由应用定义。

本地数据库事务只覆盖这两个表；Kafka offset在数据库COMMIT之后另一步提交。源码不证明Kafka与外部数据库天然原子，也不覆盖库外接口或转账等别的副作用。

## 最小实际执行映射

1. `nodeModifyTable.c:1093-1096`检查普通行约束。`1121-1139`先做无锁、非决定性的冲突预检查；预检查本身不能堵住先查后写竞态。
2. `execIndexing.c:599-610`限制仲裁索引必须立即检查，deferrable约束报错；`645-652`用`CEOUC_WAIT`进入实际冲突扫描。`781-784`使用DirtySnapshot，把其他未提交但可能冲突的行也纳入判断，区别于普通SELECT的MVCC可见行。
3. `execIndexing.c:862-890`从DirtySnapshot取正在影响行的XID；投机中先等token，否则等事务XID，结束后`goto retry`重扫。`heapam_visibility.c:832-860`把其他事务未决xmin/token返回给扫描器，已回滚的插入则返回false。
4. 若预检查找到确认冲突，`nodeModifyTable.c:1164-1179`的DO NOTHING分支直接`return NULL`，没有产生本次插入行。只有成功INSERT才走到`1332-1333`的`ExecProcessReturning`。应用把RETURNING行当成是否允许加分的门槛，不能把“SQL没报错”当成新登记成功。
5. 若预检查尚无冲突，`nodeModifyTable.c:1183-1207`获得投机令牌、写候选堆行、插索引并检查、按`!specConflict`确认或撤回候选行。`execIndexing.c:426-436`对仲裁索引使用`UNIQUE_CHECK_PARTIAL`；`nbtinsert.c:574-579`遇潜在冲突立即返回非唯一，`execIndexing.c:501-513`把`specConflict`置true。`nodeModifyTable.c:1218-1227`随后回到预检查，再等待和重检。
6. `nbtinsert.c:187-199`解释为什么两个检查不会同时漏掉对方：相同键的插入者必须争同一候选叶页写锁，从检查到索引插入连续持锁。这里是索引页内部锁，不是应用提前为不存在key建了行锁；等待事务时会释放内部锁再搜。`UNIQUE_CHECK_PARTIAL`允许暂时潜在重复索引项，不能说物理B树从不出现重复字节。
7. 对普通INSERT，`nodeModifyTable.c:1233-1243`走正常插入，立即唯一索引使用`UNIQUE_CHECK_YES`；`nbtinsert.c:213-232`可等待XID再从`search`重找，确认重复最终`666-673`报unique violation。这与本期DO NOTHING的投机撤回/重试/返回零行分开。

`heapam_handler.c:263-297`将tableAM投机操作接到`heap_insert`及`heap_finish_speculative`/`heap_abort_speculative`，后者是撤回一个候选行，不是回滚整个业务事务。成功投机完成也不等于COMMIT：`nodeModifyTable.c:1209-1214`明确等待者醒后仍可能等插入事务的XID。

## 同一E01的并发推导

- T1在上述RC事务内先插入`('points','E01')`并把17号账户从0改到10，尚未COMMIT。T1自己的后续命令能读到自身写入；其他普通查询不读到这两个未提交新版本。
- T2尝试同key。即使普通SELECT先查不到，唯一冲突检查仍看见T1未决行，等待其完成并重新判断；不因“目前不可见”立即认定可插入。
- 唯一改变条件：若T1 COMMIT，T2重查确认已有键，DO NOTHING返回零行；应用跳过加分。持久业务结果为1条登记、10分。
- 复位至相同未决状态，仅将T1结局改成ROLLBACK：T1新登记与新积分版本不生效。T2醒后重查，已回滚行不再阻挡；T2插入成功返回E01，应用在自己的事务内+10并COMMIT。最终仍为1条有效登记、10分。
- 该推导固定Read Committed。`xact.h:44-51`说明它使用语句快照；`nodeModifyTable.c:404-406`在RC跳过更高隔离级别的冲突行可见性检查。因此DO NOTHING可以基于本语句MVCC快照尚不可见的并发提交行跳过。不要扩写成所有隔离级别一定同样返回，较高隔离可能序列化失败。

## 同事务为什么一起生效或回滚

`heapam.c:2080,2282-2290`给新登记行记当前XID；`3245,3768-3778`给积分UPDATE的新版本也记当前XID。`xact.c:2359-2389`先记录该XID已提交，再从运行事务数组移除。`heapam_visibility.c:1063-1087`按xmin的提交状态和读取快照判定新版本可见；不是逐张表各自COMMIT。

回滚在`xact.c:1843-1851`把XID树记作aborted；新登记与新积分版本被相同事务状态排除，旧积分版本的xmax若回滚，`heapam_visibility.c:1129-1137`保留旧版本可见。`heapam.c:4049-4059`也把旧/新版本后续pruning与事务是否回滚分开。因而动画可画“整笔事务的新结果不生效”，不能画“ROLLBACK立即把页里所有字节擦掉”。本次未遍历VACUUM完整清理算法，不宣称具体回收时刻。

这里的一起可见指相同读取快照对同一事务结果作一致判断；RC下两个独立查询可能跨过一次COMMIT拿到不同快照，不能据此说事务只提交了一张表。COMMIT后的持久性还受实际数据库可靠性/配置边界影响，本片不展开异步提交及硬件故障。

## 两个短反例

- 只有“SELECT没登记→加分→INSERT”而无唯一约束：T1、T2都可能先查到不存在，再各自加分。即便有唯一约束，也必须在同事务且正确处理冲突/回滚；不能先把积分单独提交，再指望后续重复键错误撤销前次提交。
- 先单独COMMIT登记，再做积分：登记已提交后故障，重试看到键就跳过，积分漏加。这是把一个本地事务拆成两个造成的中间状态，不是去重键仲裁失败。

## 可直接核对的永久引用

所有精确连续源码原文、原始文件SHA与永久行号链接在`source-evidence.json`，推荐`PG-Q02`（锁住检查到插入）、`PG-Q04`（未决等待再重查）或`PG-Q03`（DO NOTHING不返回行）。JSON的`text`保留源码注释/缩进，未拼接、不加省略号；中文`claim`是编者说明。若文章要去除注释外观，须明确排版处理，不把概括、翻译或拼句冒充连续原句。片尾如引用源码，原题是文件头实际的`nbtinsert.c`、`nodeModifyTable.c`等；机构为PostgreSQL Global Development Group，未推定个人作者。
