# daily-temperatures · 原题与可核对原文

题名／引句复核日期：2026-10-25（北京时间）。LeetCode本轮GET受会话代理403限制，忠实复用已保存的真实读题记录；不将该限制伪写为新访问成功。Python页另有官方固定RST的本轮HTTP200全文证据。

证据：[sources-algorithms.json](../../docs/reference-endcards/original-titles/sources-algorithms.json)。原访问日期、真实记录的Git提交／blob SHA及原位置均保留。

## R1 · 739. Daily Temperatures

- 机构：LeetCode
- 版本：题面访问于2026-10-25
- 正式链接：<https://leetcode.com/problems/daily-temperatures/description/>
- 原题位置：Official problem heading · L18

> If there is no future day for which this is possible, keep answer[i] == 0 instead.

原文位置：Description · captured L22。

内部论点对应（制作解释，不冒充原文）：

- 输入按日期排列的每日气温，输出等待下一次严格更暖气温的天数；没有未来更暖日则保留0。
- 官方约束：数组长度1至100000，气温数值30至100。

## R2 · Data Structures

- 机构：Python Software Foundation
- 版本：Python 3.15.1 · 访问2026-10-25
- 正式链接：<https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks>
- 原题位置：Chapter heading · line 4

> The list methods make it very easy to use a list as a stack, where the last element added is the first element retrieved ("last-in, first-out").

原文位置：Using Lists as Stacks · lines 139–140。

内部论点对应（制作解释，不冒充原文）：

- 栈按后进先出顺序取回元素，最近加入的元素先取出。
- Python列表append在末尾加入；不传下标的pop从同一末尾取出并返回元素。
