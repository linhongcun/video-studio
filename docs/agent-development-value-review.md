# Agent 系列：内容价值复盘与概念选题重排

2026-10-25（北京时间）。用户观看A02/v0.59.0后认为“看完好像跟没看一样”“没什么营养”，随后明确提出以Skill、MCP、Subagent、Goal等AI领域概念为入口，关闭过浅选题。Goal已确认指**目标驱动的Agent**。

**当前方向是概念背后的机制、设计意图和取舍。此前六个API/工单开发单元是未实施的编辑草案，现已撤回，不再作为制作主线。** 用户确定的是方向与撤题授权；下列具体命题及研究优先级是编辑建议，尚未开拍，也没有观看效果结论。

## 问题不是少演示了几行代码

目标观众会基本编程、接口和JSON。A01已讲过模型选择、程序核对权限和执行、结果回传，A02约110秒又以同一关系收尾，独立信息增量不足。退款咨询场景让用户认出功能，不能自动使这个知识点值得独占一期。

A02还有实战证据的限制：本地HTTP与应用分发真实运行，模型请求和最终答复则是固定fixture，不能证明真实模型怎样选工具、提参数及继续运行。这一事实继续保留，但补上真实模型和更多接线也不必然解决选题过浅。把反馈理解成“下一次展示完整SDK调用”仍会偏离用户希望理解新概念的需求。

此前动态阶段、编码帧和上线检查是技术及可读性证据，不能充当用户认可或课程价值证据。旧媒体、冻结输入、发布记录均不改写；此次没有新模型实验、TTS、渲染或媒体部署。

## 当前选题标准

1. 以正式概念名作为入口，开头立即给出它要解释的具体矛盾，保留用户已要求的清晰主线与适合的交互场景。
2. 讲清四件事：为什么出现、机制怎样运作、与最近似方案差在哪、付出什么代价或在哪失效。定义不能代替机制，热门名词不能代替信息增量。
3. 围绕一个有解释力的对照推进因果。图解、交互、协议片段、源码或实验按论证需要选择；不强制每集写程序，也不以编码流程撑时长。
4. 概念理解与开发判断都是观看收益。去掉标题后仍只是接API、字段校验、查日志或重复旧流程的，合并或撤题。
5. 官方资料核对事实，内容审读检查独立增量，媒体检查核对表达；三者分别验收。涉及性能、可靠性或具体API行为的结论按所选版本实际验证，示意和实测分开。

这些是针对本轮反馈的编辑调整，尚非已证明成功的制作方法。资料存在也不证明它们在所有技术中热度最高。

## 优先研究的四个命题

