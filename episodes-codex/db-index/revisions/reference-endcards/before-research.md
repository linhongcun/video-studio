# EP.15 公开来源核验

核验日期：2026-10-24（北京时间）。已通过联网工具实际打开以下官方页面并定位相关正文，不以搜索摘要代替正文。MySQL 手册首页显示文档生成日期 2026-10-22，章页未单独标更新日期。网页 URL 使用官方 `8.4` 文档分支名称；本稿讨论的行为适用于 MySQL 8.4.0 所属长期支持系列。未访问内网或私人资料。

## R1 按条件查找与索引定位

- 主张：没有可用于该条件的索引时，需要逐行判断；合适的索引帮助快速找到匹配记录，不必查看所有数据。
- 来源：MySQL 官方手册 §10.3.1，How MySQL Uses Indexes。
- 链接：https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html
- 访问日期：2026-10-24；页面日期：章页未标，手册生成于 2026-10-22。
- 短引："read through the entire table"。
- 正文位置：开头段及用途列表中 `WHERE` 条件查找。
- 用在：01、03、04、05、06、07、08、09、11、13，以及文章主线。
- 边界：这证明一种访问路径的差异；不证明本片示例实际用了多少时间、比较了多少次，也不证明所有查询都会走索引。

## R2 索引不保证每次更快

- 主张：小表，以及要处理多数或全部记录的查询，顺序读取可能更合算。
- 来源：与 R1 同页的末段。
- 链接：https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html
- 访问日期：2026-10-24；页面日期：同 R1。
- 短引："reading sequentially is faster"。
- 用在：12、13，文章边界。
- 边界：原文说的是特定访问模式，不能扩写成「小表必不用索引」或固定行数阈值。本片只说「也可能选择逐行扫描」。

## R3 表和行

- 主张：表由一组行组成，行包含列所定义的数据；片中一行表示一笔教学订单。
- 来源：MySQL 官方术语表，row 条目。
- 链接：https://dev.mysql.com/doc/refman/8.4/en/glossary.html#glos_row
- 访问日期：2026-10-24；页面日期：章页未标。
- 短引："A set of rows makes up a table."。
- 用在：02；订单号、商品、金额为本片虚构示例，不是官方样例。

## R4 索引如何找到记录；回表的具体边界

- 主张：InnoDB 的普通二级索引记录包含索引列与主键，随后可用主键找到聚簇索引中的记录。
- 来源：MySQL 官方手册 §17.6.2.1，Clustered and Secondary Indexes。
- 链接：https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html
- 访问日期：2026-10-24；页面日期：章页未标。
- 短引："uses this primary key value"。
- 用在：07、08、10 的「对应记录信息」；文章中的回表解释。
- 边界：片中引导线是逻辑关系，图示行号不是磁盘物理地址。片中例子抽象出查索引后取得非索引列的路径；不能说所有索引都要查两遍，因为覆盖索引可能直接满足查询。

## R5 索引有维护和空间成本

- 主张：增加索引会增加空间需求，也会增加插入、更新、删除时的维护工作。
- 来源：MySQL 官方手册 §10.3，Optimization and Indexes。
- 链接：https://dev.mysql.com/doc/refman/8.4/en/optimization-indexes.html
- 访问日期：2026-10-24；页面日期：章页未标。
- 短引："each index must be updated"。
- 用在：仅文章。
- 边界：不声称增加某个索引会使写入变慢固定百分比，也不将所有慢查询都归因于缺索引。

## R6 树结构及命名

- 主张：常规 InnoDB 键索引使用 B-tree 类结构，索引记录存于叶页；MySQL 术语表明确这里的 B-tree 是设计家族及变体的称呼，且不等于二叉树。
- 来源：MySQL 官方手册 §17.6.2.2，The Physical Structure of an InnoDB Index；官方术语表 B-tree 条目。
- 链接：https://dev.mysql.com/doc/refman/8.4/en/innodb-physical-structure.html
- 链接：https://dev.mysql.com/doc/refman/8.4/en/glossary.html#glos_b_tree
- 访问日期：2026-10-24；页面日期：章页未标。
- 短引："Index records are stored in the leaf pages"；"not the same as a binary tree"。
- 用在：仅文章；不在视频画 B+ 树或二叉树，也不用固定树高、页大小去推导性能。
- 仅参考：MySQL 官方 2019 年文章《InnoDB : Tablespace Space Management》使用 B+ tree 称呼：https://dev.mysql.com/blog-archive/innodb-tablespace-space-management/ 。2019 年材料早于本仓优先年份，仅用于术语沿革，不作本片主论证。

## R7 联合索引与最左前缀

- 主张：联合索引中的列有顺序；文档所述常规查找可利用最左一列、最左两列等前缀。
- 来源：MySQL 官方手册 §10.3.6，Multiple-Column Indexes。
- 链接：https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html
- 访问日期：2026-10-24；页面日期：章页未标。
- 短引："any leftmost prefix"。
- 用在：仅文章。
- 边界：不简化成「跳过最左列索引必失效」；访问策略仍要看执行计划，且可能有其他优化。

## 图示与事实的分界

8 行订单、订单号 7042、金额、行号、游标运动速度、范围缩小的动画全部是教学设计。它们不能作性能测量。示例无「订单号为主键／已建唯一索引」的预设，查找也没有 `LIMIT 1`，因此全表扫描发现一个匹配后继续检查其他行是自洽的。数据总量是否为 8 行不构成「应该走索引」的论证；镜 12 特别指出小表可能选择扫描。镜 11 只比较访问过程和相同结果，不宣称示例小表实测变快。

## 核验结论

公开文档直接支持本片核心解释：合适的索引可减少为寻找少量匹配记录而检查的无关数据，并帮助取得对应记录。公开文档也直接要求保留边界：索引不保证每次更快。没有公开材料支持「索引后必然瞬间返回」「固定快若干倍」「只需固定几次比较」，所以本片不使用这些说法。
