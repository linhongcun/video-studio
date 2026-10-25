# circuit-breaker · 参考资料

实际完整GET与原文核验：2026-10-26（北京时间）。两项官方原文采用固定提交。完整响应SHA、题名与逐论点原文见[来源证据](../../docs/reference-endcards/batch-4/sources-circuit-breaker.json)。作者自检不代替独立QA、实际编码卡片或浏览器检查。

**[R1] Circuit Breaker Pattern**

Microsoft · Azure Architecture Center · 2026-10-26核验

- 正式文档：<https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker>
- 实读固定原文：<https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/circuit-breaker.md>
- 题名位置：frontmatter title · line 2
- 全文SHA-256：`29baeab9e19c54c9fdae01dfa4c431bae0c6811e0c5267a1d6c8c78267b8146e`

> A limited number of requests from the application are allowed to pass through and invoke the operation.

原文位置：Solution / Half-Open · line 45。

内部论点对应（编者说明，不是原文引句）：

- 等待下游响应的请求可占住共享资源并造成级联影响；熔断观察近期失败，达到配置条件后暂停可能失败的调用。
- Closed放行并统计近期失败；Open快速返回；Half-Open仅允许少量试探，失败继续暂停、达到成功条件后恢复。
- 熔断参数要匹配服务恢复能力，业务自行处理不可用；系统恢复仍依赖外部修复，不保证网站永不故障。

**[R2] Retry pattern**

Microsoft · Azure Architecture Center · 2026-10-26核验

- 正式文档：<https://learn.microsoft.com/en-us/azure/architecture/patterns/retry>
- 实读固定原文：<https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/retry-content.md>
- 题名位置：retry.yml / metadata.title · line 3
- 全文SHA-256：`619b34a5b1eaf6508715080192feb9fcd85447d402f29816e9f3ffaf294f91a8`
- 固定页面信息：<https://github.com/MicrosoftDocs/architecture-center/blob/b60c2b4526bab9b5e77cba2d779e695ed9d6ab9a/docs/patterns/retry.yml>

> For some noncritical operations, it's better to fail fast rather than retry several times and affect the throughput of the application.

原文位置：Issues and considerations / Impact on performance · line 44。

内部论点对应（编者说明，不是原文引句）：

- 非关键操作可选择快速失败并给出合适反馈，避免反复重试牺牲应用吞吐或加重繁忙下游。
- 持续失败时可停止继续访问，等待后少量试探；故障性质、业务要求和实际测试决定策略。
- 重试事务操作要考虑一致性和副作用；运费险教学示例不表示可以跳过库存、支付等必要业务校验。

## 使用边界

本轮片尾R1/R2是精选清单；原研究中R2的AWS资料与历史访问记录保持原意，不改称本轮新读。源文档题名字段与H1差异、canonical网络结果仅记于内部来源证据。

片中阈值、处理位、等待时间与探测量均为教学示例。保护调用、业务降级与下游修复分开；不能据此保证订单总会成功或网站永不故障。
