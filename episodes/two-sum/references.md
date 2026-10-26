# two-sum · 片尾参考资料

整理日期2026-10-26；三项技术实读日期均保留为2026-10-25（北京时间）。本轮只为Python补核原题与出版机构元数据，不新读LeetCode或editorial，不将26日固定源SHA追记为25日原页面hash。

title-author清单3项、一页5秒。原题面未记录公开个人署名；Python文档机构身份由官方版权页确认，仅作为出版机构，不从版权方或Git提交者推断个人作者。原研究及其逐论点记录、完整Git/blob/SHA、三份官方固定源GET与元数据范围见[本轮证据](../../docs/reference-endcards/batch-9/sources-two-sum.json)；既有实读记录是本仓研究笔记，不是官网固定正文。

## R1 · Two Sum

- 发布机构：LeetCode
- 版本／实读日期：LeetCode 1 · 实读2026-10-25
- 正式文档：[Two Sum](https://leetcode.com/problems/two-sum/description/)
- 原研究记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/two-sum/research.md#L7)
- 原题位置：既有实读记录 · 第7行英文题名
- 正文位置：官方题面 · 要求、示例与约束

对应主张：

- 返回和为目标的两个不同原下标；题目保证恰有一组有效答案，返回顺序不限。
- 不能重复使用同一个元素；来自不同位置的两个相同数值仍可组成答案。

## R2 · Built-in Types

- 发布机构：Python Software Foundation
- 版本／实读日期：Python 3 documentation · 实读2026-10-25
- 正式文档：[Built-in Types](https://docs.python.org/3/builtins/stdtypes.html#mapping-types-dict)
- 原研究记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/two-sum/research.md#L17)
- 原题位置：Doc/builtins/stdtypes.rst · 文档标题（第8行）
- 正文位置：字典操作条目 · key in d、d[key]、d[key] = value
- 原题／机构补核：2026-10-26；[官方固定原文](https://raw.githubusercontent.com/python/cpython/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/builtins/stdtypes.rst)

对应主张：

- 字典按键进行成员测试、取值与赋值；对同一个键再次赋值会更新映射的值。
- 本片用数值映射先前原下标；画面表格便于阅读，不表示逐行线性扫描。

## R3 · Time complexity of operations on built-in types

- 发布机构：Python Software Foundation
- 版本／实读日期：Python 3 documentation · 实读2026-10-25
- 正式文档：[Time complexity of operations on built-in types](https://docs.python.org/3/builtins/time-complexity.html#dict-frozendict)
- 原研究记录：[既有实读记录](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/two-sum/research.md#L25)
- 原题位置：Doc/builtins/time-complexity.rst · 文档标题（第4行）
- 正文位置：dict / frozendict · 平均成本、哈希假设与摊还边界
- 原题／机构补核：2026-10-26；[官方固定原文](https://raw.githubusercontent.com/python/cpython/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/builtins/time-complexity.rst)

对应主张：

- CPython字典操作的常数时间以平均成本及适当哈希分布等条件为前提，写入需考虑扩容的摊还成本。
- 大量碰撞时单次操作可退化为线性时间；据此得出本片遍历算法平均时间O(n)，不宣称无条件最坏O(n)。
