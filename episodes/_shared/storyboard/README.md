# episodes/_shared/storyboard — 分镜生成器

通用引擎 + 每期一组 spec。引擎不含任何期内容；每期的文字、坐标、挂词、SHA 前缀、期特有检查都写在 spec（普通 `.py` 模块）里，经 `--spec` 传入。字段含义见 [docs/storyboard-schema.md](../../../docs/storyboard-schema.md)，判定条目见 [docs/validate.md](../../../docs/validate.md)。全部在仓根下用 `python3 -B` 跑（不写 `__pycache__`）。

| 引擎 | 输入 → 输出 | spec |
|---|---|---|
| `make_covers.py` | covers spec → `covers.json`（indent 1） | `build()`，可选 `finalize(C)`、`check(C)`、`BANNED`、`HEADER`、`FIRST_ROW_GAP` |
| `layout.py` | layout spec + `words.json` → `layout.json`（indent 2） | `NSHOT`、`BROWSER`、`BOXSHOTS`、`build(ctx)`（每镜一次 `ctx.part(...)`） |
| `build_sb.py` | build spec + `script.md`、`words.json`、`voice.wav`、`layout.json`、`covers.json` → `storyboard.json` + `build-onsets.txt` | 常量、`SHA`、`CHAPTERS`/`ch_of`、`SUB`、`meta(ctx)`、`ASSETS`（见文件头） |
| `validate.py` | validate spec + 分镜 + 封面 + 脚本/文章/来源 → 报告，有错误退出 1 | 常量（见文件头）+ `checks(V)` 放期特有检查 |

共用件：`kit.py`（`--spec`/`--episode-dir`/`--inputs`/`--input`、按逻辑名找输入）、`layout_kit.py`（`C`/`TM`/`W`/`T`/`S`、`LayoutCtx`）、`onset_check.py`（validate 侧起音复核，算法只 import `episodes/_shared/onset_rule.py`）。

## 帧号写法（layout spec）

- `C('词', d)` = `{"$cue": 词, "d": n}`：按起音，`build_sb` 算成 `max(1, floor(onsetLocal) − 2) + d`，`d` 只能 −3..+4；同句多次出现用 `occ='last'`。
- `TM('词', n, why)` = `{"$timer": 词, "d": n, "why": …}`：按画面节奏，从该词起算，写进 `timerLog`。
- 纯整数：镜内画面帧。波纹 `bornFrame: "@"` = 所在状态帧。

## 输入怎么找

逻辑名（`script.md`、`words.json`、`voice.wav`、`voice/cues.json`、`voice/shot_frames.json`、`narration.py`、`article.mdx`、`ref-sources.md`、`src` …）依次查：`--input 名=路径`（可重复）→ `--inputs MAP.json`（`{名: 路径}`，相对仓根，`_` 开头的键忽略）→ `<--episode-dir>/<名>`。引擎只写 `--out` 指定的文件。

## 一期的顺序

```sh
S=episodes/_shared/storyboard; EX=<spec 目录>; EP=<期目录>; O=<输出目录>
python3 -B $S/make_covers.py --spec $EX/covers_spec.py --out $O/covers.json
python3 -B $S/layout.py      --spec $EX/layout_spec.py --episode-dir $EP --out $O/layout.json
python3 -B $S/build_sb.py    --spec $EX/build_spec.py  --episode-dir $EP --layout $O/layout.json --covers $O/covers.json --out $O/storyboard.json
python3 -B $S/validate.py    --spec $EX/validate_spec.py --episode-dir $EP --storyboard $O/storyboard.json --covers $O/covers.json --report $O/validate.txt
python3 -B episodes/_shared/label_onset_strict.py --storyboard $O/storyboard.json --wav <voice.wav> --words-json <words.json>
```

改文字、坐标、帧都改 spec 再从头重跑，不手改 `storyboard.json`。全过之后才冻结（`storyboard.<sha8>.json`，见 schema 文档「冻结一次」）。

## EP.14 范例（`examples/degradation/`）

EP.14 降级（`meta.slug` `degradation-v1`）的整套 spec：`covers_spec.py`、`layout_spec.py`、`build_spec.py`、`validate_spec.py`，加上仓里没有的输入 `narration.py`、`sources/ref-sources.md`、`sources/src/*.txt`；`repo-inputs.json` 把其余输入指到仓内已跟踪的文件（`episodes/degradation/`、`episodes/_shared/tests/golden/degradation/voice/`）。

```sh
sh episodes/_shared/storyboard/examples/degradation/rerun.sh [OUTDIR]
```

预期：`检查 6623 项，错误 0`，起音复核 91/91，`label_onset_strict` `91 cues, 0 fail`；`storyboard.json` sha256 `6265993b…`、`covers.json` `8cb7aafb…`，与 `episodes/degradation/` 下两份 `cmp` 无输出。

新期：复制这四个 spec 改内容即可；期特有的检查放 `validate_spec.checks(V)`，不要改引擎。引擎改动必须保证 `rerun.sh` 仍逐字节一致、仍是 6623 项。

## 自测

```sh
python3 -B episodes/_shared/storyboard/tests/test_storyboard.py     # 也在 episodes/_shared/tests/run_all.sh 里
```

`tests/make_fixture.py` 在临时目录里造一个两镜合成期（4 秒 150 Hz 正弦“字”+ 静音，没有真人声音或视频），`tests/fixtures/tiny/` 是它的脚本、文章和 spec。好路径：四步全过、重跑逐字节一致、`--inputs`/`--input` 等价。坏路径必须被拒：挂词帧偏离起音、字幕不照脚本、元素进字幕带（`layout_bad_spec.py`）、封面元素进底部 15%（`covers_bad_spec.py`，`make_covers` 不写文件）、`narration.py` 与脚本旁白不一致。
