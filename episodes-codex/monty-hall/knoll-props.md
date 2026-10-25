# EP32 · monty-hall-v1 · 按初选对错看清换门结果

依据真实声音装配后的storyboard.json与covers.json；不是临时原型。全部画面为1920×1080／30fps全屏canvas，14镜28句、5507帧。

## 输入身份

- script.md：`ca94595ec4ff984f70a0ffb76d9ce619bb72bdf82eb0f1e1ef6d54399920767f`。
- plan.json：`7bc40e7c8b4580d9e15edb59dd7af2a09d41be85704c3cc73f980b03d4efffcf`。
- voice.wav：`c12883686897cef1f983aae434ef02745ac9b9bf27660c95160658d41ab2eee6`。
- words.json：`6558a6110cdac5b3f24a0e0748c961d1c898e0d93b333ab63053811dd2b65671`。
- storyboard.json：`6a76466dade4dede42921bb2197b1caad04ba2b3e755565ba54afa18428a23b4`。
- covers.json：`16281b06f2fc498d34d42b2057bf9bf3e824e4704229a1ae48d46f01d5e215a9`。
- voice/cues.json：`978db83bbec4b517ec6e4e4a715ebcdf55007431ca35a38410d67cb507c8df8e`。
- voice/shot_frames.json：`b33f2b6354881b3a3111a842b8b10fbd99460703bd80dc06eb7c39fa4580f17d`。

音轨、public实体副本、句级区间与字幕来源见qa-voice.md。词兼容字段是整句包络，两个真实句首cue为02的主持人与14第二句的每次都换；内部开门／切换／揭奖不冒充逐字ASR对齐。

## 新一期与变化

相对上一冻结：无，本期新制作尚未冻结；不能把P03画面、镜数或媒体作为本期替代。延续连续对象表达状态的原则，重新设计固定编号门位、玩家选择框与三种初始情景。无浏览器壳、DevTools、拟真实物门、无关进度线、代码卡或下期预告。

门位、奖品、初选与当前选择分开。每一情景奖品从开局至结束固定；主持人只开未选空门，玩家只能换到另一未开门，选择框连续到达后才揭最终结果。当前移动中不宣称已经抵达，历史初选锚点不当作第二个当前选择。实际布局与动作相位由remotion/src/monty-model.ts、DoorBoard.tsx、timeline.ts及Main.tsx决定，最终快照纳入冻结。

## 镜头与真实章节

| 镜 | visualType | 章节 | 起帧 | 帧数 |
|---|---|---|---:|---:|
| 01 | hook | rules | 0 | 378 |
| 02 | host-rules | rules | 378 | 399 |
| 03 | example-open | game | 777 | 386 |
| 04 | example-switch | game | 1163 | 375 |
| 05 | choose-viewpoint | game | 1538 | 360 |
| 06 | three-positions | cases | 1898 | 434 |
| 07 | initially-right | cases | 2332 | 319 |
| 08 | right-switch-loses | cases | 2651 | 381 |
| 09 | initially-wrong-two | cases | 3032 | 449 |
| 10 | wrong-two-switch-wins | cases | 3481 | 410 |
| 11 | initially-wrong-three | cases | 3891 | 397 |
| 12 | right-wrong-relation | chance | 4288 | 464 |
| 13 | add-the-chances | chance | 4752 | 402 |
| 14 | closing | chance | 5154 | 353 |

03初选1后主持人开空3；04换2揭奖；05只提出回看分析；06该完成局缩到中行，新增上下两行为不同初始奖位。07–08上行初选正确、演示开3换2输，若改开2换3也输只作条件旁注；09–10保持已完成中行解释历史；11下行初选1、奖位3，先开空2，再换3揭奖。12–14只在三行结果已形成后合并两行初选错误的权重，回收始终保留1/3、始终换门2/3。

04、09、10口头和图注使用换门前／当时／做决定时；不得把当前已揭开的2号又说回现在未开。三行各1/3是初始奖位整组权重，首选正确的两个主持人分支合计一行；不画成四条等权路径，不把三情景当三次实验计数。分析可在门外标明假设奖位，不新增游戏中窥奖动作。

## 动态与提交边界

先按真实句窗复核03选门与主持人开空、04和08换框与揭结果，在该句完成后留结果停留再进入回看／条件说明；11依次完成开空、移动与揭奖。03–06、07–10、11–13无字幕关键连续过程均需实际解码查看，包含缩放中间态、已开门跨越、当前与历史状态、每个落点前后。未看过的动态或成片不得预写通过。

主持人规则完整前置：知情、必开未选空门、每局提供换门；有两合法空门时公平二选一。公平约定固定本期具体开门后验，总体初选错就换赢的结论不依赖公平。额外后验与盲开变体只留文章。

## 封面与收尾

封面三尺寸16:9、4:3、3:4及海报关系取本期covers.json；水印、实际文本界限和安全区由真实DOM与六张PNG/JPG验证，不能凭配置坐标宣布无溢出。

discussionQuestion = 主持人知道奖品位置且只开空门时，为什么换门获胜正好对应初选错误？

nextEpisode缺省，不编下一期。末镜仅原有三情景结果与始终保留／始终换门概率，保留IT小村 · 原创，短停后结束；不追加证明或文章口头入口。

## 发布身份修订

并行专题先使用EP31，本期制作期号顺延为EP32。实际首发版本见站点metadata与release.md，发布版本不参与画面。旧142清单、原始TTS来源与未发布候选保留在identity-revision及retired候选目录；不以新清单追认旧编码。28句旁白、选定takes、WAV与所有可视字段保持，新的canonical来源经过精确对比、重新冻结并完整重编码。复用证明见voice/metadata-sync.json。
