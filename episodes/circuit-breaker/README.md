# EP.12 熔断降级（circuit-breaker）
- storyboard.json：12 镜头，3975 帧 @30fps（不含全局片尾 60 帧，合计 4035 帧），provisionalTiming=false（Knoll 实测 timing.mimo.json，scale 1；分镜在镜头末尾加停留：hook-1 +40、avalanche-2 +47、breaker-2 +49、degrade-2 +37、recap-1 +34，只在分镜一侧加，配音从镜头开头起播，停留处为静音）
- 配音：MiMo mimo-v2.5-tts 冰糖，句间 0.28 s，章末 10 帧；按 3/2、2/2、2/2、2/2、2/2、2/1 切镜；「这是出 bug 了吗？」送 TTS 写作「这是出故障了吗？」，字幕保留原句；生成与 ASR 核对脚本见 voice/
- 工具链同第五～十一期：gen_assets.py → gen.py → validate.py；frame.py 出检查帧（check/）；map_timing.py 接实测 timing
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 视频封面帧：全片第 1550 帧（breaker-1 局部 252）；站点封面用专用设计封面 cover-16x9.jpg（`npm run covers -- circuit-breaker --set-poster`）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；无中央水印；全片无自我介绍和「下期见」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
