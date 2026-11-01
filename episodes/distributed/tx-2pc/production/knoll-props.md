# EP.21 · 2PC：制作说明

3398帧、113.267秒，14镜28句；所有数字为教学示例。分镜SHA 7f412bf2d37ad721a1bf35d010070b97226a56709df5f66dcc016024aa331ab4。
音轨SHA 34253603c648ec9f45da93d2bf0c856c33ff377e397072c6cb97d0460a14572c。
冻结由root统一执行，尚不以本说明宣称最终编码已通过。

## 输入与页型

全部canvas，无浏览器/DevTools/比喻/设备模拟；主标题47px，字幕40px，顶部白话导航22px；右上IT小村与示例数据。页面底色复用共享pageBg。

## 状态时机

动作统一由本期motion.ts events与真实cueFrames.sentences计算，下面是实际使用的局部帧：

- 01：stock-operation-fails=79f
- 02：按句级进度渐进显示
- 03：order-work-ready=70f；stock-work-ready=149f
- 04：order-state-durable=30f；stock-state-durable=73f；order-ready-reply-arrives=141f；stock-ready-reply-arrives=184f
- 05：commit-decision-durable=159f
- 06：final-commands-depart=116f
- 07：order-commits-first=65f；stock-commits-later=176f
- 08：all-completions-received=72f
- 09：order-prepared=23f；stock-rejects=96f；abort-decision-durable=188f
- 10：abort-command-arrives=74f；pending-order-discarded=146f；abort-finished=188f
- 11：coordinator-unreachable=85f
- 12：old-decision-recovered=72f；order-recovery-complete=176f；stock-recovery-complete=213f
- 13：other-modification-waits=83f
- 14：按句级进度渐进显示

## 布局与标记

中央可靠记录top304，标题/记录之间不重叠；路径标签y414，参与面板top524、面板名top494、末说明Note top834；字幕top925。准备期库存主值白色4、拟改3金色；提交后主值绿色3。
03/04只有本地准备与状态；05决定先可靠记录；06发最终指令；07订单与库存先后落实；08完成回执齐后整单完成。09/10拒绝放弃分支、11/12待决恢复分支、13回看资源占用都有明确重置/回看提示。

## 封面

三尺寸PNG/JPEG；4:3内容x315..1125，文字末底904<918；主标题先准备/再共同决定，订单与库存均待共同决定。16:9副标题y520避免两行大标题重叠。poster与3:4 JPEG相同。

## 能力与复核

语音只用真实句级边界和三个句首声学cue，不宣称内部字词识别或全片人工听辨。动态预演、关键无字幕片及实际编码复核分开记录。
