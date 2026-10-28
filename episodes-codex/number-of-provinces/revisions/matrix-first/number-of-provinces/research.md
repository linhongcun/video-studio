# LC.547 省份数量：研究与原创推导

本期选自尚未完成的制作issue #85。问题中的“省份”是直接或间接相连城市组成的完整集合，不是某个真实国家的行政划分；相连关系不被擅自解释为真实公路、地理距离或边界。六城A..F仅为教学标记，对应程序下标0..5。

## 本轮实读范围

2026-10-27北京时间实际读取3项固定GitHub公开源，逐个通过Contents API取得文件正文、解码、定位原题与引用，并记录Git blob/完整SHA。原始LeetCode域名不在所选环境允许目标中，本轮没有请求原站，更没有绕过网络限制。R1是Doocs公开题面镜像，明确区别于官方页面实读；原官方链接只作出处指针。两项实现依据分别来自Princeton官方algs4源码、维护中的CP-Algorithms原文。详细身份、原句和边界见`research/source-access.json`；不把CLI成功擅自填写成单独记录过HTTP状态200。

### R1 547. Number of Provinces

- 实读发布方：Doocs公开题面镜像；原题来自LeetCode，未把镜像维护者推定为官方作者。
- 固定版本：`42ac9040510ef8711ed8c66a4c9be2e6ffa08f73`。
- 实际链接：https://github.com/doocs/leetcode/blob/42ac9040510ef8711ed8c66a4c9be2e6ffa08f73/solution/0500-0599/0547.Number%20of%20Provinces/README_EN.md
- 原站指针（未直读）：https://leetcode.com/problems/number-of-provinces/description/
- 连续原句：A province is a group of directly or indirectly connected cities and no other cities outside of the group.
- 位置：Description，province定义段；HTML强调标记移除后单词/标点不变。
- 支持：直接及间接相连定义，n×n整数相连矩阵，1≤n≤200，对角为1、矩阵对称，返回省份总数。只使用Description、Examples和Constraints，不引用镜像题解。

### R2 UF.java

- 作者：Robert Sedgewick、Kevin Wayne，来源文件`@author`明确署名；机构：Princeton University。不是因仓库维护账号猜作者。
- 固定版本：`6157ca02644bdc24892ffbac1cf449d5169e71de`，当前读取到的该文件最后提交；不把基础算法的旧提交伪说为2026年新发明。
- 实际链接：https://github.com/kevin-wayne/algs4/blob/6157ca02644bdc24892ffbac1cf449d5169e71de/src/main/java/edu/princeton/cs/algs4/UF.java
- 连续原句：The union–find data type models a collection of sets containing n elements, with each element in exactly one set.
- 位置：UF类Javadoc集合定义；移除Javadoc/HTML/inline-code格式，连续可见文字不改写。
- 支持：初始n个单元素集合，同根等价于同集合，union只合并不同集合，count表示集合数，路径减半实现。
- 边界：该官方代码以rank平衡，本期源码以size平衡；不能声称两份代码逐字相同，也不只凭这一份资料把size实现直接归为rank实现的复杂度。

### R3 Disjoint Set Union

- 机构：CP-Algorithms；文章没有可据以确认的个人署名，不从Git维护记录推定作者。
- 固定版本：`f06f7d5e5630f0b811e37d9e657562ba38c41f6a`（2026-09-19提交）。
- 实际链接：https://github.com/cp-algorithms/cp-algorithms/blob/f06f7d5e5630f0b811e37d9e657562ba38c41f6a/src/data_structures/disjoint_set_union.md
- 连续原句：As mentioned before, if we combine both optimizations - path compression with union by size / rank - we will reach nearly constant time queries.
- 位置：Time complexity章节。
- 支持：小集合根挂到大集合根、size/rank两种平衡的等价渐近界、平衡加路径压缩的反阿克曼摊还复杂度。结合R2实际路径减半代码解释本期实现，不声称所有不平衡父指针循环都是常数时间。

## 本期主线与样例

题意/返回总数→只关心是否同组、跨组才合并→为组保存代表→沿父指针找根、不同根才合并→命名单条主线的并查集→矩阵扫描和三组结果→同根跳过以及代码闭环。方法不能在背景分析前先报，父指针虚线也不能冒充输入中的直接相连关系。

主例6城，关系AB、BC、DE，结果3：{A,B,C}、{D,E}、{F}。AB处理后5组，BC通过B找到A根后4组，DE后3组；F没有与其他城市相连，自己仍是一组。程序只扫描矩阵上三角，故AB与BA不重复，AA等自连也不作为新关系；0格仍真实检查并略过。

补例明确另加AC关系；按矩阵顺序先AB、再AC、然后BC，BC两端同根A，因此计数仍4，此时DE尚未处理。完整继续DE后是3组，不能在BC镜头过早显示完整最终3。该顺序由真实trace给出，不靠动画硬指定。

输入关系组成的图与实现父指针严格分开：BC这条直接关系存在，但按大小合并后C的父记录可指向A；那是归属记录，不是新增AC相连关系。代表城市没有行政含义或特殊地位。

## 源码、执行与复杂度

`solution.py`是唯一解题源，`Solution.findCircleNum(self,isConnected:list[list[int]]) -> int`，使用按size合并及路径减半。`solution.json`逐行绑定其完整源码，片尾Python卡与文章均应逐字取此源。矩阵上三角仍有n(n−1)/2个检查，n²级输入扫描不能省掉：时间O(n²·α(n))，额外空间O(n)，输入矩阵的存储不算额外空间。α(n)是摊还序列界，不声称每次find固定一步或严格最坏O(1)。正文可只说明必须读矩阵、归组合并已做优化，细节留图文。

`research/verify_solution.py`通过独立BFS oracle核对1099个n≤5的全部无向图、3000个确定随机图、3个n=200约束样例。穷举同时检查输入未被修改。主例与补例均为3；另有仅供程序QA的`compressionCheck`真实触发路径减半改变父记录，结果2，不把它增加为视频新支线。

`research/trace.json`由`sys.settrace`读取实际执行的locals和return产生，解题函数没有observer或渲染参数。每个输入都保留全部15个上三角`inspect`事件，包括0；find/同根跳过/父记录改动/size改动/计数改动有独立快照。observer只读父数组导出`groups/groupRoots`供渲染着色，不在JS另写并查集。`sourceLine`为观察发生、即将执行的源行；有`effectLine`时标出刚完成赋值的实际行，不能混称为同一时点。详见`research/trace-schema.md`。

目前这些程序和资料检查不等于配音、实际动画或视频已被用户认可；无新版本学习效果测量。
