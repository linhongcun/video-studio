# 配音

音色、响度和起音以 [RULES.md](RULES.md) 为准。制作音轨保存在 `episodes-codex/<slug>/`；站点目录只保留发布所需数据，不存配音整轨。参考当前 `episodes-codex/db-lock/`、`episodes-codex/http-request/` 的 README、选中 takes、铺轨及冻结检查。历史逐字 ASR 范例单独保存在固定 fixture，不能与现行句级声学数据混用。

## 合成一句

仓库里的命令：

```sh
python3 episodes/_shared/tts/mimo_say.py --text "一句带句号的旁白。" --out /tmp/line.wav --voice 冰糖 --gap 0.28 --segments /tmp/line.json
```

脚本按 `。？！` 分句，默认音色「冰糖」，模型 `mimo-v2.5-tts`，句间 `--gap` 默认 0.28 秒。`--segments` 写出每句的 `text`、`start`、`dur`。整期批量合成用 `episodes/_shared/voice/gen.py`（jobs 文件 `[[句id, take, 送模文本或 null, style?], …]`），它只调用 `mimo_say.py`，自己不读密钥。密钥只来自 `MIMO_API_KEY` 或 `--env` 文件，不提交。

## 整轨、句时间和镜头帧

复用 `episodes/_shared/voice/` 的 `prep.py`、`gen.py`、`build.py`，按 `voice/params.json` 构建整轨。选段写入 `voice/picks.json`，送模文本修订及能力边界写入 `voice/substitutions.md`；保留已选中 takes，不因普通复核重新请求非确定性 TTS。

当前句级工程通过本期 `assemble.py` 或 [共享句级装配](../episodes-codex/_shared/README.md) 建立 `words.json`、字幕、镜头边界和句首声学起音。`asrModel: none`、`wordAlignment: false` 时，兼容 words/chars 字段不代表完成逐字 ASR。具体参数与顺序按本期 README，不把旧 EP.14 的镜数或停留秒数当成统一值。

已有逐字 ASR 管线的工具仍在 [voice/README.md](../episodes/_shared/voice/README.md)：`asr.py` / `asr_full.py`、`onsets.py`、`lastword_fix.py`、`cues_rule.py`、`shot_frames.py`、`selfcheck.py`。只有模型、运行结果和检查均实际完成时才记录对应能力；不能因历史管线存在就自动填写通过。

当前整轨通过下列命令校验后，按字节复制到实体 `remotion/public/audio/voice.wav`，从第 0 帧播放：

```sh
python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole
```

`EPDIR` 为制作目录。目标不能是相对软链，Remotion bundle 后会失效，见 [render.md](render.md)。`--mode place` 只用于历史剪句回归，不用于改变当前冻结时序。已发布工程只读复核用 `--no-copy`，报告放 `/tmp`。

分镜的 `shots[].voice` 记录 `wavStart`、`wavEnd`、`localStart`、`localEnd`，元素的 `cueOnset` 记录所用起音。`words.json` 的 shots/sentences 记录真实句边界、选定 take、音轨和脚本哈希。字段说明见 [storyboard-schema.md](storyboard-schema.md)；实际语义以本期装配实现为准。

## 冻结

`audioSha256` 是实际 `voice.wav` 的完整 SHA-256。`scriptSha256` 的输入定义按本期装配代码：当前 EP.14 比较整份 `script.md`，历史回归中的旁白提取文本定义不同，不能混用。改口播、重配或重装配后，要重新核对分镜时序、起音、冻结清单及受影响媒体。

冻结与只读核对入口见 [validate.md](validate.md)。校验失败先找原因，不能用更新清单把新源码追认给旧成片。

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

历史 EP.14 fixture 的 `cueOnset.rule` 是 `source/kind`。该样例记录过 `pause/fricative/plosive`、`pause/voiced`、`pause/fricative (low, h/f)`、`asr/continuous`。`cueOnset` 还带 `sentence`、`asrFrame`、`onsetLocal`、`delay`。

标签窗口仍是 `[-6, 2]`，入场帧 `max(1, floor(onsetLocal) − 2) + d`。这道窗口不在 `onset_rule.py` 里算，由检查器算：`diff = 镜头绝对帧 − onset`。

```sh
python3 episodes/_shared/label_onset_strict.py --dir EPDIR
```

退出码 1 表示有 FAIL、NOT FOUND 或 MISMATCH。`--exc 06,18` 把对应镜头 id 前两位的窗口越界改记为 EXCEPTION。报告默认写在当期目录的 `label-onset-strict.txt`。当前工程是否另有本期检查入口，以本期 README 为准。冻结分镜 `meta.onsetRule.checker` 里的 `/workspace/video-studio/episodes-codex/_shared/label_onset_strict.py` 就是这一份。引用方式见 [validate.md](validate.md)。

冻结分镜 `meta.onsetRule.module` 还写着仓外路径 `/workspace/video-studio/episodes-codex/_shared/onset_rule.py`。以 `episodes/_shared/onset_rule.py` 这一份为准。本仓没有按期拷贝。期目录不要再复制算法；需要从本期目录 import 时，symlink 到 `_shared`，或只写转发 import 的薄包装。

预检时对照 `appearFrame` 与 `onsetLocal`：差值落在窗口外就退回分镜，不要渲染。

## 读音表

`pronunciation.md` 用表：文本、读法、出现镜号。多音字全部列出。英文缩写逐字母读；Redis、MySQL 按一个单词读。画面上的域名和数字只显示、不进读音表的口播。TTS 若把某个词读错，改送模文本，字幕和 `script.md` 的旁白保持原文。听辨由 Knoll 和 Nolan 做，不找村长。改送模文本的记录写在 `voice/substitutions.md`，选定的 take 写在 `voice/picks.json`。

## 响度

成片响度在混音时处理，不在 `mimo_say.py` 里。`episodes/_shared/music/mix_bgm.py` 默认 `--lufs -16`，`loudnorm` 的真峰值参数是 `TP=-2.0`。重制期的 `package.json` 使用 `--mode constant --below 12`。见 [render.md](render.md)。
