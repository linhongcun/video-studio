# EP07 公开资料核验

访问日期：2026-10-24（北京时间）。实际读取官方标准正文与MDN技术正文。

|编号|正文|关键主张与范围|
|---|---|---|
|R1|[RFC 9111 HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)|2022，§2缓存保存可复用响应；§4复用依赖目标、请求条件、freshness/validation等限制；§4.2与§5.2.2.1描述新鲜期和max-age。不能仅凭URL相同就断言任何响应都能复用。|
|R2|[MDN HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)|Types、Fresh/stale、ETag/If-None-Match：浏览器缓存属于私有缓存；HTTP缓存与后退前进缓存、Service Worker等机制应区分。其ETag示例帮助核对文章的验证分支。|
|R3|[RFC 9110 HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html#name-304-not-modified)|2022，§15.4.5：304无响应内容，告知客户端可以使用其已有表示；片中不展开状态码，文章说明其仍有网络往返。|

本片只追踪一张允许缓存的图片，从首次取得，到示例有效期内直接复用。60秒、20秒、61秒均为教学数字，画面标“示例数据/时间快进”，不是真实网站响应或性能实测。有效期仅用于本例，不能推广为所有资源期限。

界限：新鲜缓存仍须符合响应和请求规则；刷新方式、请求指令、Vary等会影响复用。超期并不自动删除，也不必每次重传完整内容；可能重新验证或取得更新响应，这些分支留文章。浏览器HTTP缓存不是后台服务端缓存，也不是整页完全离线。

精确临界核验：RFC9111 §4.2的判定公式为`freshness_lifetime > current_age`。本片示例期限60秒，因此显示年龄59秒为fresh、60秒起不再fresh；不把等号误当仍在新鲜期。图中的年龄是教学整数时钟，状态比较直接使用同一可见值。实际Age还涉及传输与上游缓存等计算，本文不把它简化成所有网络响应都从下载完成时零计时。
