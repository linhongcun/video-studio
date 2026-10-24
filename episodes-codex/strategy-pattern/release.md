# 策略模式D01：发布记录

## 设计思想修订（v0.56.1待发布）

2026-10-25，用户指出v0.54.4过多讲函数和参数，要求回到不绑定语言的设计思想并更新经验教训。本轮11镜22句、4410帧约2分27秒，视频完全移出语法，围绕稳定流程、变化策略、共同约定、外侧选择、委托、维护边界与成本；具体语言仅在图文可选附录。

新视频完整SHA：`9293cf4d66319a44ac7808f5f75d8bdd1da3a3cec627b8da4d57f802466a1a57`，7,927,803字节，1080p/30fps/AAC48k，-16.0LUFS/-3.8dBTP。125源、完整解码/PTS、实际新音轨相关性、独立19张正式帧（根另9张）与两视口8次seek/22字幕通过。具体范围见qa-final.md和qa-ideas-independent.md。

经验与教训已更新：L030、S017，并纠正L027/S016把函数传参当核心目标的局限。当前待合并、Release后部署与线上核验；以下旧版本均为历史，不作当前线上通过结论。


## 新手讲解重制（v0.54.4已上线）

2026-10-25，用户明确授权根据新手反馈调整并完成上线。当前13镜26句、4895帧约2分43秒；只保留会员/活动两种办法，直接解释函数本身与结果、参数对应、先选择后执行，并保留自然章节承接和成本边界。改价/新客注册/完整校验留在图文拓展。

新视频完整SHA-256：`a7056ae8ccfe6783063b6c679174fa5d15ab410cac0628fe5de12e7fcc9e6696`，8,674,537字节，1080p/30fps/AAC48k，−16.0LUFS/−3.7dBTP。137输入冻结、完整解码与PTS连续性、独立实际成片/字幕及两视口8次seek验收通过；本轮报告见qa-final.md、qa-teaching-beginner.md及site-beginner检查记录。

- [PR #216](https://github.com/linhongcun/video-studio/pull/216)已合并，提交与附注标签为`277ef7091994bedf1a2c48be978a69a59e7994a3`。
- [v0.54.4 Release](https://github.com/linhongcun/video-studio/releases/tag/v0.54.4)于2026-10-24T16:52:29Z（北京时间2026-10-25 00:52:29）发布。
- 重复push部署40113533206已取消；实际交付以Release后的[Pages部署40113587396](https://github.com/linhongcun/video-studio/actions/runs/40113587396)为准，2026-10-24T16:58:11Z完成且success，head与标签一致。实际结果见deployment.json。
- 线上核验于2026-10-25T00:58:39.395227+08:00一次通过：8个canonical普通GET全部200，视频8,674,537字节完整SHA、原海报、26条VTT逐字节一致；新标题、四章0/796/1514/4166帧、目录、源码、JSON-LD、首页、系列、RSS与v0.54.4更新日志均通过。见[完整线上报告](../../episodes/strategy-pattern/online-verification.json)。
- #163已在核验后以completed关闭，#161同步当前新手版。用户尚未观看本版，不将编辑或线上检查称作用户认可；平台未新发。

firstRelease仍为v0.52.0。以下v0.54.1及v0.52.0保留为历史，不作为新版线上核验。


## 章节衔接修订（v0.54.1已上线）

用户观看v0.52.0后认为整体问题不大，要求主要章节入口有简短口头承接。本次只重配04/11/15六句、同步延后正文动作到第二句，局部重渲三镜；十三镜原PCM和局部时序保持。新片5292帧、176.4秒，仅增加3.13秒。

新视频SHA-256：`7f5606a875198472c7f8f052c6e0f14f180a1c9c4b21b0055cb8e9ab8da68726`，−16.0LUFS/−3.7dBTP。163项冻结、连续PTS/完整解码、十三镜画面复用比较、实际章节边界及新版学习站两视口三章seek通过；本地报告见qa-final.md。firstRelease仍为v0.52.0。

- [PR #198](https://github.com/linhongcun/video-studio/pull/198)已合并，提交与附注标签为`7fcc0529c476657e48695c231d56b764002a4332`。
- [v0.54.1 Release](https://github.com/linhongcun/video-studio/releases/tag/v0.54.1)于2026-10-24T15:38:48Z发布；只上站点，不重发平台。
- Release前的本次push部署40107899978取消，实际交付以Release后的[Pages部署40107945142](https://github.com/linhongcun/video-studio/actions/runs/40107945142)为准。后者于2026-10-24T15:40:51Z完成且success，head与标签提交一致，实际结果见deployment.json。
- 线上核验于2026-10-24T23:41:19.770526+08:00一次通过：8个canonical普通GET均200；视频9,542,813字节的完整SHA、海报及32句VTT逐字节一致。四章起点0/907/3188/4541帧、目录当前课、正文锚点、源码、JSON-LD、首页、系列、RSS及v0.54.1更新日志通过。完整结果见[线上报告](../../episodes/strategy-pattern/online-verification.json)。
- #163已在核验通过后再次以completed关闭，#161同步当前补丁状态。用户已观看原版并提出本次反馈；新版尚无用户观看反馈，不把核验写成用户认可。

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
- [v0.52.0历史线上报告](revisions/v0.52.0/online-verification.json)与[历史部署结果](revisions/v0.52.0/deployment.json)保留实际结果；未把机器或上线检查写成用户已观看认可。

线上目标：[策略模式视频与配套文章](https://linhongcun.github.io/video-studio/episodes/strategy-pattern/)。线上验证脚本为本期 `verify-online.py`，读取canonical页面、视频、海报、VTT、系列、首页、RSS与更新日志；视频流式完整哈希，不下载另存远程媒体。

用户先看v0.52.0提出章节衔接反馈，后看v0.54.1仍认为新手难理解；当前v0.54.4尚无用户观看反馈。平台新发未执行。