| 概念与跟踪 | 要解开的问题 | 必须超越的浅层讲法 |
|---|---|---|
| [Agent Skills #139](https://github.com/linhongcun/video-studio/issues/139) | 一个Markdown文件为何能成为技能？ | 不只教新建SKILL.md；解释发现与路由、渐进加载、资料/脚本，以及Prompt、工具和宿主执行责任。 |
| [MCP #138](https://github.com/linhongcun/video-studio/issues/138) | 已有HTTP API和Function Calling，MCP统一哪层契约？ | 不只演示安装Server；解释Host/Client/Server、能力发现、互操作、业务授权及适配成本。 |
| [Subagent #146](https://github.com/linhongcun/video-studio/issues/146) | 拆出独立上下文，何时比一个Agent更有效？ | 不只让多个角色聊天；讲委派、上下文继承/隔离、结果归并、额外调用和共享环境冲突。 |
| [Goal #248](https://github.com/linhongcun/video-studio/issues/248) | 给AI一个目标，谁凭什么判定真的完成？ | 不只展示while循环；区分目标、约束、计划、环境反馈、评估证据和停止语义。 |

建议先研究Skills，再看MCP、Subagent、Goal；不是用户逐项批准的拍摄顺序。每项先确认对照能讲出机制，必要时继续缩范围或合并。Goal不是与MCP同类的统一协议，Claude Code `/goal`只是当前可核验的产品实例。

后续研究Harness与Context Engineering。Memory、Durable Execution、Prompt Injection、Evals、Compaction继续留在研究池；其中Memory不能停在偏好CRUD，Harness不能停在读改测，Durable Execution需证明相对现有幂等/事务系列的增量，Compaction需避免重复上下文与记忆片。保留研究机会不等于承诺每项独立成片。

## 已执行的题库处理

总览[#130](https://github.com/linhongcun/video-studio/issues/130)。原20项中，1项保留完成历史、9项撤题、10项实质重构；另建Goal #248，当前共11项开放研究候选。旧A/B编号只用于追踪，不再是课程依赖链。

| 处理 | Issue | 原因与去向 |
|---|---|---|
| 历史保留 | #131 A01 | 已上线完成状态保留，不把它当作本轮新增基础课。 |
| `not_planned`关闭 | #132 A02、#133 A03、#134 A04 | 重复执行边界、JSON/Schema接续、最小循环退出独立制作。A02 V1上线和负面反馈保留，关闭表示取消后续基础重制计划，绝非改进已完成。 |
| `not_planned`关闭 | #136 A06、#141 A11、#143 A13、#145 A15 | 基础RAG、审批流程、日志排查和省钱技巧按需并入上下文、信任边界、Evals或Harness，不否定这些领域整体的研究价值。 |
| `not_planned`关闭 | #148 B02、#150 B04 | MCP/Skills重复对比合入两支主片；工单综合实战随旧主线撤回。Skills over MCP的扩展机制与兼容边界保留。 |
| 重写并开放 | #135、#137、#138、#139、#140、#142、#144、#146、#147、#149 | 当前问题、机制、对照、边界与验收已重写，旧方案折叠保存并明确失效。 |
| 新建并开放 | #248 Goal | 新命题另建，避免把#134最小循环改名当作升级。 |

## 本轮联网核验与适用边界

访问日期均为2026-10-25（北京时间）。第一方来源支持下列技术事实，具体宿主/接口及版本在开拍时重验。

- [Agent Skills Specification](https://agentskills.io/specification)：技能元数据、指令正文和配套资源的渐进加载结构；格式兼容不保证触发、执行权限或行为可靠。
- [MCP 2026-07-28规范](https://modelcontextprotocol.io/specification/2026-07-28)及[架构](https://modelcontextprotocol.io/specification/2026-07-28/architecture)：当前核心采用无状态、自包含请求和逐请求能力协商，不沿用旧版初始化/会话必需流程。协议核心、传输、扩展与业务状态分开解释。
- [Skills over MCP](https://modelcontextprotocol.io/extensions/skills/overview)及[官方工作组状态](https://modelcontextprotocol.io/community/working-groups/skills-over-mcp)：SEP-2640已于2026-09-13合并并Final，可通过MCP发现/读取Skills，SDK和宿主支持需分别核验。不能绝对二分“Skills只教方法、MCP只给工具”；发现、获取、激活与执行不是同一步。
- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents)：普通子代理、fork的上下文继承及工具权限存在差别；文件/worktree隔离需另行配置。上下文独立不自动意味着执行环境隔离，不泛化为所有产品行为。
- [Claude Code Goal](https://code.claude.com/docs/en/goal)：每轮完成后由另一个模型判断条件；评估者只看对话已呈现的证据，不独立读文件或跑命令。它与定时`/loop`、Stop hook的触发/停止语义不同，也不改变权限模式。模型判成功仍须有可核验事实支撑。
- [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)，2025-09-29；[Scaling Managed Agents](https://www.anthropic.com/research/managed-agents)，2026-04-08：分别支持输入选择/生命周期，以及会话、Harness、执行环境分离的设计讨论；不照搬旧模型效果和厂商架构为普遍保证。
- [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)，2026-01-09：轨迹、评分与最终环境结果分开。另核对[OpenAI Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)的退役公告，独立Evals平台2026-10-31转只读、2026-11-30关闭，研究评估方法不绑定即将退役API。

## 变更范围与同步

本轮基于原策划分支先整合主干`00635e6`，再整合`7cc6f3a`，保留P02四人过桥、脚注修复及LeetCode推导修订。主干已使用L038和L039，本轮Agent价值教训最终顺延为L040。同步[选题总表](agent-development-topics.md)、教训、制作记忆、旧经验适用边界及现有策划PR #244。此前“六个优先开发单元”“MCP/Skills暂缓”“不取消原issue”等说法均已被本轮决定取代。

尚未制作或发布新视频，A01/A02原媒体和历史QA不变。后续由实际内容审读检验这些命题的信息增量，再按现行制作闸门推进。
