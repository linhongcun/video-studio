# db-index · 片尾参考资料

清单整理日期：2026-10-26（北京时间）；实际官方正文实读日期保留为2026-10-24。

本轮复用原调研，不重新GET未改变的事实。完整原记录SHA、Git blob、原题与逐论点原记录见[本轮证据](../../docs/reference-endcards/batch-5/sources-db-index.json)。Git固定链接标为“既有实读记录”，不作为官网正文镜像。发布方使用Oracle / MySQL；未记录明确个人署名，省略author，不推定Git账号为作者。

## R1 · How MySQL Uses Indexes

- 发布机构：Oracle / MySQL
- 文档版本／实读日期：MySQL 8.4 Reference Manual · 实读2026-10-24
- 正式文档：<https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html>
- 既有实读记录：<https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-index/research.md#L5-L24>
- 原题记录位置：既有实读记录 · 第8行

对应本片论点：

- 没有可用于条件的合适索引时，需要逐行检查；合适索引能定位匹配记录，减少无关读取。
- 小表或需要处理多数、全部记录的查询，顺序读取可能更合适；有索引不保证每次更快。

## R2 · Clustered and Secondary Indexes

- 发布机构：Oracle / MySQL
- 文档版本／实读日期：MySQL 8.4 Reference Manual · 实读2026-10-24
- 正式文档：<https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html>
- 既有实读记录：<https://github.com/linhongcun/video-studio/blob/76e9b36737063d109a866ff47c1dcf81ef46c638/episodes-codex/db-index/research.md#L35-L43>
- 原题记录位置：既有实读记录 · 第38行

对应本片论点：

- InnoDB普通二级索引记录包含索引列与主键，可再用主键找到聚簇索引中的记录。
- 片中的索引到原记录是逻辑关系，不把图示行号当磁盘地址，也不声称覆盖索引必须再查一次原记录。
