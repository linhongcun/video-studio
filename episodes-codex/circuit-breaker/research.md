# EP.13 权威资料核验

实际访问日期：2026-10-24（北京时间）。使用可调用网页读取工具实读正文；只使用官方文档，旧脚本不是出处。

## R1 [Microsoft Azure Architecture Center — Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)

实际读取 Context and problem、Solution、Problems and considerations：等待占用共享资源可能导致级联故障；按近期失败条件暂停调用；暂停时快速返回；少量探测；达恢复条件再恢复，失败则继续暂停。

## R2 [AWS Well-Architected — graceful degradation](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_graceful_degradation.html)

实际读取主功能与软依赖、业务一致性边界；熔断可以配合降级，但不保证修复远端，不应把关键事务跳过后当成功。此文有一处将阻止调用状态称closed，与Azure常见命名相反，视频因此只用正常/暂停/探测，术语定义以R1为准。

## 画面主张核验

|镜头|主张与教学边界|依据|
|---|---|---|
|01|一个服务故障，为什么还能下单？。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|02|下单请求 · 一直等待。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|03|局部等待 · 占满共享资源。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|04|观察失败 · 达到条件。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|05|暂停这条故障调用。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|06|运费险暂不可用 · 仍可提交订单。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|07|等待恢复 · 核心校验继续。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|08|少量探测 · 失败继续暂停。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|09|满足条件 · 恢复调用。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|10|控制故障影响 · 给恢复留时间。数据均为示例，不能推断实际系统统一策略。|R1、R2|
