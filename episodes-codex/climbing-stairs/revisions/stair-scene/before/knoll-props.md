# EP.27 climbing-stairs-v1 前两阶计数怎样得到下一阶

依据：script.md、plan.json、episode-config.json、covers.json及本期Remotion源码。真实storyboard、voice、words、cues、shot_frames的哈希与绝对帧由总控制作后冻结，当前无；不编造配音时序。所有动画以本镜第0帧与真实cueFrames.sentences定位，画面坐标1920×1080。

## 本版变化

新片，无上一冻结版。采用题目本身的路径和横向计数节点，不复用二分查找的数组、指针或排除组件。全12镜均为canvas，无browser、DevTools、假窗、装饰进度条。无strike/strikeColor，无下期预告。

## 状态与同步

| 镜 | visualType | 因果动作 |
|---|---|---|
| 01 | problem | 三阶输入、每步1或2、恰好终点、返回方法数 |
| 02 | order | 111/12/21依次建立，顺序不同共3种 |
| 03 | last-step | 同三条路径末步高亮，按末步1/2分组 |
| 04 | no-overlap | 第2阶两种与第1阶一种，接末步得2+1=3 |
| 05 | bases | 切同一条六阶计数节点，直接数清1/2起点 |
| 06 | grow | 前两计数合流，先得到3、再得到5 |
| 07 | thirteen | 先得到8，再按末步1/2将8/5合成13 |
| 08 | dynamic-programming | 第二句句首才引入动态规划；回到准备算第6阶，淡化教学留痕 |
| 09 | rolling | prev第4阶5、curr第5阶8，先求13，整体变为第5阶8/第6阶13 |
| 10 | implementation | 关键行与旧值先求值的动作对应，正文唯一代码区 |
| 11 | boundary | O(n)/O(1)，限定本题只依赖前两项 |
| 12 | closing | 回答开头；末尾独立完整Python卡5秒，可暂停，无正文字幕 |

主要计数节点固定中心x335/585/835/1085/1335/1585；阶编号、方法数有不同文字身份。正文关键信息y<900，字幕独立。状态变化依真实句长缩放：每句前段解释，随后旧计数合流，末段保留结果；新数值到达后才落定。

## 渲染读取与只读说明

Main读取storyboard的scenes/shots、durationInFrames、visualType、cueFrames.sentences/labels、subtitles、codeCardFrom；data.ts累积真实镜长。代码卡读取solution.json.lines，与solution.py及文章同源。未读取的研究、旁白描述和本说明仅供人工审读；没有伪造词级识别。

## 封面

covers.json为三尺寸配置真源：16:9 1920×1080，3:4 1080×1440，4:3 1440×1080。4:3完整竖封在x315以0.75缩放，内容x405..1035，最下重要行y895.5<918。poster为cover-16x9.jpg。图中第4/5/6阶5/8/13表示教学示例方法数，最后两项合流，文案不超安全区。

discussionQuestion：每步只上1或2阶，到终点的方法数为什么只需记住前两阶的计数？
