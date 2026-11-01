# longest-substring · 片尾参考资料

采用 `presentation: title-author`：实际原题与机构，每页最多4项、默认5秒；保留原Python代码卡150帧，再接资料名单，不显示quote/date/hint。这里仅生产来源，不记录媒体已生成/已复核。

技术实读日期为 **2026-10-24**。本批零新GET，Python完整原题/发布机构于 **2026-10-26** 只在本地核对第9批已保存官方固定原始文件，未重新阅读技术正文；完整原始响应SHA不冒充24日网页响应SHA。无明确个人作者，省略author。

完整证据见[sources-longest-substring.json](../../docs/reference-endcards/batch-10/sources-longest-substring.json)；[固定既有实读记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/longest-substring/research.md)及[原研究归档](../../docs/reference-endcards/batch-10/sources-longest-substring-prior-research-4213a233.md)是本仓历史记录，不是官方固定正文。

- 基线：`4213a233c4c242b04453b8c1215031dc421c2398`
- 原research Git blob：`8b1069dc030965fe2fcd922ae32b21e97ec496ec`
- 原research完整SHA-256：`a43a0f61bacd12ee3cd5e8757c5e8353053c4061ad55c5e0b010da5efbb1ed4e`（7183字节）
- 原article完整SHA-256：`e8db3ffabf00915713e267cb07c2ff38c018114aeca150adcfc44bac8a138bcc`（8223字节）

## R1 · Longest Substring Without Repeating Characters

- 发布方：LeetCode
- 版本：LeetCode 3 · 官方题面（未标发布日期或更新时间）
- 正式链接：[Longest Substring Without Repeating Characters（官方资料）](https://leetcode.com/problems/longest-substring-without-repeating-characters/description/)
- [既有实读记录（2026-10-24，R1）](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/longest-substring/research.md#L7-L15)
- 对照题面：[无重复字符的最长子串（力扣官方中文题面）](https://leetcode.cn/problems/longest-substring-without-repeating-characters/description/)

- 原题依据：2026-10-24既有实读记录research.md第10行：LeetCode 3.之后的英文原题
- 技术阅读范围：中英文题目正文、示例与约束；不包含未读官方editorial
- 当前镜头对应：01, 02, 03, 04, 19

旧主张记录：输入是字符串，返回无重复字符的最长子串长度；子串要求连续；长度范围0..100000，字符可以包含英文字母、数字、符号和空格。

## R2 · Set Types — set, frozenset

- 发布方：Python Software Foundation
- 版本：Python 3 Library Reference（旧记录未标小版本）
- 正式链接：[Set Types — set, frozenset（官方资料）](https://docs.python.org/3/builtins/stdtypes.html#set-types-set-frozenset)
- [既有实读记录（2026-10-24，R2）](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/longest-substring/research.md#L17-L23)
- [官方题名依据（固定版本，2026-10-26本地核对）](https://github.com/python/cpython/blob/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/builtins/stdtypes.rst)

- 原题依据：旧article.mdx第126行的完整章节题名；本地复用官方固定stdtypes.rst第5414行heading核对（26日题名/机构核对，非新技术实读）
- 技术阅读范围：Set Types：集合无序、不同可哈希成员、成员判断、add与remove；不作为最坏常数时间保证
- 当前镜头对应：05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18

旧主张记录：set是不同可哈希对象组成的无序集合，不记录元素位置或插入次序；支持成员判断、add和remove。

复用已存官方原始响应：[docs/reference-endcards/batch-9/two-sum-stdtypes.rst.source](../../docs/reference-endcards/batch-9/two-sum-stdtypes.rst.source)，完整SHA-256 `766d7f02b3872eedbffda498bfd0a23225a6082c18fdf02e2b3f420817f2422b`；只核题名与机构，没有新技术实读。

## R3 · Time complexity of operations on built-in types

- 发布方：Python Software Foundation
- 版本：Python 3 · 官方内置类型复杂度文档（旧记录未标小版本）
- 正式链接：[Time complexity of operations on built-in types（官方资料）](https://docs.python.org/3/builtins/time-complexity.html#set-frozenset)
- [既有实读记录（2026-10-24，R3）](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/longest-substring/research.md#L25-L31)
- [官方题名依据（固定版本，2026-10-26本地核对）](https://github.com/python/cpython/blob/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/builtins/time-complexity.rst)

- 原题依据：本地复用已保存官方固定time-complexity.rst第4行原始页题，26日只补题名/机构；原技术读取为research.md第25–31行的24日记录
- 技术阅读范围：set/frozenset复杂度段及脚注；平均/摊还成本与哈希碰撞边界
- 当前镜头对应：16

旧主张记录：成员判断、add与remove的平均复杂度为`O(1)`；add有摊还说明，哈希碰撞可令相应操作退化为线性。平均/摊还成本不能改写成所有输入下的最坏常数保证。

复用已存官方原始响应：[docs/reference-endcards/batch-9/two-sum-time-complexity.rst.source](../../docs/reference-endcards/batch-9/two-sum-time-complexity.rst.source)，完整SHA-256 `57a0ec0af127c75d556a2e160c079f5d2fe81a92d89634b50ecf132b38e26c17`；只核题名与机构，没有新技术实读。

## 边界与保留

R1不背书本期逐行程序或独立不变式；R2集合无序语义不提供最坏常数时间保证；R3平均/摊还与碰撞边界不替代本期线性操作次数证明。原有限执行继续按旧身份保留，没有新测试；不引用未读editorial，不把原shell403记录写成成功抓取。

旧article/research完整前缀、三脚注、全部锚点和唯一Python块保留。未修改freezer、README、source-sha、solution/代码、发布episodes、shared、QA或媒体，不预记新成片/上线/用户认可。
