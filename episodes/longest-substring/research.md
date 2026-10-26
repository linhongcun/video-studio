# LC.3 资料核验与独立推导

访问日期：2026-10-24（北京时间）。对应[issue #79](https://github.com/linhongcun/video-studio/issues/79)。本文件记录题意来源、集合语义、算法推导及教学输入，不表示配音、连续动画、正式媒体或上线检查已完成。

## 公开资料实际阅读

### R1 官方题目正文

- 中文：[LeetCode 3. 无重复字符的最长子串](https://leetcode.cn/problems/longest-substring-without-repeating-characters/description/)。
- 英文：[LeetCode 3. Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/description/)。
- 实际获取：独立调研代理通过可用网页工具打开并读取中英文题目正文、示例和约束。shell直连LeetCode曾被代理403拒绝，不能写成curl成功；本文件采用的是实际网页读取结果，不依赖搜索摘要。
- 页面日期：题目正文未标发表或更新时间，不根据版权年份推断。
- 支持主张：输入是字符串，返回无重复字符的最长子串长度；子串要求连续；长度范围0..100000，字符可以包含英文字母、数字、符号和空格。
- 官方例子：`abcabcbb`→3，`bbbbb`→1，`pwwkew`→3；`pwke`不是连续子串。
- 用在：题意前置、文章返回值/连续性/边界解释。没有把通过率、企业标签或面试频率当作制作依据。

### R2 Python集合语义

- 来源：[Python 3 Library Reference — Set Types](https://docs.python.org/3/builtins/stdtypes.html#set-types-set-frozenset)。
- 实际获取：调研代理通过网页工具打开完整正文；shell urllib直连被代理403拒绝，不将其写成curl读取成功。
- 实际阅读支持：set是不同可哈希对象组成的无序集合，不记录元素位置或插入次序；支持成员判断、add和remove。
- 用在：画面集合成员区不得被解释成另一条有序队列，位置由原字符串与左右下标记录。
- 边界：语言文档的语义说明不等于每个输入下最坏`O(1)`操作承诺。本文线性时间按常见哈希集合平均常数操作模型表述，最坏情况不作该保证。

### R3 Python官方集合复杂度说明

- 来源：[Python 3 — Time Complexity：set/frozenset](https://docs.python.org/3/builtins/time-complexity.html#set-frozenset)。旧`wiki.python.org/moin/TimeComplexity`迁移页指向该官方文档，优先使用迁移后的来源。
- 实际获取：调研代理通过网页open/click读取完整set复杂度段及脚注；shell直连同样被代理403拒绝。
- 页面实际显示最后更新：2026-10-24 11:38 UTC；这是页面元数据，不解释为算法首次提出时间。
- 支持主张：成员判断、add与remove的平均复杂度为`O(1)`；add有摊还说明，哈希碰撞可令相应操作退化为线性。平均/摊还成本不能改写成所有输入下的最坏常数保证。
- 用在：14镜“集合操作平均是常数时间”，以及文章时间复杂度的条件。算法总共线性数量的集合操作、额外空间上限仍由本期代码独立推导，不冒称官方题解逐字证明。

## 独立正确性推导

循环开始时，`seen`保存旧窗口`s[left:right]`的字符，旧窗口无重复，`s[right]`是待处理新字符。

如果新字符与旧窗口中下标`p`的字符相同，任何从`p`或更早开始、在当前`right`结束的区间都包含这两份字符，不能成为合法子串。依次移除左端，直到`left=p+1`时冲突恰好消失；剩余旧窗口仍无重复，加入新字符后合法，并保留了最多的左侧字符。

如果新字符不在集合中，原窗口直接扩展。以前排除的更早起点在上一个右端已含重复，再向右添加字符不会消除原有重复，因此不必把左边界退回。

每轮由此得到以当前右端结束的最长合法窗口。任意子串都有某个右端，取所有轮次长度的最大值，就得到全局答案。当前长度在消重后可能下降，`best`只能保持或增加，结束必须返回`best`。

## 复杂度的模型与边界

右端扫描n个位置，左端只向右、最多移过n个位置。每个位置对应的字符加入集合一次、移出至多一次，所以整个算法只有线性数量的集合操作；不能因为源码有内外两层循环，就把它机械算成`O(n²)`。

在集合成员查询、加入和删除平均为常数时间的常见哈希表模型下，平均时间是`O(n)`。这不是Python语言对恶意碰撞等最坏情况的性能保证。空间由无重复窗口的最大成员数决定，为`O(min(n, Σ))`，其中`Σ`表示可用字符种类数；本题不把字符固定成26个字母。输入字符串不计入额外空间。

## 自选教学输入

`abcbadea`是本片自行选取的教学字符串，画面应标“示例”，不是官方例子。

| 当前右下标 | 加入前需移出的下标/字符 | 完成后的左下标 | 合法窗口 | 当前长度 | 最长记录 |
|---:|---|---:|---|---:|---:|
| 0 | 无 | 0 | a | 1 | 1 |
| 1 | 无 | 0 | ab | 2 | 2 |
| 2 | 无 | 0 | abc | 3 | 3 |
| 3 | 0/a、1/b | 2 | cb | 2 | 3 |
| 4 | 无 | 2 | cba | 3 | 3 |
| 5 | 无 | 2 | cbad | 4 | 4 |
| 6 | 无 | 2 | cbade | 5 | 5 |
| 7 | 2/c、3/b、4/a | 5 | dea | 3 | 5 |

独立调研代理已实际运行该输入，确认两处重复的移除顺序和最终结果5。独立技术QA随后直接执行本期solution.py，以独立枚举连续区间的暴力解交叉核对：字母表`ab #`、长度0..7共21,845个有限输入，以及16个显式边界用例全部通过；覆盖官方三例、空串、全同、abba、主例、空格/制表符、大小写和Unicode。还逐轮核对集合与合法窗口成员相同、left为当前右端最早合法起点、best等于该前缀暴力答案。执行源、显示JSON及文章唯一Python块逐字一致。实际范围、输入SHA与复现命令见[qa-technical.md](qa-technical.md)及同名JSON；未重复执行测试。有限输入核验不能代替前面的一般性正确性论证，也不代表动画、声音或成片检查已通过。

## 稿件与动画边界

- 18镜36句围绕同一输入展开，首次重复的候选在合法窗口外，删除首字符后必须继续显示重复，不能让“挪一次”看似有效。
- 集合没有两份相同成员；候选新字符在冲突解除后才加入集合，保留原位置格并用状态表现离开当前窗口。
- 第11镜先后删除c、b、旧a，不能瞬间跳到结果而跳过本片承诺的因果动作。
- 第12镜当前3与最长5分开保留；第13镜证明回看明确标出独立回看，不把回退当作正式算法左边界后退。
- 第14镜必须说“平均”，不把期望操作时间说成最坏保证。第15镜用while而不是if；第16镜先加入，再更新长度。
- 17镜边界示意与主例分开；最后完整Python卡静态5秒、明确暂停提示，无新口播或旧字幕。程序、显示JSON和文章代码须逐字一致。

本次已对照script逐镜核读范围与叙事。本文件不表示已听辨生成TTS、完成无字幕连续动画或审过正式MP4。

## 片尾参考资料清单（2026-10-26整理，技术实读仍为2026-10-24）

选三项真实来源，title-author每页最多4项、默认5秒，仅原题/机构：Longest Substring Without Repeating Characters、Set Types — set, frozenset、Time complexity of operations on built-in types。没有明确个人作者，机构为LeetCode、Python Software Foundation。

原完整research基线`4213a233c4c242b04453b8c1215031dc421c2398`，Git blob`8b1069dc030965fe2fcd922ae32b21e97ec496ec`，完整SHA-256`a43a0f61bacd12ee3cd5e8757c5e8353053c4061ad55c5e0b010da5efbb1ed4e`（7183字节）；原article SHA-256`e8db3ffabf00915713e267cb07c2ff38c018114aeca150adcfc44bac8a138bcc`（8223字节）。[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/longest-substring/research.md)及[原全文归档](../../docs/reference-endcards/batch-10/sources-longest-substring-prior-research-4213a233.md)仅为本仓阅读记录，不是官方固定正文。

本批无新GET。R1原题取本research第10行；R2旧article第126行已有完整章节题名，另本地核第9批已保存CPython固定stdtypes.rst第5414行；R3旧Time Complexity为简称，按已有官方time-complexity.rst第4行补齐实际完整原题。三份官方原始文件字节/SHA与基线Git对象一致，26日只核题名/机构，技术verification.checkedAt仍24日；未声称新的官方技术正文阅读或24日网页响应SHA。

| 片尾编号 | 实际原题 | 机构 | 原技术记录 |
| --- | --- | --- | --- |
| R1 | [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/description/) | LeetCode | research第7–15行 |
| R2 | [Set Types — set, frozenset](https://docs.python.org/3/builtins/stdtypes.html#set-types-set-frozenset) | Python Software Foundation | research第17–23行 |
| R3 | [Time complexity of operations on built-in types](https://docs.python.org/3/builtins/time-complexity.html#set-frozenset) | Python Software Foundation | research第25–31行 |


原记录逐字块、官方固定文件完整SHA、原题/机构段落与成本边界见[sources-longest-substring.json](../../docs/reference-endcards/batch-10/sources-longest-substring.json)。保留网页读取成功与shell403失败的原区分；不引用未读editorial，不将独立窗口证明/复杂度推导或有限执行包装为官方题解。当前script复杂度为第16镜，旧research早期第14镜映射仍原样保留，不改写历史。

旧article/research/所有脚注锚点与唯一Python程序全文前缀保持，原150帧代码卡必须保留。未改媒体、solution、freezer、README、source-sha、共享或QA，不预记成片、声音/上线检查或用户认可。
