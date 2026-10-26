# LC.704 公开资料与推导

访问日期：2026-10-25（北京时间）。制作选题为[issue #76](https://github.com/linhongcun/video-studio/issues/76)。本文区分公开题面、语言语义、独立证明和有限执行核验，不表示配音、动态动画、成片或线上交付已经通过。

## R1 官方题面

- 来源：[LeetCode 704. Binary Search](https://leetcode.com/problems/binary-search/description/)与[力扣704. 二分查找](https://leetcode.cn/problems/binary-search/description/)。
- 实际获取：本次独立调研代理通过可用网页工具分别打开并读取中英文正文、两组示例及约束；没有把搜索摘要当作全文阅读。
- 页面日期：题面未标发表或更新时间，不以版权年份推断。
- 支持主张：给定升序整数数组与目标值，存在则返回下标，不存在则返回-1；所有数组元素唯一；要求算法时间复杂度为`O(log n)`。官方数组长度为1..10000，英文题面对数组值和目标值均限定在-10000与10000之间（不含两端）。
- 短引：英文题面写“return its index”和“Otherwise, return `-1`”。
- 官方示例：数组`[-1,0,3,5,9,12]`，目标9返回4，目标2返回-1。
- 用在：开头题意、成功/未找到的返回值、文章适用条件。主片采用自行选取的较易读输入，不称为官方示例；不引用题目通过率、企业标签或面试频率。

## R2 Python整除与下标语义

- 来源：[Python 3 Language Reference — Binary arithmetic operations](https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations)；[Python 3 Built-in Types — Common Sequence Operations](https://docs.python.org/3/builtins/stdtypes.html#common-sequence-operations)。
- 实际获取：网页工具打开官方表达式文档，并定位`//`解释；另打开内置类型文档。表达式页面显示最后更新2026-10-24 11:38 UTC，这是文档元数据，不表示二分算法的提出日期。
- 支持主张：整数`//`返回向下取整的整数商；序列按下标访问元素。文章里的`left + (right-left)//2`在有效非空闭区间中选择靠左的中点，偶数个候选时并无唯一“正中间那一格”。
- 短引：“floor division of integers results in an integer”。
- 用在：中点下标、Python程序与文章。该文档只提供运算语义，不作为整段算法正确性的官方证明。

## 独立正确性论证

初始闭区间为`[0,n-1]`。每轮开始时维持：若目标存在于原数组，目标下标仍在当前闭区间`[left,right]`内。

取`mid = left + (right-left)//2`，当`left <= right`时必有`left <= mid <= right`。若中点值等于目标，返回`mid`即满足题意。若中点值小于目标，升序性质保证所有下标不大于`mid`的候选值都小于目标，所以可以把`left`更新为`mid+1`。若中点值大于目标，则所有下标不小于`mid`的候选值都大于目标，所以把`right`更新为`mid-1`。

每次未命中更新都保留不变式，并且排除中点自身，使区间严格缩短。目标存在时不会被排除；如果最终`left > right`，区间没有下标，不变式说明目标在原数组中不存在，返回-1。最后只剩一格时仍应比较，所以循环条件是`left <= right`。

## 复杂度独立推导

当前候选数为`m`时，未命中后保留的候选数至多为`floor(m/2)`。循环轮数因此为`O(log n)`，每轮作常数次下标、整数运算及比较；题目范围内按常见单位成本模型计。迭代代码只维护有限个下标和中点，不切片、不递归，额外空间`O(1)`。这里“比较三次”指访问三个中点、完成三轮查找，不声称源码只执行三个布尔比较。

主片不采用issue中“百万个数最多20次”的开场数字；本片只需要同一8元素例子的可见缩减，避免用未经当前程序计数核验的规模对比替代题意。

## 自选教学轨迹

固定原数组`[1,3,5,7,9,11,13,15]`，下标0..7；原数组从不删除或移动，只改变候选区间，已排除格保留原位置并变淡。以下两次查找是独立输入情景，第二次必须重置全部候选，再把目标改成8。

| 目标 | 轮次 | 原候选下标 | 中点下标/值 | 结果 | 新候选下标或返回值 |
|---:|---:|---|---|---|---|
| 13 | 1 | 0..7 | 3 / 7 | 7 < 13 | 4..7 |
| 13 | 2 | 4..7 | 5 / 11 | 11 < 13 | 6..7 |
| 13 | 3 | 6..7 | 6 / 13 | 相等 | 返回6 |
| 8 | 1 | 0..7 | 3 / 7 | 7 < 8 | 4..7 |
| 8 | 2 | 4..7 | 5 / 11 | 11 > 8 | 4..4 |
| 8 | 3 | 4..4 | 4 / 9 | 9 > 8 | left=4，right=3，返回-1 |

执行核验已由`research/verify_algorithm.py`直接加载本期`solution.py`，与独立顺序枚举答案交叉核对：值域-4..4的全部511个非空升序独特数组、目标-5..5共5,621组通过，另有16个显式用例（含官方两例、教学两例、单元素/两元素、值域端点和10,000元素输入）及3个官方约束外的空数组健壮性用例通过。执行中通过Python行跟踪观察实际提交函数，检查目标下标留在候选闭区间、中点有效、未命中后每轮候选至多减半与输入不变。两条教学轨迹、显示JSON及文章唯一Python块均与执行源一致。实际SHA与报告见[research/algorithm-verification.json](research/algorithm-verification.json)。有限样本不代替上述一般论证，也不能证明画面或声音正确。

## 叙事与画面风险

- 开头先交代输入已有序且值不重复、按目标找位置、下标从0、找不到返回-1，再引入查找范围与二分方法。题号或标题不能代替这些信息。
- 偶数候选数取靠左中点，不能无解释地把两格中任一格称为唯一正中间。
- 暗下去表示“已排除”，不表示原数组被删除或下标重排；返回值6是原下标，不是值13，也不是剩余区间内的相对位置。
- 缺失目标情景先明确“换一个目标，重新查找”，再恢复候选；不能让观众以为同一次搜索把目标13改为8。
- 最后剩一格应继续比较；区间交错时没有候选，中点不得继续访问。
- 主线只用闭区间版，不混入半开区间的`right=mid`、`left<right`或其他终止约定。最后完整Python卡5秒，提示暂停，不新增口播/字幕。


## 片尾参考资料（2026-10-26整理，沿用2026-10-25实读）

本轮只整理既有事实来源，采用title-author；三项原题/发布机构见references.json/md，一页5秒，安排在既有完整Python卡之后。未请求官方网页，未新增官方原文标题补核、视频引文或Editorial正文阅读。逐项证据见[本轮书目证据](../../docs/reference-endcards/batch-9/sources-binary-search.json)。

原读取记录固定于Git提交`036ce88d416e08127f8135afb55d1d62044f30f6`，路径`episodes-codex/binary-search/research.md`，Git blob为`accb745bb9249a408a3e0241f5789b889da7f353`，完整6329字节SHA-256为`4dec1b05a5581ea51738292cb064962d2f8e822a3163a0c4a623203b06442059`。来源证据保留完整原记录与逐行原题，日期仍是2026-10-25，不是2026-10-26新GET。

- 新R1 · **704. Binary Search**；机构：LeetCode。来自原记录第7行，[既有实读记录](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/binary-search/research.md#L5-L13)。官方题面给出升序、元素唯一、返回原下标或-1的任务，以及O(log n)复杂度要求。上文的闭区间实现、不变式和每轮至多减半证明属于本期独立推导。
- 新R2 · **Binary arithmetic operations**；机构：Python Software Foundation。来自原记录第17行，[既有实读记录](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/binary-search/research.md#L15-L21)。该章节说明整数//的向下取整语义，用于解释程序如何取得靠左的中点；它提供语言语义依据，算法正确性与复杂度论证见上文。
- 新R3 · **Common Sequence Operations**；机构：Python Software Foundation。来自原记录第17行，[既有实读记录](https://github.com/linhongcun/video-studio/blob/036ce88d416e08127f8135afb55d1d62044f30f6/episodes-codex/binary-search/research.md#L15-L21)。该章节提供序列下标从0开始及负下标语义的依据。程序返回-1表示题目约定的未找到，后续不应据此误取nums[-1]。

**边界：**题面中的O(log n)是题目要求；上述闭区间不变式、终止、复杂度和自选8元素轨迹仍由本期原有独立推导/有限执行核验承担，不标为官方解法。Python标题是原锚点章节的真实题名，版本只标Python 3文档，不从页面维护时间推断平台小版本。没有个人署名记录时使用机构，不从仓库账号猜作者。

**编辑范围：**原article/research全文、脚注、锚点和唯一Python代码块保持为完整原字节前缀；本轮仅追加本节与文章的“片尾参考资料”。未改solution、script、分镜、words、声音、旧冻结、package、共享工具或媒体；本节不预记独立QA、渲染、浏览器或发布通过。
