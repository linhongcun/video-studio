# cdn · 原题与原文短引

本轮固定正文复核日期：2026-10-25（北京时间）。原题按文档frontmatter／RFC题名／首个H1逐字保留；短引选取完整原句，不以内部supports或译名替代原文。

本轮GET状态、全文SHA、题名及原句位置见[核验记录](../../docs/reference-endcards/original-titles/sources-core.json)。正式入口与固定版本同时保留，原有canonical访问记录未冒充本轮重新访问。

## R1 · Content Delivery Network (CDN) Reference Architecture

- 作者／机构：Cloudflare
- 年份／版本：官方文档 · 2026-10-25核验
- 原题位置：frontmatter title · line 2
- 正式文档：<https://developers.cloudflare.com/reference-architecture/architectures/cdn/>
- 固定原文：<https://github.com/cloudflare/cloudflare-docs/blob/ec32a21c71d1aa8747ef270e180ef0d31e5231f6/src/content/docs/reference-architecture/architectures/cdn.mdx>

> Edge nodes within the Cloudflare network cache content from the origin server and are able to respond to requests via a cached copy.

原句位置：Cloudflare CDN architecture and design。原始文件行号：132–132。

内部论点对应（制作解释，不作为原文引句）：

- CDN在多个网络位置缓存源站内容，可用副本能减少获取内容的回源请求。
- Cloudflare的Anycast由BGP路由，并考虑处理容量；片中地图直线长度不等于实际网络路由或时延测量。
- 标准缓存未命中可继续取源，真实部署也可有多级缓存；片中一层边缘与源站是教学简化。

## R2 · HTTP Caching

- 作者／机构：IETF HTTP WG
- 年份／版本：RFC 9111 · 2022
- 原题位置：RFC front/title
- 正式文档：<https://www.rfc-editor.org/rfc/rfc9111.html>
- 固定原文：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9111.xml>

> When a response is fresh, it can be used to satisfy subsequent requests without contacting the origin server, thereby improving efficiency.

原句位置：§4.2 Freshness。原始文件行号：659–661。

内部论点对应（制作解释，不作为原文引句）：

- 响应存储和复用受请求匹配、缓存指令及新鲜度等条件限制，不是取到内容就能永久共享。
- 缓存不能直接复用时可通过条件请求验证或获取新响应；不能把过期副本一直当成新内容使用。
- 共享缓存与私有缓存有不同边界；不带字段列表的private禁止共享缓存存储该响应，no-store限制存储。

## R3 · Cloudflare cache responses

- 作者／机构：Cloudflare
- 年份／版本：官方文档 · 2026-10-25核验
- 原题位置：frontmatter title · line 2
- 正式文档：<https://developers.cloudflare.com/cache/concepts/cache-responses/>
- 固定原文：<https://github.com/cloudflare/cloudflare-docs/blob/ec32a21c71d1aa8747ef270e180ef0d31e5231f6/src/content/docs/cache/concepts/cache-responses.mdx>

> The response is eligible for cache but was not present in Cloudflare's cache at request time, so it was served from the origin web server.

原句位置：MISS · line 29。原始文件行号：29–29。

内部论点对应（制作解释，不作为原文引句）：

- Cloudflare将从缓存找到资源与未命中后取源区分为不同状态，命中可用副本与回源是不同请求路径。
- 过期内容可能重新取源或条件验证；不适合缓存的内容也可能直接取源，未命中不是所有回源的唯一原因。
