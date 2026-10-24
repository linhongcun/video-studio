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
