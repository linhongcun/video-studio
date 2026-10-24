# 策略模式D01：发布记录

## 章节衔接修订（待发布补丁）

用户观看v0.52.0后认为整体问题不大，要求主要章节入口有简短口头承接。本次只重配04/11/15六句、同步延后正文动作到第二句，局部重渲三镜；十三镜原PCM和局部时序保持。新片5292帧、176.4秒，仅增加3.13秒。

新视频SHA-256：`7f5606a875198472c7f8f052c6e0f14f180a1c9c4b21b0055cb8e9ab8da68726`，−16.0LUFS/−3.7dBTP。163项冻结、连续PTS/完整解码、十三镜画面复用比较、实际章节边界及两视口三章seek通过；本地报告见qa-final.md。当前计划补丁v0.54.1，待合并、Release后部署和线上核验；firstRelease仍为v0.52.0。

## v0.52.0首发历史

## 已完成的本地交付

- 制作issue：[#163](https://github.com/linhongcun/video-studio/issues/163)，系列总览：[#161](https://github.com/linhongcun/video-studio/issues/161)。
- EP.23 · 设计模式D01，slug：`strategy-pattern`。
- 成片：5198帧，约2分53秒，1920×1080/30fps，−16.0LUFS、−3.7dBTP。
- 视频完整SHA-256：`c80f9e44ee8eb668fb702266170d4fd8773d14f120e315b568d6ed5d07c27431`。
- 海报完整SHA-256：`cf343bd67aecd80e26f5bb31c905a6fc9811eb1d8e23b43b02daa75dfa8c048e`。
- 完整本地媒体、实际画面与站点检查见 `qa-final.md`、`qa-independent.md` 和站点副本的检查JSON。

## GitHub发布状态

- [PR #192](https://github.com/linhongcun/video-studio/pull/192)已合并，主干与v0.52.0标签提交为`a7442bc1bc8650d81d0aa4cda1b4266bddbdd1c4`。
- [v0.52.0 Release](https://github.com/linhongcun/video-studio/releases/tag/v0.52.0)已于2026-10-24 22:56:23（北京时间）发布。
- Release前自动push部署40104661049已主动取消，避免重复构建；实际交付以Release后的[部署40104729342](https://github.com/linhongcun/video-studio/actions/runs/40104729342)为准。
- Release后的Pages部署40104729342已完成且success，发布提交与标签一致。
- 线上核验于2026-10-24T22:59:24.445321+08:00一次通过，8个canonical普通GET均为200；视频流式完整SHA、海报与VTT逐字节一致，四章、正文锚点、源码、JSON-LD、首页、独立系列、RSS及v0.52.0更新日志均通过。
- 制作issue #163已在线上核验后以`completed`关闭，系列总览#161同步D01完成。
- [v0.52.0历史线上报告](revisions/v0.52.0/online-verification.json)与本期`deployment.json`保留实际结果；未把机器或上线检查写成用户已观看认可。

线上目标：[策略模式视频与配套文章](https://linhongcun.github.io/video-studio/episodes/strategy-pattern/)。线上验证脚本为本期 `verify-online.py`，读取canonical页面、视频、海报、VTT、系列、首页、RSS与更新日志；视频流式完整哈希，不下载另存远程媒体。

用户尚未观看本期，不将本地或线上检查称为用户认可。平台新发未执行。
