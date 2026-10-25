# 本地 API 兼容性审查记录

**结论：`after-required.json` 会使指定旧请求在本例必填字段校验中失败；`after-optional.json` 通过已检查的必填字段规则。**

审查日期：2026-10-25（来自环境日期）。本轮是根代理分配的本地任务，不是完整产品宿主的自动技能触发测试。工作目录为 `/workspace/video-studio`，演示根目录为 `episodes-codex/agent-skills/demo`。

## 技能选择与实际读取

首先只读取 `outputs/catalog.json` 中的技能名称与描述。选择 **api-compat-review**，因为其描述直接覆盖“契约变更后，旧客户端能否继续省略字段”。随后读取 [所选 SKILL.md](../skills/api-compat-review/SKILL.md) 和 [必填字段规则](../skills/api-compat-review/references/request-fields.md)，按步骤执行检查。

实际进入模型上下文的文件如下，路径相对演示根目录：

- `outputs/catalog.json`
- `skills/api-compat-review/SKILL.md`
- `skills/api-compat-review/references/request-fields.md`
- `fixtures/before.json`
- `fixtures/after-required.json`
- `fixtures/after-optional.json`
- `fixtures/old-client-request.json`

通过 `rg --files … -g SKILL.md` 找到了两个技能文件的路径；没有读取 `release-notes/SKILL.md` 正文，也没有将检查器源码读入模型上下文。Python 解释器实际执行了检查器。完整读取命令记录保存在 [JSON 证据](agent-review.json) 中；所有读取及检查命令均返回退出码 0。

## 实际命令与返回结果

以下两条命令依次通过命令执行工具运行，执行目录均为：

`/workspace/video-studio/episodes-codex/agent-skills/demo/skills/api-compat-review`

```sh
python3 scripts/check_fields.py --before ../../fixtures/before.json --after ../../fixtures/after-required.json --client-request ../../fixtures/old-client-request.json
```

实际返回：`newRequiredFields=["channel"]`；旧请求在变更前为 `accepted_by_example_required_field_validator`，变更后为 `rejected_by_example_required_field_validator`；`missingRequiredFields=["channel"]`；`verdict=breaking_required_field_change`。退出码 0，工具输出块 `ca0b04`。

```sh
python3 scripts/check_fields.py --before ../../fixtures/before.json --after ../../fixtures/after-optional.json --client-request ../../fixtures/old-client-request.json
```

实际返回：`newRequiredFields=[]`；旧请求在变更前后均为 `accepted_by_example_required_field_validator`；`missingRequiredFields=[]`；`verdict=passes_checked_required_field_rules`。退出码 0，工具输出块 `b0c2a7`。

[JSON 证据](agent-review.json) 保留两次 stdout 的完整 JSON 内容。脚本的 `checkedRule` 在两次输出中均标为 R2；本记录保留原值，可选版的解释同时依据团队 R1。

## 兼容性依据

端点为示例 `POST /orders`。旧请求是 `{"sku":"SKU-7","quantity":1}`，没有 `channel`。

| 对照 | 契约级证据 | 请求级证据 | 判断 |
| --- | --- | --- | --- |
| `after-required.json` 相对 `before.json` | `required` 从 `sku, quantity` 增加为 `sku, quantity, channel` | 缺少新必填字段 `channel`，旧请求被本地校验器拒绝 | 对指定旧请求构成破坏性变更，依据 R2 |
| `after-optional.json` 相对 `before.json` | 新增 `channel` 属性，但 `required` 仍为 `sku, quantity` | 旧请求省略 `channel` 仍通过本地校验 | 通过本例已检查的必填字段规则，依据 R1 |

## 范围与限制

契约、端点、规则与请求均为合成教学示例。本轮只检查简化 JSON 请求对象的必填字段变化和这一份旧请求。没有发起网络或 HTTP 请求；本地校验器“拒绝”不代表观测到真实服务返回某个状态码。

未分析响应字段、类型收窄、枚举、格式、认证、默认值、状态码语义或实际服务行为，也不是完整 OpenAPI 兼容性分析。单一样例通过不能证明所有旧客户端都兼容，可选版不能据此称为“完全兼容”。本次记录不证明通用准确率提升，也不证明所有宿主的自动技能路由可靠。

本执行者仅写入 `outputs/agent-review.json` 与 `outputs/agent-review.md`，未编辑业务脚本，未创建提交。
