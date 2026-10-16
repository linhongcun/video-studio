# EP.21 分布式事务（distributed-tx）
- storyboard.json（v4，sha 50e1dfab…de1ab）：26 章 39 镜头，7754 帧 @30fps（正片 7326 + 四张章节卡 4×78 + 术语停留 补偿事务 14 / 可靠消息 10 + recap-2 末尾 92）+ 全局片尾卡 60 帧 = 成片 7814 帧；每段一种整屏底色
- 停顿：card-1/2/3 各 78（ch4-1 / ch9-1 / ch14-1 前，原音 31.463 / 75.220 / 119.048 s）、补偿事务 14 + card-4 78（ch19-1 前，158.536 s）、可靠消息 10（ch25-1 前，205.661 s）、recap-2 末尾 92；build_voice.py 在下一句开口前 0.1 s 的句间静音里插入，整轨 voice.wav ≈ 7754 帧；术语标签完整显示 ≥89 帧（均 ≥63）
- 配音：MiMo 冰糖第二次返工定稿（/workspace/share/ep21，整轨 narration.wav sha c3f65e55…，7326 帧；开场 op2-b 停顿 0.2 s；MySQL 整词、TCC 逐字母、Saga 整词）
- 渲染器沿用 EP.20（camera.pushIn + 单条整轨 voice.wav），10 个推镜
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS，TP −1.9 dBTP）；成片 sha 260f4103…；渲染器新增 shot.background 整屏底色
- 封面：Miyazaki 设计稿 cover/ep21-*.png → cover-*.jpg（ffmpeg -q:v 2，同 EP.20；不取视频帧）
