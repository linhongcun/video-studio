# 做片流程

从调研做到站点发版。命令只列仓库里真实存在的脚本。现行工程参考 `episodes-codex/db-lock/`、`episodes-codex/db-transaction/` 及各期 README；开新期的目录说明在 [../episodes-codex/_template/README.md](../episodes-codex/_template/README.md)。规范在 [RULES.md](RULES.md)。

本文中 `episodes/degradation` 的20镜、5152帧及旧组件结构属于上一轮范例。EP.01–14 再次重制后，站点目录已换成新片数据，不能将 live 目录当作旧回归输入或当前制作工程；[固定历史输入](../episodes/_shared/tests/fixtures/degradation-v0.45.0/README.md)保存旧分镜、音轨及完整哈希，旧制作说明在 `docs/examples/`。每期实际命令、哈希定义和能力边界以该期 `episodes-codex/<slug>/README.md` 为准。

制作与发布范围按 [RULES.md 的 STATUS](RULES.md#status) 执行。2026-10-24 起，用户交办或已确定选题的视频做好并检查后，可自主合并、发布 Release、部署 GitHub 站点；不再逐期等待用户批准。平台新发仍须另行授权。

## 检查清单

- [ ] 调研笔记里的每条事实都有公开链接和访问日期
- [ ] 确定观众需要的前置概念、本期层级及单集范围；每集一个机制，内容超出短片容量优先拆分或移入文章
- [ ] 有多个情景时先设计全局流程与当前位置，检查放大局部、缩回定位、情景重置及结尾回收；导航不遮关键动作
- [ ] 检查主要章节的口头衔接：先承接并说明下一段方向，再展开新动作；章节标题不能代替旁白过渡
- [ ] 算法题意前置：假设没见过原题，只看开头能复述输入、允许做什么、关键限制、目标和返回值；用小例子说明合法选择，必要时对比不合法选择，先通过此项再介绍解法
- [ ] `script.md`、`article.mdx`、`pronunciation.md` 三条主线一致
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

交付物：公开出处清单。本仓没有统一的 `research.md` 文件名。`episodes/degradation/script.md` 把片外事实放在文首「文章提醒」，`episodes/degradation/article.mdx` 用脚注写链接和访问日期。新期沿用这个写法。格式见 [research-template.md](research-template.md)。

内部 handoff、旧分镜、对话不能当引用。

## 2. 脚本

先为本期写一句要兑现的问题，再把机制、成功过程、失败收尾与适用边界连成一条可观看的因果链。篇幅超出短片容量时拆成独立课程，不只在长视频里增加章节，也不靠加速配音压时长。脚本定稿前估算时长；真实配音后复核，动画须留出状态变化与结果停留的时间。

算法题先做题意复述检查：先看开头，不查题目网页或文章，写出“给了什么、允许做什么、受什么限制、要找什么、返回什么”。这五项应由画面与旁白直接支持；只有题号、标题、数组或字符串上屏不算完成。先用一个小例子建立合法选择与目标，再进入指针、窗口、栈或其他解法。题意里的冲突可以作为开头，不能把算法内部问题当作观众已知前提。

脚本冻结前另做叙事检查：明确“本片唯一回答的问题、开头给观众的悬念或方向、结尾怎样兑现”，逐镜判断删掉后是否损失因果。开头应立即让观众知道主题与为何继续看，不能先连续讲范围、常识或术语。事实与状态核验不能代替这一项编辑判断；未过时先改稿，不启动配音和全片渲染。Agent A01本次用首2/5/15秒及结尾回扣检查作为具体标准，不把单期镜数与时间点照搬为所有片子的固定结构。

场景入口另检查：遮住技术大标题后，观众能否从首屏看出谁在使用什么功能、想完成什么事。对话或操作界面适合建立场景时，直接演示该功能；随后再展开内部机制。不要把内部框图出现或用户读到题名，当成使用情境已经建立。

多情景内容另核对观众能否回答“现在走哪条路、从哪里分开、为什么切到下一种情况”。先画简明流程，再安排总览、局部聚焦和返回的位置；路径空间位置保持稳定，回边用于恢复/重试，不能把情景重置画成同一笔业务经历相反结局。无字幕动态复核须包括变焦中间态与跨情景连续片段，不能只看各镜静态端点。


交付物：

| 文件 | 作用 |
|---|---|
| `script.md` | 旁白、画面、屏幕文字、出处。旁白以「旁白：」为准 |
| `article.mdx` | 站点文章。前置信息见 degradation：`title`、`summary`、`chapters`、`related` |
| `pronunciation.md` | 多音字和整词读法，三列表：文本、读法、出现镜号 |

degradation 的脚本写明旧比喻作废、一条主线、术语在口播到时才上屏。画面约定（browser / canvas、示例域名、DevTools 次数）写在 `script.md` 文首，并原样进分镜 `meta.style`。

`plan.md` 只在部分旧期出现。degradation 脚本写的是「无单独 plan」。不要为了凑文件新建 `plan.md`。

## 3. 分镜与封面

交付物：

| 文件 | 作用 |
|---|---|
| `storyboard.json` | 镜头、字幕、配音区间、元素。字段见 [storyboard-schema.md](storyboard-schema.md) |
| `covers.json` | 16:9 / 4:3 / 3:4。重制期由本期 `remotion/src/Cover.tsx` 经别名 `@covers` 读取 |
| `knoll-props.md` | 制作说明。空白模板 [knoll-props.template.md](knoll-props.template.md)，EP.14 全文 [examples/knoll-props.degradation.md](examples/knoll-props.degradation.md)。可生成：`python3 episodes/_shared/make_knoll_props.py --dir EPDIR`（骨架，散文是待填）或 `--spec SPEC.py`。模板仍是标题和散文的参照。`episodes/degradation/storyboard.json` 的 `assets.procedural.description` 仍点名 `knoll-props.md`，该期目录里没有这份文件。新页型以范例和 `episodes/degradation/remotion/src/components/` 里实际使用的组件为准 |

参考镜头：`episodes/degradation` 共 6 个 `scenes`、20 个 `shots`，`meta.durationInFrames` 为 5152，`fps` 30，`frame` 只有 `browser` 和 `canvas`。

## 4. 配音

交付物：`remotion/public/audio/voice.wav`、`words.json`，以及分镜里每个镜头的 `voice` / `timing`。细节见 [voice.md](voice.md)。

逐句 TTS：

```sh
python3 episodes/_shared/tts/mimo_say.py --text "一句带句号的旁白。" --out /tmp/line.wav --voice 冰糖 --gap 0.28 --segments /tmp/line.json
```

密钥读环境变量 `MIMO_API_KEY`，或 `--env` 指向的文件（默认 `/workspace/video-studio/.mimo.env`：工作区根目录下、已被 `.gitignore` 忽略的文件）。不要把密钥写进仓库；`episodes/_shared/tests/secret_scan.py` 会拦。

从脚本到整轨的脚本在 `episodes/_shared/voice/`，用法见那里的 `README.md`。顺序：`prep.py`（`voice/sents.json`）→ `cue_tests.py`（`voice/cue_tests.json`）→ `gen.py`（TTS takes，结果每次不同）→ `take_asr.py` / `score.py` / `take_sandhi.py` / `take_probe.py` 选 take、改送模文本，必要时 `pitch_edit.py` + `splice_edit.py`，写 `voice/picks.json` 和 `voice/substitutions.md` → `sh episodes/_shared/voice/run.sh EPDIR`（`build.py`：逐句 −21 LUFS，镜内间隔 0.35 秒、镜间 0.70 秒，句前 0.30 秒、句尾 0.60 秒，非末镜至少 225 帧，整轨 −16 LUFS，真峰值限制；`asr.py` / `asr_full.py`：faster-whisper medium；`onsets.py`、`lastword_fix.py`、`cues_rule.py`、`shot_frames.py`、`selfcheck.py`、读音检查）。产出 `voice.wav`、`words.json`、`voice/cues.json`、`voice/shot_frames.json`。参数默认即 EP.14 的值，按期改写 `voice/params.json`。选 take 和听辨（读音、变调、`selfcheck.log` 里的 ASR 不一致）要人或代理判断，脚本不替你判。`selfcheck.py` 退出码 1 就停。每镜旁白以 。？！ 结尾：跨镜的一句 `onsets.py` 处理不了。铺轨完成前不要渲染成片。

整轨已经在手、并且是 EP.05 起那种整轨放在第 0 帧时：

```sh
python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole
```

先核对 `shots[].voice` 与 wav：`|from + localStart − wavStart|` 默认不超过 0.5 帧，`wavEnd` 不超出总帧，按时间排的句子不重叠，样本数等于 `durationInFrames × 1600`。通过后把源文件原样复制到 `remotion/public/audio/voice.wav`（实体文件，不是软链）。`--no-copy` 只写报告。失败时打印有问题的 id，退出码 1，不写文件。

`--mode place` 只给 EP.02–04 那种先分镜后剪句：从 `wavStart..wavEnd` 剪出，放在 `from + localStart`，再做到 −16 LUFS，软拐点 0.7。`spansInto` 的句子播完，不在镜尾切断。输出默认 `voice/placed.wav`。

标签窗口：

```sh
python3 episodes/_shared/label_onset_strict.py --dir EPDIR
```

任一 FAIL、NOT FOUND、MISMATCH 则退出码 1。报告默认 `label-onset-strict.txt`。已批准的例外用 `--exc 06,18`（对镜头 id 前两位）。制作说明用上一节的 `make_knoll_props.py`。

## 5. 冻结 SHA-256

`episodes/degradation/words.json` 用全文：

- `scriptSha256`：脚本旁白所依据的文本
- `audioSha256`：`voice.wav`

`storyboard.json` 的 `meta.timingSource` 和每个镜头的 `timing.source` 写前缀，例如 `voice.wav 9e70470c`、`words.json 36bccee8`。

EP.02 把整份分镜的全文 SHA-256 写死在 `episodes/https/remotion/scripts/verify-storyboard.tsx`。那是该期回归，不是全系列脚本。

本仓没有统一的冻结脚本。核对时用与上述文件相同的 SHA-256（`hashlib.sha256`，见 `verify-storyboard.tsx` 和 `episodes/http-request/validate_v6.py`）。前缀对不上就停止，不要渲染。

## 6. Deming 预检

见 [validate.md](validate.md)。预检不过就改分镜或配音，然后回到第 5 步重新冻结。

打勾顺序见 [qa.md](qa.md)（预检和成片审）。

## 7. 渲染

见 [render.md](render.md)。参考实现：

```sh
cd episodes/degradation/remotion
npm ci
npm run render
```

`npm run render` 先出 `out/voice.mp4`，再调用 `episodes/_shared/music/mix_bgm.py`，得到 `episodes/degradation/video.mp4`。

封面走本期的 `Cover16x9` / `Cover4x3` / `Cover3x4`，不要对 degradation 运行 `episodes/_shared/cover` 的 `npm run covers`：它的分镜没有顶层 `cover`，`covers/cover-spec.json` 里也没有 `degradation`。

## 8. 成片审与上线

完成动态表达与实际成片复核，记录执行者、检查结果和能力限制。通过后沿用 STATUS 的持续授权，按 [publish.md](publish.md) 接入 `episodes/<slug>/`、更新元数据与版本、合并站点 PR、打 tag、发 Release，再部署并核验线上文件；不再逐期等待用户 widget 批准。收到反馈后修正、重新检查和发布。平台新发需用户另行明确授权。

站点只改页面、不重发平台时，沿用 v0.45.0 的做法：PR 说明写「只上站点」，Release 同样写明，平台链接保持不动。

## 9. 按实际反馈复盘

每期完成制作、返工或收到用户反馈时，先判断有没有需要带到下一期的新发现。有实际错误就追加到 [教训](lessons-learned.md)，有独立检查或用户观看支持的有效做法就补 [成功经验](successful-practices.md)；仅有指导、尚待验证的做法先写 [项目记忆](production-memory.md)。写明案例、适用范围、具体改法与验证证据，后续收到观看反馈再更新结论，不把“已发布”当作“用户认可”。没有新发现时不机械增加条目。

EP.21 的教学层级反馈是例子：五类方案分章解决了覆盖范围，但用户还要求单独增加“什么是分布式事务”的前置篇。因此选题阶段要同时确认本期讲什么、观众应先知道什么，以及从入门到深入怎样衔接；不把复杂内容全部塞进同一集，也不替用户删去需要的方案覆盖。随后用户观看方案合集又指出时长、密度与单方案深度不足，要求常见实现各自成短片；因此“有章节”“有入门篇”不能代替单集范围控制，最新编排为入门接四个独立机制短片。
