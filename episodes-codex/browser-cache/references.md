# browser-cache · 片尾参考资料

本轮访问与核验日期：2026-10-25（北京时间）。

RFC Editor和MDN网站在本轮均被会话代理拒绝访问（Tunnel 403），因此实际阅读的是负责工作组或MDN官方GitHub仓库中的固定commit正文。下面同时给出正式链接和本轮实读链接；正式站点未记为本轮已访问成功。完整响应哈希、原文节选及访问结果见[核验记录](../../docs/reference-endcards/batch-1/source-verification.json)。

## R1 · IETF HTTP WG：HTTP Caching

- 版本：RFC 9111 · 2022
- 正式链接：<https://www.rfc-editor.org/rfc/rfc9111.html>
- 本轮实读：<https://github.com/httpwg/http-core/blob/3cdfb4df4dc47e75e9642efc99ab699a0495d883/rfc9111.xml>
- 固定commit：`3cdfb4df4dc47e75e9642efc99ab699a0495d883`
- 正文完整SHA-256：`800d7f7c39dbe9b580c5d1bac28bd6328e396d66608a25c8bc9c1f78b6da5a25`
- 实读章节：§2 Overview；§4 Constructing Responses from Caches；§4.2 Freshness；§5.2.2.1 max-age
- 对应镜头：2, 3, 4, 5, 6, 7, 8, 9, 10
- 核验方式：实际HTTP 200读取固定正文，逐段审读，保留原文节选；未声称已访问正式站点。

支持的具体主张：

- 缓存复用须满足目标、请求方法、请求字段与缓存指令等条件
- 新鲜度判定为freshness_lifetime > current_age；示例60秒期限在60秒时已不再新鲜

## R2 · MDN Web Docs：HTTP caching

- 版本：持续维护文档 · 2026-10-25核验
- 正式链接：<https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching>
- 本轮实读：<https://github.com/mdn/content/blob/b13e73fdf1fedcb837aebdd842f1a9a6adc76e10/files/en-us/web/http/guides/caching/index.md>
- 固定commit：`b13e73fdf1fedcb837aebdd842f1a9a6adc76e10`
- 正文完整SHA-256：`95ca406025178d12948fddefb8257453ff962f37d24acb15716c8859b9a4efc5`
- 实读章节：Types of caches／Private caches；Fresh and stale based on age；Validation；Don’t cache
- 对应镜头：2, 3, 4, 6, 7, 8, 9, 10
- 核验方式：实际HTTP 200读取固定正文，逐段审读，保留原文节选；未声称已访问正式站点。

支持的具体主张：

- 浏览器HTTP缓存属于私有缓存；新鲜响应可省去获取对应资源的网络请求
- no-cache要求复用前验证，no-store要求不存储；不要将HTTP缓存与浏览器的其他缓存机制混同

## 示例与边界

60秒、20秒、61秒为教学数字，实际缓存复用还受请求、响应指令与浏览器策略等影响；示例60秒达到期限时已不再fresh。超期不等于自动删除或必须重传整个内容。RFC9110的304细节保留在配套文章；本次片尾仅列与正文主线相关的RFC9111和MDN，不为了增加条数而把拓展资料列上卡。
