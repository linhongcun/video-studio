# cdn · 片尾参考资料

本轮核验日期：2026-10-25（北京时间）。

原文响应SHA、逐论点短引、版本与实际访问范围见[核验记录](../../docs/reference-endcards/batch-2/sources-cdn.json)。正式站点正文在本轮不可读，实际阅读并核对的是负责机构官方仓库中的固定正文；没有将正式站点记为已成功访问。

## R1 · Cloudflare：Content Delivery Network (CDN) Reference Architecture

- 版本：官方文档 · 2026-10-25核验
- 正式链接：<https://developers.cloudflare.com/reference-architecture/architectures/cdn/>
- 本轮实读：<https://github.com/cloudflare/cloudflare-docs/blob/ec32a21c71d1aa8747ef270e180ef0d31e5231f6/src/content/docs/reference-architecture/architectures/cdn.mdx>
- 固定commit：`ec32a21c71d1aa8747ef270e180ef0d31e5231f6`
- 正文完整SHA-256：`4a281ae24e3576bbccdf4ad776a3853df8d136cb95beb4d4deb1b364317f5b16`
- 实读章节：How a CDN tackles web application challenges；Routing requests to CDN nodes；Tiered Cache及流量示例
- 对应镜头：2, 3, 4, 5, 6, 7, 8, 11, 12

支持的具体主张：

- CDN在多个网络位置缓存源站内容，可用副本能减少获取内容的回源请求。
- Cloudflare的Anycast由BGP路由，并考虑处理容量；片中地图直线长度不等于实际网络路由或时延测量。
- 标准缓存未命中可继续取源，真实部署也可有多级缓存；片中一层边缘与源站是教学简化。

## R2 · IETF HTTP WG：HTTP Caching

- 版本：RFC 9111 · 2022
- 正式链接：<https://www.rfc-editor.org/rfc/rfc9111.html>
- 本轮实读：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9111.xml>
- 固定commit：`3cdfb4df4dc47e75e9642efc99ab699a0495d883`
- 正文完整SHA-256：`800d7f7c39dbe9b580c5d1bac28bd6328e396d66608a25c8bc9c1f78b6da5a25`
- 实读章节：§2 Overview；§3 Storing Responses in Caches；§4/§4.2/§4.3复用、新鲜度与验证；§5.2.2响应缓存指令；Caching of Sensitive Information
- 对应镜头：4, 6, 7, 9, 10, 12

支持的具体主张：

- 响应存储和复用受请求匹配、缓存指令及新鲜度等条件限制，不是取到内容就能永久共享。
- 缓存不能直接复用时可通过条件请求验证或获取新响应；不能把过期副本一直当成新内容使用。
- 共享缓存与私有缓存有不同边界；不带字段列表的private禁止共享缓存存储该响应，no-store限制存储。

仅配套图文：

- Set-Cookie本身不自动禁止HTTP缓存，服务器仍应设置适当Cache-Control；带Cookie不等于共享副本天然安全。

## R3 · Cloudflare：Cloudflare cache responses

- 版本：官方文档 · 2026-10-25核验
- 正式链接：<https://developers.cloudflare.com/cache/concepts/cache-responses/>
- 本轮实读：<https://github.com/cloudflare/cloudflare-docs/blob/ec32a21c71d1aa8747ef270e180ef0d31e5231f6/src/content/docs/cache/concepts/cache-responses.mdx>
- 固定commit：`ec32a21c71d1aa8747ef270e180ef0d31e5231f6`
- 正文完整SHA-256：`261e6e29bc3e9e54a6dbacb213ad2a6aaf8bb8882609d18b624455fd3dd84ef3`
- 实读章节：HIT；MISS；EXPIRED；STALE；REVALIDATED；DYNAMIC
- 对应镜头：4, 5, 7, 9, 11

支持的具体主张：

- Cloudflare将从缓存找到资源与未命中后取源区分为不同状态，命中可用副本与回源是不同请求路径。
- 过期内容可能重新取源或条件验证；不适合缓存的内容也可能直接取源，未命中不是所有回源的唯一原因。

## 版本与边界

- Cloudflare架构页frontmatter的reviewed为2022-12-02；本轮实际读的是2026-10-25生产分支固定版本，核验日不是发布日期。Cloudflare状态页未标发布日期。
- CDN实现可采用不同调度与缓存层级；地图、节点及路径为教学示意，不由直线距离保证选点、实际时延或固定加速倍数。
- 产品状态、Anycast与Tiered Cache用作公开实现依据，不扩称所有CDN采用同样产品配置。
- AWS旧链接与Natural Earth素材许可保留原文的2026-10-24记录，本轮未重新读到canonical正文，不作为新增片尾资料；地图许可不是技术机制论证来源。
