# EP.17 片尾参考资料清单

画面仅原始题名与机构署名；不显示版本、日期、定位或引文。机构统一为Oracle / MySQL，未猜测个人作者。

本轮整理日期：2026-10-26；沿用的官网实读日期：2026-10-24。未进行新GET，不能将下列Git记录称为官网固定原文。


以下选列支撑视频核心流程的两项官方资料，沿用本期2026-10-24的实读记录。本节于2026-10-26整理，未将本轮整理记作新的官网访问。原有资料及脚注保留。

**[R1] Locking Reads**

Oracle / MySQL · MySQL 8.4 Reference Manual：[官方资料](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)；[既有实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-lock/research.md#L7)。

**[R2] InnoDB Locking**

Oracle / MySQL · MySQL 8.4 Reference Manual：[官方资料](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html)；[既有实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-lock/research.md#L8)。

本片采用已存在主键记录的教学示例。锁用于协调冲突访问，库存检查和更新结果判断由应用负责；不将获取锁等同于购买成功，也不保证等待必定成功或先来先得。
