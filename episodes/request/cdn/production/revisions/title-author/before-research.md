# EP05 公开资料核验

访问日期：2026-10-24（北京时间）。通过联网阅读工具实际打开正文，以下为独立概括。

1. AWS，How CloudFront delivers content（持续维护）
   https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/HowCloudFrontWorks.html
   读取交付流程与 regional edge caches 章节：请求被路由到适合服务的边缘位置，通常按网络时延接近；命中直接返回，未命中继续从上层或源站获取；返回内容可供后续请求复用。首字节到达时可开始转发。支持镜2–8。这里只借其真实实现核验通用流程，不将某一家分层拓扑画成所有 CDN 的固定结构。
2. IETF，RFC 9111 HTTP Caching，2022年6月
   https://www.rfc-editor.org/rfc/rfc9111.html
   实际阅读2、3、4.2、4.3节：缓存保存可复用的响应，使用受缓存键、存储条件和新鲜度规则限制；过期后可验证或按明确条件使用，不是永久有效。支持镜4、6–10。
3. Cloudflare，Default cache behavior（2026-09-14更新）
   https://developers.cloudflare.com/cache/concepts/default-cache-behavior/
   已打开正文，核验缓存受响应头与配置控制，不是所有内容都会自动缓存。支持镜6、9、10；厂商默认规则不当作普遍标准。
4. MDN，HTTP caching（持续维护）
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching
   实际阅读 Types of caches：共享缓存位于客户端与源站之间；个性化内容进入共享缓存可能造成信息泄漏，Cookie 本身也不能替代正确缓存指令。支持镜10。

## 边界

- 只讲同一公开商品图片。真实大陆轮廓用于说明相对地域；节点与网络路径仍为教学示例，不由线长推断真实物理线路、网络跳数、时延或保证性能；无无来源毫秒/倍数。
- 边缘“合适”不等于地理上最近，按路由、网络时延、负载与配置选择。
- 命中且可复用时才省掉本次取图的回源；未命中不承诺第一次一定快。
- 简化为一层边缘与源站，真实系统可能有多级缓存、请求合并、流式回填。
- 私人订单演示配置正确的私有响应绕开共享缓存，不主张仅有 Cookie 就会自动安全。
- 缓存不能自动修好源站程序和数据库瓶颈，动态内容加速的其他能力留在文章。

## 地图与术语返工的新增来源与复核

- 2026-10-24实际通过现有proxy读取Natural Earth官方维护者上游仓库README与110m land GeoJSON。README原文明确“Natural Earth is a public domain map dataset”及“free for use in any type of project”。固定commit `ca96624a56bd078437bca8184e78163e5039ad19`，GeoJSON完整SHA `9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9`，138160字节；本地原文、固定URL、许可依据与转换方式在assets/map/。未成功取得不存在的/LICENSE（404），不称其为一个已读取的许可证文件。
- 地图上只画大陆轮廓，不画行政边界。位置、调度和路径为示例，不暗示具体CDN部署或真实测量。地图的相对地域帮助理解临近服务点；“近”不能只看直线距离，需结合实际网络路径、时延与调度。
- 新词引入：CDN与内容分发网络并列，边缘节点与请求检查动作对应，回源与本例未命中后的长路径对应；没有新增DNS/Anycast/分层机制讲解。
- 独立事实预审remake_ep06_07本轮重新读取AWS交付流程、RFC9111与Cloudflare缓存正文，确认本例未命中回源、命中可复用短返及过期/私人边界；该独立来源复核与主制作实际读取原资料的记录分开，不把源审当成新片观看通过。

## 参考资料片尾补充核验（2026-10-25）

本轮只在旧文后追加，原访问日期和地图许可记录保持。详细响应SHA、短引与版本检查见[docs/reference-endcards/batch-2/sources-cdn.json](../../docs/reference-endcards/batch-2/sources-cdn.json)；片尾清单见[references.json](references.json)，可读说明见[references.md](references.md)。

