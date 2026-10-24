# 校验

Deming 预检在配音和分镜 SHA-256 冻结之后、渲染之前。成片审在渲染之后。现行检查没有一支覆盖全系列的 `validate.py`。

按顺序打勾用 [qa.md](qa.md)。页身色的规则和成片采样在本文件「页身色」。本文件是命令和阈值。下面补进的通用项来自 EP.13/EP.14 的 validate 脚本。标成只对某一期成立的检查不进正文，例子见文末。

## 不要跑的脚本

`episodes/db-lock/validate.py`、`episodes/db-isolation/validate.py`、`episodes/db-replication/validate.py`、`episodes/db-sharding/validate.py`、`episodes/global-id/validate.py`、`episodes/distributed-tx/validate.py` 依赖 `episodes/_audit/labelcore.py`。本仓没有 `_audit/`，这些命令现在不能跑。其中还有「画面不出数字 / 不出英文」，该规矩已废止，见 [RULES.md](RULES.md)。

`episodes/db-index/validate.py` 和 `episodes/db-transaction/validate.py` 引用本期目录里的 `common_split.py`，服务旧分镜，不是重制期闸门。

`episodes/http-request/validate_v6.py` 是 EP.01 专用，里面写死了 `voice.wav` / `words.json` 的 SHA-256 前缀，并提到尚未接入的 `onset.py`。不要把它当成新期入口。

`episodes/https/remotion` 的 `npm run verify:storyboard` 只回归 EP.02 那一版分镜全文 SHA-256，组件白名单含 `NotepadWindow`。换一期会直接断言失败。那是该期的冻结测试，不是系列质检。

## 冻结

手工。本仓没有统一的冻结脚本。SHA-256 用 `hashlib.sha256` 全文，分镜里写前 8 位。做法与打勾命令见 [qa.md](qa.md)。`words.json` 的 `audioSha256` 等于配音全文；`meta.timingSource` 和每个镜头的 `timing.source` 含这份 `voice.wav`、这份 `words.json` 的前缀。

冻结副本与 `storyboard.json` 逐字节相同。文件名是 `storyboard.<sha8>.json`，`sha8` 是 `storyboard.json` 的 SHA-256 前 8 位。比较写在 `episodes/_shared/make_knoll_props.py` 的 `load_episode`：副本在但字节不同就退出。预检用只读比较，不要为了检查去改期目录。

```sh
python3 - <<'PY'
import hashlib
from pathlib import Path
D = Path("EPDIR")
raw = (D / "storyboard.json").read_bytes()
sha8 = hashlib.sha256(raw).hexdigest()[:8]
frozen = D / f"storyboard.{sha8}.json"
print(sha8, "MISSING" if not frozen.exists() else "OK" if frozen.read_bytes() == raw else "DIFF")
PY
```

通过：打印 `OK`。缺文件或 `DIFF` 都停。要走现成入口时：

```sh
python3 episodes/_shared/make_knoll_props.py --dir EPDIR --require-frozen --out /tmp/knoll-props.md
```

`--require-frozen` 在副本缺失时失败。`--out` 指到 `/tmp`，避免把 `knoll-props.md` 写进期目录。

## 起音

读取 `storyboard.json` 里带 `cueText` 的元素和 `stateKeyframes`：

- `onsetLocal` 来自 `cueOnset.onsetLocal` 或关键帧上的 `onsetLocal`。
- 入场帧按 `meta.onsetRule.frameFormula`：`max(1, floor(onsetLocal) − 2) + d`。
- `appearFrame` 或关键帧 `frame` 相对 onset 的差要在 `[-6, 2]`。

阈值写在 [RULES.md](RULES.md) 和 [voice.md](voice.md)。算法是 `episodes/_shared/onset_rule.py`。窗口由检查器计算：

```sh
python3 episodes/_shared/label_onset_strict.py --dir EPDIR [--exc 06,18] [--out FILE]
```

退出码 0：没有 FAIL、NOT FOUND 或 MISMATCH。`--exc` 只把这些镜头（id 前两位）的窗口越界改记为 EXCEPTION，不抵消 NOT FOUND 和 MISMATCH。退出码 1：仍有 FAIL、NOT FOUND 或 cueLog 的 MISMATCH。报告默认 `{期目录}/label-onset-strict.txt`。`--words 红包,降级` 只列出规则起音，退出码 0。没有 `storyboard.json` 时必须给 `--words`。wav 默认 `{D}/voice.wav`，没有则用 `{D}/remotion/public/audio/voice.wav`。

期目录里的 `validate.py` 目前都不 import 它，包括 `episodes/db-index/validate.py` 以及依赖 `episodes/_audit/` 的那几份。`episodes/http-request/validate_v6.py` 的文档字符串写的是另接 `episodes/http-request/onset.py`，那个文件也不在本仓。不要把那次未接线的调用改成对共享模块的调用后再当成 EP.01 已经接上。

