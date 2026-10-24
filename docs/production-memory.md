# 项目制作记忆

更新于2026-10-24（北京时间）。本文件保留用户偏好、案例状态与阅读入口；具体错误及有效做法分别积累到下面两份文件，避免多处复制后互相冲突。

## 开工阅读入口

1. [教训](lessons-learned.md)：发生过什么、下次如何避免、如何验证已修复。
2. [成功经验](successful-practices.md)：实际有效的做法、适用场景和证据。
3. [现行规范](RULES.md)与[制作流程](pipeline.md)：规范和流程的真源；案例参数不自动变成新规定。

新问题和成功做法使用稳定编号追加，已有条目若发现局限，补充适用范围和证据。不要只记录口号，也不要把尚未验证的建议写成成功经验。

## 用户明确的质量偏好

- “一定要去查阅一些核心的权威资料。”
- “制作动画的时候一定要通俗易懂，并且尽可能好看吧。”
- EP.16第一版被指出信息持续密集、主要变化是字幕；第二版通过逐步揭示、焦点移动和因果动作重做后，用户表示“这次就符合预期了”。详见教训L001至L004、成功经验S003至S005。
- 动画要引导观众知道看什么、发生了什么。静帧整齐、文字不溢出、渲染成功，不等于讲解效果合格。

## GitHub 自主发布授权

2026-10-24 用户在认可EP.17后明确说：“代码可以提交合并了，视频可以布置上线了。以后做好后就可以自己这样做了……要是有问题，我会跟你说的。大不了你再重新改，再上个线就行。”

据此，后续视频制作和质量检查完成后，可自主合并主干、发Release、部署GitHub Pages并核验线上文件，不再逐期要求观看确认或widget。收到反馈后修正、检查并重新上线。资料与动态表达要求继续，检查能力不足须如实记录。平台新发不包含在本次持续授权中。真源见[RULES的STATUS](RULES.md#status)。

同日用户补充：“以后制作完将对应的那个issue也进行关闭吧。”后续制作、合并上线及核验完成后，以`completed`关闭对应制作issue，作为发布收尾，不再另问。未执行的平台事项仍如实保留，不扩大平台发布授权。

## 已验证案例与当前状态

### EP.15 数据库索引

- 对应 [#66](https://github.com/linhongcun/video-studio/issues/66)，已按用户指令标记完成并关闭。
- [PR #112](https://github.com/linhongcun/video-studio/pull/112)已合并；[v0.45.1](https://github.com/linhongcun/video-studio/releases/tag/v0.45.1)只上站点，不重发平台。[部署运行40054122723](https://github.com/linhongcun/video-studio/actions/runs/40054122723)成功。
- [线上页面](https://linhongcun.github.io/video-studio/episodes/db-index/)的视频与用户批准版完整SHA一致，前缀为`1b903ab2`；海报、外挂字幕和更新日志也已核验。
- [制作工程](../episodes-codex/db-index/README.md)、[权威资料核验](../episodes-codex/db-index/research.md)、[媒体指标](../episodes-codex/db-index/render-result.json)已入库。

### EP.16 数据库事务

- 对应 [#67](https://github.com/linhongcun/video-studio/issues/67)。第一版SHA前缀`3085d678`；重做后的第二版`6aa379dd`，4066帧、约135.5秒。
- 用户已观看并认可第二版，随后明确批准合并主干并部署 GitHub；本次发布版本为[v0.45.2](https://github.com/linhongcun/video-studio/releases/tag/v0.45.2)，只上站点，不重发平台。
- [制作工程](../episodes-codex/db-transaction/README.md)、[连续动画检查](../episodes-codex/db-transaction/qa-motion-v2.md)、[媒体指标](../episodes-codex/db-transaction/render-result.json)与[发布记录](../episodes-codex/db-transaction/release.md)随本期入库；[站点页面](https://linhongcun.github.io/video-studio/episodes/db-transaction/)使用批准版的原样副本。
- EP.16当时按单期明确指令合并和部署；后续GitHub持续授权及完成后关闭制作issue的约定见上节。

### EP.17 数据库锁

- 用户明确要求选择并开始制作下一期，选定 [#69](https://github.com/linhongcun/video-studio/issues/69)，接上EP.16片尾的最后一件库存问题。
- [制作工程](../episodes-codex/db-lock/README.md)成片为14镜、28句、3457帧、约115.2秒；用户观看认可后批准[PR #119](https://github.com/linhongcun/video-studio/pull/119)合并，发布版本为[v0.45.3](https://github.com/linhongcun/video-studio/releases/tag/v0.45.3)。视频SHA前缀`93804b48`。
- [权威资料核验](../episodes-codex/db-lock/research.md)、[动态预检](../episodes-codex/db-lock/qa-motion.md)与[成片核验](../episodes-codex/db-lock/qa-final.md)及[发布记录](../episodes-codex/db-lock/release.md)随本期入库。重点是乙等待后加锁读取新库存0，再由程序判定缺货，不把行锁当成业务检查。
- [站点页面](https://linhongcun.github.io/video-studio/episodes/db-lock/)使用本期通过的同一份视频；平台历史投稿保留。#69 已按用户后续指令以`completed`关闭。

## 复用边界

- 14或16镜、具体时长、字号、滚动位移及坐标都是单期实现，不照搬成后续硬规则。
- 官方ASR模型下载在当时环境被拒绝，后续重新检查能力。既有句级音频边界和声学起音不能冒充逐字识别或完整人工听辨。
- 授权范围和系列状态以最新用户指令及RULES的STATUS判断；GitHub站点已有持续授权，平台新发仍未授权。
