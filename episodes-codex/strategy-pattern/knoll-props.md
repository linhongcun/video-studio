# 制作说明：策略模式

本期Remotion工程位于 `remotion/`，使用16镜真实句级 `storyboard.json`；30fps、1920×1080，总帧数由共享句级装配输出，根数据模块逐镜累加，不在渲染器另加片尾。配音由共享 `episodes/_shared/voice/` 生成，`public/audio/voice.wav` 必须为实体副本。

## 主体与构图

布局按 `visual-direction.md`：旧结算内具体分支 → 算法逐个抽出 → 外部选函数 → 统一委托 → 结果返回 → 修改与新增范围 → 代价。输入为示例100元；普通100、会员90、旧活动80、新活动75、新客90。每次只选一种，换规则先重置，绝不把90或80当下一次折扣的输入。

07起调用方左侧、结算中间、规则右侧保持锚点；活动改动仅其函数金色标记，新客新增同时标实现与选择入口。移动金额沿调用或返回路线推进；靠近节点文本时在接收口前淡出，底层路径仍接入，再更新最终落定值，以免“等待返回”和金额形成重影。

## 字体、颜色与品牌

页身使用共享深色主题，中文字体Noto Sans CJK SC，代码Noto Sans Mono。主题由 `src/theme.ts` 转发共享页身色，不修改共享主题。正文代码最多两处；不存在完整代码附录或算法题专用组件。右上角“IT小村”、片尾“IT小村 · 原创”。无假窗、比喻、装饰进度条或持续运动的章节线。

## 脚本入口

从 `remotion/` 运行：

```sh
npm ci
npx tsc --noEmit
node scripts/qa.mjs out/true-timing-all --no-captions
node scripts/qa.mjs out/true-timing-motion --shots=04,07,08,09,10,11,13 --motion --no-captions
npm run covers
```

QA覆盖最终 `composition.props` 的 `hideSubtitles:true/showSubtitles:false`，不只在最外层传参；实际输出仍由主任务和独立复核者查看。记录里 `voice:false` 表示QA片无声，不代表没有真实配音时序；`provisional:false` 才表示用的是根真实装配文件。

全部写入者停写、动态复核闭合后，由根任务冻结生产输入，再执行 `npm run render`。正式渲染明确注入真实音频存在标记，编码H.264/CRF20，配乐使用共享Wallpaper及混音工具，成片目标−16 LUFS。封面组件遵守 `covers.json` 的各尺寸内容区域及4:3安全区，PNG转JPG与站点副本由根任务负责。

旧 `out/provisional-key/` 是早期临时时序与返回叠字修订前的预演，不作最终合格证据。真实时序最终采样/连续片及最终媒体的执行结果以实际QA报告为准，不预写已通过或用户认可。
