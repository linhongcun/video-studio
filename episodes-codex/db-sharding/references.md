# db-sharding · 片尾参考资料

采用 `presentation: title-author`：片尾仅列四项实际原题与机构，最多4项/页、默认5秒。来源输入完成不代表实际附录已编码、审片或发布。

核验日沿用 **2026-10-24（北京时间）**。本轮复用当时已实际打开官方正文的制作记录，没有新GET；未明确个人署名，不填写 `author`，不从Git提交者推定作者。

来源证据见[sources-db-sharding.json](../../docs/reference-endcards/batch-6/sources-db-sharding.json)；[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-sharding/research.md)及[归档副本](../../docs/reference-endcards/batch-6/evidence/db-sharding-prior-reading-278f69a7.md)都是本仓研究记录，不是官方固定正文。

- 基线：`278f69a71151cada63e7068b4cfc0d5222501ac7`
- 原research Git blob：`8a36d0f003c26aca09d91e7a6ae8fb033c85f098`
- 原research完整SHA-256：`42a769580bc5286097d10c44102391ba23eb36680ed7a69f62c233d653d8c718`（2372字节）

## R1 · Sharding pattern

- 机构：Microsoft · Azure Architecture Center
- 版本：官方文档 · 原记录未标页面版本或发布日期
- 正式链接：[Sharding pattern（官方文档）](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding)
- [既有实读记录（2026-10-24，R1）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-sharding/research.md#L7)（本仓研究记录，非官方固定正文）
- 原题证据：2026-10-24既有官方实读记录：research.md第7行R1的官方资料栏，题名部分（去除机构前缀）
- 记录位置：2026-10-24实读记录R1（第7行）；原记录未单列官方小节标题或段落号
- 原访问日期：2026-10-24（北京时间）
- 对应镜头：01, 02, 04, 05, 06, 07, 12, 13, 14

支持的主张：将数据拆成不同子集，分片键和路由决定位置；存储/写入压力可能适用，均衡与资源条件影响收益。

适用边界：只演示按用户固定教学映射，不把所有下单卡顿归于数据库，不给容量阈值或性能数字。

## R2 · Shard

- 机构：Vitess
- 版本：Vitess 23.0
- 正式链接：[Shard（官方文档）](https://vitess.io/docs/23.0/concepts/shard/)
- [既有实读记录（2026-10-24，R2）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-sharding/research.md#L8)（本仓研究记录，非官方固定正文）
- 原题证据：2026-10-24既有官方实读记录：research.md第8行R2的官方资料栏，题名部分（去除机构前缀）
- 记录位置：2026-10-24实读记录R2（第8行）；原记录未单列官方小节标题或段落号
- 原访问日期：2026-10-24（北京时间）
- 对应镜头：01, 02, 05, 12

支持的主张：分片是逻辑数据空间的子集；分片数据不重叠，分片与副本是不同概念。

适用边界：画面A/B/C是逻辑库与订单表，不是物理机或复制三份完整数据。

## R3 · Vindexes

- 机构：Vitess
- 版本：Vitess 23.0
- 正式链接：[Vindexes（官方文档）](https://vitess.io/docs/23.0/reference/features/vindexes/)
- [既有实读记录（2026-10-24，R3）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-sharding/research.md#L9)（本仓研究记录，非官方固定正文）
- 原题证据：2026-10-24既有官方实读记录：research.md第9行R3的官方资料栏，题名部分（去除机构前缀）
- 记录位置：2026-10-24实读记录R3（第9行）；原记录未单列官方小节标题或段落号
- 原访问日期：2026-10-24（北京时间）
- 对应镜头：03, 06, 07, 08, 09, 10, 11, 13

支持的主张：映射列值到keyspace ID以确定目标分片；Primary Vindex决定插入路由；同映射值可以有多条记录；缺少适用路由信息可能需要散播查询。

适用边界：本例按用户编号42/17/86映射A/B/C，只是教学规则，非具体哈希算法；规则不变时用户42同路由。

## R4 · Resharding

- 机构：Vitess
- 版本：Vitess 23.0
- 正式链接：[Resharding（官方文档）](https://vitess.io/docs/23.0/user-guides/configuration-advanced/resharding/)
- [既有实读记录（2026-10-24，R4）](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-sharding/research.md#L10)（本仓研究记录，非官方固定正文）
- 原题证据：2026-10-24既有官方实读记录：research.md第10行R4的官方资料栏，题名部分（去除机构前缀）
- 记录位置：2026-10-24实读记录R4（第10行）；原记录未单列官方小节标题或段落号
- 原访问日期：2026-10-24（北京时间）
- 对应镜头：10, 11, 13, 14

支持的主张：选择客户编号可共置相关订单，映射与访问模式须规划；重分片要复制、校验和切流，序列也需要安排。

适用边界：扩容不是多建表名就自动完成；下一期只预告跨库编号碰撞，不在本期展开方案。

## 保留范围

原article/research全文、frontmatter、全部章节锚点和原参考资料逐字节保留，仅追加新节。订单编号、用户编号和A/B/C映射为教学设计，不能当性能、容量或具体哈希算法证明；分片不是复制多份完整数据，同机多表不增加单机资源，缺少用户编号不必然查所有分片，扩容也不等于多建表名。

本轮没有新官方响应或可用的官方正文固定快照，因此不新增quotation、官方正文响应SHA或本轮成功HTTP状态；历史日期不改成整理日期。视频只显示原题与机构，无摘录、定位、年份、日期、链接或提示。
