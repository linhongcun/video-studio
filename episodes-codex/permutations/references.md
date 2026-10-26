# permutations · 片尾参考资料

技术实读沿用2026-10-25 UTC原记录；本轮整理于2026-10-26（北京时间）。本轮0新GET，未读或引用官方Editorial。Python精确原题和发布机构另由26日已经保存的官方固定RST核对，原字节与完整SHA保留，不以网页<title>后缀推定H1。完整证据见[来源记录](../../docs/reference-endcards/batch-10/sources-permutations.json)。

**[R1] 46. Permutations**

LeetCode · 官方题面 · 实读2026-10-25 UTC

- 正式入口：[原官方题面或章节](https://leetcode.com/problems/permutations/)
- 实际旧请求：[原读取入口](https://leetcode.com/problems/permutations/)
- 实读证据：[既有读取记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/permutations/research/source-access.json)
- 研究范围：[原研究记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/permutations/research.md)
- 原题位置：既有source-access.json · sources[0].title

**编者说明：**官方题面规定独异整数输入、返回全部排列及输出顺序不限。逐位选择、保存副本、撤销选择的方案与正确性、复杂度分析由本期独立推导和执行核验支撑。

**[R2] Built-in Types**

Python Software Foundation · Python 3官方文档 · 技术实读2026-10-25 UTC

- 正式入口：[原官方题面或章节](https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types)
- 实际旧请求：[原读取入口](https://docs.python.org/3/library/stdtypes.html#list.copy)
- 实读证据：[既有读取记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/permutations/research/source-access.json)
- 研究范围：[原研究记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/permutations/research.md)
- 原题位置：固定官方CPython Doc/builtins/stdtypes.rst首题 · 第7行

**编者说明：**可变序列条目说明copy创建浅副本、pop默认移除并返回最后一项。本题元素为整数，复制工作列表可保留独立答案；回退时改变工作列表，不改变已保存的副本。

- 原题固定材料：[官方RST固定版本](https://github.com/python/cpython/blob/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/builtins/stdtypes.rst#L6-L8)
- 发布信息：[官方文档版权页固定版本](https://github.com/python/cpython/blob/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/copyright.rst#L5-L7)

## 使用边界

输入独异、返回所有排列与输出顺序不限由官方题面提供；当前回溯选择树、不变式、撤销顺序与复杂度是本片独立推导。旧源码、原文章和完整Python卡不改。

旧网页连接器记录只覆盖列明的事实和观察行，不冒称完整读完全部Python手册；固定官方RST仅补原题及机构元数据。内部verifiedFacts是原读取记录中的概括，不伪装为官方逐字引文。
