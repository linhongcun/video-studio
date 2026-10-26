# db-replication · 片尾参考资料

清单整理于2026-10-26（北京时间）；原官方正文实际阅读日期保留为2026-10-24。

本轮不重新请求未改变的技术事实。原研究完整SHA、基线Git/blob及逐论点原记录见[本轮证据](../../docs/reference-endcards/batch-6/sources-db-replication.json)；记录链接是既有阅读笔记，不是官网固定正文或新GET。无明确个人署名，采用发布机构Oracle / MySQL，不推定维护账号为作者。

## R1 · Replication Implementation

- 发布机构：Oracle / MySQL
- 文档版本／实读日期：MySQL 8.4 Reference Manual · 实读2026-10-24
- 正式文档：[Replication Implementation](https://dev.mysql.com/doc/refman/8.4/en/replication-implementation.html)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-replication/research.md#L7)
- 原题记录位置：既有实读记录 · 第7行

对应主张：

- 源记录更改，副本请求日志并在各自本地重放；图示箭头表示更改流向，不等同源无条件主动推送。

## R2 · Replication Threads

- 发布机构：Oracle / MySQL
- 文档版本／实读日期：MySQL 8.4 Reference Manual · 实读2026-10-24
- 正式文档：[Replication Threads](https://dev.mysql.com/doc/refman/8.4/en/replication-threads.html)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-replication/research.md#L8)
- 原题记录位置：既有实读记录 · 第8行

对应主张：

- 副本接收日志与应用更改是不同阶段；收到更改不等于相关记录已更新、查询已能读到新值。

## R3 · Using Replication for Scale-Out

- 发布机构：Oracle / MySQL
- 文档版本／实读日期：MySQL 8.4 Reference Manual · 实读2026-10-24
- 正式文档：[Using Replication for Scale-Out](https://dev.mysql.com/doc/refman/8.4/en/replication-solutions-scaleout.html)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-replication/research.md#L9)
- 原题记录位置：既有实读记录 · 第9行

对应主张：

- 在适合的读多写少场景，可将写入交源、读取按需求选源或副本；这不是所有数据库部署的固定架构。
- 本片刚修改后的核对查询定向同一个已提交的主库，是教学路由选择，不是忽略旧事务快照、缓存或故障切换的一致性保证。

## R4 · Semisynchronous Replication

- 发布机构：Oracle / MySQL
- 文档版本／实读日期：MySQL 8.4 Reference Manual · 实读2026-10-24
- 正式文档：[Semisynchronous Replication](https://dev.mysql.com/doc/refman/8.4/en/replication-semisync.html)
- 原阅读记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-replication/research.md#L10)
- 原题记录位置：既有实读记录 · 第10行

对应主张：

- 默认异步复制下，源提交成功不能证明某副本已经取得并应用该事务。
- 半同步确认也不等于相关事件已在副本执行完成；此半同步边界在配套文章展开。
