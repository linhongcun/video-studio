# browser-cache · 原题与原文短引

本轮固定正文复核日期：2026-10-25（北京时间）。原题按文档frontmatter／RFC题名／首个H1逐字保留；短引选取完整原句，不以内部supports或译名替代原文。

本轮GET状态、全文SHA、题名及原句位置见[核验记录](../../docs/reference-endcards/original-titles/sources-core.json)。正式入口与固定版本同时保留，原有canonical访问记录未冒充本轮重新访问。

## R1 · HTTP Caching

- 作者／机构：IETF HTTP WG
- 年份／版本：RFC 9111 · 2022
- 原题位置：RFC front/title
- 正式文档：<https://www.rfc-editor.org/rfc/rfc9111.html>
- 固定原文：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9111.xml>

> When a response is fresh, it can be used to satisfy subsequent requests without contacting the origin server, thereby improving efficiency.

原句位置：§4.2 Freshness。原始文件行号：659–661。

内部论点对应（制作解释，不作为原文引句）：

- 缓存复用须满足目标、请求方法、请求字段与缓存指令等条件
- 新鲜度判定为freshness_lifetime > current_age；示例60秒期限在60秒时已不再新鲜

## R2 · HTTP caching

- 作者／机构：MDN Web Docs
- 年份／版本：持续维护文档 · 2026-10-25核验
- 原题位置：frontmatter title · line 2
- 正式文档：<https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching>
- 固定原文：<https://github.com/mdn/content/blob/b13e73fdf1fedcb837aebdd842f1a9a6adc76e10/files/en-us/web/http/guides/caching/index.md>

> The HTTP cache stores a response associated with a request and reuses the stored response for subsequent requests.

原句位置：Opening paragraph · line 8。原始文件行号：8–8。

内部论点对应（制作解释，不作为原文引句）：

- 浏览器HTTP缓存属于私有缓存；新鲜响应可省去获取对应资源的网络请求
