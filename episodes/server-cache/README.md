# EP.08 服务端缓存（server-cache）
- storyboard.json：12 镜头，3449 帧 @30fps（不含全局片尾 60 帧），provisionalTiming=false（Knoll 实测 timing.json / timing.mimo.json，scale 1，无 extraHold；第 3 章按新词重配去掉「命中」，第 6 章第一句改为「……三层缓存都在帮你省一趟路」后重配）
- 工具链同第五～七期：gen_assets.py → gen.py → validate.py；frame.py 出检查帧（check/）；map_timing.py 接实测 timing
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面 poster.jpg = 全片第 1370 帧（hit-miss-1 局部 212）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；无中央水印；全片无「我是 IT小村」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
