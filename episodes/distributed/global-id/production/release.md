# EP.20 站点发布记录

2026-10-24，按用户已授权的旧版重制任务及GitHub持续发布流程，将本期纳入v0.45.4的EP.18–21批次。只上站点，不重发平台。本期按制作和独立检查结果发布，没有将其记为用户已经观看认可。

视频SHA-256：`14bd428ea60068a454310759cbf329e80e33a3f5aef6deed3761c8bce21da471`，规格1920×1080、30fps、4419帧、147.306秒。`episodes/global-id/video.mp4` 使用同一份冻结成片，不在发布阶段重新生成音频或画面。

站点同步文章、研究、脚本、封面、海报、冻结分镜 `storyboard.2fb344e3.json` 与30句字幕，设置实际 `finalVideoFrames`，移除旧时序与旧版标记。保留原发布日期、首发版本和平台链接。当前入口见 [README.md](README.md)。

制作检查证据见 [qa-motion.md](qa-motion.md)、[qa-final.md](qa-final.md)、[source-sha256.json](source-sha256.json) 与 [render-result.json](render-result.json)。检查包括真实编码抽帧、全部字幕/冻结输入核对及完整媒体解码；没有可用官方ASR权重，不声称已做逐字ASR或全片人工听辨。

发布顺序：本地站点构建与逐项核验 → PR合并 → 附注tag及Release → Release后再次部署Pages → 核验线上完整视频SHA、海报、全部VTT、章节、时长及更新日志 → 将对应 [#72](https://github.com/linhongcun/video-studio/issues/72) 以 `completed` 关闭。未执行的平台新发事项不勾选完成。

## 片尾参考资料补齐 · v0.71.4

[PR #347](https://github.com/linhongcun/video-studio/pull/347)已合并`daccc593ecfc9333600a2e3ad310c900746497ed`，附注tag与[Release v0.71.4](https://github.com/linhongcun/video-studio/releases/tag/v0.71.4)后[Pages40297652180](https://github.com/linhongcun/video-studio/actions/runs/40297652180)成功。2026-10-26T17:17:47+08:00正式线上核验通过。

本期8项原始题名与作者/机构、2页，每页5秒；最终5946帧，完整SHA-256：`64276c2b4d9977a65151ec378eacc52fd1ff1acfd915726fab756dd9e007e941`。原Git正文全帧/PTS及AAC/PCM保持，原文章/研究/脚注、创建与首发信息保留。技术实读日期沿用24/25日，26日题名补查独立记录；无新配音或正文重渲。

本批来源、冻结、实际片尾和6组播放器检查通过，13项完整GET核对视频/字幕/海报/页面/更新日志与发布身份，见[第六批证据](../../docs/reference-endcards/batch-6/README.md)。累计23片已具备参考片尾；只上GitHub站点，无平台重发，不预记新版观看认可。
