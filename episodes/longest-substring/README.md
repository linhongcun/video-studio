# LC.3 · 无重复字符的最长子串

对应[#79](https://github.com/linhongcun/video-studio/issues/79)，当前制作目录为`episodes-codex/longest-substring/`，站点目录为`episodes/longest-substring/`。用户授权继续选择并制作下一条算法精品，完成检查后按既有GitHub站点持续授权发布；不包含外部平台投稿。

本期围绕“重复了，左边为什么有时要移动多次”展开。用同一教学输入`abcbadea`演示窗口、集合与最长记录：第一次重复需连续移除`a`和旧`b`；曾达到的`cbade`长度为5，最后窗口`dea`长3，但返回仍为5。

文章四章为`goal`、`shrink`、`best`、`code`，与正式冻结分镜的章起点对应。完整Python实现来自`solution.py`，画面读取同源`solution.json`，片尾静态5秒并给暂停提示。正文仅突出当前规则的两处关键代码；无装饰进度条，原生播放器控件保留。

文件入口：`script.md`和`plan.json`记录旁白/镜头；`article.mdx`、`research.md`、`pronunciation.md`记录题解与出处/读音；`visual-direction.md`和`knoll-props.md`规定动作；真实音轨完成后生成`words.json`、`storyboard.json`、冻结清单与QA记录。

配音、起音、铺轨和混音均使用仓内共享实现，不复制算法。正式构建使用本期`remotion/package.json`，冻结与编码检查使用`episodes-codex/_shared/`，站点读取同一份检查通过的媒体副本。

独立技术检查已通过：本期执行源与暴力枚举交叉核对21,845个有限输入及16个显式边界用例，代码/显示JSON/文章逐字一致；具体范围见`qa-technical.md/json`，不把程序核验当作音画或成片验收。

本地制作与检查已完成，合并及线上状态按实际结果写入release.md；不把文字方案当作动态效果通过，不声称用户已观看本期，也不声称未执行的逐字ASR或全片人工听辨。

## 实际交付检查

正式5078帧、约2:49，含末尾150帧代码卡。161项真实输入、完整解码、−16.0LUFS/−3.6dBTP和46帧编码保真通过；独立实际查看10个MP4关键帧。80页站点构建、既有学习路径及1440/390新页检查通过，见qa-final.md、qa-encoded-independent.md和qa-site.md。首发采用v0.53.0，合并与线上结果见release.md；不将这些检查写成用户认可或完整听辨。
