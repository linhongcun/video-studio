# EP.21 站点发布记录

2026-10-24，按用户已授权的旧版重制任务及GitHub持续发布流程，将本期纳入v0.45.4的EP.18–21批次。只上站点，不重发平台。本期按制作和独立检查结果发布，没有将其记为用户已经观看认可。

视频SHA-256：`4f01d09aceeab441d82b162caf90337b99faff4388b015978d29469a506c4356`，规格1920×1080、30fps、3791帧、126.378秒。`episodes/distributed-tx/video.mp4` 使用同一份冻结成片，不在发布阶段重新生成音频或画面。

站点同步文章、研究、脚本、封面、海报、冻结分镜 `storyboard.2a871098.json` 与28句字幕，设置实际 `finalVideoFrames`，移除旧时序与旧版标记。保留原发布日期、首发版本和平台链接。当前入口见 [README.md](README.md)。

制作检查证据见 [qa-motion.md](qa-motion.md)、[qa-final.md](qa-final.md)、[source-sha256.json](source-sha256.json) 与 [render-result.json](render-result.json)。检查包括真实编码抽帧、全部字幕/冻结输入核对及完整媒体解码；没有可用官方ASR权重，不声称已做逐字ASR或全片人工听辨。

发布顺序：本地站点构建与逐项核验 → PR合并 → 附注tag及Release → Release后再次部署Pages → 核验线上完整视频SHA、海报、全部VTT、章节、时长及更新日志 → 将对应 [#73](https://github.com/linhongcun/video-studio/issues/73) 以 `completed` 关闭。未执行的平台新发事项不勾选完成。
