# LC.11 题意前置修订

用户指出算法视频默认观众见过原题，要求先讲题意再讲解法。本版替换前两镜四句，默认零刷题前置；修后独立检查不等同用户已观看认可。

- 开头先交代输入、可选内容/限制、目标和返回值。LC11明确高度、任选两边与底边、间隔1/不倾斜/返回最大面积；LC3明确字符串、连续/无重复/尽可能长/返回长度。候选12和3不当整题答案。真实PNG复述检查及实际新MP4各8帧目视均通过，见qa-problem-first-preflight与qa-problem-first-encoded的JSON/MD。
- 第03镜后Main源码后缀、后续40句送模文字与选中takes保持；只重配前4句、通过共享build重建整轨，不声明整条归一化PCM逐字节不变。共享句级字幕、whole放置/样本数和首次术语起音通过，见qa-timing.json、label-onset-strict.txt及voice/qa-problem-first-inputs.json。
- 新前两镜562帧由本期render:opener渲染。其余画面取自已发布媒体，逐镜只在旧旁白结束后的静止尾停补/剪至多1帧；调整为[('07', -1), ('08', 1), ('20', -1), ('21', 1), ('22', -1)]。不在运动/配音过程中删帧，完整Python卡仍150帧。输入Git提交/完整SHA、逐镜范围及实际命令见revisions/problem-first/baseline.json和opener-remix-plan.json，连续PTS及输入未变见opener-remix-result.json。
- 最终6734帧/30fps、画面224.466667秒、容器224.469秒，1080p/H264/AAC48kHz。190项输入冻结核对、完整解码、−16.0LUFS/-3.8dBTP通过。视频10,208,542 bytes，完整SHA256 `0c356319fcbe49b429b17a5afd6b2cbea776fad725a40df60bd1c5b2a5994639`。
- 12个最终采样与新预演保真对照通过，最大平均RGB绝对差1.8320/255，仅作编码保真证据。独立实际检查题意、02→03接点、原正文代表状态和末尾return；卡片从6584到6733帧无旧字幕。
- 四章按新分镜精确派生：[('area', 0.0), ('proof', 45.63333333333333), ('scan', 104.43333333333334), ('code', 177.56666666666666)]。新学习站82页构建/29索引、当前learning-path回归与1440两页局部检查通过；44/36句VTT逐字/全部边界与新分镜一致、四章精确seek、代码卡CC0和原生控件正常。LC3总长的既有0.1秒舍入使页面首轮显示2:51，已改精确frame/fps并单独复验2:50，未重跑无关矩阵。见qa-problem-first-site.json/md；v0.54.2已合并上线，实际GET核验完整视频/海报SHA、字幕字节、四章/锚点、源码入口、学习站目录与真实Release条目通过，见本期online-verification.json及release.md。

旧版QA/媒体/线上记录已归档revisions/problem-first/before-*，原算法测试与不变正文过程沿用已验证证据，不重复执行全量矩阵。未新增逐字ASR、句内词级对齐或全片人工听辨；平台没有新增投稿。
