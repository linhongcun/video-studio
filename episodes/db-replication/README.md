# EP.18 主从复制和读写分离（db-replication）
- storyboard.json：10 章 22 镜头，4506 帧 @30fps（含 4 处术语标签停顿共 172 帧，recap-2 末尾留白 60 帧）+ 全局片尾卡 60 帧 = 4566 帧（与 EP.17 同规则：3850+60=3910）
- 标签停顿：主从复制 38（@1026）、主从延迟 42（@2025）、异步复制 49（@2528）、读写分离 43（@4094）（帧位为原始配音帧）；落在镜头尾的无声段，由逐镜切音自然留空（不改整轨）；8 个术语标签完整显示均 ≥63 帧
- 配音：MiMo 冰糖逐句（/workspace/share/ep18，整轨 narration.wav sha 93324572…（v3：「一份」改读 yí 重配 ch2-2、ch4-3；ch6-3 改「主从延迟」），4274 帧）；build_shot_audio.py 按 timing.json 切出 remotion/public/audio/<shot>.wav
- 渲染器沿用 EP.17：从库按 delayFrames 推后、信号线/圆点（dotStopAt 断信号）、手机昵称文字节点、w/h 动画
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面：Miyazaki 设计稿 cover/ep18-*.png → cover-*.jpg q95（不取视频帧）
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
