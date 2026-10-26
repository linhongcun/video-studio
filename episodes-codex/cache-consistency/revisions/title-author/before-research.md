# EP.09 公开资料核验

访问日期：2026-10-24（北京时间）。本次实际打开并读取下列官方正文，不以旧分镜或内部记录作事实来源。

|编号|公开正文|采用的事实|边界|
|---|---|---|---|
|R1|[Microsoft Cache-Aside pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)|更新数据源后删除对应缓存，后续未命中重新填充；先删缓存再写源存在旧值回填窗口；此模式不保证一致性|实际读取Solution、Problems and considerations、Example末尾顺序说明；不是跨系统原子更新，也不把正确顺序说成消除所有并发问题|
|R2|[Microsoft Caching guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching)|缓存包含原数据的临时副本，需要选择适合业务的新鲜程度和更新策略|本片仅讨论应用管理的服务端缓存，不混同浏览器HTTP缓存与数据库主从延迟|
|R3|[Redis client-side caching reference](https://redis.io/docs/latest/develop/reference/client-side-caching/)|旧副本可在原数据变化后继续返回旧信息；过期或失效通知使应用移除对应副本|正文讲特定产品的本地缓存，只作旧副本与失效的一般依据；本片不承诺通知一定到达、不讲具体命令|

## 分镜核验

- 01–04：数据库更新不等于另一份副本自动更新；请求命中该旧副本，就可能拿到旧值。R1、R2、R3。
- 05–08：常见更新路径是写原记录成功、使缓存失效、后续未命中取新值并填充。R1。
- 09–10：先删缓存、还没改源时，另一个读可回源得到旧值并填充；写源随后完成，副本仍旧。R1示例末尾明确描述此窗口。
- 11：先写后删仍非强一致协议；删除失败是本片为解释边界设计的故障示例。并发读写也可能交错，不暗示一种顺序能根治所有旧读。R1的Consistency条目。
- 12：过期限制单个条目的使用期限，不保证实时更新，不排除旧值被再次填充。R1、R3。

## 示例约束

商品7042与199→179是教学数据，没有引用外部价格。动画将多个线程事件按时间顺序拉开以便观察，并非测量真实耗时。删除缓存不删除数据库原记录；刷新页面只产生新请求，不承诺越过应用缓存。对需要严格价格正确性的交易路径，文章建议从权威记录核验，不让展示缓存代替最终业务检查。

## 流程导航返工的实际复读（2026-10-24）

本轮实际复读Microsoft官方仓库的[Cache-Aside正文](https://github.com/MicrosoftDocs/architecture-center/blob/8abcc13a84f992292283cb3ba879621d011d011c/docs/patterns/cache-aside-content.md)。Azure网页被当前代理以403拦截，改读同一官方仓库正文，不使用旧稿代替资料。该文件最近提交日期2026-07-02；实际获取正文SHA-256为`eb19852e710d924d98a39f386928ef1b0d763391f0e9e22a353ce818dd57881f`，访问记录见`revisions/flow-map-sources.json`。

正文Solution的读取三步、写后失效段落、Consistency/Lifetime条目及Example末尾顺序说明均已实际阅读：先保存数据源再撤对应副本；先删后写时读取可以插入并回填旧值；此模式不保证一致性，期限也不能代替更新治理。本轮沿用原事实、商品7042与199→179示例，不扩成缓存策略比较。


## 本轮片尾原始资料核验（2026-10-26）

本轮只为既有视频补充参考资料，不改原稿、配音、分镜与原R1/R2/R3研究编号。新的片尾清单选用以下两项，安排在既有正文末尾一页5秒；媒体生成与独立审片尚由其他任务执行，本节不预记完成。

- 新R1：Microsoft **Cache-Aside Pattern**，原题按[cache-aside.yml metadata.title](https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/cache-aside.yml)逐字保留，同提交content包含[实际正文](https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/cache-aside-content.md)；不是自行翻译的模式名称。完整正文GET200，14318字节，SHA-256 `eb19852e710d924d98a39f386928ef1b0d763391f0e9e22a353ce818dd57881f`；题名／包含关系文件GET200，752字节，SHA-256 `0db2e1bd74a35bb014ac8da4ae66cfe931e39d934e10e23fef56bcf15069f0cd`。
- 新R2：Redis **EXPIRE**，原题按[固定命令参考](https://github.com/redis/docs/blob/4fe762f8dab40f0b661207374378ed52113c9fe3/content/commands/expire.md)frontmatter title第74行保留。完整GET200，10783字节，SHA-256 `8724f37add5b23122fc8f7b78e5c250888a0c2321850a463b0a80709cbe00f6b`。用于第12镜期限结束后删除条目的机制，不把具体命令或Redis客户端tracking冒充视频已展开的流程。

两canonical入口本轮实际GET均遭Tunnel 403；它们的旧访问日期和旧复读记录仍保留，本轮成功读取仅指以上固定官方仓库原文。访问时间、最终响应URL、完整SHA与逐论点原始行见[本轮来源证据](../../docs/reference-endcards/batch-3/sources-cache-consistency.json)。

片尾实际短引（原文，非内部supports翻译）：

> When an application updates information, it writes the change to the data store and then invalidates the corresponding item in the cache.

位置：Solution，cache-aside-content.md第24行的完整首句。读操作第19–22行、写后失效第24行、Consistency第38行与Example第154行共同支持未命中回填、写后删除、先删后写的交错窗口及非强一致边界。第11镜删除失败是本片教学故障示例，不说官方文档保证自动重试成功。

> After the timeout has expired, the key will automatically be deleted.

位置：EXPIRE正文开头第77行。第81–91行说明清除期限的操作，第219–231行说明期限可更新／移除，第256–267行说明被动与主动过期。不从“超时删除”推导“每次读取都是数据库最新值”；期限被重设、移除或旧值重新回填的边界保留。

**编者说明：**原R2 Caching guidance及原R3 client-side caching仍是历史调研来源，但本轮主卡不凑第三项，也不把client-side invalidation通知协议当成本片通用服务端Cache-Aside的实现保证。两条引句均连续、保留原语言与标点，无拼接省略、无译文冒充原文。
