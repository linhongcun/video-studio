# 校验

Deming 预检在配音和分镜 SHA-256 冻结之后、渲染之前。成片审在渲染之后。现行检查没有一支覆盖全系列的 `validate.py`。

## 不要跑的脚本

`episodes/db-lock/validate.py`、`episodes/db-isolation/validate.py`、`episodes/db-replication/validate.py`、`episodes/db-sharding/validate.py`、`episodes/global-id/validate.py`、`episodes/distributed-tx/validate.py` 依赖 `episodes/_audit/labelcore.py`。本仓没有 `_audit/`，这些命令现在不能跑。其中还有「画面不出数字 / 不出英文」，该规矩已废止，见 [RULES.md](RULES.md)。

`episodes/db-index/validate.py` 和 `episodes/db-transaction/validate.py` 引用本期目录里的 `common_split.py`，服务旧分镜，不是重制期闸门。

`episodes/http-request/validate_v6.py` 是 EP.01 专用，里面写死了 `voice.wav` / `words.json` 的 SHA-256 前缀，并提到尚未接入的 `onset.py`。不要把它当成新期入口。

`episodes/https/remotion` 的 `npm run verify:storyboard` 只回归 EP.02 那一版分镜全文 SHA-256，组件白名单含 `NotepadWindow`。换一期会直接断言失败。那是该期的冻结测试，不是系列质检。

## 起音

读取 `storyboard.json` 里带 `cueText` 的元素和 `stateKeyframes`：

- `onsetLocal` 来自 `cueOnset.onsetLocal` 或关键帧上的 `onsetLocal`。
- 入场帧按 `meta.onsetRule.frameFormula`：`max(1, floor(onsetLocal) − 2) + d`。
- `appearFrame` 或关键帧 `frame` 相对 onset 的差要在 `[-6, 2]`。

阈值写在 [RULES.md](RULES.md) 和 [voice.md](voice.md)。实现是 `episodes/_shared/onset_rule.py`。本仓没有 `label_onset_strict.py`，也没有覆盖全系列的起音命令。下面只是 import，不是新的检查入口。

期目录里的 `validate.py` 目前都不 import 它，包括 `episodes/db-index/validate.py` 以及依赖 `episodes/_audit/` 的那几份。`episodes/http-request/validate_v6.py` 的文档字符串写的是另接 `episodes/http-request/onset.py`，那个文件也不在本仓。不要把那次未接线的调用改成对共享模块的调用后再当成 EP.01 已经接上。

期目录里的脚本要使用规则时：

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_shared'))
from onset_rule import Rule
```

`label_onset_strict.py` 若以后放进仓库，同样 `from onset_rule import Rule`，先把 `episodes/_shared` 放进 `sys.path`。不要在 `episodes-codex/_shared/` 再留一份。`Rule(samples, sr).onset(st, en, prevStart, prevEnd)` 的参数见 [voice.md](voice.md)。返回的 `onset` 是小数帧。窗口仍用分镜里的 `appearFrame − onsetLocal`，模块自己不算这道窗口。

以 `episodes/_shared/onset_rule.py` 为准。本仓没有按期拷贝。期目录需要同名文件时，symlink 到 `_shared`，或只写转发 import 的薄包装，不要复制函数体。

`words.json` 的 `onsetTable` 和 `lastWordFix` 用来核对句首和句末字，不代替标签窗口。

## COPYFIT

溢出由 `episodes/degradation/remotion/src/components/ui.tsx` 的 `Copy` 打到浏览器日志，前缀是 `COPYFIT overflow`。文字不自动缩小。预检通过的条件是这些日志为空。

在该期工程里（先 `npm ci`）：

```sh
cd episodes/degradation/remotion
node scripts/prep-stills.mjs /tmp/ep-stills frames.json
node scripts/prep-stills.mjs /tmp/ep-stills frames.json --covers /tmp/ep-covers
node scripts/diagfit.mjs /tmp/ep-stills frames.json --covers
```

`frames.json` 是调用者提供的数组，不是仓库里的固定文件。元素形状来自脚本：`{"name": "hook", "frame": 0}`。`frame` 是成片绝对帧。封面合成 id 为 `Cover16x9`、`Cover4x3`、`Cover3x4`。

`scripts/stills.mjs` 同样接受 `<outDir> <framesJson> [--covers]`，但不会把 `COPYFIT` 打出来。查溢出用 `prep-stills.mjs` 或 `diagfit.mjs`。

`still.sh` 会对本期 `Root.tsx` 里每个 `id="..."` 跑 `npx remotion still`，日志在 `/tmp/still-<id>.log`。它不是 COPYFIT 的专用入口。

同一套 `prep-stills.mjs` / `diagfit.mjs` / `stills.mjs` 也在 `episodes/circuit-breaker/remotion/scripts/`。换期时进那一期的 `remotion/` 再跑，不要假定每期都有这三个文件。没有的期次就待补，不要从旧期 `validate.py` 顶上。

## 封面 4:3 安全区

读 `covers.json` 的 `sizes["4x3"]`：

- `centerRegion` 在 degradation 是 `[315, 1125]`
- `bottom15Y` 是 `918`
- 内容元素的横向范围落在 `centerRegion` 内，纵向底边小于 `bottom15Y`
- 水印用该尺寸的 `watermarkZone`（degradation 4:3 为 `[1200, 30, 1400, 100]`），不要为了塞进 `centerRegion` 去挪水印

本仓没有单独的安全区脚本。坐标不合格就改 `covers.json`。同时还要满足上一节的无 `COPYFIT`。

根 README 里曾经写过的 16:9「x280–1640、y>900」和 3:4「y<144、y>1224」不是现行闸门。

## 涟漪帧

degradation 的涟漪对象在 `ripples[]`：`id`、`bornFrame`、`center`、`r0`、`r1`、`growFrames`、`holdOpacity`、`color`。`meta.timingSource` 写明点击波纹 20 帧长满，实例的 `growFrames` 为 20。

没有涟漪检查脚本。预检时对照 `timingSource` 和 `growFrames`。组件绘制在 `episodes/degradation/remotion/src/components/ShopPricePage.tsx`（以及同目录里同样读取 `e.ripples` 的页面）。EP.14 的波纹字段写在 [examples/knoll-props.degradation.md](examples/knoll-props.degradation.md)。

## 其他和分镜写在一起的限制

这些不是独立命令，预检时读 `meta`：

- `devtoolsShots` 不超过 2。degradation 为空。
- `boxShots` 与 `boxShotRule` 一致。
- `durationInFrames` 等于各镜头 `durationInFrames` 之和，并等于 `words.json` 的 `durationFrames`（degradation 为 5152）。
- 术语标签完整显示至少 63 帧（[RULES.md](RULES.md) 仍有效条）。本仓没有计算这 63 帧的通用脚本。

## 成片响度

渲染后的报告由混音脚本写出。degradation 的 `package.json` 把报告放在 `remotion/out/mix-report.json`（`npm run render` 的 `render:mix`）。字段 `final_LUFS` 应在 −16 附近，`true_peak_dBTP` 来自 `mix_bgm.py` 的测量。脚本本身的 `loudnorm` 目标是 `I=-16`、`TP=-2.0`。
