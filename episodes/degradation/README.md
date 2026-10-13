# EP.12 降级（degradation）
- storyboard.json：4 章 9 镜头，3259 帧 @30fps（不含全局片尾 60 帧，合计 3319 帧，约 110.6 秒），provisionalTiming=false（Knoll 实测 timing.mimo.json，scale 1；镜尾停留 hook-1 +18、hook-2 +7、problem-2 +5、auto-degrade-2 +26、active-degrade-2 +22）
- 只讲降级（核心链路、降级、自动降级、主动降级；雪崩一句带过），不涉及熔断 / 半开 / 超时
- 配音：MiMo 冰糖；「bug」TTS 读作「出故障了吗」，字幕仍为「bug」（pronunciation.md）
- 工具链：sh run.sh → map_timing.py → gen.py → validate.py；remotion/src/timing.json = timing.json（渲染前同步）
- 制作：`cd remotion && npm ci && npm run render`（Remotion 渲染 + mix_bgm.py constant --below 12，Wallpaper，−16 LUFS）
- 封面：Miyazaki 设计封面 cover-16x9 / 4x3 / 3x4.jpg（「两个价，」/「不一样？」，标签「降级」，系列「扛住高峰 04」）；视频封面帧 = 全片第 300 帧
- branding v1.3.0：只有右上「IT小村」+ 60 帧片尾卡；全片无自我介绍和「下期见」
- 配乐：Kevin MacLeod「Wallpaper」（incompetech.com），CC BY 4.0
