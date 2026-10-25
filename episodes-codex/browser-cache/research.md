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

## 2026-10-25 片尾参考资料补充核验

本轮对照`references.json`／`references.md`读取资料正文，实际读取日期为2026-10-25（北京时间）。正式文档站点均被会话代理以Tunnel 403拒绝，因此改读负责工作组或MDN官方GitHub仓库固定commit；不沿用2026-10-24的访问记录冒充本轮联网结果。原文节选、完整SHA与可达性记录见[本批证据](../../docs/reference-endcards/batch-1/source-verification.json)。

- R1 IETF HTTP WG，HTTP Caching（RFC 9111 · 2022）：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9111.xml>。实读§2 Overview；§4 Constructing Responses from Caches；§4.2 Freshness；§5.2.2.1 max-age；支撑：缓存复用须满足目标、请求方法、请求字段与缓存指令等条件；新鲜度判定为freshness_lifetime > current_age；示例60秒期限在60秒时已不再新鲜。
- R2 MDN Web Docs，HTTP caching（持续维护文档 · 2026-10-25核验）：<https://github.com/mdn/content/blob/b13e73fdf1fedcb837aebdd842f1a9a6adc76e10/files/en-us/web/http/guides/caching/index.md>。实读Types of caches／Private caches；Fresh and stale based on age；Validation；Don’t cache；支撑：浏览器HTTP缓存属于私有缓存；新鲜响应可省去获取对应资源的网络请求；no-cache要求复用前验证，no-store要求不存储；不要将HTTP缓存与浏览器的其他缓存机制混同。

## 2026-10-25 原题与原文短引核验

按最新要求，片尾采用文献原标题及可核对的完整原句，不再用displayTitle／displaySupport概括替代题名。内部supports保持为论点映射，不能冒充原文。本轮13份去重固定正文实际GET记录、题名位置与各句原文见[统一证据](../../docs/reference-endcards/original-titles/sources-core.json)；本片sources的titleEvidence与quotation均指向该记录。XML仅解析实体和内联标记、合并排版空白；DNS的Markdown粗体标记按可见正文还原，不删改词句。旧canonical访问与其他历史来源记录继续保留。
