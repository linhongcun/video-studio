# 做片流程

从调研做到站点发版。命令只列仓库里真实存在的脚本。现行工程参考 `episodes-codex/db-lock/`、`episodes-codex/db-transaction/` 及各期 README；开新期的目录说明在 [../episodes-codex/_template/README.md](../episodes-codex/_template/README.md)。规范在 [RULES.md](RULES.md)。

制作目录统一使用 `episodes-codex/<slug>/`，`episodes/<slug>/` 只保存站点发布数据。已被替代的旧制作工程已清理；[固定历史输入](../episodes/_shared/tests/fixtures/degradation-v0.45.0/README.md)仍用于共享工具回归，旧制作说明在 `docs/examples/`。每期实际命令、哈希定义和能力边界以当前工程 README 为准。

制作与发布范围按 [RULES.md 的 STATUS](RULES.md#status) 执行。2026-10-24 起，用户交办或已确定选题的视频做好并检查后，可自主合并、发布 Release、部署 GitHub 站点；不再逐期等待用户批准。平台新发仍须另行授权。

## 检查清单

- [ ] 开工前已保护工作区、拉取并整合最新主干；记录基线SHA，检查重构/删除及共享脚本、源码入口、锁文件与依赖位置；同步后重读更新手册，再开始复制或修改工程
- [ ] 调研笔记里的每条事实都有公开链接和访问日期
- [ ] 确定观众需要的前置概念、本期层级及单集范围；每集一个机制，内容超出短片容量优先拆分或移入文章
- [ ] 有多个情景时先设计全局流程与当前位置，检查放大局部、缩回定位、情景重置及结尾回收；导航不遮关键动作
- [ ] 检查主要章节的口头衔接：先承接并说明下一段方向，再展开新动作；章节标题不能代替旁白过渡
- [ ] 算法题意前置：假设没见过原题，只看开头能复述输入、允许做什么、关键限制、目标和返回值；用小例子说明合法选择，必要时对比不合法选择，先通过此项再介绍解法
- [ ] `script.md`、`article.mdx`、`pronunciation.md` 三条主线一致
- [ ] 结尾直接回收本片方法与结果，不追加让视频复杂冗长的证明支线，不口头引导观众去文章补证明；严格推导按选定范围保留在文章，不自动搬进短片
- [ ] 核心术语与对应对象/动作有明确引入；地域关系参与解释时，用地图或空间参照展示，并交代地理距离与网络调度的边界
- [ ] `storyboard.json`、`covers.json` 冻结，并写上配音 SHA-256
- [ ] `words.json` 的 `scriptSha256`、`audioSha256` 与文件一致
- [ ] Deming 预检：起音窗口、无 `COPYFIT`、封面 4:3 安全区
- [ ] 检查持续动态元素是否参与当前讲解：成片内不叠加与内容无关的装饰进度条；播放器原生可操作进度控件保留
- [ ] 算法题解片尾完整代码卡：与执行源和文章同源、运行验证通过，完整程序整屏可读，默认5秒并提示暂停阅读；核对代码卡独立区间与原旁白、字幕边界
- [ ] 小修先确定影响范围，复用已验收的不变部分；优先可证实的无损剪短或局部重渲，只复核受影响区间及必要上线结果，不自动整条重渲或重复无关检查
- [ ] `video.mp4` 与封面由当期 `package.json` 的脚本产出；复用已验收媒体作时长小修时，记录原媒体SHA、准确命令与边界核验
- [ ] 成片复核完成，执行者和实际检查范围已记录，未执行的能力未伪称通过
- [ ] 符合 STATUS 的 GitHub 持续发布授权范围
- [ ] 站点 PR 合并、`site/package.json` 升版本、tag 与 Release
- [ ] Release 后部署完成，线上媒体完整 SHA、字幕、章节、海报和更新日志核验
- [ ] 将对应制作或重制 issue 以 `completed` 关闭
- [ ] 结合本期检查与用户指导复盘：有新问题/有效做法时补教训/成功经验，并更新项目记忆中的状态与证据
- [ ] 若另获平台发布授权，再发抖音（头条同步）、B站、微信视频号；不发快手或 X，链接不上群

## 1. 调研

交付物：本期 `research.md` 等公开出处清单，在脚本和文章中记录事实来源、访问日期及适用边界。参考当前 `episodes-codex/degradation/research.md`，格式见 [research-template.md](research-template.md)。

内部 handoff、旧分镜、对话不能当引用。

## 2. 脚本

先为本期写一句要兑现的问题，再把机制、成功过程、失败收尾与适用边界连成一条可观看的因果链。篇幅超出短片容量时拆成独立课程，不只在长视频里增加章节，也不靠加速配音压时长。脚本定稿前估算时长；真实配音后复核，动画须留出状态变化与结果停留的时间。

算法题先做题意复述检查：先看开头，不查题目网页或文章，写出“给了什么、允许做什么、受什么限制、要找什么、返回什么”。这五项应由画面与旁白直接支持；只有题号、标题、数组或字符串上屏不算完成。先用一个小例子建立合法选择与目标，再进入指针、窗口、栈或其他解法。题意里的冲突可以作为开头，不能把算法内部问题当作观众已知前提。

脚本冻结前另做叙事检查：明确“本片唯一回答的问题、开头给观众的悬念或方向、结尾怎样兑现”，逐镜判断删掉后是否损失因果。开头应立即让观众知道主题与为何继续看，不能先连续讲范围、常识或术语。事实与状态核验不能代替这一项编辑判断；未过时先改稿，不启动配音和全片渲染。Agent A01本次用首2/5/15秒及结尾回扣检查作为具体标准，不把单期镜数与时间点照搬为所有片子的固定结构。

场景入口另检查：遮住技术大标题后，观众能否从首屏看出谁在使用什么功能、想完成什么事。对话或操作界面适合建立场景时，直接演示该功能；随后再展开内部机制。不要把内部框图出现或用户读到题名，当成使用情境已经建立。

另按目标观众检查理解所需的前置关系：首次出现的参数、对象和动作是否已用具体例子解释，术语能否指向观众刚看懂的内容。独立审读者应仅用片中信息说清核心概念、谁做什么、为什么这样安排；不能靠已有专业知识补全跳步。复杂支线在主概念尚未建立前先收减或移入图文，避免把“定义说过了”或“运行检查通过”当作已经讲懂。策略模式的用户反馈与具体修订草案见[新手讲解复盘](strategy-beginner-reference.md)。

设计模式另做语言无关的思想审查：隐藏代码、语言名和语法说明后，仍应能说清同一任务的变化怎样隔离、职责如何协作、依赖什么共同约定、谁选择以及替换与维护边界。先把概念关系讲完整，再决定是否需要简短实现说明；不要因为某个实现前置难懂，就把设计模式视频改成语法教程。策略模式的本次纠正见L030。

多情景内容另核对观众能否回答“现在走哪条路、从哪里分开、为什么切到下一种情况”。先画简明流程，再安排总览、局部聚焦和返回的位置；路径空间位置保持稳定，回边用于恢复/重试，不能把情景重置画成同一笔业务经历相反结局。无字幕动态复核须包括变焦中间态与跨情景连续片段，不能只看各镜静态端点。


交付物：

| 文件 | 作用 |
|---|---|
| `script.md` | 旁白、画面、屏幕文字、出处。旁白以「旁白：」为准 |
| `article.mdx` | 站点文章。前置信息包括：`title`、`summary`、`chapters`、`related` |
| `pronunciation.md` | 多音字和整词读法，三列表：文本、读法、出现镜号 |

脚本保持一条主线，不用比喻；术语随对象和动作建立后引入。画面约定（browser / canvas、示例域名、DevTools 次数）写在 `script.md` 文首，并与分镜 `meta.style` 一致。

计划文件按本期装配工具采用的格式保存，不为凑目录机械增加 `plan.md`；当前句级工程的 `plan.json` 见共享工具说明。

## 3. 分镜与封面

制作目录交付 `storyboard.json`、`covers.json`、`knoll-props.md`。分镜字段见 [storyboard-schema.md](storyboard-schema.md)，实际结构与生成代码以本期工程为准；封面由本期 `remotion/src/Cover.tsx` 读取。不要将历史 EP.14 的 20 镜、5152 帧或旧组件当作新期模板。

制作说明可参考 [模板](knoll-props.template.md)，也可在制作阶段运行 `python3 episodes/_shared/make_knoll_props.py --dir EPDIR` 生成骨架，再按真实实现填写。`docs/examples/` 中旧 EP.14 全文只服务历史 fixture。新期入口见 [制作模板](../episodes-codex/_template/README.md)。

## 4. 配音

交付物：`voice.wav`、实体 `remotion/public/audio/voice.wav`、`words.json`、选定 takes 和分镜里的 voice/timing。细节见 [voice.md](voice.md)。逐句 TTS 入口：

```sh
python3 episodes/_shared/tts/mimo_say.py --text "一句带句号的旁白。" --out /tmp/line.wav --voice 冰糖 --gap 0.28 --segments /tmp/line.json
```

密钥只读环境变量 `MIMO_API_KEY` 或 `--env` 指向的已忽略文件，不写入仓库。提交前运行 `python3 episodes/_shared/tests/secret_scan.py`。

脚本到整轨复用 `episodes/_shared/voice/`：准备句子、合成 takes、选段、修改送模文本、按 `voice/params.json` 构建音轨。具体装配顺序按本期 README。现行句级工程可复用 [共享装配工具](../episodes-codex/_shared/README.md)，已有逐字 ASR 管线的能力和参数见 [voice/README.md](../episodes/_shared/voice/README.md)。选段与读音记录在 `voice/picks.json` 和 `voice/substitutions.md`。ASR、听辨和声学边界分别记录，不能冒充未完成的检查。

整轨就位后，在仓根执行下列本期步骤；`EPDIR` 指制作目录，不是站点副本：

```sh
python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole
python3 episodes/_shared/label_onset_strict.py --dir EPDIR
```

铺轨核对 `|from + localStart − wavStart|` 不超过 0.5 帧、句子不重叠、样本数与帧数一致，通过后把音轨按字节复制为公开实体文件。起音检查有 FAIL、NOT FOUND 或 MISMATCH 就停；报告默认写入期目录，已发布输入的只读复核应加 `--out /tmp/label-onset-strict.txt`。旧版剪句模式只用于固定回归，不套给当前整轨。

## 5. 冻结 SHA-256

定稿后按本期 README 调用冻结器。当前 EP.14 用 `episodes-codex/degradation/freeze.py` 写快照和 `source-sha256.json`，`verify-freeze.py` 逐文件只读核对完整 SHA-256。句级导航工程的共享冻结入口见其 README；不能假定所有期都用同一冻结器。

`words.json` 的 `audioSha256` 对应实际音轨全文，`scriptSha256` 的输入定义按本期装配代码和 README。分镜 `meta.timingSource` 和镜头 `timing.source` 对应实际音轨与时序输入。检查不一致时先查原因，不能重写清单追认旧成片未采用的源码。详见 [validate.md](validate.md)。

## 6. Deming 预检

见 [validate.md](validate.md)。预检不过就改分镜或配音，然后回到第 5 步重新冻结。

打勾顺序见 [qa.md](qa.md)（预检和成片审）。

## 7. 渲染

见 [render.md](render.md)。参考实现：

```sh
cd episodes-codex/degradation/remotion
npm ci
npm run render
```

`npm run render` 先出 `out/voice.mp4`，再调用 `episodes/_shared/music/mix_bgm.py`，得到 `episodes-codex/degradation/video.mp4`。

封面运行当期 package.json 的 `npm run covers`，由本期 Cover.tsx 与 covers.json 生成，实际文件和安全区见 [render.md](render.md)。

## 8. 成片审与上线

完成动态表达与实际成片复核，记录执行者、检查结果和能力限制。通过后沿用 STATUS 的持续授权，按 [publish.md](publish.md) 接入 `episodes/<slug>/`、更新元数据与版本、合并站点 PR、打 tag、发 Release，再部署并核验线上文件；不再逐期等待用户 widget 批准。收到反馈后修正、重新检查和发布。平台新发需用户另行明确授权。

站点只改页面、不重发平台时，沿用 v0.45.0 的做法：PR 说明写「只上站点」，Release 同样写明，平台链接保持不动。

## 9. 按实际反馈复盘

每期完成制作、返工或收到用户反馈时，先判断有没有需要带到下一期的新发现。有实际错误就追加到 [教训](lessons-learned.md)，有独立检查或用户观看支持的有效做法就补 [成功经验](successful-practices.md)；仅有指导、尚待验证的做法先写 [项目记忆](production-memory.md)。写明案例、适用范围、具体改法与验证证据，后续收到观看反馈再更新结论，不把“已发布”当作“用户认可”。没有新发现时不机械增加条目。

EP.21 的教学层级反馈是例子：五类方案分章解决了覆盖范围，但用户还要求单独增加“什么是分布式事务”的前置篇。因此选题阶段要同时确认本期讲什么、观众应先知道什么，以及从入门到深入怎样衔接；不把复杂内容全部塞进同一集，也不替用户删去需要的方案覆盖。随后用户观看方案合集又指出时长、密度与单方案深度不足，要求常见实现各自成短片；因此“有章节”“有入门篇”不能代替单集范围控制，最新编排为入门接四个独立机制短片。
