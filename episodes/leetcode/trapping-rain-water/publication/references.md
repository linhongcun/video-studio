# 片尾参考资料 · 接雨水

以下资料对应本片的题意与程序语义。视频片尾仅列原始题名与机构；公式推导、教学示例与算法正确性论证仍是本期独立工作。

**[R1] Trapping Rain Water**

- 机构：LeetCode；未据旧读取记录推断个人作者。
- 年份或版本：LeetCode 42 · 官方题面 · 原读取记录未标发表或更新时间。
- 正式出处：[官方题面](https://leetcode.com/problems/trapping-rain-water/description/)。
- 定位：Problem statement；Examples；Constraints（旧读取返回行18–46）。
- 实际阅读：2026-10-25（原web工具访问为UTC11:49:45，北京时间19:49:45）。本轮沿用已保存的题面阅读记录，没有重新访问题面或官方题解。
- 编者说明：支持非负柱高、每柱宽1、返回总水量及两组官方示例和约束；不把左右最高值算法说成已读官方题解。
- 原题与实读证据：[固定原研究记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/trapping-rain-water/research.md#L3)及[固定工具访问记录](https://github.com/linhongcun/video-studio/blob/4213a233c4c242b04453b8c1215031dc421c2398/episodes-codex/trapping-rain-water/research/source-access.json)。这两项是本仓已读记录，不冒充官方正文快照。

**[R2] Built-in functions**

- 机构：Python Software Foundation；未从Git账号、贡献者或版权行推断个人作者。
- 年份或版本：CPython官方文档固定提交 c436e8d83597c6f8c1bc7e37812c98d46670c29a · 未据此推断平台运行时小版本。所核段落未标独立发布日期。
- 正式出处：[Python官方文档](https://docs.python.org/3/library/functions.html)；本轮实际读取[官方固定源码](https://raw.githubusercontent.com/python/cpython/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/builtins/functions.rst)，出版机构见[同提交文档版权页](https://raw.githubusercontent.com/python/cpython/c436e8d83597c6f8c1bc7e37812c98d46670c29a/Doc/copyright.rst)。
- 定位：len；max；min（固定源码行1256–1260、1344–1354、1382–1392）。原题位于固定源码第4行；机构记录位于copyright.rst第5–7行。
- 实际阅读：2026-10-26，新增核对函数语义和原题/机构，不追记成2026-10-25已读。
- 编者说明：`len`返回元素数，`max`选择较大值，`min`选择较小值；这些说明对应程序中的列数、最高柱高更新和较低挡水高度的取值。文档不证明接雨水算法；为何取两侧最高值的较小值、为何包含当前柱以及三次扫描的复杂度，沿用上文独立推导。

本轮只补资料附录及出处记录，不改原文章、研究、程序或完整Python代码页，也没有重跑旧算法测试。
