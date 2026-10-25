# A02 资料核验：AI 说要调用工具，到底是谁在执行？

访问日期：**2026-10-25（Asia/Shanghai，北京时间）**。本期开工重新通过联网工具读取下列官方正文，并通过 GitHub 原始文件核对协议字段；没有把 A01 的旧稿或聊天记忆当成引用。动态页面没有可确认的发布日期时不推定发布日期。

本期范围是 **应用自己实现的只读函数工具**。只追踪合成订单8124的查询：模型侧调用请求 → 应用检查 → HTTP读取 → 输出交回模型侧 → 用户答复。不会演示退款，也不会把本地测试伪称真实模型推理或电商服务。

## 核心资料与支持范围

### S01 OpenAI：Function calling

- [官方指南](https://developers.openai.com/api/docs/guides/function-calling)，动态文档，未标固定发布日期；实际读取 How it works、The tool calling flow、Defining functions、Formatting results、Strict mode 与 Python Responses 示例。
- 支持主张：工具定义描述可用能力和参数；模型先返回调用请求，应用执行后回传工具输出，再请求模型继续；返回结果关联原调用。
- 本期接口固定为 **Responses API 的 function tools**。`function_call`、`arguments`、`call_id` 和 `function_call_output` 是这套接口的字段，不能原样混到 Chat Completions 或 Agents API。
- `strict: true`约束参数形状；它不等于业务授权。片中不以“严格schema仍随机缺字段”制造失败，失败来自应用明确拒绝读取权限。
- 推理模型的返回项可能还有 reasoning；实际接真实API时须按指南保留完整上下文。本地fixture只包含一个函数调用项，不声称涵盖所有响应类型。

### S02 OpenAI Python SDK：固定字段契约

官方仓库 [openai/openai-python](https://github.com/openai/openai-python)，核验提交 **718aee979a9c334d37302aeff21cee6cbff4d43c**，`_version.py` 为 **3.37.0**。

| 文件 | 本期核对内容 | 完整SHA-256 |
|---|---|---|
| [function_tool_param.py](https://github.com/openai/openai-python/blob/718aee979a9c334d37302aeff21cee6cbff4d43c/src/openai/types/responses/function_tool_param.py) | function定义的name、parameters、strict等字段 | `0203429340e2b601ebb8d0f0620bdeb7223e808a259ca403c91b9f5fd6cc2b86` |
| [response_function_tool_call.py](https://github.com/openai/openai-python/blob/718aee979a9c334d37302aeff21cee6cbff4d43c/src/openai/types/responses/response_function_tool_call.py) | 请求的type、name、JSON字符串arguments及call_id | `b7e6a86f691f18b0539b8d1c08c16386ef202836b692ef16c7f867249f349891` |
| [response_input_param.py](https://github.com/openai/openai-python/blob/718aee979a9c334d37302aeff21cee6cbff4d43c/src/openai/types/responses/response_input_param.py) | 回传项function_call_output及call_id/output | `4160fb61307b6b2680bf04ea49194a3d5c0dd05ab1de4f02545f1f80f8b973ff` |
| [_version.py](https://github.com/openai/openai-python/blob/718aee979a9c334d37302aeff21cee6cbff4d43c/src/openai/_version.py) | 参考版本3.37.0 | `79285c9c3bc4d27b0184b8924f418c3b312ee02c321d748c07a88c0affd9e8c9` |

这是协议来源核对。**本地演示没有安装或调用该SDK**，不能把3.37.0写成已执行的SDK版本；演示真实运行环境为Python3.12.14标准库，详见[锁定记录](demo/protocol-lock.json)。未向真实OpenAI API验证schema接受情况。

### S03 OpenAI Agents SDK：Tools

- [官方Tools页](https://openai.github.io/openai-agents-python/tools/)，动态文档；实际读取 Hosted tools、Local runtime tools、Function tools、Conditional tool enabling。
- [固定源文件](https://github.com/openai/openai-agents-python/blob/0dc4cf152bff1f50bdc0e41f28808563406545b2/docs/tools.md)，提交 `0dc4cf152bff1f50bdc0e41f28808563406545b2`，完整SHA-256为`762d91079338475d3935af8e36ca8a958a6f476ac1b0ecfb81536a573c6cdbeb`。
- 支持主张：执行环境有本地和托管之分；模型侧请求与环境实际执行分开。按工具参数、资源决定的权限仍由实现核验，开关可见性不能代替授权。
- 适用边界：本期手工分发自定义函数，不使用Agents SDK；平台托管工具的具体执行不在片中展开。“应用执行”不表示只能在开发者个人电脑上执行。

### S04 OWASP：REST Security Cheat Sheet

- [官方正文](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)，动态文档；实际读取 Access Control、Restrict HTTP methods、Input validation。
- 支持主张：受保护资源需检查访问权限，输入也需验证类型/格式等；这些是程序执行前后应有的业务边界，不因来源是模型而省略。
- 本地HTTP只绑定127.0.0.1，使用合成身份头演示接口读取，**不属于生产身份认证实现**。真实网络服务应使用HTTPS和真实认证/资源授权；本期没有实现整套生产安全方案。

## 实际演示与动画依据

执行[本地程序](demo/tool_demo.py)得到[完整证据](demo/verified-results.json)。两次是独立演示，使用相同工具名/参数、不同合成用户及新调用标识，各自启动新的测试服务，不能拼成同一次查询先成功再失败。

| 状态 | 有读取权限 | 重置后没有读取权限 |
|---|---|---|
| 收到模型侧固定请求时 | HTTP次数为0 | HTTP次数为0 |
| 应用检查 | 参数、权限通过 | 参数通过、权限拒绝 |
| 真实HTTP读取 | `GET /orders/8124`一次、200 | 零次，执行器没有被调用 |
| 函数输出 | `ok=true`，`signed_days=3`、`usage=null` | `ok=false`，`permission_denied` |
| 关联 | 回传`call_demo_01` | 回传`call_demo_02`，属于本次独立演示 |
| 最后固定答复 | 订单8124已签收3天 | 没有读取权限，未查询订单 |

失败中的`application_status:403`是应用自己的状态字段，**不是订单HTTP接口返回的403**；因为订单接口从未收到此次请求。模型侧请求和最后答复由fixture/固定格式器替代，只有应用检查、分发、本地HTTP、返回数据、日志和断言是真实运行。动画可以解释来源支持的模型流程，但不要把它标为一次真实模型API运行录像。

演示数字均是明确构造的教学值，HTTP次数为本次程序实际计数，不表示性能或统计结论。`usage=null`只表示未知；本片不据此断言商品已使用/未使用，也不给退款资格结论。

## 核验边界

- 没有真实模型、SDK执行或OpenAI账户网络请求；没有编造模型名、token量、成功率或耗时比较。
- 没有真实电商资料、退款/写入端点、生产认证、人工审批或托管工具实测。
- 资料核验支持技术主张；成片是否讲清场景和谁做什么，须由独立脚本/动画复核另行判断。
