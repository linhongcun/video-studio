---
name: api-compat-review
description: Review a proposed JSON API request-contract change for backward compatibility with an existing client. Use when a task asks whether old clients can still omit fields after a request schema changes. Check the team's required-field rule and report the evidence and scope.
---

# API 请求兼容审查

目的：按团队约定审查请求字段变更，不根据“新增字段”四个字直接判定兼容。

1. 确认旧契约、新契约及一份真实或明确标注的旧客户端请求。缺输入时先说明缺口。
2. 阅读 [必填字段兼容规则](references/request-fields.md)。区分新增可选字段与新增必填字段。
3. 使用宿主允许的命令执行工具运行 `scripts/check_fields.py`，传入旧契约、新契约与旧请求。脚本由工具执行；不要把 Markdown 指令当作已执行的结果。
4. 根据工具返回的 `newRequiredFields`、`oldClientValidation` 和 `verdict` 输出结论，指出触发规则的字段。
5. 必须保留限制：本脚本只检查简化请求契约的必填字段变化，不是完整 OpenAPI 兼容性分析；不证明实际服务或所有客户端都已验证。

命令形式（路径相对本技能目录）：

```sh
python3 scripts/check_fields.py --before OLD.json --after NEW.json --client-request CLIENT.json
```

结论格式：兼容性判断、关键字段、旧请求结果、依据与未检查范围。不要输出未经实际运行的“检查通过”。
