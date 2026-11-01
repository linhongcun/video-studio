# EP.12 权威资料核验

实际访问日期：2026-10-24（北京时间）。使用可调用网页读取工具实读正文；只使用官方文档，旧脚本不是出处。

## R1 [AWS Builders Library — Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

已实际读取正文 Retrying and side effects、Reducing client complexity、Retries and semantic equivalence：没有回应时结果未知；用调用者提供的请求标识表达同一意图；记录编号与业务变更须原子一致；同编号重放应提供语义相同的结果。

## R2 [Stripe API — Idempotent requests](https://docs.stripe.com/api/idempotent_requests)

已实际读取 API v1 与 v2 的区别、参数比较和保留期。片中讲教学设计，不承诺所有接口永久记住编号；v1 的同键响应重放和 v2 重试恢复的具体差异仅作文章边界，不泛化。

## 画面主张核验

|镜头|主张与教学边界|依据|
|---|---|---|
|01|为什么只扣一次？。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|02|一笔支付 · 同一个编号。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|03|没收到结果 ≠ 没有扣款。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|04|第二次仍是 7042。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|05|扣款与记录 · 一起确认。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|06|命中结果 · 不再扣款。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|07|请求多次 · 效果一次。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|08|并发到达，也只处理一份。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|09|不同支付 · 不同编号。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|10|同一次支付 · 同一个结果。数据均为示例，不能推断实际系统统一策略。|R1、R2|


## 片尾参考资料

2026-10-26整理为`title-author`模式，2项1页5秒，片尾只显示原题与明确作者/机构。两项技术正文阅读仍是2026-10-24，不因本次整理改写日期。

- **[R1] Making retries safe with idempotent APIs** — Malcolm Featonby；Amazon Web Services；The Amazon Builders' Library · 未标可核验的独立发布日期。正式链接：[https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。定位：Retrying and side effects；Reducing client complexity；Retries and semantic equivalence。26日真实TinyFish正式页面提取仅补核H1（解码text第7行）和By Malcolm Featonby（第13行及About the author），未打开PDF；顶层HTML/OG标题占位值不作为原题。完整提取JSON已归档，但其SHA是保存的结构化提取字节身份，不是HTTP/PDF原响应或24日页面SHA。
- **[R2] Idempotent requests** — Stripe；Stripe API Reference · API v1/v2边界 · 原实读未绑定特定接口版本。正式链接：[https://docs.stripe.com/api/idempotent_requests](https://docs.stripe.com/api/idempotent_requests)。定位：Idempotent requests：API v1与v2；参数比较；保留期；并发冲突。本轮只本地复用基线已跟踪的26日TinyFish正式提取与H1，没有新Stripe请求；保留24日技术实读与26日既有文章来源证据的不同身份。

旧完整研究和新/旧元数据提取、Git/blob/完整SHA见[本轮来源记录](../../docs/archive/2026-10/reference-endcards-batch-12/sources-idempotency.json)及同前缀证据。新增AWS题名署名补核不替换旧技术日期；旧Stripe提取既有获取时间不改。编号与业务原子一致、语义相同结果、同额新交易用新编号及参数/调用者/并发/保留期边界保持；未改旧SB、words、音轨、教学例子或媒体，未新增程序/服务端实现或性能测量。
