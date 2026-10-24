# EP.01 http-request-codex-v1 浏览器输入网址后发生了什么？

依据：storyboard.json 43563d31；covers.json bf5e8028。冻结副本为storyboard.43563d31.json，freeze.py写入时逐字节复制。
script 37741cd9 / voice f503e22b / words fafecb46 / cues 7c79d498 / shot_frames b71d07cc；3417帧，12镜。画面1920×1080、30fps，封面16:9、4:3、3:4。

## 相对上一制作轮次的变化

全片新配音、新分镜、新主题动画与封面，必须全量渲染。上一轮视频不作为来源；本轮不使用实物比喻，不将全流程图套进浏览器。

## Knoll必读

Main.tsx读取冻结分镜时序；Scenes.tsx按production.json中的本期镜序执行主题动作。Primitives.tsx只提供文字、逻辑节点、传输路径和真网页。网页使用深色pageBg/pageInk；没有DevTools。角色位置尽量保持，当前步骤才揭示。句首术语标签由cueFrames驱动，不靠估算句内字时序。

cueOnset、timing、scriptVisual、direction、assets为检查/制作字段，渲染不直接读取；渲染读取from、durationInFrames、subtitles、cueFrames与production.json。strike本期不用。

## 画面类型与时间轴

| 镜 | id | frame | 绝对起帧 | 帧数 |
|---|---|---|---|---|
| 1 | 01 | browser | 0 | 229 |
| 2 | 02 | browser | 229 | 253 |
| 3 | 03 | canvas | 482 | 305 |
| 4 | 04 | canvas | 787 | 274 |
| 5 | 05 | canvas | 1061 | 274 |
| 6 | 06 | canvas | 1335 | 244 |
| 7 | 07 | canvas | 1579 | 226 |
| 8 | 08 | canvas | 1805 | 307 |
| 9 | 09 | browser | 2112 | 310 |
| 10 | 10 | browser | 2422 | 305 |
| 11 | 11 | browser | 2727 | 310 |
| 12 | 12 | canvas | 3037 | 380 |

## 页型与接续

只有实际网页使用Page组件，地址栏是保留示例网址。其余为全屏讲解画布；无窗口标签、无假应用窗。当前对象的来源和结果通过路径运动、状态变更、渐进绘制表达，分镜direction与visual-direction.md逐镜对应。

## 术语与同步

- 镜04 dnsLabel：域名解析，[130,175,1660,77]，字号57，本镜第1帧入场；对「域名解析」句首声学起音1.23帧。
- 镜06 requestLabel：HTTP请求，[130,175,1660,77]，字号57，本镜第1帧入场；对「HTTP请求」句首声学起音1.32帧。

## 封面

三个尺寸均由本期Cover生成，正文、图示、品牌说明在textBoxes记录；4:3内容严格落在x315..1125与y<918，水印单独放在右上。poster取3:4。封面标题和图示来自production.json，位置来自covers.json。

## 讨论与下期

boxShots=[]，无讨论题，不编下一期预告。末镜品牌为IT小村 · 原创。
