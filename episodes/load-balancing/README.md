# EP.06 负载均衡（load-balancing）
- storyboard.json：12 镜头，3824 帧 @30fps（不含全局片尾 60 帧），provisionalTiming=false（Knoll 实测 /workspace/share/ep6-timing.json → timing.mimo.json，scale 1，spof-1 的 +30 hold 已含，未重复；recap-1 为「放在一起看」）
- 工具链同第五期：gen_assets.py → gen.py → validate.py；frame.py 出检查帧（check/）；map_timing.py 接实测 timing
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面 poster.jpg = 全片第 1905 帧（solution-2 局部 299）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；无中央水印；全片无「我是 IT小村」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