期目录里的脚本要使用规则时：

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_shared'))
from onset_rule import Rule
```

`episodes/_shared/label_onset_strict.py` 在文件开头把所在目录放进 `sys.path`，再 `import onset_rule`。不要在 `episodes-codex/_shared/` 再留一份，也不要复制 `Rule` 的函数体。`Rule(samples, sr).onset(st, en, prevStart, prevEnd)` 的参数见 [voice.md](voice.md)。返回的 `onset` 是小数帧。窗口 `[-6, 2]` 在检查器里算：`diff = cueFrameAbs − onsetAbs`。

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

不缩字还有一条分镜估算，来自 EP.13 Deming 终审，EP.14 的 validate 脚本同样在用。估算宽度 ≤ 元素 `w − 16 − padLeft`（没有 `padLeft` 就只减 16）。字宽用该期 `ui.tsx` 的 `textWidth`。那两份脚本里的估算是全角 1em、其余 0.62em，只作预检，不能代替上面的空 `COPYFIT`。

## 镜头连贯

手工。没有通用脚本。`episodes/_shared/place_v2.py` 只覆盖配音对位。

- `scenes` 与镜头的 `from` 首尾相接。
- 整轨原位铺时，镜头 `holdFrames` 为 0。`--mode place` 的期不套这条。
- 配音对位用 `episodes/_shared/place_v2.py`。`|from + localStart − wavStart|` 不超过 0.5 帧。失败退出码 1。`--no-copy` 不改 `voice.wav`。报告不要落在期目录里：

```sh
python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole --no-copy \
  --src EPDIR/remotion/public/audio/voice.wav --report /tmp/place_v2.json
