# 配音

音色、响度和起音以 [RULES.md](RULES.md) 为准。参考实现：`episodes/degradation/words.json`、`episodes/degradation/pronunciation.md`、`episodes/degradation/remotion/public/audio/voice.wav`。

## 合成一句

仓库里的命令：

```sh
python3 episodes/_shared/tts/mimo_say.py --text "一句带句号的旁白。" --out /tmp/line.wav --voice 冰糖 --gap 0.28 --segments /tmp/line.json
```

脚本按 `。？！` 分句，默认音色「冰糖」，模型 `mimo-v2.5-tts`，句间 `--gap` 默认 0.28 秒。`--segments` 写出每句的 `text`、`start`、`dur`。密钥只来自 `MIMO_API_KEY` 或 `--env` 文件，不提交。

`episodes/_shared/tts/kokoro_say.py` 是另一套引擎。现行配音不用它。

`episodes/tts_timing.py` 会按镜头调用 TTS，默认引擎是 edge-tts（`zh-CN-YunxiNeural`），并写出 `remotion/src/timing.json`，用 `scale` 改镜头时长。`--engine=mimo` 时它去调用 `episodes/_shared/tts/.venv/bin/python`，不是直接调用上面的 `python3 .../mimo_say.py`。degradation 没有 `timing.json`，整轨从第 0 帧播放。重制期不要跑 `tts_timing.py`，否则会把已经冻结的绝对帧改掉。

## 整轨、词时间和镜头帧

degradation 的成片把整轨放在 `episodes/degradation/remotion/public/audio/voice.wav`。`remotion.config.ts` 用这个文件是否存在来定义 `__HAS_VOICE_AUDIO__`。`Main.tsx` 从第 0 帧播放 `staticFile('audio/voice.wav')`，注释写明轨道已按 `shots[].voice` 铺好（`voice/place_v2.py`）。

`words.json` 顶层字段：`script`、`scriptSha256`、`fps`、`audio`、`audioSha256`、`durationFrames`、`asrModel`、`note`、`shots`、`onsetTable`、`lastWordFix`。

`shots[]`：`id`、`onsetFrame`、`sentences`、`speechStartFrame`、`speechEndFrame`、`startFrame`、`endFrame`、`durationFrames`。

`sentences[]`：`index`、`id`、`text`、`take`、`startFrame`、`endFrame`、`onsetFrame`、`asr`、`asrCoverage`、`chars`、`words`。`words[]` 为 `{w, startFrame, endFrame}`。`chars[]` 为 `{ch, startFrame, endFrame}`。

`onsetTable[]`：`shot`、`sentence`、`onsetFrame`、`frameInt`、`sec`、`source`。

`lastWordFix[]`：`id`、`ch`、`old`、`new`、`speechEnd`。`note` 写明句末字若落在静音上，改用能量谷，并点名 `voice/lastword_fix.py`。

`asrModel` 记的是 `faster-whisper medium`。本仓没有调用它的脚本。

待补：`voice/place_v2.py`、`voice/shot_frames.json`、`voice/lastword_fix.py`，以及从逐句 wav 生成上述 `words.json` 的命令。见最新一期 knoll-props。不要用猜测的参数去跑一个不存在的文件。

分镜侧与词时间对齐的字段是 `shots[].voice`（`wavStart`、`wavEnd`、`localStart`、`localEnd`）和元素上的 `cueOnset`。见 [storyboard-schema.md](storyboard-schema.md)。

## 冻结

`audioSha256` 是 `voice.wav` 的 SHA-256 全文。`scriptSha256` 是当时脚本的全文。改口播或重配之后两个值都要重写，并改 `storyboard.json` 的 `meta.timingSource` 与 `shots[].timing.source` 前缀。EP.02 另把分镜全文写进 `verify-storyboard.tsx`，只有那一期这么做。

## 起音

现行规则：静音之后的第一个摩擦音、爆破音或浊音，电平 ≥ −45 dB。标签入场相对该 onset 的偏差在 −6 到 +2 帧之间。

degradation 分镜把同一条规则写成：

- 模块：`episodes-codex/_shared/onset_rule.py`（本仓没有）
- 检查：`episodes-codex/_shared/label_onset_strict.py`（本仓没有）
- 窗口：`[-6, 2]`
- 入场帧：`max(1, floor(onsetLocal) − 2) + d`

`cueOnset.rule` 在这一期使用 `pause/fricative/plosive`、`pause/voiced`、`pause/fricative (low, h/f)`、`asr/continuous`。`cueOnset` 还带 `sentence`、`asrFrame`、`onsetLocal`、`delay`。

预检时对照 `appearFrame` 与 `onsetLocal`：差值落在窗口外就退回分镜，不要渲染。没有入库的检查脚本，这一步按字段手算，或等 `onset_rule.py` 进仓后再改 [validate.md](validate.md)。

## 读音表

`pronunciation.md` 用表：文本、读法、出现镜号。多音字全部列出。英文缩写逐字母读；Redis、MySQL 按一个单词读。画面上的域名和数字只显示、不进读音表的口播。TTS 若把某个词读错，改送模文本，字幕和 `script.md` 的旁白保持原文。听辨由 Knoll 和 Nolan 做，不找村长。

## 响度

成片响度在混音时处理，不在 `mimo_say.py` 里。`episodes/_shared/music/mix_bgm.py` 默认 `--lufs -16`，`loudnorm` 的真峰值参数是 `TP=-2.0`。重制期的 `package.json` 使用 `--mode constant --below 12`。见 [render.md](render.md)。
