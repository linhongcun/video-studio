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

`voice/place_v2.py`、`voice/shot_frames.json`、`voice/lastword_fix.py`，以及从逐句 wav 生成上述 `words.json` 的命令，都不在本仓。[knoll-props.template.md](knoll-props.template.md) 只写画面制作说明，没有这些命令。不要用猜测的参数去跑一个不存在的文件。

分镜侧与词时间对齐的字段是 `shots[].voice`（`wavStart`、`wavEnd`、`localStart`、`localEnd`）和元素上的 `cueOnset`。见 [storyboard-schema.md](storyboard-schema.md)。

## 冻结

`audioSha256` 是 `voice.wav` 的 SHA-256 全文。`scriptSha256` 是当时脚本的全文。改口播或重配之后两个值都要重写，并改 `storyboard.json` 的 `meta.timingSource` 与 `shots[].timing.source` 前缀。EP.02 另把分镜全文写进 `verify-storyboard.tsx`，只有那一期这么做。

## 起音

实现是 `episodes/_shared/onset_rule.py`（2026-10-21 起，EP.06 及以后）。类名 `Rule`。模块自带的自检：

```sh
python3 episodes/_shared/onset_rule.py
```

打印 `selftest True` 只说明三条合成样本过了。它不读分镜，也不是系列预检入口。

规则与文件头注释一致：

1. 找停顿：从提示字的 ASR 起点往回搜，不早于 `max(起点 − 15 帧, 上一字 ASR 起点)`。停顿是连续不少于 2 帧、低于 −40 dB，并且停顿结束不早于上一字的 ASR 结束。起点自己落在停顿里，就用这段停顿。
2. 起音是停顿之后第一个不低于 −45 dB、且判成摩擦音、爆破音或浊音的时刻。气口不算，跳过，起音落在真正开口处。
3. 没有合格停顿（连读）时，起音等于提示字的 ASR 起点，`source` 为 `asr`。

帧是 30 fps 的小数帧，分析步长 1/4 帧。和提示帧比较时不取整。

调用：

```python
Rule(samples, sample_rate).onset(st, en, prevStart=None, prevEnd=None)
```

`samples` 是一维浮点波形。`st` / `en` 是提示字 ASR 的起止帧。`prevStart` / `prevEnd` 是上一字的 ASR 起止，句首传 `None`。返回字典含 `onset`、`source`（`pause` 或 `asr`）、`kind`、`pause`、`breaths`。

degradation 的 `cueOnset.rule` 是 `source/kind`。这一期见过 `pause/fricative/plosive`、`pause/voiced`、`pause/fricative (low, h/f)`、`asr/continuous`。`cueOnset` 还带 `sentence`、`asrFrame`、`onsetLocal`、`delay`。

标签窗口仍是 `[-6, 2]`，入场帧 `max(1, floor(onsetLocal) − 2) + d`。这道窗口不在 `onset_rule.py` 里算。`episodes-codex/_shared/label_onset_strict.py` 仍不在本仓。现有期级 `validate.py` 也不 import 这个模块。引用方式见 [validate.md](validate.md)。

冻结分镜 `meta.onsetRule.module` 还写着仓外路径 `/workspace/video-studio/episodes-codex/_shared/onset_rule.py`。以 `episodes/_shared/onset_rule.py` 这一份为准。本仓没有按期拷贝。期目录不要再复制算法；需要从本期目录 import 时，symlink 到 `_shared`，或只写转发 import 的薄包装。

预检时对照 `appearFrame` 与 `onsetLocal`：差值落在窗口外就退回分镜，不要渲染。

## 读音表

`pronunciation.md` 用表：文本、读法、出现镜号。多音字全部列出。英文缩写逐字母读；Redis、MySQL 按一个单词读。画面上的域名和数字只显示、不进读音表的口播。TTS 若把某个词读错，改送模文本，字幕和 `script.md` 的旁白保持原文。听辨由 Knoll 和 Nolan 做，不找村长。

## 响度

成片响度在混音时处理，不在 `mimo_say.py` 里。`episodes/_shared/music/mix_bgm.py` 默认 `--lufs -16`，`loudnorm` 的真峰值参数是 `TP=-2.0`。重制期的 `package.json` 使用 `--mode constant --below 12`。见 [render.md](render.md)。