```

期目录根上已有 `voice.wav` 时可以不写 `--src`。
- 字幕拼起来与 `narration` 逐字一致（[RULES.md](RULES.md)）。首条 `from` 为 0，末条接到镜头末帧，中间相接。
- 元素 `id` 在镜内唯一。字幕层只有一个（`role` 为 `subtitle`）。`appearFrame` 落在 `[0, durationInFrames)`。
- 同元素的 `stateKeyframes` 按 `frame` 严格递增。`disappearFrame` 不早于 `appearFrame`。

单镜 180–300 帧是 EP.13/EP.14 validate 脚本里的旧上限。[RULES.md](RULES.md) 不设时长上限，预检不卡这条。`durationExceptions` 只解释该期自己写下的数字。

## 画面延续

手工。浏览器壳只给真网页、地址栏和 DevTools；讲解表、图、流程图是 `canvas`，不出现 `BrowserChrome`。假应用窗（含旧组件 `NotepadWindow`）不算通过。见 [RULES.md](RULES.md)。

browser 镜的接续来自 EP.14 Deming 预检：

- 按时间排列 `frame` 为 `browser` 的镜头。后一镜第 0 帧的标签（`backTabs`、当前标题、`afterTabs`）和 `view`，等于前一个 browser 镜结束时的状态。
- 中间隔着 canvas 时，后一镜的第 1 到第 8 帧不再改标签和 `view`。

地址栏逐字输入时：每帧一字，帧严格递增，加载或回车晚于最后一字。EP.14 的 `timingSource` 写的是输完再过 3 帧回车。换期以该期 `timingSource` 为准。

## 版式

手工。没有通用脚本。箭头和节点的位置还要对照旁白，见 [qa.md](qa.md)。

- 子流程画在父节点下方，且子节点 `x` ≥ 父节点 `x`。教训来自 EP.13 的渲染。
- 同一个服务只画一个节点。箭头的 `pointsTo` 都指向它。教训来自 EP.14 Deming 预检。
- 画面上有「核心链路」时，标签在它所标的核心元素正下方：横向与该元素对齐，`y` 更大。没有这个标签的期跳过。教训来自 EP.14 Deming 预检。
- `CalloutTag`、`CornerBadge` 的宽度余量 ≥ 12 px（框宽减去字宽）。教训来自 EP.14 Deming 预检。
- 页面注释离按钮 ≥ 16 px。教训来自 EP.14。
- 元素不重叠。分镜标明 `overlayOk` 的除外。
- 水印净区读 `meta.safeArea.watermarkClearZone`，里面没有元素。内容底边不进入 `meta.safeArea.subtitleBand`。degradation 的净区是 `[1680, 30, 1880, 100]`，字幕带是 `[900, 980]`。
- 窗内深色条若写了 `padLeft`，不少于 32。教训来自 EP.12 的讨论镜，EP.13/EP.14 的脚本都在查。

## 封面

`storyboard.json` 的 `meta.covers` 与 `covers.json` 解析后的对象相等。EP.13/EP.14 的 validate 脚本都查这个。两边空白可以不同，不要拿文件字节去比。

4:3 安全区读 `covers.json` 的 `sizes["4x3"]`。规范在 [RULES.md](RULES.md)：内容落在 `centerRegion` 内，底边小于 `bottom15Y`。degradation 是 `centerRegion` `[315, 1125]`、`bottom15Y` `918`。水印用该尺寸的 `watermarkZone`（degradation 4:3 为 `[1200, 30, 1400, 100]`），不要为了塞进 `centerRegion` 去挪水印。各尺寸的内容底边都要小于该尺寸的 `bottom15Y`。水印区里没有内容元素。

本仓没有单独的安全区脚本。坐标不合格就改 `covers.json`。同时还要满足「COPYFIT」一节的空日志。

根 README 里曾经写过的 16:9「x280–1640、y>900」和 3:4「y<144、y>1224」不是现行闸门。

封面窗口里的第一行，离页头至少 24 px。常规页头高 80，见该期 `browserHeaderHeight`。第一行顶边 ≥ 窗口顶 + 页头 + 24。`w < 600` 的 compact 窗先读该期头高，不要套死 80。教训来自 EP.14 Knoll 预检。

封面地址栏按 `episodes/degradation/remotion/src/components/BrowserChrome.tsx` 的公式留得下网址，并再空 24 px。`w` 是窗口宽，标签数含当前页。非 compact（`w ≥ 600`）时标签宽取 `min(160, 0.2w)`，地址栏宽 = `w − Σ标签宽 − 132`；有锁再减 34。`w < 600` 走 compact，地址栏宽 = `w − 44`，有锁再减。网址按 32 px 等宽的 `textWidth` 计算，结果 ≤ 地址栏宽 − 24。EP.13 脚本里的 `w − 182 − min(160, 0.2w)` 已过时，不要再用。教训来自 EP.14 Deming 预检。

## 点击和下一状态

手工。degradation 的涟漪对象在 `ripples[]`：`id`、`bornFrame`、`center`、`r0`、`r1`、`growFrames`、`holdOpacity`、`color`。组件绘制在 `episodes/degradation/remotion/src/components/ShopPricePage.tsx`（以及同目录里同样读取 `e.ripples` 的页面）。字段说明见 [examples/knoll-props.degradation.md](examples/knoll-props.degradation.md)。

点击到下一状态至少 12 帧。带 `ripples` 的状态帧，到同一元素的下一状态帧，间隔 ≥ 12。`growFrames` 仍与 `meta.timingSource` 里的波纹时长一致（degradation 为 20），那是长满的时间，不代替这 12 帧。教训来自 EP.14 Knoll 预检。本仓没有通用脚本，不要新写。

## 其他和分镜写在一起的限制

这些不是独立命令，预检时读 `meta`：

- `devtoolsShots` 不超过 2。degradation 为空。
- `boxShots` 与 `boxShotRule` 一致。
- `durationInFrames` 等于各镜头 `durationInFrames` 之和，并等于 `words.json` 的 `durationFrames`（degradation 为 5152）。
- 术语标签完整显示至少 63 帧（[RULES.md](RULES.md) 仍有效条）。本仓没有计算这 63 帧的通用脚本。

## 成片响度

渲染后的报告由混音脚本写出。degradation 的 `package.json` 把报告放在 `remotion/out/mix-report.json`（`npm run render` 的 `render:mix`）。字段 `final_LUFS` 应在 −16 附近，`true_peak_dBTP` 来自 `mix_bgm.py` 的测量。脚本本身的 `loudnorm` 目标是 `I=-16`、`TP=-2.0`。

## 页身色

规范在 [RULES.md](RULES.md)：演示页身用 `episodes/_shared/theme/pageTheme.ts` 的 `pageBg` `#0F172A`、`pageInk` `#E5E7EB`，禁止大面积纯白页身。浏览器框和 DevTools 用各期 `remotion/src/theme.ts` 的 `P`。这一节同时写分镜阈值和成片采样。两套数都服务于同一条规范，都不是新的设计色。本仓没有页身色脚本，不要新写 `validate.py`。

### 分镜和源码

渲染前手工查。阈值来自 EP.14 页身改走 `pageTheme` 之后的提案，EP.13/EP.14 的 validate 脚本里还没有这段。

- 每个镜头，以及 `covers.json` 每个尺寸：`background` / `fill` 为 `#` 色、且相对亮度 > 0.8 的元素，面积之和 ≤ 该画布的 5%。画布面积是该镜的 `meta.width × meta.height`，封面用该尺寸的 `width × height`。
- `#FFF` / `#FFFFFF` 不得作为面积 > 1% 的底。不足 1% 的仍计入上面的 5%。
- `remotion/src/components/*Page.tsx` 不用 `#fff`、`#ffffff`、`white` 作背景。页身底取 `PAGE.bg`。勾选图标上的 `stroke="white"` 是笔画，不是页身底。
- 分镜和封面的字段里不出现 `pageBg`、`pageInk`。页身色只写在 `pageTheme.ts`。

