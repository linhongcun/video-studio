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
