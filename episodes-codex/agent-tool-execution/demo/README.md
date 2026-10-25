# A02 可运行的工具执行边界示例

本目录重放固定的Responses `function_call`项，应用检查后读取真实启动的本地HTTP测试服务，再准备对应的`function_call_output`。**没有真实模型推理**：请求是固定JSON，最终答复也是读取结果后的固定格式器。接口定义参考官方OpenAI Responses API；不同提供者字段不同。

在仓库根目录运行：

```sh
python3 episodes-codex/agent-tool-execution/demo/tool_demo.py --out episodes-codex/agent-tool-execution/demo/verified-results.json
```

仅依赖Python标准库，实际核验环境为Python3.12.14。每个case临时绑定`127.0.0.1`的随机端口并自动关闭，不访问外网、不读取密钥。参考SDK版本/提交与实际未使用SDK的边界写在[protocol-lock.json](protocol-lock.json)；不能把契约参考当成已执行SDK。

- [tool-definition.json](tool-definition.json)：自定义只读`get_order`定义，只有一个订单号参数；不能退款。
- [model-call.fixture.json](model-call.fixture.json)：固定模型侧调用项。两个case使用相同工具名和参数；成功是用户A/`call_demo_01`，拒绝是用户B/`call_demo_02`。各自是独立演示和新的服务，`call_id`只在相应case内关联。
- [tool_demo.py](tool_demo.py)：参数检查、固定分发、可信应用会话权限、真实HTTP读取、结果包装与断言。
- [verified-results.json](verified-results.json)：已实际执行的事件轨迹、HTTP计数、输入SHA及结果。

`allowed_query`实际执行一次`GET /orders/8124`，收到合成的`{"order_id":"8124","signed_days":3,"usage":null}`。`reset_permission_denied`在应用侧拒绝，HTTP次数保持0；`application_status=403`是本地应用状态，不是服务HTTP响应。每次刚收到固定调用时都断言HTTP次数为0，表明请求项本身不会执行函数。

演示只把用户身份从应用会话传给接口，没有让模型生成身份或URL。测试中的`X-Demo-User`只是合成身份传递方式，不构成生产认证；真实系统必须从经认证会话获得身份，并在受保护接口授权。`strict:true`用于协议示意，程序没有向真实模型API提交schema，不证明某模型已接受该schema。

此程序的断言验证本地分发与接口边界，不测试模型会选哪个工具，也不测量初学者是否理解。片中的动画必须标教学示例；完整资料和演示范围见[research.md](../research.md)。
