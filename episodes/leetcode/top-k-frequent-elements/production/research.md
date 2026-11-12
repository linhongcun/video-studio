# LC347 研究与范围

实际日期：2026-11-12（北京时间）。目标读者未读过原题、不要求已知堆；唯一问题是为什么只要前k名却要让最少候选在堆顶。读者应能依据同一16项例子说明计数、淘汰、安全保留、父子规则及更新路径；完整实现、正确性不变量和精确复杂度放文章深入层。

## 实读来源

### R1 · Doocs：《347. Top K Frequent Elements》

- 固定源：[README_EN.md](https://github.com/doocs/leetcode/blob/42e5712371b45d9005bfffee602d860f610c40da/solution/0300-0399/0347.Top%20K%20Frequent%20Elements/README_EN.md)，commit `42e5712371b45d9005bfffee602d860f610c40da`。
- 实际HTTPS读取时间、状态、完整SHA与字节保存在`research/source-access.json`；原始字节为`research/problem.md`。题名在Markdown一级标题，机构来自公开项目Doocs；没有擅自推断个人作者。
- 读取并采用题意、例子、Constraints及Follow up：输入整数数组与k、返回出现次数最多的k个元素、顺序任意、答案保证唯一。n≤100000，k≤不同数字种数；进阶要求比O(n log n)更优。
- 原始HTML片段为`You may return the answer in <strong>any order</strong>.`；文章引用使用它的渲染等价纯文本`You may return the answer in any order.`。本轮仅去掉strong强调标签、不改字词标点，HTMLParser派生方式、原片段、原始文件SHA与输出保存在`source-evidence.json`；不把纯文本冒称含标签的.raw源码逐字匹配，也不把派生记成新访问。该短引只支持返回顺序，不支持堆正确性或复杂度。
- 这是公开题面镜像；原始LeetCode域名不在当前出站允许列表，本轮没有直接读取其网页，不把镜像称为官方访问。完整保存的镜像含解法段，但本片推导与测试不以其作为证明。

### R2 · Python官方：《heapq — Heap queue algorithm》

- [CPython v3.14.0文档源码](https://github.com/python/cpython/blob/v3.14.0/Doc/library/heapq.rst)与[实现源码](https://github.com/python/cpython/blob/v3.14.0/Lib/heapq.py)，保存原始字节`research/heapq.rst`和`research/heapq.py`。
- 标题源为`:mod:\`!heapq\` --- Heap queue algorithm`，片尾使用去除RST角色后渲染的题名；`source-evidence.json`保存原行与文本形式，不能误称直接抓取了docs.python.org网页。
- 明确moduleauthor/sectionauthor：Kevin O'Connor、Guido van Rossum、François Pinard、Raymond Hettinger。不是按Git提交者推断作者。
- 读取intro的父≤孩子规则、数组子节点下标、heap[0]最小、heappush/heappop API，以及`Lib/heapq.py`相应函数与_siftdown/_siftup。原文短引在references与证据中保留连续换行。
- 映射05–14镜：父子局部规则导致root最小；逐层从左到右填位、插入后沿祖先修复、根被删后末尾补根并修复；正文经典交换是等价教学分解，不冒充CPython的洞移动逐条赋值。正式trace的稳定状态须与实际heapq一致。
- Python v3.14的max-heap新增API不在本片范围，本片代码只使用长期开源的min-heap API，并不要求观众使用3.14。

## 独立算法分析（不是来源原句）

令n为输入长度，u为不同数字数。先用字典一次计数，期望O(n)；按首次出现顺序遍历u条(数字,次数)，每次push后若超过k就pop。堆稳定容量≤k、临时最多k+1；一次堆调整沿树高，O(log(k+1))，因此期望总时间O(n+u log(k+1))，额外空间O(u+k)，由于k≤u也可化简O(u)。哈希字典的期望边界明确，不把最坏散列攻击包含为本片保证。

维护不变量：处理t种数字后，堆包含这t种中频次最大的min(k,t)种。t<k时全部留下；已满后从旧topk与新项组成的k+1项中删最少，其余仍为新topk。没入堆的旧项早已有k个不弱于它的候选，不会因来了新项而重新必要。题目唯一答案保证k/u边界没有影响答案集合的平频；代码元组以数字打破平手只决定等频项目选择/布局，不改变频次比较主线。

通用堆法当k与u同量级时可到O(n log n)，不能笼统宣称严格满足题面进阶最坏要求。正文以只需维护少量候选解释方法，不使用旧issue“题面不让全排序所以该法总能满足”的钩子。本文只完整展开一种解法，进阶的严格最坏优化应另行选择线性方法，不在本片再开算法支线。

## 真实执行边界

唯一可提交程序为`solution.py`，完整卡由`solution.json`绑定其完整SHA。输入是教学构造，不冒充官方例子：16项、6种频次依次3/2/1/4/5/1，k=3，真实返回`[1,5,4]`与集合`{1,4,5}`一致。事件轨迹由动画作者`research/build_trace.py`生成，其程序版本与测试报告单独留证。此记录本身不把尚未生成的TTS、动画、图文截图或媒体记为已验收。
