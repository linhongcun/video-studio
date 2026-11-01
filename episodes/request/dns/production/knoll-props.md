# EP.03 dns-codex-v1 输入网址后，怎么找到服务器？

当前为flow-map-20261024/#199导航小样，尚未重新冻结。旧发布输入以revisions/pre-flow-map.json的6765032基线完整SHA索引追溯；storyboard.828753a4.json与旧QA属于历史。covers.json保持不变。
script 3d4e4d32 / voice 09b8dde7 / words 0511fb64 / cues 652476a4 / shot_frames 25745e45；3200帧，12镜。画面1920×1080、30fps，封面16:9、4:3、3:4。

## 相对上一制作轮次的变化

本轮只重做查询全局/局部导航与角色连续性，保留原script、voice、words、字幕、12镜与3200帧；暂不正式全片编码。使用既有共享branch-map/index.ts，不修改共享实现。根/TLD/权威与解析器分别往返，两种缓存捷径分开；全流程图为干净画布。

## Knoll必读

Main.tsx读取冻结分镜时序；Scenes.tsx按production.json中的本期镜序执行主题动作。Primitives.tsx只提供文字、逻辑节点、传输路径和真网页。网页使用深色pageBg/pageInk；没有DevTools。角色位置尽量保持，当前步骤才揭示。句首术语标签由cueFrames驱动，不靠估算句内字时序。

cueOnset、timing、scriptVisual、direction、assets为检查/制作字段，渲染不直接读取；渲染读取from、durationInFrames、subtitles、cueFrames与production.json。strike本期不用。

## 画面类型与时间轴

| 镜 | id | frame | 绝对起帧 | 帧数 |
|---|---|---|---|---|
| 1 | 01 | browser | 0 | 280 |
| 2 | 02 | canvas | 280 | 254 |
| 3 | 03 | canvas | 534 | 250 |
| 4 | 04 | canvas | 784 | 260 |
| 5 | 05 | canvas | 1044 | 289 |
| 6 | 06 | canvas | 1333 | 302 |
| 7 | 07 | canvas | 1635 | 231 |
| 8 | 08 | canvas | 1866 | 226 |
| 9 | 09 | canvas | 2092 | 243 |
| 10 | 10 | canvas | 2335 | 272 |
| 11 | 11 | canvas | 2607 | 278 |
| 12 | 12 | canvas | 2885 | 315 |

## 页型与接续

只有实际网页使用Page组件，地址栏是保留示例网址。其余为全屏讲解画布；无窗口标签、无假应用窗。当前对象的来源和结果通过路径运动、状态变更、渐进绘制表达，分镜direction与visual-direction.md逐镜对应。

## 术语与同步

- 镜03 dnsLabel：域名解析，[130,175,1660,77]，字号53（固定前景），本镜第1帧入场；对「域名解析」句首声学起音1.82帧。
- 镜05 resolverLabel：递归解析器，[130,175,1660,77]，字号53（固定前景），本镜第1帧入场；对「递归解析器」句首声学起音1.20帧。
- 镜10 ttlLabel：缓存有效期，[130,175,1660,77]，字号53（固定前景），本镜第1帧入场；对「缓存有效期」句首声学起音2.77帧。

## 封面

三个尺寸均由本期Cover生成，正文、图示、品牌说明在textBoxes记录；4:3内容严格落在x315..1125与y<918，水印单独放在右上。poster取3:4。封面标题和图示来自production.json，位置来自covers.json。

## 讨论与下期

boxShots=[]，无讨论题，不编下一期预告。末镜品牌为IT小村 · 原创。

## 导航与检查入口

branch-map.ts定义固定7节点查询图及shot绑定，motion.ts列出重要动作完整窗口。02–03全图、04本地缓存→回图、05进入递归局部、06–08固定局部、09回图、10缓存时限→回图、11明确重置未到期→缓存短路→回图、12回收DNS内部核心图后定位后续连接。

预演复用共享qa.mjs；freeze.py已纳入共享导航源依赖，但本轮小样阶段未执行冻结。新增flow-map-check.mjs检查原始媒体/字幕/时序保持、所有重要动作窗口的相机稳定与实际拓扑边界。小样不替代独立编辑复核或最终媒体检查。
