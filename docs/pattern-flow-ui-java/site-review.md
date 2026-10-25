# D01/D02 产品界面、结构与Java修订：站点检查

执行者：Codex pattern revision site agent。修订版本v0.60.3，实际检查时间2026-10-25T01:44:20.230Z。

在包含最新协作主干的稳定输入上完成一次最终构建、一次历史学习路径回归和4个浏览器用例（两期各1440浅色/390深色）。共18次章节实际seek与短静音播放，最大跳转误差约0.000000667秒。22/24句字幕的每句文字与起止时间均对应冻结分镜，制作/发布/构建/HTTP媒体与海报完整SHA一致；38个发布页面保留，D01↔D02及系列/资料库/RSS入口通过。

D01为4778帧（约159.267秒），Java卡4628起150帧；D02为5328帧（177.6秒），Java卡5178起150帧。每页每视口的卡区0.1/2.5/4.8秒采样均载入完整字幕轨且mode=showing、activeCues=0。实际播放进入卡段再暂停，导出真实1920×1080解码帧。播放器页截图恢复原生字幕默认disabled，不用disabled轨道冒充卡区无字幕。

两期保留原URL、标题、EP23/28、学习顺序、发布日期、首发v0.52.0/v0.58.0、源码入口与平台记录；三种封面保持原字节。当前文章直接同字节复制owner的原生SVG稿，不再使用旧观察者派生文章。Java图文入口为#java。全部页面无水平溢出，SVG字号/锚点按原生属性生效、文本bbox未出界。

实际打开8张最终图：两张Java卡、两张390px Java图文入口、两张窄屏SVG，以及桌面D01/窄屏D02播放器。代码与暂停提示清楚，文章和页面可读；具体文件/SHA见site-visual-review.json。不是全片听辨、ASR、用户观看认可或学习实验。

本地更新日志读取GitHub Releases失败并按现行代码降级外链，未把本地构建写成正式Release条目已通过。Release之后的Pages工作流完成后，继续运行verify-online.py核验13个canonical普通GET、两片完整媒体流SHA与真实Release条目。

根任务收尾发现D01发布目录仍留旧制作报告，本轮另同字节同步两期source-sha256.json、render-result.json和mix-report.json，并写入发布清单。定向核对meta/article/storyboard/video完整SHA未变；这些报告不参与Astro媒体/正文构建，因此未重复构建或18次seek。证据见site-production-reports-sync.json。
