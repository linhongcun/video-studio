# EP.21 分布式事务（distributed-tx）
- storyboard.json：13 章 25 镜头，6383 帧 @30fps（正片 6076 + 标签停留 247 + 全片末尾留白 60）+ 全局片尾卡 60 帧 = 成片 6443 帧（返工版：旁白讲全两阶段提交 / TCC / Saga / 可靠消息）
- 停顿：commit-2 41（ch6-1 前，原音 63.01 s）、tcc-4 52（ch8-1 前，107.72 s）、saga-3 61（ch10-1 前，144.42 s）、message-3 50（ch12-1 前，177.89 s）、eventual-1 41（ch13-1 前，186.18 s）、recap-1 末尾 2；build_voice.py 在下一句开口前 0.1 s 的句间静音里插入，整轨 voice.wav = 6323 帧；术语标签完整显示：两阶段提交 / 预留确认取消 / 补偿事务 / 可靠消息 / 最终一致 69、分布式事务 81（均 ≥63）
- 配音：MiMo 冰糖返工版（/workspace/share/ep21，整轨 narration.wav sha 0a9baec4…，6076 帧；MySQL 整词、TCC 逐字母、Saga 整词）
- 渲染器沿用 EP.20（camera.pushIn + 单条整轨 voice.wav），10 个推镜
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS，TP −2.0 dBTP）；成片 sha 01ac3b0e…
- 封面：Miyazaki 设计稿 cover/ep21-*.png → cover-*.jpg（ffmpeg -q:v 2，同 EP.20；不取视频帧）
