# EP.13 熔断（circuit-breaker）重制版
- storyboard.json：20 镜头，5252 帧 @30fps（约 175.07 秒），provisionalTiming=false
- 浏览器只打一个结算接口 `checkout`；商品、地址、运费险由后台依次去问；熔断后本地跳过运费险、不再调用；补半开试探与恢复
- 配音：MiMo mimo-v2.5-tts 冰糖（pronunciation.md）；words.json 对齐
- 制作：`cd remotion && npm ci && npm run render`（Remotion + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面：cover-16x9 / 4x3 / 3x4（jpg+png）；poster.jpg = cover-3x4.jpg
- branding：右上「IT小村」+ 60 帧片尾卡
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
