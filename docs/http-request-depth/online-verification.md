# EP.01 技术细节修订：线上核验

[v0.68.2](https://github.com/linhongcun/video-studio/releases/tag/v0.68.2)已由PR #288合并，附注标签提交`f1fe833c70ee0a6c9e3296ba2710b77f05a34823`与[Release后手动部署40190399664](https://github.com/linhongcun/video-studio/actions/runs/40190399664)的head一致；部署成功后实际核验时间为`2026-10-25T19:53:15.399929+08:00`（北京时间）。

首轮9次完整HTTPS响应、共9,691,106字节通过。成片5406帧/180.2秒，9,161,920字节，完整SHA-256为`593c528daae0aca8540d9daa34e53455fce6776fcdc330ff3ff705564234a1c6`；海报完整SHA与制作、canonical、tag一致。34句字幕逐句文字及毫秒时序、七章未舍入起点与锚点、媒体/源码/原生控件、日期版`2026-10-25 19:38:59 版`、创建/首发日期及RSS首发保持，request系列/库/首页和本次Release自己的日志项通过。日志项只关联EP01，非任务canonical按最终基线`2ca6e1e0661bbb2b9683f7909de5c0949272ec04`保持。

线上读取与精确身份见[JSON](online-verification.json)，实际尝试见[attempts](online-attempts.json)。本地实际播放/字幕/seek来自原候选真实检查，新候选按完整媒体/SB/VTT及播放器源码SHA复用并定向检查页面，范围见[本地QA](qa-site.json)。不声称完成配音人工听辨、逐字ASR、完整线上播放或用户观看认可；未重发外部平台。
