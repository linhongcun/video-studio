# EP.14 权威资料核验

实际访问日期：2026-10-24（北京时间）。使用可调用网页读取工具实读正文；只使用官方文档，旧脚本不是出处。

## R1 [AWS Well-Architected — graceful degradation](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_graceful_degradation.html)

实际读取主功能保持、减少非核心依赖、业务一致性、降级路径必须测试和简化；商品/价格/红包数字都是教学设计，不是网站真实性能或价格行为数据。

## R2 [Microsoft Well-Architected — self-healing and self-preservation](https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation)

实际读取 Implement a graceful degradation mode：检测故障信号、维持关键流程、告诉用户功能改变。监控与恢复为本片教学设计，不宣称统一自动恢复算法。

## R3 [AWS Builders Library — Avoiding fallback in distributed systems](https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/)

实际读取Distributed fallback：备用路径可能难测、增加依赖压力甚至扩大故障。片外说明降级不是任意换一个更脆弱的备用系统，且不能保证系统永远不崩。

## 画面主张核验

|镜头|主张与教学边界|依据|
|---|---|---|
|01|同一商品 · 为什么差 20 元？。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|02|标价 199 − 红包 20 = 179。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|03|搜索预估也要计算。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|04|搜索少算一步 · 结算继续算。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|05|减少部分功能 · 保住关键服务。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|06|搜索 199 元 · 优惠以结算为准。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|07|结算核验红包 · 确认 179 元。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|08|把资源留给结算与下单。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|09|不能把校验失败当成功。数据均为示例，不能推断实际系统统一策略。|R1、R2|
|10|监控恢复 · 逐步恢复功能。数据均为示例，不能推断实际系统统一策略。|R1、R2|
