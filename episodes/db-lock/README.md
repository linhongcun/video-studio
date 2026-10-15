# EP.17 数据库锁（db-lock）
- storyboard.json：10 章 17 镜头，3850 帧 @30fps（含 6 处术语标签停顿共 151 帧，recap-2 末尾留白 60 帧）+ 全局片尾卡 60 帧 = 3910 帧（与 EP.16 同规则：2664+60=2724）
- 标签停顿：丢失更新 22（603–624）、写锁 21（1040–1060）、读锁 34（1383–1416）、死锁 26（2227–2252）、悲观锁 26（2839–2864）、乐观锁 22（3286–3307）；落在镜头尾的无声段，由逐镜切音自然留空（不改整轨）
- 配音：MiMo 冰糖逐句（/workspace/share/ep17，整轨 narration.wav sha 3487654c…（v3：行→háng 重配 ch5-2、ch10-1），121.291 s）；build_shot_audio.py 按 timing.json 切出 remotion/public/audio/<shot>.wav，切点首尾 5 ms 振幅 ≤ 44/32768
- 渲染器沿用 EP.16；实物图全部 staticFile 直出；动画属性 rotation 与 rotate 同义（dead-2 时钟旋转）
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面：Miyazaki 设计稿 cover/ep17-*.png → cover-*.jpg q95（不取视频帧）
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
