# EP.07 浏览器缓存（browser-cache）
- storyboard.json：13 镜头，4033 帧 @30fps（不含全局片尾 60 帧），provisionalTiming=false（Knoll 实测 /workspace/share/ep7v122-timing.json → timing.mimo.json，scale 1；v0.12.2：旁白补上术语（Cache-Control、max-age、强缓存、ETag、304、协商缓存），第 4、5 章重配，第 5 章拆成 revalidate-1～3，revalidate-3 末尾留 24 帧静音；recap-1 为「CDN 是附近的门店，离你近」）
- 工具链同第五、六期：gen_assets.py → gen.py → validate.py；frame.py 出检查帧（check/）；map_timing.py 接实测 timing
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面 poster.jpg = 全片第 1290 帧（second-1 局部 152）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；无中央水印；全片无「我是 IT小村」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
