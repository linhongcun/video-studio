# EP.08 公开资料核验

访问日期：2026-10-24（北京时间）。本次通过联网读取工具打开官方正文，非复用旧稿或搜索摘要。产品文档仅作事实依据，片中不点名产品。

|编号|公开正文|本片采用的事实|适用边界|
|---|---|---|---|
|R1|[Microsoft Cache-Aside pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)|先查缓存；未找到才从数据源取回并填充；不保证缓存与数据源一直一致|此处讲应用主动管理的缓存，不说所有缓存都采用同一实现；实际读取正文Solution与Problems and considerations|
|R2|[Microsoft Caching guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching)|常被重复读取的数据可临时复制到更靠近应用的位置；缓存可在进程内或共享服务中|仅减少部分重复读取，不承诺固定加速比；数据变化频繁和命中少的情况另作权衡|
|R3|[Redis client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/)|本地内存可复用常用查询结果，减少数据库请求；过期与失效用于防止继续采用旧副本|此文说明的是Redis客户端缓存，本片只采用内存复用和副本失效的一般事实，不把它当成所有服务端缓存机制|
|R4|[AWS Caching patterns](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/caching-patterns.html)|按需填充会在首次未命中时增加额外访问；不同填充策略有成本取舍|白皮书版本可能较旧，标记“仅参考”；片中不讲产品API，不承诺只要加缓存就更快|

另实际打开了[AWS Caching challenges and strategies](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/)，发布日期2019-12-05，标记“仅参考”。仅用于提醒冷缓存或不可用时数据库压力可能增大；本片不展开该支线。

## 逐镜主张与教学设计

- 01–03：重复查询会消耗处理能力；是否真的排队取决于负载，动画明确是教学场景，不断言所有慢页都由数据库造成。R2。
- 04–05：同一商品临时副本放在服务器一侧；可以是本地内存，也可以共享缓存。R2、R3。
- 06–08：检查缓存、未命中取源并填充、命中复用。R1、R4。
- 09：数据库读取次数在本动画的三次请求中少于每次回源，仅是流程计数，不是实际压测数据。R1支持流程，具体次数是教学设计。
- 10：缓存会到期或移除，未命中可以重新取回。R1、R3。
- 11–12：复用收益与额外开销取决于访问模式；原记录不因为缓存存在而消失。R1、R2。

商品7042、199元、三次请求和示例计数没有外部统计含义，片中持续标“示例数据”。未使用未核验的性能数字。

## 第三批片尾参考资料核验（2026-10-26）

本轮在原文后追加，两项片尾资料采用原题名、连续逐字原句和独立定位。完整核验记录见[sources-server-cache.json](../../docs/reference-endcards/batch-3/sources-server-cache.json)；公开完整链接见[references.md](references.md)。原research表的访问日期和来源编号保留，本轮片尾编号独立记录于references.json。

- R1 原题：Cache-Aside Pattern；位置：Solution, step 1 (line 19)；实读固定正文：https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/cache-aside-content.md。
  - 原句：The application determines whether an item currently resides in the cache by attempting to read from the cache.
  - 完整正文SHA-256：`eb19852e710d924d98a39f386928ef1b0d763391f0e9e22a353ce818dd57881f`。

- R2 原题：EXPIRE；位置：Opening paragraph (line 77)；实读固定正文：https://github.com/redis/docs/blob/1406db84d01f1d6a07fe567cbdea4d051456a2d7/content/commands/expire.md。
  - 原句：After the timeout has expired, the key will automatically be deleted.
  - 完整正文SHA-256：`8724f37add5b23122fc8f7b78e5c250888a0c2321850a463b0a80709cbe00f6b`。

- Microsoft当前页面由cache-aside.yml入口的metadata.title与cache-aside-content.md组成，两个文件都在同一官方固定commit中实际GET读取。旧cache-aside.md路径已删除，未把404当成已取得的正文。
- Redis采用当前未归档redis/docs官方仓库中的EXPIRE文档；旧redis/redis-doc仓库已归档，不作为本轮来源。since 1.0.0是命令引入版本，不能当文档发布日期。
- 实读Microsoft Solution步骤1–3、Lifetime/Evicting/Consistency/Local caching及适用条件，确认本片命中/未命中/回填、共享与本地缓存及开销边界；该文明确不保证数据源与缓存一致。
- Redis原文确认默认键可不带TTL、已设置超时的键会过期、到期处理含主动与访问时检查。EXPIRE不负责数据库更新传播，也不会自动替应用读取数据库和回填，因此固定TTL不证明强一致。
- 本轮不重新GET旧稿canonical页或地图/产品图标素材，不把历史记录改成本轮新访问；没有改script、分镜、voice、冻结或媒体。