实际HTTP GET取得官方Cloudflare生产分支固定commit `ec32a21c71d1aa8747ef270e180ef0d31e5231f6` 的CDN架构与缓存状态正文，以及HTTP工作组固定commit `3cdfb4df4dc47e75e9642efc99ab699a0495d883` 的RFC9111正文；三项均为200完整响应。正式站点访问均返回会话代理Tunnel 403，未记为成功读取。

- R1 Cloudflare / Content Delivery Network (CDN) Reference Architecture：支持CDN在多个网络位置缓存源站内容，可用副本能减少获取内容的回源请求。；Cloudflare的Anycast由BGP路由，并考虑处理容量；片中地图直线长度不等于实际网络路由或时延测量。；标准缓存未命中可继续取源，真实部署也可有多级缓存；片中一层边缘与源站是教学简化。。正式链接：https://developers.cloudflare.com/reference-architecture/architectures/cdn/；本轮实读：https://github.com/cloudflare/cloudflare-docs/blob/ec32a21c71d1aa8747ef270e180ef0d31e5231f6/src/content/docs/reference-architecture/architectures/cdn.mdx。

- R2 IETF HTTP WG / HTTP Caching：支持响应存储和复用受请求匹配、缓存指令及新鲜度等条件限制，不是取到内容就能永久共享。；缓存不能直接复用时可通过条件请求验证或获取新响应；不能把过期副本一直当成新内容使用。；共享缓存与私有缓存有不同边界；不带字段列表的private禁止共享缓存存储该响应，no-store限制存储。。正式链接：https://www.rfc-editor.org/rfc/rfc9111.html；本轮实读：https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9111.xml。

- R3 Cloudflare / Cloudflare cache responses：支持Cloudflare将从缓存找到资源与未命中后取源区分为不同状态，命中可用副本与回源是不同请求路径。；过期内容可能重新取源或条件验证；不适合缓存的内容也可能直接取源，未命中不是所有回源的唯一原因。。正式链接：https://developers.cloudflare.com/cache/concepts/cache-responses/；本轮实读：https://github.com/cloudflare/cloudflare-docs/blob/ec32a21c71d1aa8747ef270e180ef0d31e5231f6/src/content/docs/cache/concepts/cache-responses.mdx。

- 版本区别：Cloudflare架构页reviewed=2022-12-02，本轮固定源取自2026-10-25的production提交；不把核验日写成页面发布日期。旧/cache/reference/cdn-reference-architecture.mdx只是跳转壳，已沿external_link实读真正架构正文，没有引用213字节占位文件。
- AWS仓库元数据显示archived=true，默认分支archived，最后push2023-06-15；canonical本轮未取得。因此保留旧稿2026-10-24记录、不将归档源当现行文档、不作为本轮卡片主依据。
- 本轮还读取Cloudflare默认缓存行为页，确认产品默认受规则影响；没有把其概述当成所有Origin Cache Control配置的统一保证。最终用RFC9111与缓存状态页交叉约束存储、复用、过期验证和私人响应边界。
- 本轮未重新读取Natural Earth、MDN旧链接等历史素材。原地图许可、公有领域依据、GeoJSON SHA、节点/路径示例与性能边界均照旧，未把旧日志日期改成本轮在线核验。

## 2026-10-25 原题与原文短引核验

按最新要求，片尾采用文献原标题及可核对的完整原句，不再用displayTitle／displaySupport概括替代题名。内部supports保持为论点映射，不能冒充原文。本轮13份去重固定正文实际GET记录、题名位置与各句原文见[统一证据](../../docs/reference-endcards/original-titles/sources-core.json)；本片sources的titleEvidence与quotation均指向该记录。XML仅解析实体和内联标记、合并排版空白；DNS的Markdown粗体标记按可见正文还原，不删改词句。旧canonical访问与其他历史来源记录继续保留。
