# server-cache · 片尾参考资料

核验日期：2026-10-26（北京时间）。两项资料使用原题名与连续原句，`presentation`为`original-title-quote`；默认每页两项、5秒。这里只记录来源输入，不预记附录渲染或上线已完成。

完整响应SHA、原题证据、原文语段和边界见[sources-server-cache.json](../../docs/reference-endcards/batch-3/sources-server-cache.json)。本轮片尾R1/R2独立编号，与原research.md的2026-10-24表号分别对应。

## R1 · Cache-Aside Pattern

- 机构：Microsoft · Azure Architecture Center
- 版本：官方文档 · 2026-10-26核验
- 正式链接：<https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside>
- 实读固定正文：<https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/cache-aside-content.md>
- 正文SHA-256：`eb19852e710d924d98a39f386928ef1b0d763391f0e9e22a353ce818dd57881f`
- 原题位置：cache-aside.yml, metadata.title (line 3)
- 引文位置：Solution, step 1 (line 19)
- 对应镜头：01, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12

> The application determines whether an item currently resides in the cache by attempting to read from the cache.

支持的主张（内部对应，不作为屏幕上的原句）：

- 应用先检查缓存，未命中再读取数据源、填回缓存并返回；命中时可复用临时副本，减少重复读取。
- 缓存可以在应用进程内，也可以由多个应用实例共享；Redis是原文给出的共享缓存实现示例。
- 条目过期或被清理后可能重新取源；命中少或复用少时额外缓存检查与填充可能得不偿失。
- Cache-Aside不保证缓存与数据库始终一致，过期时间也不能证明数据库修改会立即反映到旧副本。

原题元数据固定正文：<https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/cache-aside.yml>；标题与实际内容由同一提交的YAML入口和Markdown正文组成。

## R2 · EXPIRE

- 机构：Redis
- 版本：官方命令文档 · 2026-10-26核验
- 正式链接：<https://redis.io/docs/latest/commands/expire/>
- 实读固定正文：<https://github.com/redis/docs/blob/1406db84d01f1d6a07fe567cbdea4d051456a2d7/content/commands/expire.md>
- 正文SHA-256：`8724f37add5b23122fc8f7b78e5c250888a0c2321850a463b0a80709cbe00f6b`
- 原题位置：frontmatter title (line 74)
- 引文位置：Opening paragraph (line 77)
- 对应镜头：05, 06, 10, 12

> After the timeout has expired, the key will automatically be deleted.

支持的主张（内部对应，不作为屏幕上的原句）：

- 对已设置超时的Redis键，超时后键会过期；Redis通过访问时的惰性检查和主动检查处理到期键。
- Redis键并非天然都带TTL，未设置过期的键可以持续存在，也可以显式删除或清除其TTL。
- 过期或删除后的数据读取仍需由应用的cache-aside逻辑决定是否重新读取数据库并回填；EXPIRE本身不定义数据库更新传播或强一致协议。

## 适用边界

- Cache-Aside是应用主动管理的读取/填充方式，不代表所有缓存机制。
- Redis EXPIRE的过期、Cache-Aside的数据库回读、数据库更新后的缓存一致性是不同职责；固定TTL不是强一致性证明。
- 价格、请求次数和读取次数均为教学示例，无统一性能倍数。
- 原稿的Microsoft缓存指南、Redis客户端缓存和较早AWS材料保留历史访问日期，本轮没有重新请求其canonical正文；不把旧记录标成本轮已读取。
