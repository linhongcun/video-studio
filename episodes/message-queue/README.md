# EP.09 消息队列（message-queue）
- storyboard.json：12 镜头，3953 帧 @30fps（不含全局片尾 60 帧），provisionalTiming=false（Knoll 实测 timing.mimo.json，scale 1；producer-1 末尾分镜加 24 帧停留，号单划掉动画用）
- 配音：MiMo mimo-v2.5-tts 冰糖，句间 0.28 s，章末 10 帧；slice_ep9.py 按 2/3、3/2、2/2、3/2、2/2、2/1 切镜；producer 第 4 句、recap 第 2 句按新措辞重配
- 工具链同第五～八期：gen_assets.py → gen.py → validate.py；frame.py 出检查帧（check/）；map_timing.py 接实测 timing
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 渲染器新增：arrow 元素 `headless: true` 只画线段不画箭头（producer-1 划掉号单的红线）
- 封面 poster.jpg = 全片第 2612 帧（peak-2 局部 330）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；无中央水印；全片无「我是 IT小村」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
