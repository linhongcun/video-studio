# EP.14 数据库索引（db-index）
- storyboard.json：6 章 12 镜头，3645 帧 @30fps + 全局片尾 60 帧 = 3705 帧（123.5 秒）；封面帧 1632（index-2 第 260 帧）
- 配音：MiMo 冰糖逐句（/workspace/share/ep14，timeline.json；ch3-4「这份索引，…」第 2 轮重配），B+树 送 TTS 写「B 加树」
- 工具链：map_timing.py <timeline.json> → gen.py → validate.py；remotion/public/audio/<shot>.wav 由逐句 wav 按 timing.json 放置
- 制作：`cd remotion && npm ci && npm run render`（--bundle-cache=false，mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面：cover-spec.json（Miyazaki 草稿，主图改为截帧 assets/cover-poster.svg），`npm run covers -- db-index`
- branding v1.3.0：右上「IT小村」+ 60 帧片尾卡
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
