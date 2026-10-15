# EP.19 分库分表（db-sharding）
- storyboard.json：13 章 23 镜头，3915 帧 @30fps（含 5 处停顿共 166 帧，全片末尾留白 60 帧）+ 全局片尾卡 60 帧 = 3975 帧
- 停顿：46（@1796）、3（@2117）、44（@2417）、36（@2679）、37（@3110）（帧位为原始配音帧）；build_voice.py 在对应章首句前 0.1 s 的句间静音里插入，生成整轨 remotion/public/audio/voice.wav（3855 帧）；9 个术语标签完整显示均 ≥66 帧
- 配音：MiMo 冰糖逐句（/workspace/share/ep19，整轨 narration.wav sha b135a8f0…，3689 帧；ch9-2「跨片」、ch6-3「分片键」重配，ch6-3 句尾不截断）
- 渲染器沿用 EP.18，新增 camera.pushIn（8 个镜头，静止段 1.00→1.04 轻推镜，origin [960,470]，字幕和水印不缩放）；配音改为单条整轨；实物图全部内联本期 assets/*.svg
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS，TP −1.9 dBTP）；成片 sha b537afcd…（r2：table-2 四张表与库框同时淡入、色条依次点亮、去掉推镜；reshard-1 黄站随「新」出现，推车红站→黄站）
- 封面：Miyazaki 设计稿 cover/ep19-*.png → cover-*.jpg q95（不取视频帧）
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
