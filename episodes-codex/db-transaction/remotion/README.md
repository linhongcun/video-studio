# EP.16 数据库事务重制工程

本工程读取上层 `storyboard.json` 的真实镜头时长、句级字幕与术语起音，配音实体文件位于 `public/audio/voice.wav`，第 0 帧连续播放。冻结稿尚未生成时，静帧工具只使用 `src/placeholders/storyboard.json` 预览，不能将占位时间用于最终成片。

## 制作

环境：Node.js 20+、Python 3/numpy、FFmpeg、`/usr/bin/chromium` 与系统 Noto Sans CJK SC 字体。

```sh
npm ci
npx tsc --noEmit
npm run stills
npm run covers
npm run render
```

静帧写到 `/tmp/db-transaction-stills/`；可用 `npm run stills -- /绝对目录` 指定位置。`covers` 输出上层三尺寸 PNG。`render` 输出 `out/voice.mp4`，再由共享混音脚本加入 Wallpaper 背景音乐，成片为上层 `video.mp4`，混音记录位于 `out/mix-report.json`。

当前工作区复用现有 Remotion 依赖的 node_modules 软链；该软链不应入库，独立环境用锁定依赖 `npm ci`。

## 数据与画面

固定教学示例：同一个数据库的两个账户，原值为 1000/500，转账 200，成功结果 800/700，撤销后保留 1000/500。前五镜的 800/500 是两步分别确认的半成例子，不能理解成一笔事务已经保证的结果。

画面上层始终明确标“已确认余额”，下层金色标“本次修改预览·尚未确认生效”。未提交过程中上层保持原值，提交时两处已确认余额同帧变化；回滚撤掉当前操作的预览，不撤销已经提交的另一笔转账。

镜 10 和 12 都重新从原始余额开始，并显式标明是另一示例。镜 11 表示应用发现失败后请求回滚；镜 12/13 只表示提交前数据库进程崩溃、重启恢复时撤回未提交修改，不概括成任意错误都会自动整笔回滚。

主体、字幕与注释分区，示例范围说明常驻。金额不连续滚动成中间数，避免出现虚构的中间余额。术语首次挂词用 `cueFrames.transactionLabel`、`commitLabel`、`rollbackLabel`，分别对应镜 06、09、11。

`cueFrames.sentences` 为真实句首相对帧。句内的高亮、扣款/入账、报错和预告切换按该句长度和阅读节奏计时，属于视觉调度，不声称具备逐字 ASR 对齐。关键动作与旁白次序由静帧及后续成片复核。

## 封面

16:9、4:3、3:4 独立布局。4:3 核心内容在 x315..1125，声明底边 y908，小于918。三种尺寸均标“同一数据库·示例数据·非真实转账”，不把教学例子作为银行支付界面或性能实测。
