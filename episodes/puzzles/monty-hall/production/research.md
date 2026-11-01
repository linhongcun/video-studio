# P04 三门问题：一手资料实际阅读

核验/访问日期：2026-10-25（北京时间）。对应[#208](https://github.com/linhongcun/video-studio/issues/208)，slug `monty-hall`，趣味推理P04、内部EP.32。

主任务已同步最新主干并创建`codex/monty-hall`。本任务实际核对基线`4a00d8a0f84b0d20eb1a87fbd6fb87a6b870a6f0`及该分支，不切分支、不提交、不执行外部代码。

## S1：Stanford STATS60的一手讲义

- 主张：可由对称性固定玩家初选1号门；按三种奖品位置或初选正确/错误分类，始终换门胜率2/3、坚持1/3。
- 来源：[Lecture 11: Coincidences — STATS60, Intro to statistics](https://web.stanford.edu/class/stats60/lectures/11-lecture-coincidences.html#the-monty-hall-problem)，Stanford大学课程网页。
- 实际读取：本期通过TinyFish `fetch_content`成功提取完整页面，定位“The Monty Hall Problem”“Monty Hall: solution”“Monty Hall: switch”“Monty Hall: stay”正文；不是只读取搜索摘要、issue旧初核或页面标题。
- 读取结果：返回原目标URL，`errors: []`，正文实际包含三门汽车/山羊题面、开另一扇山羊门、提供换门，以及两种策略的分类推导。本期用“奖品/空门”表述同一个胜负结构。
- 页面日期：正文及返回元数据没有可核验的发布日期或更新时间，不从课号、搜索抓取时间或页面其他例子的年份推断。访问日期2026-10-25（北京时间）。
- 短引："By symmetry, we can assume that the contestant always picks door 1."
- 支持范围：固定门1的一般性、三种初始情景及总体策略胜率。讲义没有明确规定初选正确时两扇空门须公平挑选，也没有在读取到的Monty Hall段讨论随机盲开变体；本期不把这两点冒充该讲义已证明的事实。
- 用在：题面、先完整一局、再按初选对错回到三种奖品位置的主线，以及图文脚注。

## S2：另一所大学作者的独立事件论证（旧资料，仅参考）

- 主张：主持人知道奖品位置、开另一扇空门后允许换门；坚持与始终换门的获奖事件互补，总体为1/3和2/3。
- 来源：[The Monty Hall game — Jayadev Misra](https://www.cs.utexas.edu/~misra/Notes.dir/MontyHall.pdf)，University of Texas at Austin作者主页的两页讲义。
- 实际读取：本期TinyFish `fetch_content`完整提取PDF两页正文，包括题面、Proof 1—4及“A Final Note”；返回`errors: []`。没有将链接可打开冒充已阅读证明。
- 页面/文档日期：PDF封面原样写`8/10/2011`，本期仅确认年份2011，不另外猜测日月顺序；因早于2020，按项目规范标**旧资料，仅参考**。访问日期2026-10-25（北京时间）。
- 短引："His choice does not have to be random"。
- 核验要点：末注明确指出，两扇空门可开时，主持人不必随机，仍不改变始终换门的总体2/3结论。这避免把本期的公平二选一误说成总体结论的必要条件。
- 支持范围：知情主持人规则、初选对错事件方法、总体策略结论；不以该旧资料替代本期清楚列出的模型和精确核验，也不说它讨论了本期盲开条件概率。

## 本期显式固定的完整主模型

奖品在三门均匀分布且不移动，玩家不知位置；主持人知情、每次必开未选空门、每次都提供换门，初选正确有两个空门可开时等概率选择。本片只比较“始终坚持”与“始终换到另一扇未开门”。

这些规则必须与题面一起说明；不能从屏幕剩两扇门就重置为各半，不能把随手开门偶然见空当作知情必空的同一模型，也不能选择性只在某些回合提供换门。

固定门1后，主片三个初始奖品位置各1/3。初选正确的情景虽然有两个开门分支，每支1/6，但整组仍只有1/3；另外两种初选错误情景各1/3且都换赢。视频用开3演示正确初选的一个代表分支时，要同时说明开2也换输，不把四个细分路径画成四个等概率情景。

主持人公平二选一是本期具体开门后验的固定条件。总体“初选错则换赢”的事件结论不依赖公平；本片不拓展其他主持人偏好的后验讨论。

## 自有精确推导及适用范围

| 主张 | 可核查依据 |
|---|---|
| 始终坚持1/3、始终换门2/3 | S1主线、S2事件法；本期完整Fraction枚举与独立基础签交叉核验 |
| 固定初选1时四条细路径权重1/6、1/6、1/3、1/3 | 本期奖品先验×主持人选择概率，见`research-math.md` |
| 本模型具体开3后，奖品1/2的后验分别1/3和2/3 | 本期按相容路径权重归一化；不只数剩下的门 |
| 随机盲开且恰好开空时，两策略各1/2 | 本期另建允许开奖品的盲开模型，条件枚举与事件法核对；不冒引未讨论此变体的大学讲义 |

数学说明见[research-math.md](research-math.md)，独立核验源见[verify_math.py](verify_math.py)，实际结果及路径权重见[qa-math.json](qa-math.json)。视频只讲三个初始情景和策略比较；附录可解释条件概率和变体，不在片尾追加证明或口头引流。

## 读取、网络及检查边界

两份大学公开来源通过本任务明确指定的TinyFish connector实际读取，不使用执行环境shell访问受限目标、不改代理、不执行网页或外部源码。没有访问失败，不虚构网络拒绝；没有读取的外链、课程其他章节或视频不记作已读。

本期`verify_math.py`是独立质量检查，不是视频程序附录，不新增代码卡。精确概率核验不代替门位、选中状态、主持人信息边界、动画、配音、媒体或网页检查；用户观看结论另记。


## 片尾参考资料

2026-10-26整理，`presentation: title-author`，2项1页5秒。两份资料实际技术阅读日期仍为2026-10-25（北京时间），本轮不新GET原站/PDF或题名署名，不把整理日期写成技术访问日期。

- **[R1] Lecture 11: Coincidences** — Stanford University；STATS60, Intro to statistics · Lecture 11 · 原实读未标发布或更新时间。正式出处：[https://web.stanford.edu/class/stats60/lectures/11-lecture-coincidences.html#the-monty-hall-problem](https://web.stanford.edu/class/stats60/lectures/11-lecture-coincidences.html#the-monty-hall-problem)。定位：The Monty Hall Problem；Monty Hall: solution；Monty Hall: switch；Monty Hall: stay。题名直接沿用旧完整文献名中的Lecture题名，STATS60课程站名另列。只支撑对称性固定初选与总体策略分类；公平空门二选一/盲开变体不冒引讲义。
- **[R2] The Monty Hall game** — Jayadev Misra；University of Texas at Austin；2011 · 文档原样日期8/10/2011，未推断日月顺序 · 两页讲义，**旧资料，仅参考**。正式出处：[https://www.cs.utexas.edu/~misra/Notes.dir/MontyHall.pdf](https://www.cs.utexas.edu/~misra/Notes.dir/MontyHall.pdf)。定位：题面；Proof 1—4；A Final Note。旧研究与同日独立来源复核明确记录题名/作者及完整两页读取；末注“不必随机”的支撑限于总体始终换门2/3，不扩为本期具体开门后验或盲开模型。

完整原研究与独立读取复核按固定基线Git/blob/完整SHA归档在[本轮来源记录](../../docs/reference-endcards/batch-11/sources-monty-hall.json)及同前缀文件；这些是本仓真实旧读取记录，不是原大学网页/PDF的原始HTTP快照。没有原始响应字节就不声明原页正文SHA/状态码，也未虚构新26日请求。原全文/脚注/锚点、主持人规则与精确推导字节prefix全部保留；未新增代码卡、执行概率程序、渲染或解码影片。
