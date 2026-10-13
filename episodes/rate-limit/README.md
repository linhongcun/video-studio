# EP.10 限流（rate-limit）
- storyboard.json：12 镜头，3729 帧 @30fps（不含全局片尾 60 帧，合计 3789 帧），provisionalTiming=false（Knoll 实测 timing.mimo.json，scale 1；breaker-2 末尾分镜加 14 帧停留，「降级」后共停 24 帧，只在分镜一侧加）
- 配音：MiMo mimo-v2.5-tts 冰糖，句间 0.28 s，章末 10 帧；slice_ep10.py 按 3/2、2/1、3/2、3/2、2/1、2/1 切镜；QPS 按字母读（tts_lexicon.json）；回顾第 1 句改为「……一个不丢；而限流，让门口不被挤爆。」让「限流」读清楚
- 工具链同第五～九期：gen_assets.py → gen.py → validate.py；frame.py 出检查帧（check/）；map_timing.py 接实测 timing
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面 poster.jpg = 全片第 2082 帧（token-bucket-1 局部 195）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；无中央水印；全片无自我介绍和「下期见」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
