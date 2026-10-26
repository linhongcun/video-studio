# EP.19 权威资料核验

访问日期2026-10-24（北京时间）。以下官方正文已实际打开并核验，不以issue、旧分镜或搜索摘要作为引用。

|ID|官方资料|已核验主张|本期用法与边界|
|---|---|---|---|
|R1|[Microsoft Azure Architecture Center: Sharding pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding)|将数据拆成不同子集，分片键和路由决定位置；存储/写入压力可能适用，均衡与资源条件影响收益|只演示按用户固定教学映射，不把所有下单卡顿归于数据库，不给容量阈值或性能数字|
|R2|[Vitess: Shard](https://vitess.io/docs/23.0/concepts/shard/)|分片是逻辑数据空间的子集；分片数据不重叠，分片与副本是不同概念|画面A/B/C是逻辑库与订单表，不是物理机或复制三份完整数据|
|R3|[Vitess: Vindexes](https://vitess.io/docs/23.0/reference/features/vindexes/)|映射列值到keyspace ID以确定目标分片；Primary Vindex决定插入路由；同映射值可以有多条记录；缺少适用路由信息可能需要散播查询|本例按用户编号42/17/86映射A/B/C，只是教学规则，非具体哈希算法；规则不变时用户42同路由|
|R4|[Vitess: Resharding](https://vitess.io/docs/23.0/user-guides/configuration-advanced/resharding/)|选择客户编号可共置相关订单，映射与访问模式须规划；重分片要复制、校验和切流，序列也需要安排|扩容不是多建表名就自动完成；下一期只预告跨库编号碰撞，不在本期展开方案|

补充边界：同机分表不能凭空增加单机资源；读多时缓存或副本等方法可能更适合。分片键应结合稳定性、基数、热点、常用查询选择，不是用户编号在所有系统里都最合适。查询不带这个字段也不必然查所有分片，可能有其他路由或索引；跨片访问一般带来额外协调成本，不能说所有JOIN或事务都不支持。上述边界来自R1、R3及R4的适用范围，视频仅选其中必要的两句。

示例订单7042、7043、7044、7045、7046、7047与新订单7050、7051、7052仅为追踪标签。示例用户42、17、86，以及A/B/C映射和进入顺序均为教学设计，无QPS、延迟、吞吐或容量实测。画面订单表是节选，不表示迁移、删除或完整数据量。

## 片尾参考资料清单（2026-10-26整理，沿用2026-10-24访问）

原片主线和事实未改。以上R1–R4均进入片尾，采用 `presentation: title-author`，只显示原题与机构，每页最多4项、默认5秒；没有明确个人署名，不填author。题名从原“官方资料”栏原值中分离明确机构前缀，保留题名字词及大小写，不翻译或概括。

既有完整研究基线`278f69a71151cada63e7068b4cfc0d5222501ac7`；Git blob`8a36d0f003c26aca09d91e7a6ae8fb033c85f098`；完整SHA-256`42a769580bc5286097d10c44102391ba23eb36680ed7a69f62c233d653d8c718`（2372字节）。[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/278f69a71151cada63e7068b4cfc0d5222501ac7/episodes-codex/db-sharding/research.md)和[本轮独立归档](../../docs/reference-endcards/batch-6/evidence/db-sharding-prior-reading-278f69a7.md)只标识本仓阅读记录，不是官方原文固定快照。

本轮没有新GET，清单及verification.checkedAt保留2026-10-24；不声称重新取得官方正文、当前head、发布日期或响应SHA。Azure原记录未单列页面版本/日期，保持未标；Vitess正式URL明示23.0，沿用该版本。

| 片尾编号 | 实际原题 | 机构 | 原记录位置 |
| --- | --- | --- | --- |
| R1 | [Sharding pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding) | Microsoft · Azure Architecture Center | 第7行 |
| R2 | [Shard](https://vitess.io/docs/23.0/concepts/shard/) | Vitess | 第8行 |
| R3 | [Vindexes](https://vitess.io/docs/23.0/reference/features/vindexes/) | Vitess | 第9行 |
| R4 | [Resharding](https://vitess.io/docs/23.0/user-guides/configuration-advanced/resharding/) | Vitess | 第10行 |


证据、四条原主张与边界逐字记录见[sources-db-sharding.json](../../docs/reference-endcards/batch-6/sources-db-sharding.json)。原研究补充边界、示例说明及文章所有章节/脚注保持；不把映射示例扩展为统一算法、容量/性能保证或所有跨片JOIN/事务均不可用。

这里只记录资料复用与清单生产，不记录冻结、媒体生成、声音复核、附录观看或上线已通过，也不预记用户认可。
