# EP.17 权威资料核验

访问日期：2026-10-24（北京时间）。已实际打开以下官方正文，不以旧稿、搜索摘要或issue建议充当来源。技术背景为 MySQL 8.4 长期支持系列的 InnoDB；视频不口播产品版本，文章示例写8.4.0所属系列。

| ID | 官方资料 | 已核验主张 | 片中适用范围 |
|---|---|---|---|
| R1 | [§17.7.2.4 Locking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html) | 普通读后再修改不足以保护先前读值；FOR UPDATE读取最新可用数据，冲突读取等待；需要显式事务，提交或回滚释放锁 | 08—12，乙等待后才得到0，不先返回旧1 |
| R2 | [§17.7.1 InnoDB Locking](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html) | 记录锁锁定索引记录；唯一索引定位唯一已存在记录的范围不同于范围扫描 | 本例id7042为主键且记录已存在，不说所有查询只锁一行 |
| R3 | [§17.7.3 Locks Set](https://dev.mysql.com/doc/refman/8.4/en/innodb-locks-set.html) | UPDATE本身也加锁；范围与扫描路径有关，无合适索引可能扩大锁定范围 | 错例不是“UPDATE没有锁”，而是普通读取旧值后绝对值写回 |
| R4 | [§17.7.2.3 Consistent Nonlocking Reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html) | 常见隔离级别普通一致性读使用快照；不等同FOR UPDATE | 不说所有SELECT都阻塞；后续SQL不能继续用旧读取结果 |
| R5 | [§17.7.2.2 autocommit, Commit, and Rollback](https://dev.mysql.com/doc/refman/8.4/en/innodb-autocommit-commit-rollback.html) | 显式多语句事务，提交与回滚结束并释放其锁 | 甲提交后乙继续；乙缺货后也结束事务，不永远持锁 |
| R6 | [§17.20.5 InnoDB Error Handling](https://dev.mysql.com/doc/refman/8.4/en/innodb-error-handling.html) | 不同错误可能只撤销语句或整笔；超时与死锁不能混为一谈 | 仅文章，不给默认超时秒数，不声称一定等待成功 |
| R7 | [§17.7.5 Deadlocks](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks.html) | 多事务互等可能死锁，应处理失败重试、缩短事务和统一访问次序 | 仅文章，不在主线加入多锁支线 |

库存1、商品7042、请求甲乙是教学设计，无吞吐、等待时长或性能实测。错误流程允许程序忽略相同值写回未实际改变行数，并在未重新核验库存时错误放行；SQL没有报错不等于业务购买成功。这是针对程序流程的推演，不是实际银行或商城故障结论，也不声称已运行真实MySQL并发压测。加锁读取后的库存判断是程序责任，不能把锁当成库存业务约束。没有先来先得/FIFO或无饥饿承诺。


## 片尾书目整理（2026-10-26，复用既有实读记录）

本轮只整理片尾title-author书目，选取Locking Reads, InnoDB Locking两项核心资料；不新增官方正文读取结论，也不将原R3简写Locks Set用作完整题名。上方2026-10-24访问日期、全部原研究内容和已有资料编号原字节保留。

原实读记录固定于[本批基线research.md](https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-lock/research.md)；Git blob为`aad662403e90f4315e8df99c38e355512a2c6b17`，完整SHA-256为`ea0fae457b9084490c2b0370ac90b0448698d98ec7f857a836cb8a11402db590`。该链接是既有实读记录，不是MySQL官网正文的固定副本。两项原记录行、完整原研究上下文和适用边界存入`docs/reference-endcards/batch-5/sources-db-lock.json`，供独立复核。
