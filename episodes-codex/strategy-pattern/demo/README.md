# 策略模式的可运行示例

需要 Python 3.12 或更高版本，只用标准库。

```sh
python3 episodes-codex/strategy-pattern/demo/pricing.py
python3 episodes-codex/strategy-pattern/demo/verify_demo.py
```

`pricing.py` 保留重构前的分支实现、重构后的稳定结算入口、三种初始策略、活动替换和新客扩展。`verify_demo.py` 实际执行等价、金额舍入、非法输入与扩展边界检查，生成 `verified-results.json`，其中的金额及调用轨迹可供动画核对。

`pricing.py` 同时保留两个活动版本，并通过映射切换以便同场比较；它不是最小源码补丁。真正的单点修改由 `snapshots/before.py` 和 `snapshots/after.py` 演示：保持同名函数、注册表和结算入口，只有活动函数体80→75。验证器实际导入两快照、运行21组案例，并将唯一差异导出为 `snapshots/campaign-only.diff`，报告包含两份源文件的SHA-256和AST变化范围。

金额单位为整数分；百分比向下取整到分；一次只选一个规则。折扣与舍入方式均为教学设定，不代表真实商家的政策。验证结果不是任意定价函数的正确性证明。
