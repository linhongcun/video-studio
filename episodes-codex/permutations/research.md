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


## 片尾参考资料（2026-10-26整理）

本轮仅补title-author书目。技术阅读日期保留原2026-10-25 UTC；source-access.json原字节固定于`4213a233c4c242b04453b8c1215031dc421c2398`，Git blob `a2ffc2bfc71672ce9bda0ea3ecb8b3a0e55e0aaf`，1266字节SHA-256 `d1cad2a1e1c002c4d01153bdac6f5cb5ce4f4095076b05b842b708655cccc12d`。[原读取记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/permutations/research/source-access.json)记载官方web connector实际读取题面和Python copy/pop对应条目，未读官方Editorial。

- 新R1：**46. Permutations**，LeetCode。标题直接取原source-access.json sources[0].title，输入、返回要求、示例与约束沿用原读取事实。

- 新R2：**Built-in Types**，Python Software Foundation。技术内容仍据原25日copy/pop条目读取；原请求为https://docs.python.org/3/library/stdtypes.html#list.copy，记录的最终地址为https://docs.python.org/3/builtins/stdtypes.html。26日从batch9已存固定CPython材料实际复核RST第7行首题及版权页发布机构，不从HTML站点后缀猜题名。

元数据原固定提交`c436e8d83597c6f8c1bc7e37812c98d46670c29a`，STDTypes完整262618字节SHA-256 `766d7f02b3872eedbffda498bfd0a23225a6082c18fdf02e2b3f420817f2422b`；版权材料446字节SHA-256 `f2c1d094466270ed41fc4dd2904d91b34d58cbb5033403b2de5cc153aba8e608`。本批按sources-permutations-*独名保留相同原字节，原HTTP取回时间与URL见[来源证据](../../docs/reference-endcards/batch-10/sources-permutations.json)。本轮未执行新GET，也未把26日元数据核对当作25日网页全文的SHA或新的技术阅读。

**编者说明：**题面没有指定本片回溯实现，唯一性、完整性、撤销恢复与O(n·n!)分析仍沿用原独立论证。list.copy与pop官方语义只支持副本和工作列表的区别，不当作整段算法证明；现有itertools执行对照不是新增未读文档出处。

**编辑边界：**原article/research完整字节前缀、脚注与锚点（如有）、唯一完整程序及全部制作输入保持。本轮不改freeze、README、source-sha、代码、SB、words、媒体、已发episodes、QA或共享文件，不预记独立复核、成片或发布通过。
