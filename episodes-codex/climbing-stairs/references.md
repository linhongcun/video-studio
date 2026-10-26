# climbing-stairs 片尾参考资料

以下两项官方资料分别支撑题意和Python赋值语义，均沿用2026-10-25（北京时间）的实际阅读记录。本轮2026-10-26只整理固定的既有实读记录，未新读取官网或官方题解正文。末步分类证明、六阶得到13以及程序核验是本期独立推导与验证，不冒称官方动态规划题解；原文章、研究和全部旧脚注保留。

`title-author`简表：2项1页、5秒，只显示实际原题与机构；完整链接、版本、日期、定位和边界留在文章或内部记录。

**[R1] Climbing Stairs**

LeetCode · LeetCode 70 · 官方题面 · 原记录未标发表或更新时间：[官方资料](https://leetcode.com/problems/climbing-stairs/description/)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/climbing-stairs/research.md#L7)。 [同题官方中文题面](https://leetcode.cn/problems/climbing-stairs/description/)。

支持范围：输入楼梯阶数n，每步只能前进1阶或2阶，返回恰好到顶部的不同走法数量。；n=3官方示例分别计算先1后2与先2后1，支持顺序不同的走法分别计数；题目范围为1至45。

边界：本片六阶得到13是独立教学输入和推导，不冒充官方示例。；官方editorial只取得登录/导航空壳，未读取题解正文；本条不为动态规划递推、滚动优化、复杂度或独立程序核验提供官方解法背书。

内部定位：Problem statement；n=2与n=3的Examples；Constraints（1 <= n <= 45）

**[R2] Assignment statements**

Python Software Foundation · Python 3 Language Reference · 原实读2026-10-25，未绑定运行时小版本：[官方资料](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements)；[既有实读记录（2026-10-25）](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/climbing-stairs/research.md#L17)。

支持范围：多目标赋值先求值右侧表达式，再将结果赋给左侧目标。；prev, curr = curr, prev + curr的右侧使用更新前两值；不能先覆盖prev再用新prev计算curr。

边界：本条只核对Python语言语义，不当作官方爬楼梯算法或动态规划解法。；所见文档2026-10-24更新时间只是旧读取记录中的元数据，不能推断平台实际运行时小版本或算法发表日期。

内部定位：Assignment statements：右侧表达式求值；目标列表从左到右赋值

内部证据：`docs/reference-endcards/batch-9/sources-climbing-stairs.json`。旧研究完整SHA-256 `9df68817a4fb1ec5d93e8b2397fccbb366f6a23b959f4863cc068518a997c274`；26日整理不改变25日实际读取日期。
