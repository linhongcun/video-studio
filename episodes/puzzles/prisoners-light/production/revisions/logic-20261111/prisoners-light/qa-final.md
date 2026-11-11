# P10 一盏灯 · 2026-11-11逻辑修订验收

源、实际声音装配、独立动态与实际MP4复核、默认完整媒体检查及两张JPEG导出/制作者实看已完成；待主agent统一站点接入与播放器/线上核验，未改publication或发布。

- 修改范围为03第一句与04两句，共3句新take，其余25句完整复用选定take。补足把累计集中到一人的选择依据，以及亮→亮无新信号、发信人擅自关灯会丢待收信号、未成功发送时资格保留的因果。
- 规则预览与实际主例分开。错误关灯全程显著标记为反事实，原共享状态保持；退出明确回到亮＋未发，05独立初始化原12访。其他场景及Walk流程逐字保持，model同SHA；纯DOM任意灯态标记的收窄及旧源身份单独保留在qa/pending-marker-correction.json、source-scope-v2.json。
- 配音前独立四问审读已由root及audio_qa完成，见qa/script-logic-review.json。实际新3句和25旧句输入身份、共享整轨与时序见qa/voice-reuse-and-timing.json；独立音频回执在docs/archive/2026-11/puzzles-followup-logic/audio/prisoners-light/。25句的75份WAV/raw/文本逐项同SHA，新3句raw→48k转换、cut长度和新整轨切片通过。没有本轮ASR或语义听辨结论。
- 实际正文6362帧、14镜28句、5章，完整新WAV为a13eb3f4e69616a21bc9be9b186296f72b15eed3bd8a2ceecb968e077ce0531a；整条旧PCM和后段时间戳不作为保留条件。声音未加速，未另加hold；源轨信号−16 LUFS，内部真峰约−2.2dBTP，实际混音为−16 LUFS／−3.7dBTP，完整解码与正文/资料保真通过。
- 协议数据及有限模型的旧字节复用，另在本轮只读重新计算10916可达状态、82639转移、1122660不变量实例，结果吻合，见qa/model-recomputed.json。不以有限运行替代任意有限人数的安全性与公平完成论证。
- 独立动态预检覆盖21个过程/边界时点、3张原生字幕图与14项实际DOM条件；任意灯态字段补采2025帧，PNG同SHA证明无视觉变化。实际范围和当前源绑定见docs/archive/2026-11/puzzles-followup-logic/motion/prisoners-light/preflight-visual-review.json及preflight-current-source-binding.json。制作者另查看qa/caption-v1的3张最长字幕样张，未见COPYFIT或字幕/机制区相互覆盖。
- 当前169项实际输入冻结，manifest完整SHA为b5da6c08aa85690f658a3c588664c58c3a85c8647eae65ddcffd07bdb2faa79d；编码前fetch确认HEAD/origin/main仍为27329c38aae4e8388a9999ab1c357fa9c8783fd9。fresh npm ci按本期锁文件安装，类型及来源预检通过；来源预检不冒称本轮重新阅读原文。
- 文章沿当前已维护稿，仅改两处Figure seekTo为87.7与156.2，精确2631/4686帧；正文、结构、SourceQuote及出处保持。五章起点为0、895、2076、4809、5869帧，见qa/article-timing-plan.json和stage-guide.md。截图仅向新修订article/输出，不写publication。
- 选定历史制作文件与整个当前publication均与27329c38基线同SHA，见qa/historical-preservation.json。旧来源、冻结、媒体与QA身份保留，未因本轮反馈回填旧验收。

本期尚未改publication或发布；统一接入由主agent处理。检查限于实际记录的脚本、信号、有限模型、动态与后续媒体范围，无全片实时观看、ASR、语义听辨、实体手机或用户观看认可声明。GitHub持续授权不扩展为外部平台重发。

默认完整成片为6512帧／217.0666667秒（正文[0,6362)、资料[6362,6512)），11,313,057字节，完整SHA为 `a8bfe657f39ff9b08688ffd410775829ef593c116deb54cdb7612b825b4e018d`。`verify.py --final` 核对解码、H.264/AAC、1920×1080／30fps及媒体身份通过；资料adapter另核对limited BT.709。两张JPEG从新MP4精确2631/4686帧导出并实际查看，见qa/article-image-export.json与qa/article-image-visual-review.json；只改时间映射后稳定画面字节与旧图相同。独立实际MP4的29帧（8张合辑＋4张原尺寸图）视看通过，核对03/04因果、反事实与复原、05独立初态、待收与完成的区分及资料首末；见docs/archive/2026-11/puzzles-followup-logic/motion/prisoners-light/encoded-visual-review.json。此为选定编码帧检查，不是全片实时观看、语义听辨或播放器检查。
