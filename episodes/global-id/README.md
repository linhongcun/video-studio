# EP.20 全局唯一 ID（global-id）
- storyboard.json：9 章 15 镜头，2649 帧 @30fps（含 snowflake-3 停顿 40 帧，全片末尾留白 60 帧）+ 全局片尾卡 60 帧 = 2709 帧
- 停顿：40（@1989，snowflake-3「雪花算法」）；build_voice.py 在 ch7-1 开口前 0.1 s 的句间静音里插入，整轨 voice.wav = 2589 帧；4 个术语标签完整显示：自增 66、雪花算法 66、时钟回拨 97、全局唯一 ID 87（均 ≥63）
- 配音：MiMo 冰糖（/workspace/share/ep20，整轨 narration.wav sha 457d3369…，2549 帧）
- 渲染器沿用 EP.19：camera.pushIn（8 镜，静止段 1.00→1.04，origin [960,470]，字幕和水印不缩放）；配音单条整轨；实物图全部内联本期 assets/*.svg
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS，TP −2.0 dBTP）；成片 sha 9f79a650…
- 封面：Miyazaki 设计稿 cover/ep20-*.png → cover-*.jpg（不取视频帧）
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
