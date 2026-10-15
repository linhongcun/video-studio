# EP.20 全局唯一 ID（global-id）
- storyboard.json：9 章 14 镜头，2739 帧 @30fps（正片 2633 + 停顿 46 + 全片末尾留白 60）+ 全局片尾卡 60 帧 = 成片 2799 帧
- 停顿：autoinc-2 7 帧（原音帧 1292，ch5-1 前）、snowflake-3 39 帧（原音帧 2105，ch7-1 前）；build_voice.py 在下一句开口前 0.1 s 的句间静音里插入，整轨 voice.wav = 2679 帧；术语标签完整显示：自增 66、雪花算法 66、时钟回拨 97、全局唯一 ID ≥84（均 ≥63）
- 配音：MiMo 冰糖（/workspace/share/ep20，整轨 narration.wav sha 9db4978f…，2633 帧）
- 渲染器沿用 EP.19：camera.pushIn（8 镜，静止段 1.00→1.04，origin [960,470]，字幕和水印不缩放）；配音单条整轨；实物图全部内联本期 assets/*.svg
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS，TP −2.0 dBTP）；成片 sha 78bfad13…
- 封面：Miyazaki 设计稿 cover/ep20-*.png → cover-*.jpg（不取视频帧）
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
