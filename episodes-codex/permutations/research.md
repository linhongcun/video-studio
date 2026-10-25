# LC.46 调研与制作边界

访问日期：2026-10-25 UTC。实际访问工具为官方web connector；LeetCode不在executor允许列表，不使用curl规避。访问证据见research/source-access.json。

| 事实 | 原始来源 | 制作采用 |
|---|---|---|
| 输入是互不相同的整数数组，返回所有排列，返回顺序不限；示例[1,2,3]有六项 | [LeetCode 46](https://leetcode.com/problems/permutations/) | 01–02先讲题意；同一组三张原题数字卡贯穿，不另造比喻 |
| 原题n在1到6之间，整数值在-10到10之间，各元素唯一 | 同上，Constraints | 独异条件是按下标used防重复与唯一性证明的前提；不将重复值题LC47混入 |
| list.copy创建浅副本，pop默认移除并返回最后一项 | [Python Built-in Types](https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types) | ans.append(path.copy())保存独立列表，path.pop()只撤销工作排列；元素为整数，浅复制足够 |

回溯方案是本片自行推导与实现，不声称LeetCode官方推荐或原题要求回溯。每位枚举未使用下标；路径满n时复制；返回后恢复。正确性：深度k不重复选择下标；每个完整排列对应唯一长度n选择链；枚举所有合法候选保证不漏。时间O(n·n!)包含输出复制；path/used/递归的额外工作空间O(n)，不含O(n·n!)完整输出。

独立验证通过标准库itertools.permutations对照1229个合法输入，测试集含所有五元素池的非空有序子集、900个固定种子随机输入、三个官方示例及n=6极值。另核对每项独立列表、修改某项不影响其他项、输入不变。trace由同一solution.py的AST插入观察调用生成，83个快照记录check/skip/choose/save-copy/unchoose/done，不包含第二套求解算法。

表达边界：第三位在选择3之前已经实际检查并跳过1/2；撤销3后对候选记录的回顾，不假造新的检查事件。返回完整结果仅用已保存副本，和三张工作卡身份分开；used只约束当前路径，撤销后可以再次使用。阶段1未做TTS、声学、ASR、听辨、静帧或视频QA。
