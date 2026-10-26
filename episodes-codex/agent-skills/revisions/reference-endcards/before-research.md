# Agent Skills：本期资料与主张核验

访问日期均为 **2026-10-25（北京时间）**。本期只用第一方公开规范、客户端文档与原始工程文章；文档支持技术事实，不证明热度排名、本片教学效果或“有Skill必然比无Skill更准确”。

核心命题：**SKILL.md没有变成自动执行的程序。Skill将可复用工作方法及其资源打包，宿主让模型发现并按需加载，具体动作再交给工具。** 影片沿同一份API请求兼容审查推进，比较信息组织与加载路径；不伪造两组模型表现。

## S01 Agent Skills格式规范

- 来源：[Specification](https://agentskills.io/specification)。页面未标发布日期；动态规范，访问基线如上。
- 已读范围：目录结构、frontmatter、正文、可选资源与progressive disclosure。
- 支持主张：技能以目录为单位，至少有`SKILL.md`；标准要求`name`和`description`，脚本、参考资料和资产可选。元数据用于发现，正文在激活时交入上下文，资源按需使用。
- 短引：`Required: metadata + instructions`。
- 用在：正文的技能包展开及目录→指令→资源过程；必填字段/推荐长度细节只留文章。
- 边界：约5000 tokens、500行属于编写建议，不是宿主统一硬上限；`allowed-tools`仍标实验性，支持依实现。格式相同不保证触发、依赖、权限或运行结果相同。

## S02 客户端怎样实现技能支持

- 来源：[How to add skills support to your agent](https://agentskills.io/client-implementation/adding-skills-support)。页面未标发布日期；原`/integrate-skills`现跳转至此。
- 已读范围：三层加载、目录生成、模型/用户激活、资源列举及会话保留。
- 支持主张：宿主可以扫描文件，也可用API或注册表发现；将候选名称、描述及访问位置交给模型。激活可通过普通文件读取或专用工具，用户显式选择也可由宿主注入。资源列表不等于资源正文已全部加载。
- 短引：`The model sees the catalog from the start`。
- 用在：发现阶段与宿主/模型的职责；本片不限定所有产品必须提供同一条斜杠命令。
- 边界：模型自动选择是常见方式，不是本期demo已经实测的能力；“没有交给模型全文”也不等于宿主从未读取底层文件。已加载内容需要会话管理、去重和压缩策略，不应表现为任务结束自动清空。

## S03 当前概述与设计意图

- 来源：[Agent Skills Overview](https://agentskills.io/home)。页面未标发布日期；`/what-are-skills`现跳转至此。
- 支持主张：Skill打包程序性知识、团队约定和专用资源，便于复用、版本管理及按需使用；发现、激活、执行是不同阶段。
- 短引：`portable, version-controlled folders`。
- 用在：为什么不一直复制整段工作说明，以及片尾回答“技能究竟增加了什么”。
- 边界：这是标准的设计意图，不是对任意宿主或任意技能效果的保证。它不改模型权重，不能从技能文件数推断模型能力提升。

## S04 Claude Code：产品行为与生命周期

- 来源：[Extend Claude with skills](https://code.claude.com/docs/en/skills)，重点为[Skill content lifecycle](https://code.claude.com/docs/en/skills#skill-content-lifecycle)。页面未标统一发布日期；动态产品文档。
- 已读范围：普通会话的description/body加载、调用控制、标准与扩展、上下文保留、工具预授权和触发评估。
- 支持主张：该产品将技能作为提示指导；与常驻CLAUDE.md相比，正文在使用时加载。已加载正文作为会话消息跨轮保留，压缩时按预算续带。工具执行和模型遵循不是仅凭文件格式自动保证的。
- 短引：`stays there across later turns`。
- 用在：脚本工具路径与保留边界；具体配置只进文章。
- 边界：Claude Code允许部分frontmatter省略，不能覆盖S01标准的必填要求；`disable-model-invocation`、fork等为产品特性。其`allowed-tools`是当轮预授权，非封闭工具白名单，不表示Skill能自行授予任意能力；标准和其他宿主的同名字段不可混讲。

## S05 原始工程文章：参考文本与脚本是两条路径

- 来源：[Equipping agents for the real world with Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills)。原发布日期 **2025-10-16**，页面另有2025-12-18开放标准更新。
- 已读范围：技能结构、PDF案例、上下文过程、代码执行及先评估再补技能的建议。
- 支持主张：详细参考材料可以在需要时读取；配套脚本可以直接经工具执行，不必先把脚本源码或待处理文件全文塞进模型，必要结果再回传。
- 短引：`Skills can also include code`。
- 用在：本片核心分流：`references → 按需读入上下文`；`scripts → 工具执行 → 结果回到上下文`。
- 边界：旧文解释稳定设计，不作为当前SDK接口说明。确定性程序执行不等于程序正确、输入覆盖充分或完整业务兼容；本片自制检查器仅覆盖明确的必填规则。

## S06 Skills over MCP：获取不是自动激活

- 来源：[Skills extension overview](https://modelcontextprotocol.io/extensions/skills/overview)。动态官方扩展文档；页面标注SEP-2640为Final，示例适用MCP **2026-07-28或以后**。
- 支持主张：MCP服务器可暴露技能元数据、说明与资源；该扩展规定发现和获取。宿主决定怎样向模型/用户呈现并走技能加载路径，直接读到`SKILL.md`不自动构成激活。
- 短引：`This extension defines discovery and retrieval over MCP`。
- 用在：仅文章补充，防止将“Skill给方法、MCP只给工具”当绝对二分。
- 边界：SDK/宿主支持仍需逐一核验；完整性、内容信任、加载与执行不能混成一个保证。本片没有演示MCP宿主兼容性。

## S07 开放治理的近期变化

- 来源：[Donating Agent Skills to the Agentic AI Foundation](https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation)。发布日期 **2026-10-22**。
- 支持主张：Anthropic宣布将Agent Skills标准及名称/标识、GitHub组织、域名等捐赠给AAIF。
- 用在：仅文章背景，不进入视频机制主线。
- 边界：公告中的平台数、发布量和安装量为厂商报告，不用于本片量化效果、普遍兼容性或最热门排名。

## S08 MCP工作组确认扩展状态

- 来源：[Skills Over MCP Charter](https://modelcontextprotocol.io/community/working-groups/skills-over-mcp)。动态工作组记录；完成里程碑写明SEP-2640于 **2026-09-13**合并并Final。
- 支持主张：Skills over MCP已经发布，不只是路线图计划；当前工作仍包括实现支持与互操作。
- 短引：`Client implementation mandates`列在范围之外。
- 用在：文章核对S06的交付状态与宿主边界。
- 边界：扩展正式发布不等于每个SDK或客户端均已实现；不把工作组意图写成全部宿主的统一行为。

## 本期自制示例的证据边界

公开资料支持上方机制；以下路径属于本项目示例，不作外部引用或行业效果依据。已只读核对当前文件，未由本调研代理重跑或修改demo。

- 同一份合成旧请求省略`channel`；`after-optional.json`与`after-required.json`分别检查可选/必填变化。所谓接受/拒绝来自本地必填字段校验器，不是实际HTTP服务响应。
- 技能入口：`demo/skills/api-compat-review/SKILL.md`；参考规则：`references/request-fields.md`；执行脚本：`scripts/check_fields.py`（二者路径均相对该技能目录）。
- 运行脚本需要旧契约、新契约、旧请求三个输入。结论覆盖必填变化，不涵盖所有类型/枚举、响应、认证、默认值或实际服务行为；“可选字段分支通过”只能称通过已检查规则。
- `demo/outputs/trace.json`明确无LLM请求、由演示宿主显式选择。四阶段输入载荷是机制示意，实际文件I/O、命令和检查结果可复核；不声称测到了模型自动触发、token成本或准确率。
- 建立目录索引时宿主读过两个`SKILL.md`；模型侧示意载荷初始只含名称/描述。未选中`release-notes`正文和脚本源码没有加入该载荷，不能说底层文件从未被读取。
- 常驻对照是人为选定“两个工作方法预先粘贴”的配置，不代表所有Prompt用法；同样资料也能直接写入Prompt，Skill的区别在组织、发现、复用和按需供给。

## 技术审稿检查点

- 不把Skill描述成训练、插件二进制或自动执行程序。
- 不把目录/资源存在、实际读入模型、经工具执行、任务正确完成混为一步。
- 图中区分参考文本进入上下文与脚本执行后结果回流；脚本可被读取，但不是必须先全文载入。
- 不预设所有技能默认可自动触发，不把演示显式选择写成真实模型选择实测。
- 不表现任务一结束所有内容自动卸载，不把宿主特有权限/语法推广成标准。
- 不用“加字段一定兼容”、单一旧请求通过或一次脚本退出0证明完整兼容。

## 文稿技术复审

调研代理只读审查了`script.md`、`plan.json`和`visual-direction.md`，并与当前demo路径、输入和输出逐项对照。初审提出：两种配置不能画成同会话自动卸载；候选数应与两项实际示例一致；脚本执行应包含旧契约、新契约和旧请求三个输入。

编辑修正后，锁定脚本SHA-256为`915c23f9445eeaf615d2b9b471134a4f6ad3ffa934e410709b444c8607c41eac`，上述三项技术问题已落实。正文还明确目录索引有开销、小技能包未必更省，未使用编造的token/价格/准确率收益，宿主保留/压缩与审查正确性分别说明。**本轮技术主张复审通过**；这不是动画实际实现、成片表达、模型自动触发实验或用户观看效果已经通过。视觉实现仍需核对03的配置切换、07读取、08执行与结果回流以及11不自动清空。
