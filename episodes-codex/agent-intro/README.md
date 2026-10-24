# EP.22：AI 能回答问题，怎么才能真正帮你办事？

Agent 开发系列 A01，制作 issue [#131](https://github.com/linhongcun/video-studio/issues/131)，系列总览 [#130](https://github.com/linhongcun/video-studio/issues/130)。用户要求先制作一期查看效果；本期为概念入口，后续按批次安排。

20镜40句、5章，同一笔合成订单8124贯穿：查询订单、读取示例政策、询问使用情况，再按当前查询与用户陈述给出申请建议。退款始终未执行。画面为机制动画，不代表运行真实订单接口或模型性能实验。

- 内容与来源：script.md、content-plan.json、research.md、article.mdx、pronunciation.md。四份官方正文按2026-10-24实际阅读记录，主张、日期与边界逐镜对应。
- 动画与构图：visual-direction.md、knoll-props.md、covers.json，以及 remotion/src/Main.tsx。
- 配音：共享 episodes/_shared/voice/ 负责生成、裁尾与整轨；本期 voice/build-metadata.py 只根据真实句边界和共享 Rule 生成句包络元数据，不推断句内逐字时间。
- 检查：qa-teaching.md、qa-timing.json、label-onset-strict.txt、qa-motion.md、qa-final.md 与 render-result.json，以实际存在的报告和执行范围为准。

首次术语在句首：04“模型”、07“工具”、14“智能体”。字幕逐句保持实际脚本文本。当前没有可用ASR权重，句包络不冒充逐字识别，不声称全片人工听辨；能力说明保留在声音和最终检查报告。

重建已有配音不必再次请求TTS。使用已配置的Python环境（numpy/scipy/soundfile）：

    python3 episodes/_shared/voice/build.py --dir episodes-codex/agent-intro
    python3 episodes-codex/agent-intro/voice/build-metadata.py
    python3 episodes-codex/agent-intro/assemble.py
    python3 episodes/_shared/place_v2.py --dir episodes-codex/agent-intro --mode whole
    python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/agent-intro
    python3 episodes-codex/agent-intro/check-timing.py

动画及封面从本期 remotion/ 运行实际脚本：

本期辅助QA脚本的干净构建记录使用Node 24.19.0；脚本会读取TypeScript模块，使用其他Node版本时需核对原生TypeScript支持或配置相应loader。正式渲染由Remotion打包，浏览器系统依赖为Chromium。

    npm ci
    npx tsc --noEmit
    node scripts/qa.mjs /tmp/agent-intro-qa
    node scripts/qa.mjs /tmp/agent-intro-motion --shots=08,10,12,14,15,17,19 --motion --no-captions
    npm run covers

关键动作和实际时序复核通过、所有生产输入负责人停写后，从仓根运行 freeze.py，再使用本期 package.json 的 npm run render 编码。多人共用时以 /tmp/video-studio-render.lock 串行渲染。冻结后修改生产输入，必须先停止本期排队或执行的渲染，再重新冻结并完整编码，不能用新清单认可旧视频。

混音报告复制至 mix-report.json 后运行 check-final.py，核对冻结输入、真实编码帧数、音频、响度及完整解码。站点发布副本位于 episodes/agent-intro/，视频、字幕、章节和海报必须对应同一最终产物。

配乐：Kevin MacLeod《Wallpaper》，CC BY 4.0。站点发布与平台授权遵守仓库 docs/RULES.md 的当前 STATUS。
