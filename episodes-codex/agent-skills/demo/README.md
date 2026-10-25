# 一个可复现的小技能包

这是“发现候选→选中正文→读规则→经工具执行脚本→返回证据”的**本地加载与执行示例**，不是模型效果评测。全部契约和客户端数据为合成资料，不连接网络业务服务或生产订单系统。

本目录保留两层证据：`run_demo.py`及`outputs/trace.json`是确定性宿主载荷示例，`llmRequests=0`只指这段脚本没有发起模型请求；另有[agent-review记录](outputs/agent-review.md)及其[JSON证据](outputs/agent-review.json)，来自真实Codex子代理按任务读取候选元数据、所选技能和规则，再通过工具运行两种检查。后者不是完整商业宿主的自动触发测试，也不是另行调用外部模型API的实验，更不证明准确率、成本或性能提升。

从仓库根运行：

```sh
python3 episodes-codex/agent-skills/demo/run_demo.py
```

只运行示例中的主检查：

```sh
cd episodes-codex/agent-skills/demo
python3 skills/api-compat-review/scripts/check_fields.py \
  --before fixtures/before.json \
  --after fixtures/after-required.json \
  --client-request fixtures/old-client-request.json
```

## 输入与两个分支

同一个旧客户端请求只含`sku`和`quantity`。新契约都增加`channel`（来源渠道），但约束不同：

| 新契约 | 真实本地检查结果 | 能下的结论 |
|---|---|---|
| `after-optional.json` | 无新增必填字段，旧请求通过示例校验 | 通过已检查的必填字段规则。 |
| `after-required.json` | 新增必填`channel`，旧请求缺少它 | 该变更会破坏本例旧请求；新增字段不必然兼容。 |

`outputs/review.json`是必填分支的工具输出；`outputs/review-optional.json`保存对照。输出中的“接受/拒绝”仅指这个必填字段校验器，不是实际HTTP响应，更不是全量OpenAPI兼容性结论。检查执行成功返回exit 0，即使发现破坏性变更；输入格式错误才返回exit 2。

## 上下文示意的精确边界

`outputs/trace.json`记录实际文件身份、脚本命令及结果，并构造四阶段的**示意宿主输入载荷**。阶段包含候选名称与描述、选中技能正文、相关参考规则、脚本返回结果。脚本源码不加入这个载荷，未选中发布说明技能的正文也不加入。建立目录索引时宿主实际读了两个SKILL.md文件；“模型未看到正文”不等于底层文件从未被读取。

技能选择在本例中由演示宿主显式指定，没有声称模型自动触发成功。字节数按真实UTF-8文件测量，仅描述这份示例载荷，不能换算成token、价格、准确率或普遍节省比例。常驻对照是人为选择的“两个方法都预先粘贴”配置，并非所有Prompt用法都如此。

本次启动阶段的候选元数据载荷为555字节，指定常驻方法包为3025字节；两者不是全任务费用对比。加入同一份596字节主检查结果后，渐进路径累计新增3649字节，常驻路径为3621字节。这个只有两个短技能的小例子里，索引与重复元数据带来28字节额外开销，**没有得到总字节节省**。保留这一结果，不通过拉长无关说明制造收益；渐进加载的设计价值与实际收益需要分开解释。

读取资料和运行脚本是两种动作：前者把文本加入载荷；后者由宿主工具运行，结果再加入载荷。SKILL.md本身不成为可自动执行的程序，不修改模型权重，也不获得额外权限。已加载内容何时保留/压缩取决于宿主，本例不表现任务结束自动清空。

## 文件结构

```text
skills/api-compat-review/
  SKILL.md
  references/request-fields.md
  scripts/check_fields.py
skills/release-notes/SKILL.md   # 发现阶段的无关候选
fixtures/                     # 旧/新契约与旧请求
outputs/                      # 实际运行结果与加载示意证据
```

Agent Skills格式和渐进加载机制参考[官方规范](https://agentskills.io/specification)；原始工程文章中脚本可通过工具执行、只回传结果的例子见[Equipping agents for the real world with Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills)。官方事实由本期调研另行核验；本目录只证明当前小例子的实际行为。
