# degradation 片尾参考资料

以下两项资料支撑本片减少非核心功能、保留关键业务正确性，以及监控和恢复的边界。技术正文沿用2026-10-24（北京时间）的实际阅读记录；完整原题据本仓已保存的2026-10-22官方读取记录核对。本轮2026-10-26只整理和核对这些固定记录，没有重新读取官网正文或题名；旧文章、研究记录与公开来源全部保留。

`title-author`：2项1页、5秒，画面只显示完整原题与机构，日期、定位、链接和边界留在文章或内部记录。

**[R1] REL05-BP01 Implement graceful degradation to transform applicable hard dependencies into soft dependencies**

Amazon Web Services · AWS Well-Architected Framework · REL05-BP01：[官方资料](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_graceful_degradation.html)；[既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/degradation/research.md#L5)；[既有题名读取归档（2026-10-22）](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes/_shared/storyboard/examples/degradation/sources/src/aws-gd.txt)。

支持范围：依赖异常时仍应维持应用的核心功能，尽量限制局部失败对整体核心业务价值的影响。；本片按业务一致性边界减少搜索红包预估并保留结算核验；降级路径需要预先设计、测试并保持简单。

边界：199元、20元红包和179元结算价均为教学数字，不是网站价格事实或统一降级策略。；保留核心功能不意味着跳过库存、支付等正确性校验；不能把失败假装成功。；不引用性能倍数、永不宕机或任意备用系统都安全的保证。

内部定位：主功能保持；减少非核心依赖；业务一致性；降级路径测试和简化（2026-10-24既有实读）

**[R2] Architecture strategies for self-healing and self-preservation**

Microsoft · Microsoft Azure Well-Architected Framework：[官方资料](https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation)；[既有技术实读记录（2026-10-24）](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes-codex/degradation/research.md#L9)；[既有题名读取归档（2026-10-22）](https://github.com/linhongcun/video-studio/blob/61d3b984a594578a67bc34aa374cccd0326cd9d6/episodes/_shared/storyboard/examples/degradation/sources/src/azure-self.txt)。

支持范围：通过监控和故障信号识别降级情形，维持关键业务流程，并向用户说明仍可用的功能及发生的变化。；关键依赖不可用时可以采用只读或保存待完成工作等情形；恢复措施取决于工作负载与可靠性目标，不能笼统承诺所有业务自动完成。

边界：根据监控逐步恢复搜索预估是本片的说明性设计；旧研究明确不宣称统一自动恢复算法。；不把未完成支付或失败校验标成业务成功，也不将只读或待完成状态说成所有系统必选方案。；具体自愈、切换和恢复需适合实际系统并经过验证；文档并未证明本例的具体部署或压测结果。

内部定位：Implement a graceful degradation mode；故障信号；关键流程；用户功能变化提示（2026-10-24既有实读）

内部证据：`docs/reference-endcards/batch-8/sources-degradation.json`。源归档完整SHA绑定所存记录，不是当前HTTP响应SHA；22日标题/24日技术阅读/26日整理分开。
