# EP.21 分布式事务（distributed-tx）
- storyboard.json：9 章 16 镜头，3582 帧 @30fps（正片 3386 + 停顿 136 + 全片末尾留白 60）+ 全局片尾卡 60 帧 = 成片 3642 帧
- 停顿：commit-2 36 帧（ch6-1 前，原音 66.52 s）、message-3 50 帧（ch8-1 前，94.27 s）、eventual-1 49 帧（ch9-1 前，101.36 s）、recap-1 末尾 1 帧；build_voice.py 在下一句开口前 0.1 s 的句间静音里插入，整轨 voice.wav = 3522 帧；术语标签完整显示：两阶段提交 69、可靠消息 69、最终一致 69、分布式事务 81（均 ≥63）
- 配音：MiMo 冰糖（/workspace/share/ep21，整轨 narration.wav sha 8d663d45…，3386 帧）
- 渲染器沿用 EP.20（camera.pushIn + 单条整轨 voice.wav），5 个推镜
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS，TP −2.0 dBTP）；成片 sha a74bb4ff…
- 封面：Miyazaki 设计稿 cover/ep21-*.png → cover-*.jpg（ffmpeg -q:v 2，同 EP.20；不取视频帧）
