# EP.13 熔断（circuit-breaker）
- storyboard.json：6 章 12 镜头，3811 帧 @30fps（不含全局片尾 60 帧，合计 3871 帧，约 129.0 秒），provisionalTiming=false（Knoll 实测 timing.mimo.json = /workspace/share/ep13-timing.json，scale 1；镜尾停留 hook-2 +9、cascade-2 +14、half-open-1 +13）
- 讲雪崩（级联故障）、超时、熔断、关闭 / 打开 / 半开三种状态；熔断不能代替超时；例子为运费险服务（弱依赖，举例）：熔断后结算页少显示这一项（上期降级一句带过），下单付款照常；hook-1 / recap-1 灰色虚线框（rect dash: true）标出消失的那一行；示例参数（100 次、50%、30 秒）上屏标「示例」
- 配音：MiMo 冰糖（pronunciation.md）
- 工具链：sh run.sh → map_timing.py → gen.py → validate.py；remotion/src/timing.json = timing.json（渲染前同步）
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面：Miyazaki 设计封面（标签「运费险」）cover-16x9 / 4x3 / 3x4.jpg（「一个挂了，」/「全站都崩？」，标签「熔断」，系列「扛住高峰 05」）；视频封面帧 = 全片第 1737 帧（breaker-2 第 196 帧）
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；全片无自我介绍和「下期见」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
