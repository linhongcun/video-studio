# EP.16 事务隔离级别（db-isolation）
- storyboard.json：7 章 12 镜头，2664 帧 @30fps + 全局片尾 60 帧 = 2724 帧；开场大字 0–36、36–45 淡出，第一句字幕第 45 帧进
- 配音：MiMo 冰糖逐句（/workspace/share/ep16 精简流程，整轨 narration.wav sha dd79cdaa…）；build_shot_audio.py 按 timing.json 切出 remotion/public/audio/<shot>.wav
- 字幕严格按 storyboard 数字 from/to；空字幕不画框；水印第 0 帧常显（watermarkFadeIn={false}）
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面：Miyazaki 设计稿 cover/ep16-*.png → cover-*.jpg q95（不取视频帧）
- branding v1.3.0：右上「IT小村」+ 60 帧片尾卡
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
