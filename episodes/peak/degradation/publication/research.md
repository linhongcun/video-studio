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


## 片尾参考资料

以下两项资料支撑本片减少非核心功能、保留关键业务正确性，以及监控和恢复的边界。技术正文沿用2026-10-24（北京时间）的实际阅读记录；完整原题据本仓已保存的2026-10-22官方读取记录核对。本轮2026-10-26只整理和核对这些固定记录，没有重新读取官网正文或题名；旧文章、研究记录与公开来源全部保留。

旧技术实读记录固定于提交`61d3b984a594578a67bc34aa374cccd0326cd9d6`，Git blob SHA-1 `a960b5156d86af6b0e2b5eceabc5fcee9c31744e`，完整旧研究SHA-256 `d5f76a5edfd0077ff9846954719c773d39ef4112b51c2b01fd88394fc9a71dbf`。固定Git链接标明本仓“既有实读记录”或“既有题名读取归档”，不冒充官网固定响应。22日AWS材料保存的是WebFetch题名和逐字短句记录，并非完整官方HTML；Azure材料是既有页面正文抽取，SHA仅绑定所存文本。完整身份、原读取说明和边界见`docs/reference-endcards/batch-8/sources-degradation.json`。

- [R1] REL05-BP01 Implement graceful degradation to transform applicable hard dependencies into soft dependencies — Amazon Web Services；技术实读2026-10-24，题名归档2026-10-22。支持：依赖异常时仍应维持应用的核心功能，尽量限制局部失败对整体核心业务价值的影响。；本片按业务一致性边界减少搜索红包预估并保留结算核验；降级路径需要预先设计、测试并保持简单。 边界：199元、20元红包和179元结算价均为教学数字，不是网站价格事实或统一降级策略。；保留核心功能不意味着跳过库存、支付等正确性校验；不能把失败假装成功。；不引用性能倍数、永不宕机或任意备用系统都安全的保证。
- [R2] Architecture strategies for self-healing and self-preservation — Microsoft；技术实读2026-10-24，题名归档2026-10-22。支持：通过监控和故障信号识别降级情形，维持关键业务流程，并向用户说明仍可用的功能及发生的变化。；关键依赖不可用时可以采用只读或保存待完成工作等情形；恢复措施取决于工作负载与可靠性目标，不能笼统承诺所有业务自动完成。 边界：根据监控逐步恢复搜索预估是本片的说明性设计；旧研究明确不宣称统一自动恢复算法。；不把未完成支付或失败校验标成业务成功，也不将只读或待完成状态说成所有系统必选方案。；具体自愈、切换和恢复需适合实际系统并经过验证；文档并未证明本例的具体部署或压测结果。

关键校验失败不能当作成功；只读或待完成是说明性选项，不是所有系统统一执行。根据监控逐步恢复搜索预估仍为原研究明确的教学设计，不推导统一自动恢复算法。AWS Builders Library Avoiding fallback in distributed systems仍保留在原研究和文章的公开来源中，属于片外边界；本轮不猜其个人作者，也不加入新的片尾核心清单。候选官方GitHub仓库元数据未能定位可用原文件，未继续网络尝试；本轮没有新的官方题名或技术正文GET。
