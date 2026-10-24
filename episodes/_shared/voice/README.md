# 配音整轨（episodes/_shared/voice）

EP.14 degradation 配音那一步的脚本，按期参数化。每个脚本都带 `--dir EPDIR`，在 `EPDIR/voice/` 里运行，读写的相对路径和 EP.14 一样（`sents.json`、`takes/`、`../voice.wav`、`../words.json`）。默认参数就是 EP.14 的值，见 `common.py` 的 `DEFAULTS`；某一期要改，就写 `EPDIR/voice/params.json`，只写要改的键。起音只 import `episodes/_shared/onset_rule.py`，不复制。30 fps，48 kHz。

依赖：python3、ffmpeg、numpy、scipy、soundfile；QA 脚本另需 praat-parselmouth；ASR 需 faster-whisper（首次运行从 Hugging Face 下载 Systran/faster-whisper-medium，约 1.5 GB）。TTS 需环境变量 `MIMO_API_KEY`（或 `mimo_say.py --env` 指向的文件，不进仓库）和网络。

## 顺序

| 步 | 命令（都加 `--dir EPDIR`） | 产出 | 谁判断 |
|---|---|---|---|
| 1 | `prep.py` | `voice/sents.json`（tts = 原句 + 「好。」尾巴） | 机器 |
| 2 | `cue_tests.py` | `voice/cue_tests.json`（画面行里出现在旁白中的「」词） | 机器，可手改 |
| 3 | `gen.py [--jobs voice/jobs_x.json]` | `voice/takes/{sid}-{take}.wav` | 机器（TTS，不确定性） |
| 4 | `take_asr.py takes/...wav > voice/tc_x.log`，`score.py tc_x.log` | `voice/score.json` | 机器 |
| 5 | `take_sandhi.py`、`take_probe.py 词 takes/...`；读错的改送模文本再 `gen.py --jobs`；必要时 `pitch_edit.py` + `splice_edit.py` | `voice/picks.json`、`voice/substitutions.md` | **人或代理听辨** |
| 6 | `sh episodes/_shared/voice/run.sh EPDIR` | `voice.wav`、`words.json`、`voice/cues.json`、`voice/shot_frames.json`、`voice/build.json`、各 log | 机器；`selfcheck` 失败退出 1 |
| 7 | 读 `voice/selfcheck.log` 的 ASR 不一致、`sandhi_*.log`、`probe.log` | 回到 5 或通过 | **人或代理听辨** |
| 8 | `python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole` | `remotion/public/audio/voice.wav` | 机器 |

`run.sh` 依次跑 build → asr → asr_full → onsets → lastword_fix → cues_rule → shot_frames → selfcheck → sandhi（一、不）→ sandhi_verdict →（有 `voice/probe.in` 时）probe。`--no-asr` 复用已有 `voice/asr.json`，只在 takes 和 build 参数都没变时用。

## 已知限制

- 一句话跨两镜（prep 打出 `spansShots` 警告）时 `onsets.py` 会失败，EP.14 没有这种句子。每镜旁白都以 。？！ 结尾。
- `build.py` 只把非末镜拉长到 `minShotFrames`；末镜不拉长，`selfcheck` 也只标记不判失败。
- `sandhi_verdict.py` 的「期望声调」只认 EP.14 出现过的后字，新稿要补字表。
- TTS 每次结果不同；同一批 takes、同一份 picks 之后的 build、ASR（同一 CPU 上 faster-whisper 1.2.1 / ctranslate2 4.8.3，float32）、onsets 都逐字节可复现。