用这段 `lum()` 扫 EP.14 的分镜和封面，没有亮度 > 0.8 的 `background` / `fill`。镜 6 的 `res-free` 是 `#86EFAC`、22400 px²（约 1.1%），相对亮度约 0.70，不计入 0.8 那一档。

相对亮度用下面的函数。这是参考实现，尚未接入 validate.py。

```python
def lum(h):
    h = h.lstrip('#'); h = ''.join(c*2 for c in h) if len(h) == 3 else h[:6]
    r, g, b = (int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    f = lambda c: c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4
    return .2126*f(r) + .7152*f(g) + .0722*f(b)
for s in shots:
    area = sum(e['w']*e['h'] for e in s['elements'] for k in ('background', 'fill')
               if isinstance(e.get(k), str) and e[k].startswith('#') and lum(e[k]) > .8)
    check(area <= .05*1920*1080, f'镜 {s["scriptShot"]} 浅色大底 {area} px²')
```

`check` 不是本仓的函数。手工跑时改成打印 `area`。封面每个尺寸用该尺寸的宽乘高代替 `1920*1080`。`#FFF` / `#FFFFFF` 的面积另计，超过画布 1% 就失败。

### 成片静帧

渲染后手工采样页身像素，不采样浏览器壳。静帧只写到 `/tmp`，不要覆盖 `video.mp4`。

```sh
cd EPDIR/remotion
npx remotion still src/index.ts Main /tmp/qa-frame.png --frame=绝对帧 --log=error
```

这和 `still.sh` 用的是同一个 `remotion still`。`still.sh` 不接收任意帧，所以这里加上 `--frame`。`prep-stills.mjs` 的 jpeg 是 `scale: 0.5`，用那些图时把坐标乘 0.5。量色值用全尺寸 PNG。

页身矩形从该镜 `BrowserChrome` 的 `x`、`y`、`w`、`h` 来。`browserPageBox` 把边框算作 3 px。`browserHeaderHeight`：带 `boxes` 且页型是 `shopPrice` 等列出的那几种时，头高 80；`w < 600` 且不是这种页时，头高在 104 到 110 之间；其余也是 80。换期先读该期自己的函数。

- 左 = `x + 3`
- 上 = `y + 3 + 头高`
- 右 = `x + w - 3`
- 下 = `y + h - 3`

开发者工具停在窗口下半部时，只采样面板上沿以上。标签、地址栏、窗口外的深色底不算页身。canvas 镜采样全帧，去掉 `meta.safeArea.subtitleBand` 和水印区。讲解 canvas 的外底可以是 `meta.palette.bg`，不要求等于 `pageBg`。

```sh
python3 - <<'PY'
from PIL import Image
L, T, R, B = 0, 0, 0, 0  # 改成该镜页身矩形：左、上、右、下
im = Image.open("/tmp/qa-frame.png").convert("RGB")
body = im.crop((L, T, R, B))
px = list(body.getdata())
n = len(px)
if n == 0:
    raise SystemExit("先把 L, T, R, B 改成页身矩形")
near = sum(1 for r, g, b in px if r >= 240 and g >= 240 and b >= 240)
print("page pixels", n)
print("near-white fraction", round(near / n, 4))
for name, xy in (("tl", (12, 12)), ("tr", (body.width - 13, 12)), ("bl", (12, body.height - 13)), ("br", (body.width - 13, body.height - 13))):
    print(name, body.getpixel(xy))
PY
```

`pageInk` `#E5E7EB` 是 229,231,235，三个通道并不都 ≥ 240，正文笔画不计入 `near`。`pageBg` `#0F172A` 是 15,23,42。通道差 8 和页身 2% 只用于这次像素测量。

静帧失败，满足任一条即可：

- `near` 占页身像素超过 2%。
- 四个内角和 `#0F172A` 比，每个角都有通道差超过 8。只差一个角时记下来看，角标或按钮不单独判失败。
- 肉眼能看出整页或一整块内容区是白底或近白底。

按钮、价格高亮、`pageInk` 正文不单独判失败。JPEG 有压缩，不要用 jpeg 去卡通道差；jpeg 只用来看是不是整页发白。

通过：页身四角接近 `pageBg`，近白像素不超过 2%，肉眼没有大块白底。分镜和源码三条也同时通过。

## 每期专属检查示例

下面两条只对写出它们的那一期成立。换期要按该期脚本重写，不能当成系列闸门。

- EP.14：片中文字不出现上一期的术语「熔断」。
- EP.13：应付「101 元」只在镜 16；半开失败分支不进画面；开发者工具只在镜 6，列表里不出现保险字段。
