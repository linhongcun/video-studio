# EP.16 公开资料核验

访问日期：2026-10-24（北京时间）。以下七篇均已通过联网工具实际打开官方页面，并定位正文；不是以搜索摘要或旧工程替代核验。版本 URL 为官方 MySQL `8.4` 分支；文章讨论 MySQL 8.4.0 所属长期支持系列的 InnoDB，不涵盖非事务存储引擎。

## R1 多条修改为何需要归在一笔事务中

- 来源：MySQL 官方手册 §17.7.2.2《autocommit, Commit, and Rollback》。
- URL：https://dev.mysql.com/doc/refman/8.4/en/innodb-autocommit-commit-rollback.html
- 正文位置：开头以及 Grouping DML Operations with Transactions。
- 核验：默认自动提交时，每个成功语句各自形成事务；显式开始事务后，可以把多条修改一起提交或回滚。
- 短引："each SQL statement forms a single transaction"。
- 用在：镜 01–09、11、14。示例最初两步各自确认，后来才将两步合在一笔事务。
- 边界：不能说数据库原本完全没有事务；本片的错误案例是没有把两条修改放在**同一笔**事务，不是否认单条语句自身的事务边界。

## R2 提交与回滚的直接语义

- 来源：MySQL 官方手册 §15.3.1《START TRANSACTION, COMMIT, and ROLLBACK Statements》。
- URL：https://dev.mysql.com/doc/refman/8.4/en/commit.html
- 正文位置：控制事务的四条语句说明，COMMIT、ROLLBACK 两项。
- 核验：提交确认当前事务的更改；回滚取消当前事务的更改。已经完成独立提交的第一条修改，不会因之后另一条修改失败而被直接撤销。
- 短引："canceling its changes"。
- 用在：镜 03–11、14–15。
- 边界：提交不等于两个 SQL 在同一时刻执行；回滚当前事务不能撤销此前另一笔已提交事务。本片镜 10 明确是另一个从相同初始余额开始的失败示例。

## R3 提交前进程崩溃与恢复

- 来源：MySQL 官方手册 §17.18.2《InnoDB Recovery》。
- URL：https://dev.mysql.com/doc/refman/8.4/en/innodb-recovery.html
- 正文位置：InnoDB Crash Recovery，自动检查日志、恢复，以及撤销未完成事务的说明。
- 核验：服务端意外退出后，正常重启时会执行崩溃恢复，回滚崩溃时未提交的事务。
- 短引："automatically rolls back uncommitted transactions"。
- 用在：镜 12、13。
- 边界：不说恢复瞬间完成，不把“提交前的数据库进程崩溃”扩写为任何硬件毁坏或提交结果不明。介质毁坏、日志缺失等可能需要备份与额外恢复处理，本片不展开。

## R4 语句错误不总等于整笔事务自动回滚

- 来源：MySQL 官方手册 §17.20.5《InnoDB Error Handling》。
- URL：https://dev.mysql.com/doc/refman/8.4/en/innodb-error-handling.html
- 正文位置：开头、死锁、锁等待超时与重复键等错误项目。
- 核验：部分错误只撤销出错语句，有些错误会撤销整笔事务。不能把任意失败都画成无条件自动整笔回滚。
- 短引："only the statement that failed"。
- 用在：镜 05、10、11，以及文章中的关键纠错。
- 本片做法：明确“应用发现转账没做完，选择回滚”，不依赖未说明的数据库错误类型。

## R5 当前事务为何可以显示自身未提交修改

- 来源：MySQL 官方手册 §17.7.2.3《Consistent Nonlocking Reads》。
- URL：https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html
- 正文位置：开头有关一致性读与当前事务自身更改的例外。
- 核验：一致性读基于快照，但当前事务能够读到其前面语句产生的自身修改；旧快照也可能让其他事务暂时继续看到旧版本。
- 用在：镜 07、08 的“本次修改·待确认”视图。
- 边界：下层不是另一个会话读取到的余额，不承诺所有会话提交后立即看到新值；“待确认”是逻辑示意，不说明修改是否已经写入某级存储。

## R6 脏读只留在文章

