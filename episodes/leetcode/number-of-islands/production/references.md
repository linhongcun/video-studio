# number-of-islands 片尾参考资料

以下三项核心官方资料分别支撑题意、列表作栈和集合语义，技术正文均沿用2026-10-25（北京时间）的实际读取记录。本轮2026-10-26另补Python集合章节的完整原题；只核题名，不将该补证写成新的技术正文核验。DFS方法、连通性证明、实际trace与独立程序验证由本期另行完成，不冒称官方题解；旧文章、研究和全部公开来源保留。

`title-author`：3项1页5秒，只显示实际原题和机构，完整链接、日期、版本、位置和边界不上视频。

**[R1] Number of Islands**

LeetCode · LeetCode 200 · 官方题面 · 原记录未标独立发布日期：[官方资料](https://leetcode.com/problems/number-of-islands/description/)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/number-of-islands/research/source-access.json)。 [同题官方中文题面](https://leetcode.cn/problems/number-of-islands/description/)。

支持范围：输入字符网格，1为陆地、0为水，仅上下左右相邻陆地连通，返回岛的座数；斜角接触不相连。；官方第二例11000/11000/00100/00011有7块陆地、3座岛；维度各1至300，网格外为水不要求边缘格全为水。

边界：官方题面支持题意、约束和示例，不给本期独立DFS方法、正确性证明或复杂度分析加官方题解背书。；本期资料没有读取或使用官方editorial正文的证据，故不将其列为已读来源。；视频行列从1起，代码/trace下标从0起；资料清单不改变原地图或坐标映射。

内部定位：Problem statement；Example 2；Constraints；原题读取行22—54及中文交叉核对

**[R2] Using Lists as Stacks**

Python Software Foundation · Python 3.13 Tutorial · 章节原题：[官方资料](https://docs.python.org/3.13/tutorial/datastructures.html#using-lists-as-stacks)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/number-of-islands/research/source-access.json)。

支持范围：列表append在末端添加元素，不给索引的pop取出最后一个元素。；这两个操作支持后进先出栈，用来保存本片已归属但尚待展开的位置。

边界：方向循环右、下、左、上不等于弹栈展开顺序；本片实际顺序由独立程序trace固定，不冒充Python文档规定的DFS顺序。；列表作栈的语言说明不替代找全一座岛、每座只加一的独立连通性证明。

内部定位：Using Lists as Stacks；2026-10-25读取行83—98

**[R3] Set Types — set, frozenset**

Python Software Foundation · Python 3.13 Documentation · Built-in Types章节：[官方资料](https://docs.python.org/3.13/library/stdtypes.html#types-set)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/number-of-islands/research/source-access.json)。 [完整章节原题补证（2026-10-26，官方固定源码）](https://github.com/python/cpython/blob/42155a0feaca9ba6991942c323cbe9fb7278be3c/Doc/builtins/stdtypes.rst)。

支持范围：集合由互异的可哈希对象组成，支持成员测试和添加元素，可用于seen去重和归属判断。；集合无序，不将展示时排序的集合快照说成Python集合插入或遍历顺序保证。

边界：已加入seen表示已经归属，仍可能在栈中等待展开；这些程序状态由本片实现区分，不是集合自动提供的DFS状态机。；O(mn)分析采用通常集合操作的期望常数成本模型，不由本章节推出所有输入或实现都绝对常数时间。；26日固定源码GET仅补完整章节题名，不回写为25日官方响应、实际运行时patch版本或新增技术实读。

内部定位：Set Types；2026-10-25读取行2708—2738、2858—2861；本轮仅补官方RST第4824行完整原题

内部证据：`docs/reference-endcards/batch-10/sources-number-of-islands.json`；25日技术实读与26日题名补证分开。无个人署名凭据，使用官方机构，不推定Git提交者为作者。
