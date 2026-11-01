# 片尾参考资料 · 幂等性

视频片尾仅显示原始题名与作者或机构；完整出处、阅读日期和支持边界如下。技术依据沿用2026-10-24的实际正文阅读，不把此次整理或题名署名补核写成新的技术阅读。

**[R1] Making retries safe with idempotent APIs**

- 作者：Malcolm Featonby；机构：Amazon Web Services。
- 年份或版本：The Amazon Builders' Library · 未标可核验的独立发布日期。26日网页OG更新时间是站点元数据，不据此推断文章首次发表日。
- 正式出处：[The Amazon Builders' Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。
- 定位：Retrying and side effects；Reducing client complexity；Retries and semantic equivalence。
- 技术阅读：2026-10-24，本期原研究已记录上述章节的实际阅读。2026-10-26另通过TinyFish取得正式页面提取，只补核正文H1与“By Malcolm Featonby”明确署名；工具返回的标题元数据为占位值，未用它代替实际原题。
- 编者说明：支持响应丢失后结果未知、用调用者请求标识表达同一意图、将编号登记与业务变更原子保存，以及语义相同的重试结果。30元、余额100到70、7042均为本片教学设定；不据此宣称AWS采用同一支付实现。
- 原实读身份：[固定旧研究记录](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/idempotency/research.md#L5)。新署名证据保留完整工具结构化提取与SHA，属于26日题名/署名补核，不冒称原HTTP响应或PDF原字节，也没有把它追记成24日原页SHA。

**[R2] Idempotent requests**

- 机构：Stripe；已保存文档未建立明确个人署名，不推定作者。
- 年份或版本：Stripe API Reference · API v1/v2边界 · 原实读未绑定特定接口版本；未标独立发表日期。
- 正式出处：[Stripe API Reference](https://docs.stripe.com/api/idempotent_requests)。
- 定位：Idempotent requests：API v1与v2；参数比较；保留期；并发冲突。
- 技术阅读：2026-10-24。本轮没有重新GET Stripe，仅复用基线已保存的26日正式页面题名与原文提取；其原始获取时间保持，不把提取记录SHA冒称24日官方响应SHA。
- 编者说明：支持客户端幂等键、参数校验、保留期和并发冲突边界；v1保存首个执行结果与v2重试恢复的行为有区别，不能推广为所有接口永久返回逐字节相同的报文。
- 原实读身份：[固定旧研究记录](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes-codex/idempotency/research.md#L9)；26日既有页面提取见[固定公开证据](https://github.com/linhongcun/video-studio/blob/f3610e244f9e23e7a9075e406bbc990ba53b7699/episodes/idempotency/article/source-evidence.json)。

本次只追加资料名单及完整出处。前文关于“同一次支付”的编号语义、并发认领、业务效果和响应契约的区分不变，原图文和制作声画不在本次来源修改范围。
