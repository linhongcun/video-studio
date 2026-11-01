# db-transaction · 片尾参考资料

采用 `presentation: title-author`：视频仅显示原题与机构，最多4项/页、默认5秒。以下是来源输入，不代表附录已编码、审片或上线。

原访问日期：**2026-10-24（北京时间）**。本轮复用既有官方正文实读记录，没有新GET，不改写为2026-10-26访问。无明确个人署名，省略 `author`，统一使用机构 `Oracle · MySQL`。

完整来源证据见[sources-db-transaction.json](../../docs/reference-endcards/batch-5/sources-db-transaction.json)；[既有实读记录](https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-transaction/research.md)是本仓制作记录，**不是官方固定正文**。

- 基线：`76e9b36737063d109a866ff47c1dcf81ef46c638`
- research Git blob：`31cc8d38612f7bdca7a6a2c6445de3baf698f5a8`
- 原research完整SHA-256：`be16c916b6d25ff4341eb9ef30240fcc460d16888299888b60d43ebb808e9168`（5758字节）

## R1 · autocommit, Commit, and Rollback

- 机构：Oracle · MySQL
- 版本：MySQL 8.4 Reference Manual
- 正式链接：<https://dev.mysql.com/doc/refman/8.4/en/innodb-autocommit-commit-rollback.html>
- 既有实读记录：<https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-transaction/research.md#L5-L13>（本仓研究记录，非官方固定正文）
- 原题证据：2026-10-24既有官方实读记录：research.md第7行，§17.7.2.2原题转录
- 正文位置：§17.7.2.2；开头以及 Grouping DML Operations with Transactions。
- 原访问日期：2026-10-24（北京时间）
- 对应镜头：01, 02, 03, 04, 05, 06, 07, 08, 09, 11, 14

支持的主张：默认自动提交时，每个成功语句各自形成事务；显式开始事务后，可以把多条修改一起提交或回滚。

适用边界：不能说数据库原本完全没有事务；本片的错误案例是没有把两条修改放在**同一笔**事务，不是否认单条语句自身的事务边界。

## R2 · START TRANSACTION, COMMIT, and ROLLBACK Statements

- 机构：Oracle · MySQL
- 版本：MySQL 8.4 Reference Manual
- 正式链接：<https://dev.mysql.com/doc/refman/8.4/en/commit.html>
- 既有实读记录：<https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-transaction/research.md#L15-L23>（本仓研究记录，非官方固定正文）
- 原题证据：2026-10-24既有官方实读记录：research.md第17行，§15.3.1原题转录
- 正文位置：§15.3.1；控制事务的四条语句说明，COMMIT、ROLLBACK 两项。
- 原访问日期：2026-10-24（北京时间）
- 对应镜头：03, 04, 05, 06, 07, 08, 09, 10, 11, 14, 15

支持的主张：提交确认当前事务的更改；回滚取消当前事务的更改。已经完成独立提交的第一条修改，不会因之后另一条修改失败而被直接撤销。

适用边界：提交不等于两个 SQL 在同一时刻执行；回滚当前事务不能撤销此前另一笔已提交事务。本片镜 10 明确是另一个从相同初始余额开始的失败示例。

## R3 · InnoDB Recovery

- 机构：Oracle · MySQL
- 版本：MySQL 8.4 Reference Manual
- 正式链接：<https://dev.mysql.com/doc/refman/8.4/en/innodb-recovery.html>
- 既有实读记录：<https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-transaction/research.md#L25-L33>（本仓研究记录，非官方固定正文）
- 原题证据：2026-10-24既有官方实读记录：research.md第27行，§17.18.2原题转录
- 正文位置：§17.18.2；InnoDB Crash Recovery，自动检查日志、恢复，以及撤销未完成事务的说明。
- 原访问日期：2026-10-24（北京时间）
- 对应镜头：12, 13

支持的主张：服务端意外退出后，正常重启时会执行崩溃恢复，回滚崩溃时未提交的事务。

适用边界：不说恢复瞬间完成，不把“提交前的数据库进程崩溃”扩写为任何硬件毁坏或提交结果不明。介质毁坏、日志缺失等可能需要备份与额外恢复处理，本片不展开。

## R4 · InnoDB Error Handling

- 机构：Oracle · MySQL
- 版本：MySQL 8.4 Reference Manual
- 正式链接：<https://dev.mysql.com/doc/refman/8.4/en/innodb-error-handling.html>
- 既有实读记录：<https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-transaction/research.md#L35-L43>（本仓研究记录，非官方固定正文）
- 原题证据：2026-10-24既有官方实读记录：research.md第37行，§17.20.5原题转录
- 正文位置：§17.20.5；开头、死锁、锁等待超时与重复键等错误项目。
- 原访问日期：2026-10-24（北京时间）
- 对应镜头：05, 10, 11

支持的主张：部分错误只撤销出错语句，有些错误会撤销整笔事务。不能把任意失败都画成无条件自动整笔回滚。

适用边界：明确“应用发现转账没做完，选择回滚”，不依赖未说明的数据库错误类型。

## 保留范围

原文章全部正文、frontmatter、章节锚点、参考资料与7条脚注逐字节保留；原研究R5–R7及教学示例边界保留。本轮新增清单不代表只使用这四篇，也不把应用主动回滚扩大为任意语句错误自动整笔回滚，不把提交前进程崩溃扩大为所有硬件/介质故障。

现有短引只在固定基线中的旧研究记录中保留，本轮不新增 `quotation`，不在视频显示摘录、定位、版本、日期、链接或暂停说明。没有新官方响应，不设置官方正文SHA或声称取得官方固定版本。
