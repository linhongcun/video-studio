# 做片流程

从调研做到站点发版。命令只列仓库里真实存在的脚本。某一步没有脚本时写成待补，参考实现是 `episodes/degradation`（分镜 `meta.slug` 为 `degradation-v1`）。开新期的目录说明在 [../episodes-codex/_template/README.md](../episodes-codex/_template/README.md)。规范在 [RULES.md](RULES.md)。

EP.14 之后暂停。STATUS 改掉之前，做到「对照参考实现」为止，不要开新目录、不要重渲。

## 检查清单

- [ ] 调研笔记里的每条事实都有公开链接和访问日期
- [ ] `script.md`、`article.mdx`、`pronunciation.md` 三条主线一致
- [ ] `storyboard.json`、`covers.json` 冻结，并写上配音 SHA-256
- [ ] `words.json` 的 `scriptSha256`、`audioSha256` 与文件一致
- [ ] Deming 预检：起音窗口、无 `COPYFIT`、封面 4:3 安全区
- [ ] `video.mp4` 与封面由当期 `package.json` 的脚本产出
- [ ] Nolan 与 Deming 审过成片
- [ ] 村长 widget 批准上线
- [ ] 站点 PR 合并、`site/package.json` 升版本、tag 与 Release
- [ ] 抖音（头条同步）、B站、微信视频号；没有快手，没有 X；链接没有发到群里

## 1. 调研

交付物：公开出处清单。本仓没有统一的 `research.md` 文件名。`episodes/degradation/script.md` 把片外事实放在文首「文章提醒」，`episodes/degradation/article.mdx` 用脚注写链接和访问日期。新期沿用这个写法。格式见 [research-template.md](research-template.md)。

内部 handoff、旧分镜、对话不能当引用。

## 2. 脚本

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

Nolan 和 Deming 看成片。通过之后，村长用单选 widget 批准上线。然后按 [publish.md](publish.md) 改 `episodes/<slug>/meta.json`、开站点 PR、打 tag、发 Release、发三个平台。站点发版由 Knoll 做。

站点只改页面、不重发平台时，沿用 v0.45.0 的做法：PR 说明写「只上站点」，Release 同样写明，平台链接保持不动。