- 来源：MySQL 官方手册 §17.7.2.1《Transaction Isolation Levels》。
- URL：https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html
- 正文位置：READ UNCOMMITTED 段及默认隔离级别说明。
- 核验：隔离级别影响一个事务能读到其他事务何种状态的数据；READ UNCOMMITTED 会允许不一致的读取，文档称其为脏读。
- 用在：仅文章，吸收已取消的旧隔离级别独立期中的脏读主题。
- 边界：本片不枚举四种隔离级别，也不把事务原子性与并发可见性混成同一个保证。

## R7 原子性与 ACID 的定位

- 来源：MySQL 官方手册 §17.2《InnoDB and the ACID Model》。
- URL：https://dev.mysql.com/doc/refman/8.4/en/mysql-acid.html
- 正文位置：ACID 四项、Atomicity 与 Durability 小节。
- 核验：原子性与事务、提交、回滚相关；持久性还依赖软件设置和硬件配置。
- 用在：仅文章。
- 边界：不把 ACID 当成所有业务逻辑自动正确、跨系统支付自动成功或永久不丢数据的保证。

## 教学数据与已验证主张的分界

1000／500 的原始余额、200 的转账、800／700 的成功结果，以及 800／500 的半成状态，都是同一数据库内的虚构教学数据。它们不是银行真实接口、支付时效或故障概率；镜头时长也不是崩溃恢复耗时。没有真实机构、真实资金操作或跨行协议。

本期可支持的结论：在正确使用事务的前提下，一笔事务中的扣款、入账共同提交或撤销；遇到演示的语句失败时应用请求整笔回滚；在演示的提交前进程崩溃场景中，恢复会撤销未提交事务。片中不推断现实“扣款后未到账”的唯一原因。

## 片尾参考资料清单（2026-10-26整理，沿用2026-10-24访问）

原片主线与事实未改。本轮从以上七篇既有官方正文实读记录中选R1–R4进入片尾，采用 `presentation: title-author`，只显示实际原题与机构 `Oracle · MySQL`，每页最多4项、默认5秒；没有明确个人署名，不填写author。四项分别覆盖多语句事务、提交/回滚、提交前进程崩溃恢复、不同错误回滚范围。

既有完整研究基线：`76e9b36737063d109a866ff47c1dcf81ef46c638`，Git blob：`31cc8d38612f7bdca7a6a2c6445de3baf698f5a8`，SHA-256：`be16c916b6d25ff4341eb9ef30240fcc460d16888299888b60d43ebb808e9168`（5758字节）。[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-transaction/research.md)只是本仓研究记录，不是官方原文固定快照。本轮没有新GET，`verification.checkedAt`与清单核验日保留`2026-10-24`；未声称重新读取当前官方页面、核对新head或取得官方正文响应SHA。

| 片尾编号 | 实际原题 | 版本 | 旧记录位置 |
| --- | --- | --- | --- |
| R1 | [autocommit, Commit, and Rollback](https://dev.mysql.com/doc/refman/8.4/en/innodb-autocommit-commit-rollback.html) | MySQL 8.4 Reference Manual | R1，第5–13行 |
| R2 | [START TRANSACTION, COMMIT, and ROLLBACK Statements](https://dev.mysql.com/doc/refman/8.4/en/commit.html) | MySQL 8.4 Reference Manual | R2，第15–23行 |
| R3 | [InnoDB Recovery](https://dev.mysql.com/doc/refman/8.4/en/innodb-recovery.html) | MySQL 8.4 Reference Manual | R3，第25–33行 |
| R4 | [InnoDB Error Handling](https://dev.mysql.com/doc/refman/8.4/en/innodb-error-handling.html) | MySQL 8.4 Reference Manual | R4，第35–43行 |

证据与原主张逐字记录见[`sources-db-transaction.json`](../../docs/reference-endcards/batch-5/sources-db-transaction.json)；完整标题/机构/链接同时记入`references.json`、`references.md`和文章末尾新增的“片尾参考资料”节。原研究全文、R5自身修改可见性、R6隔离级别、R7 ACID及其适用边界保留，不以片尾精选替代全部参考。

本条只记录资料复用与清单生产；未执行冻结、媒体生成、声音复核、附录实际观看或发布，不预记用户认可。
