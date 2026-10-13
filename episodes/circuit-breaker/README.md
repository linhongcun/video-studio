# EP.13 熔断（circuit-breaker）
- storyboard.json：6 章 12 镜头，3653 帧 @30fps（不含全局片尾 60 帧，合计 3713 帧，约 123.8 秒），provisionalTiming=false（Knoll 实测 timing.mimo.json = /workspace/share/ep13-timing.json，scale 1；镜尾停留 hook-2 +12、cascade-2 +19、half-open-1 +19）
- 讲雪崩（级联故障）、超时、熔断、关闭 / 打开 / 半开三种状态；熔断不能代替超时；库存校验不跳过；示例参数（100 次、50%、30 秒）上屏标「示例」
- 配音：MiMo 冰糖（pronunciation.md）
- 工具链：sh run.sh → map_timing.py → gen.py → validate.py；remotion/src/timing.json = timing.json（渲染前同步）
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面：Miyazaki 设计封面 cover-16x9 / 4x3 / 3x4.jpg（「一个挂了，」/「全站都崩？」，标签「熔断」，系列「扛住高峰 05」）；视频封面帧 = 全片第 1690 帧（breaker-2 第 190 帧）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；全片无自我介绍和「下期见」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
