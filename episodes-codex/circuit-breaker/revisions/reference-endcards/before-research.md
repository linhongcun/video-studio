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

## 导航重制实际复读（flow-map-20261024 / #199）

2026-10-24 UTC，实际重新下载并阅读MicrosoftDocs官方仓库的[architecture-center/docs/patterns/circuit-breaker.md](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/circuit-breaker.md)，不是用旧稿代替资料。正文`ms.date`为2025-02-05，本次读取Context and problem、Solution与相关considerations；实际获取的正文SHA-256：`29baeab9e19c54c9fdae01dfa4c431bae0c6811e0c5267a1d6c8c78267b8146e`。会话正文副本位于工作盘`/workspace/.video-studio-flow-audit/circuit-breaker-official.md`。

- Closed仍转发调用，并观察近期失败；满足设定窗口/阈值后进入Open。因此无保护基线不能直接称为Closed，另作不连接状态箭头的图外教学对照。
- Open立即返回不可用，不把调用送往该下游；它不表示下游已经修复。
- 等待条件满足后进入Half-Open，仅允许少量请求；探测失败回Open并重新等待，满足恢复条件才回Closed。08失败与09等待后的新一轮探测分开，不把一次失败直接剪成成功。
- 异常如何处置由调用方业务决定，可选运费险不可用不等于跳过必要库存或支付校验；下游本身的恢复仍取决于外部修复。

本次只为原机制增加空间关系与明确状态名，保留原旁白、20句字幕、10镜与2926帧，不新增实现分类或通用阈值承诺。示例3次失败仍明确为教学阈值，真实恢复条件按服务设计。
