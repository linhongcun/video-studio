# cache-consistency · 原题与原文短引

本轮固定原文核验：2026-10-26（北京时间）。实际完整GET、全文SHA、原题及逐论点原文见[来源记录](../../docs/reference-endcards/batch-3/sources-cache-consistency.json)。两个canonical本轮均因代理Tunnel 403未取得正文，引用采用各自官方仓库的固定提交，不把历史canonical访问写成本次成功访问。

本轮片尾R1/R2为精选清单；原script.md和research.md中的历史R1/R2/R3编号保持原意，不用新R2去覆盖旧研究的R2/R3。配音、分镜及商品7042、199→179的教学示例均保持。

## R1 · Cache-Aside Pattern

- 作者／机构：Microsoft
- 年份／版本：Azure Architecture Center · 2026-10-26核验
- 原题位置：cache-aside.yml · metadata.title · line 3
- 正式入口：<https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside>
- 固定原文：<https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/cache-aside-content.md>
- 同版本原题及正文绑定：<https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/cache-aside.yml>（metadata.title；content包含上述正文）

> When an application updates information, it writes the change to the data store and then invalidates the corresponding item in the cache.

原句位置：Solution · cache-aside-content.md line 24。连续完整原句，保留原语言与标点。

内部论点对应（编者说明，不作为原文引句）：

- 缓存未命中时从数据源取出并填充，应用更新先写数据源，再使对应缓存项失效。
- 先删缓存再写数据源时，另一读请求可在窗口中把旧值重新填入缓存。
- Cache-Aside不保证数据源与缓存始终一致；有效期要匹配访问模式，不能替代更新治理。

使用边界（编者说明）：

- This document supports the generic cache-aside flow and its ordering/consistency boundary; it is not an atomic transaction across the source store and cache.
- The deletion failure in shot 11 and product 7042/prices 199 to 179 are this episode's teaching examples. No claim that this document promises retries always succeed or eliminates every concurrent stale read.
- The body also discusses write-through, semantic caching and Azure products; those unneeded claims are not imported into this existing episode.

## R2 · EXPIRE

- 作者／机构：Redis
- 年份／版本：官方命令参考 · 2026-10-26核验
- 原题位置：frontmatter title · line 74
- 正式入口：<https://redis.io/docs/latest/commands/expire/>
- 固定原文：<https://github.com/redis/docs/blob/4fe762f8dab40f0b661207374378ed52113c9fe3/content/commands/expire.md>

> After the timeout has expired, the key will automatically be deleted.

原句位置：Opening description · line 77。连续完整原句，保留原语言与标点。

内部论点对应（编者说明，不作为原文引句）：

- Redis为键设置超时后，期限结束会删除该键；这是本片条目过期机制的官方实现依据。
- 键的期限可被更新或移除，重写键可清除既有期限；期限本身不会主动取得数据库的新值。

使用边界（编者说明）：

- EXPIRE is an official implementation example for expiration. The fixed video describes generic application-managed cache-aside, not an instruction to run this specific Redis command.
- The deadline does not fetch a new database value or guarantee cache/source consistency. Resetting/removing TTL or refilling an old value can defeat a simple freshness bound.
- Do not expand Redis's own replication/AOF expiration discussion into a guarantee about external database-and-cache consistency. Client-side tracking/invalidation protocols read as candidates are not used as the procedure taught in this video.
