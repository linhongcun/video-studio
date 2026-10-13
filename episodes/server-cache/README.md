# EP.08 服务端缓存（server-cache）
- storyboard.json：13 镜头，3900 帧 @30fps（不含全局片尾 60 帧），provisionalTiming=false（Knoll 实测 timing.json / timing.mimo.json，scale 1，无 extraHold；v0.12.1：旁白补上术语（服务端缓存、Redis、缓存命中/没命中、TTL、CDN），第 1、3、4、6 章重配）
- 工具链同第五～七期：gen_assets.py → gen.py → validate.py；frame.py 出检查帧（check/）；map_timing.py 接实测 timing
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面 poster.jpg = 全片第 1505 帧（hit-miss-1 局部 227）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；无中央水印；全片无「我是 IT小村」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
