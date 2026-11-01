# LC.42 公开调研与范围

实际访问：2026-10-25 UTC。官方原题 [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/description/) 由 web 工具实际打开，返回61行，包括题意、两组示例与约束；工具访问证据见 [source-access.json](research/source-access.json)。没有通过执行环境绕过站点限制，也未声称读过题解页。

| 事实 | 官方证据 / 自行验证 |
| --- | --- |
| 输入是一列非负柱高，各柱宽1；目标是雨后留下的单位水量，返回整数 | 原题描述22行；本稿自行改述 |
| 长度1至20000，柱高0至100000 | 原题44–46行 |
| 官方示例分别返回6和9 | 原题29–37行；原样纳入独立测试 |
| 固定教学样例为[3,0,2,0,4,0,1]，返回8 | 自选非官方示例；solution.py真实执行，水平逐层格子oracle独立核对 |
| 当前列水位=min(含本列的左侧最高,含本列的右侧最高)，水深=水位−柱高 | 本期自行推导；两侧可达高度与泄漏解释，水位/水深分开；oracle穷举支持实现 |
| 时间O(n)，辅助空间O(n) | 唯一源码两个保存最高值的扫描、一个累加扫描；保存两个长度n数组 |

本批用户授权从既有issues自选有把握的题目。issue #86 的旧选题草案曾考虑双指针；本期主动选更适合讲透两侧挡水和不同水位的**单一左右最高值预处理**，不在视频中塞入另一种方法。原问题目标不变，旧issue原稿不改，发布PR透明说明本次范围调整；双指针仅作为以后的进阶候选，不当成本片已讲内容。

推导先从柱子与水开始：第四列的左右高柱分别3和4，超过3先从左侧漏出；第三列高2被淹过，说明相邻柱不一定是挡水边；第六列右侧只有高1，说明全局最高不能直接当全部水位。然后观察每列重新向两边找高柱会重复经过同一批柱子，推得从左到右/从右到左分别记住见过的最高柱，最后命名前缀/后缀最高值。两组定义都包含当前柱，与代码一致，首尾自然水深0，首次明确解释为何不能留水。

同源与测试： [solution.py](solution.py) 是唯一完整解法；[generate_demo_trace.py](research/generate_demo_trace.py) 在同一源码AST赋值之后插入只读观察器，21个真实事件供动画消费；没有在动画中另写求解器。[verify_algorithm.py](research/verify_algorithm.py) 用按水平层逐个检查真实左右挡柱的独立oracle核对22257组输入，另测两组满约束输入并核对全部trace不变量，报告见 [algorithm-verification.json](research/algorithm-verification.json)。这些不是成片、听辨、ASR或新手学习效果检查。


## 片尾参考资料

2026-10-26整理为`title-author`模式，2项1页5秒，屏幕只显示原题与机构。原25日题面实读与26日Python新增技术核验分开，完整证据见[来源核验记录](../../docs/reference-endcards/batch-10/sources-trapping-rain-water.json)。

- **[R1] Trapping Rain Water** — LeetCode；LeetCode 42 · 官方题面 · 原读取记录未标发表或更新时间。正式链接：[https://leetcode.com/problems/trapping-rain-water/description/](https://leetcode.com/problems/trapping-rain-water/description/)。定位：Problem statement；Examples；Constraints（旧读取返回行18–46）。保留2026-10-25 UTC11:49:45的真实工具记录（北京时间同日19:49:45），本轮不新GET。题意、示例6/9及约束按原记录；`source-access.json`是读取记录而不是官方61行原文快照，完整题名另见原研究第3行。不声称读过editorial。
- **[R2] Built-in functions** — Python Software Foundation；CPython官方文档固定提交 c436e8d83597c6f8c1bc7e37812c98d46670c29a · 未据此推断平台运行时小版本。正式链接：[https://docs.python.org/3/library/functions.html](https://docs.python.org/3/library/functions.html)；实际GET固定源：[https://raw.githubusercontent.com/python/cpython/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/builtins/functions.rst](https://raw.githubusercontent.com/python/cpython/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/builtins/functions.rst)。定位：len；max；min（固定源码行1256–1260、1344–1354、1382–1392）；题名第4行，出版机构见[同提交copyright.rst](https://raw.githubusercontent.com/python/cpython/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/copyright.rst)第5–7行。2026-10-26新增实际读取上述技术段落：`len`返回元素数，两个位置参数时`max`/`min`返回较大/较小者。原始响应完整保存在`sources-trapping-rain-water-functions.rst.source`（SHA256`a56d77a0f03ddc5eccbccfd58577aa3cc97a837c0ca4539ca634797f0ce58ec5`），机构原始响应另存，状态/字节/SHA/真实请求时间均记在来源JSON。未访问docs.python.org规范页面，未推断LeetCode运行时小版本。

取两侧最高值较小者为水位的证明、前缀/后缀预处理、复杂度及示例8，是本片独立推导；Python文档只核函数语义。旧oracle/trace测试结果保留为25日既有工作，本次未重跑算法、未读取题解、未渲染或解码媒体。旧文章/研究/脚注/锚点及全部程序源原样保留。
