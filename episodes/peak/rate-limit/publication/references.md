# rate-limit · 片尾参考资料

本轮核验日期：2026-10-26（北京时间）。每页两项、默认5秒，使用原题与连续原句；本文件只记录资料输入，不预记渲染或发布完成。

完整响应SHA、原题证据、原句上下文及边界见[sources-rate-limit.json](../../docs/reference-endcards/batch-4/sources-rate-limit.json)。

## R1 · Local rate limit

- 机构：Envoy
- 版本：维护文档 · 2026-10-26核验
- 正式原文：<https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/local_rate_limit_filter>
- 实读固定正文：<https://github.com/envoyproxy/envoy/blob/83297dad103f3dbd6320d0b29cd1e7781cf45305/docs/root/configuration/http/http_filters/local_rate_limit_filter.rst>
- 全文SHA-256：`7db0308c39cb772046dc9e604df049ae591871926ea2252a7bcdf695bc178bdf`
- 原题证据：reStructuredText document heading (line 3)
- 引文位置：Opening behavior description (lines 15–16)

> If the local rate limit token bucket is checked, and there are no tokens available, a 429 response is returned (the response is configurable).

内部论点对应：

- 已启用并执行的本地令牌桶检查按请求消耗令牌；没有可用令牌时按配置拒绝，默认状态是429而非让该请求等待额度。
- max_tokens配置容量和初始令牌数；tokens_per_fill配置每次补充量；fill_interval配置补充间隔，补充后不超过容量。
- 令牌桶可按Envoy进程或下游连接等范围配置；可选Retry-After仅在指定条件下发出，不是所有429都默认附带。

## R2 · 429 Too Many Requests

- 机构：MDN Web Docs
- 版本：维护文档 · 2026-10-26核验
- 正式原文：<https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429>
- 实读固定正文：<https://github.com/mdn/content/blob/87ca9db1ebe56eb20c1f20b91fca43955d8f0e26/files/en-us/web/http/reference/status/429/index.md>
- 全文SHA-256：`9d00420fcbd41b38a4016031ec5df0c13f8a495295d38b4c0b3487c60c5bbe8b`
- 原题证据：frontmatter title (line 2)
- 引文位置：Opening discussion (line 14)

> Implementations of rate limiting vary; restrictions may be server-wide or per resource.

内部论点对应：

- HTTP429表示客户端在一段时间内发送的请求过多，具体限流条件由服务的规则决定。
- Retry-After响应头是可选的等待信息，不意味着所有429都带该字段；等待后仍需按当时规则判断请求。
- 限流范围可以是整个服务或某项资源，也可基于IP、身份等条件；仅凭系统繁忙文案不能断言HTTP状态或算法。

## 教学与实现边界

- 容量2、每秒补1是教学配置；tokens_per_fill默认1不意味着整个示例是默认配置。
- 缺额拒绝是本片选定的执行模式，不等于所有运行配置必定拒绝或都使用相同全局预算。
- Retry-After不是所有429都默认附带；等待信息不能保证下一次请求成功。
- 令牌桶控制速率与允许突发，不是并发计数器、库存判断或公平保证。
- 原research.md的2026-10-24访问记录保留，本轮没有重写为新访问；网络实现与额外API读取只在内部证据记录。
