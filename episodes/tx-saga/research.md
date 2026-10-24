# Saga 独立短片：权威资料核验

访问日期：2026-10-24（北京时间）。实际阅读公开官方正文；未以旧合集、聊天或搜索摘要作事实来源。本片只讲本地步骤已经提交后，如何用新的业务动作补偿，不在视频内再开编排/协同的比较分支。

## 实际阅读

| ID | 官方正文与阅读位置 | 本片采用的主张和边界 |
|---|---|---|
| R1 | [AWS Saga patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-patterns.html)，本地事务序列、forward/backward recovery、两种实现段落；通过网页工具实际打开 | 业务拆成本地步骤，各步完成后推进；暂时技术故障与业务拒绝需分开处理。视频用明确缺货拒绝触发退款，不把每个超时都当成已确定失败。编排/协同只放文章补充。 |
| R2 | [Azure Saga distributed transactions](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)，Solution、Irreversible local database changes、Potential data anomalies；实际读取其[官方GitHub正文](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/saga-content.md) | 前步骤已经本地提交，不能把失败收尾画成原数据库事务回滚；没有内建全局隔离，中间状态可能对其他操作可见。 |
| R3 | [Azure Compensating Transaction](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)，Solution、Problems and considerations、When to use；网页与[官方GitHub正文](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/compensating-transaction.md)均实际阅读（当前页2026-04更新） | 补偿由业务定义，不能简单覆写旧快照而盖掉并发变化；补偿自身也会失败，需可恢复进度、可安全重复、告警与必要人工处理。不是每个动作都可逆，也不要求补偿抹除发生历史。 |
| R4 | [Azure Retry](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry)，Retry strategies、Idempotency、When to use；实际读[官方GitHub正文](https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/retry-content.md) | 重试适合可重试的临时故障，重复操作必须控制额外效果；长期故障和业务拒绝不能无条件重试。视频用相同退款R8124再次抵达但不再退款。 |

| R5 | [AWS：Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)，Reducing client complexity段落实际打开 | 调用方提供同一操作标识，服务端将标识与业务修改作为原子操作处理；不能一边成功一边丢失。支撑11镜退款去重的本地保存边界。 |

上述均为访问时当前官方正文，未凭页脚推断原始发表年份。本片不依赖早于2020的论文或经验数字；1000/200/800、库存4/3/0均是明示教学数据，不是性能数据或某平台流程。

## 逐镜主张映射

- 01–03：一业务的部分成功、本地步骤先完成，R1/R2；本例规则为扣款和库存都完成才确认订单。
- 04–05：账户与库存各自本地提交，先后不同，不暗示同一毫秒共同可见，R1/R2。
- 06–08：失败分支重置账户1000、库存0；明确缺货拒绝后，不能跨库撤销已提交扣款，R1/R2。
- 09–10：以新退款+200补偿已提交扣款-200；原记录保留，R3。完全退200只是本例业务规则，现实可能有手续费、部分退款或不可退项目。
- 11：相同R8124被识别，已处理记录与退款结果在账户库正确原子衔接，R3/R4/R5；并发重复也要受唯一键/锁或等价条件保护，不能只先查内存。
- 12–13：另起“退款尚未成功”分支，保留800与待完成进度，持续失败告警/人工处理，R3/R4。
- 14：回看已提交阶段，中间状态可见；适用性受业务补偿与等待规则限制，R2/R3。

## 开工独立审阅

独立编辑逐句核对14镜28句后未发现配音阻断项。按反馈将视频导航使用白话“失败怎么收尾”，不提前露出09首次补偿标签；14明确回看已经提交的阶段，避免与12退款失败分支的当前值混淆。此记录只说明稿件审阅，动态预演与最终编码另记。
