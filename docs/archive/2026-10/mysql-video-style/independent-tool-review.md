# MySQL制作工具独立只读审核

日期：2026-10-28。执行者：独立代理mysql_site_scope（未实现本次制作工具）。基线：`d7a5d7682080232617a03cc988b7c25cb50446f4`。结论：未发现阻塞本批冻结与渲染的工具问题；发布稿证据依赖缺项已由工具作者补齐并复核。

## 实际范围

阅读新`mysql-video/render.py`、`references.py`、`qa.mjs`，私有复用的puzzles媒体核心、palette适配层及三代原题/作者媒体引擎，当前4份baseline-publication、4份article快照，以及既有tool-selftest的结果与QA记录。只读重新计算4份实际生产依赖闭包，未写新测试、未重跑fixture、正文渲染或全媒体解码。实际打开既有db-index第0帧自测PNG，核对其DOM坐标与真实MySQL/InnoDB首屏对应。

## 冻结、快照与入口

- 新薄wrapper为旧核心函数创建共享的私有globals namespace；context、依赖收集、marker与新result说明在私有层选择，旧puzzles工具与三代资料引擎相对HEAD无字节差异。
- 当前实际依赖预检计数：db-index **47**、db-transaction **52**、db-lock **47**、db-replication **48**。它们包含新入口闭包、原模型/分镜与旧冻结本身、新wrapper和palette adapter库、catalog、MySQL素材来源/许可、原题证据及本轮article快照。正式清单随后已生成，本代理只读执行4次verify_inputs并重算闭包，47/52/47/48个key集合与当前实际闭包完全相同，输入、外部字体及baseline完整SHA均匹配；没有把输入冻结称作已编码产物验证。
- 原补齐前`tool-selftest/dependency-preflight.json`的45/50/45/46是当时记录。本轮计数另行列在本报告，不改写旧自测证据。
- 新增的4份发布`article-sources.json`与4份`article/source-evidence.json`均已进入实际闭包；这8份原文件字节逐一与HEAD匹配。递归声明的savedPath/savedResponsePath/archivePath/savedCapturePath必须有完整匹配SHA，缺件、越仓或身份不符会停止。4份revision/article.mdx与当前已准备的发布稿逐字节相同；原生产稿保留。
- 4份baseline-publication中的publishedMetadata均与基线Git发布元数据相同；4个完整baseline MP4的实际SHA与记录相同，未把本轮先改的summary误当历史发布稿。引用/资料实读沿原日期，没有新GET或新技术核验声明。
- 渲染命令以各期remotion为cwd、使用仓库相对入口与输出，均为`src/mysql-style/index.ts` / `Main`、H.264/CRF20、concurrency2和`--muted`，不冻结本机workspace绝对路径。实际正文帧数为3924/4066/3457/3560；预期加150资料帧后为4074/4216/3607/3710，最终仍须由真实receipt与ffprobe确认。

## 媒体与资料身份

无声正文完成后先检查音轨不存在，再完整流拷贝baseline AAC，不使用切段、shortest或重编码。baseline→body比较全部AAC payload、PTS/DTS/duration与解码PCM；body→final继续由原引擎比较全部正文帧/时间戳、连续输出时间线、完整AAC及PCM。baseline音频不得超过正文边界一帧的guard已包含在既有4片预检。

资料adapter仅私有选择MySQL catalog的墨绿/薄荷palette；原题/署名排版、最多4项每页5秒、原题与作者/机构身份检查继续由旧引擎执行。receipt记录实际MySQL adapter、palette、puzzles adapter库、bibliography/original/media引擎SHA。不是把原题改成MySQL概括，也不把Oracle机构署名改成产品结论。新result从真实receipt生成finalVideoFrames与referenceAppendix，verify重新核对媒体身份与声明。

既有一秒合成H.264/AAC fixture的30→180帧结果、全部帧/PTS/AAC/PCM检查及只读verify的SHA/mtime保持记录均已阅读；没有重新执行，也不将此自测说成4条正式正文已通过。新verify沿用临时目录写媒体报告，不覆盖生产receipt；MySQL追加说明只在append/render时写入输出。

## QA DOM取样边界

已核对当前锁定的`@remotion/renderer` Page实现：`closed`为实际布尔字段，renderStill在捕获帧后等待cleanup中的`page.close()`。新wrapper在close之前读取实际DOM与已加载字体；采样循环串行await，每个requestedFrame在该次捕获/关闭期间稳定，不会把旧异步日志当本帧的最终审计。composition初次选择时renderFrame为空，不计入实际采样。

坐标用真实`data-mysql-canvas`校准回1920×1080，逐文本Range而非只取SVG文字；可见性考虑祖先display/visibility/opacity。缺audit、异常、解析失败、浏览器/编译错误会使报告失败。第0帧既有自测的calibration为data-mysql-canvas，3924帧composition声明匹配、1个审计且0边界/字幕包络违规；实际PNG与记录相符。

这类审计覆盖文本外边界与字幕包络，不能代替所有图形/文字成对遮挡、裁切路径、对比度、连续动作或最终影片审看。正式视觉/动态、实际播放器、真机/听辨/ASR与上线检查不在本次工具审范围；不作这些能力的通过声明。

## 本次审读文件身份

| 文件 | SHA-256 |
| --- | --- |
| `episodes-codex/_shared/mysql-video/render.py` | `fe934121a4edfacf20ee60ae73e5d8282ca9956574b6979b96c580c38b745ea8` |
| `episodes-codex/_shared/mysql-video/references.py` | `823b15b4060e1f73f78951593c7f51db982b49e5b02fafbdce4414f2a264009d` |
| `episodes-codex/_shared/mysql-video/qa.mjs` | `19092b919e1c06bf53459e7b1e7a9eaea9ccf9830903503d8e08ed41ddea11cf` |
| `episodes-codex/_shared/puzzles-video/render.py` | `486feeb845e2814dc7b3ba998d16311f48ec3464441d788a94c9d66607dd613e` |
| `episodes-codex/_shared/puzzles-video/references.py` | `ae33ca3983c444336283b77cb908835775218dd98eabf95628855709cba5e15a` |
| `episodes-codex/_shared/append_references_bibliography.py` | `fe2eb02aa15cb5fc1f39752bc34ecbb879459445721f9044da38ddf6e3fee70b` |
| `episodes-codex/_shared/append_references_original.py` | `cacd1e138e3ccb030dc6d5aee9ca8c5ea3104edb802000780a015dee4acc3579` |
| `episodes-codex/_shared/append_references.py` | `6688770d1221a115c9c1f591e3bffd14a6603d8c809c5b66f5e03e2fa4639f02` |
