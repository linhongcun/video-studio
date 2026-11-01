# MQ04 / EP44 制作与发布记录

制作issue [#312](https://github.com/linhongcun/video-studio/issues/312)，系列总览 [#308](https://github.com/linhongcun/video-studio/issues/308)，slug为kafka-send-confirmation。

当前已完成本期稿件/模型/句级音轨与分镜，独立动态预检接受并停写冻结，正式媒体与四幅图已产出并完成根代理实际复核；本地与线上网站核验已通过，GitHub主干、Release和Pages交付完成，#312已completed关闭。本页只按实际产物补记，不沿用上期参数或回执。

开工基线 `2c54aa7c5f4e3236500728d3078b356d06625099`，分支codex/mq04-20261030，记录见startup.json。制作与发布前按实际主干核对上游差异、冻结输入交集及版本，最终首发为v0.96.0；merge/Release/Pages身份见文末。

交付范围沿RULES STATUS持续授权：GitHub主干、Release与Pages；平台无本轮新发。本次已在完整媒体与线上实际播放器等必要检查通过后，以completed关闭#312并同步#308。不将教学模型写成真实Kafka集群实验，也不将技术检查写成用户观看认可。


## 正式编码前已完成的输入检查

定稿为11镜22句、4章；正文3417帧/113.9秒，完整voice.wav SHA-256为 `2dc60dc34160c538c8d0e9f41dbb18b0c0e91b6d558e5d6eb542520dd18ac7e4`。来源/稿件、有限教学模型、句级声音来源与信号、三比例封面、颜色小样与实际动态预检按本期报告通过。没有真实Kafka Broker/Java Producer、网络故障注入或业务副作用实测，不将源码/模型路径写成实测。

独立动态最终报告qa/motion-independent-final.json接受正式冻结/编码。早期92份PNG/DOM、最终定向19份及实际连续小样的范围分别保留；04成功回传与08终态超时的标题/说明曾过早出现，已在正式编码前按实际状态守卫修正，旧失败报告和图保留，不追认为最终整源重跑。

正式清单175项，source-sha256.json完整SHA-256为 `5886ba7ec04585ed01d70c459ac385d2ae8194522cb4626f58a8e2986ca5c671`。生产输入已停写。编码前计划在正文后追加150帧/5秒原题机构资料页，实际成片符合3567帧/118.9秒及该附录区间；输出身份、解码、混音与附录保真结果见后文。


## 实际成片与本地安装

正式video.mp4为3567帧/118.9秒、6,189,865字节，完整SHA-256为 `a3dd3f640b0032e363d7010410b496c6321a951b2e6c257ee2fde1efda3c2e13`；正文3417帧，资料页3417–3566共150帧。实际混音−16LUFS、−3.7dBTP；完整解码、limitedBT709、正文前缀/AAC/PCM与附录保真以及175项冻结只读复验通过。独立成片检查55整数帧/10合辑实际查看通过，精确3416→3417的尾句字幕/资料边界、资料首中末两项原题/机构正确，见qa/encoded-independent.json。

根代理实际查看四幅准确图位JPEG、资料页首/末及两组相邻状态联系图，通过本轮有界成片/图文实看；图从实际limitedBT709明确转换到fullBT601，冻结文章不改。正式publisher已在本地安装23文件，媒体与真实初建/首发时间元数据按qa/publication-dates.json记录；此处记录本地安装身份，远程交付证据见文末。站点build与实际本地网站结果见下一节。


## 本地网站实际检查

本轮site完整build通过：52份日期/资料输出、51篇当前文章、84处原文和66幅有效图。独立preview使用本任务4324端口，未干预既有服务。普通本地HTTP全量GET核对生产、发布、dist与实际响应的完整MP4 SHA一致。

qa/site-independent/report.json记录48项实际浏览器动作与20次严格RVFC/ffprobePTS核验，四课目录、22cue默认关闭避免双字幕、四章/四图回看、四处原文悬停/点击/点按/键盘、实际播放/暂停、Fullscreen API及同标签页原图入口通过，页面JS错误为空。实读桌面暂停资料、844×390模拟手机全屏、A2手机浮层和原图四张截图；资料两项原题/机构清楚，原生暂停控件保留，所看图无等待弧。

qa/site-supplement/report.json另记两项A2长浮层实际触摸滚动，亮暗主题底部出处、定位和固定原文链接可见并可键盘聚焦；实际查看两张补充截图后才标visualReviewed。均为Chromium视口/触屏模拟与Fullscreen API，不是物理手机或原生移动播放器测试。本地与远程结果分别留证，实际远程交付见下一节。


## GitHub上线、线上核验与收尾

[PR #440](https://github.com/linhongcun/video-studio/pull/440)合并提交 `8d852e2ccf8e751efbd6f095d508edca991410a5`，首发[Release v0.96.0](https://github.com/linhongcun/video-studio/releases/tag/v0.96.0)已发布。Release后workflow_dispatch [Pages 41035467904](https://github.com/linhongcun/video-studio/actions/runs/41035467904)在相同SHA成功（created2026-10-30T09:43:11Z，updated09:54:54Z）。本轮自身发布前push重复运行41035382103已确认主动取消，不记作媒体或构建失败；未修改部署工作流。

[online-verification.json](online-verification.json)于北京时间2026-10-30T17:55:05.689215+08:00记录14项普通canonical完整GET通过，完整MP4、16:9海报、VTT与四幅图SHA与发布输入一致，4章22cue、四课MQ目录、入口与真实Release更新日志正确，无Range或缓存绕过。最终线上MP4仍为 `a3dd3f640b0032e363d7010410b496c6321a951b2e6c257ee2fde1efda3c2e13`。

[qa/site-online-native/report.json](qa/site-online-native/report.json)为直接原生Chromium canonical HTTPS的48项实际动作/20次严格PTS，errors为空，未使用TLS忽略、响应回填或fallback；[qa/site-online-supplement/report.json](qa/site-online-supplement/report.json)补A2长浮层亮暗两主题实际触摸滚动。共实际查看六张线上原图后标visualReviewed，资料题名/机构与原生控件分离，所看参考图无等待弧，A2底部出处和固定原文链接可见可聚焦；物理手机/原生移动端播放器能力不扩大。

#312已在2026-10-30T09:57:41Z以completed关闭，#308已同步当前4/9核心已交付、其余5题未开工，原14题维持取消。仅GitHub主干、Release与Pages，无外部平台新发。有限教学模型、抽帧/截图实读与信号检查不冒称真实Broker/Java Producer/网络故障/序列化器/业务副作用实验、逐字ASR、全片人工语义听辨、物理手机或学习效果验证，不预记用户已观看认可。实际发布身份与证据索引见[publication.json](publication.json)。
