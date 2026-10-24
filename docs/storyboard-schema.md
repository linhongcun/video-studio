# 分镜字段

以下字段说明保留上一轮 EP.14 的历史范例。EP.01–14 本轮 Codex 制作在 `episodes-codex/<slug>/`；站点 `episodes/degradation/` 已是新片数据，不能再用它复现6265993b/5152帧的旧范例。固定旧输入见 `episodes/_shared/tests/fixtures/`，当前结构与检查入口见各期 README；哈希定义按当期冻结文件明确记录。

从 `episodes/degradation/storyboard.json` 和 `episodes/degradation/covers.json` 归纳（冻结稿 storyboard `6265993b`、covers `8cb7aafb`）。该分镜 `meta.slug` 是 `degradation-v1`。没有出现的字段不要加。`assets.procedural.description` 点名 `knoll-props.md`；空白模板是 [knoll-props.template.md](knoll-props.template.md)，EP.14 全文范例是 [examples/knoll-props.degradation.md](examples/knoll-props.degradation.md)。`episodes/degradation/` 里没有这份期文件。组件行为以范例和 `episodes/degradation/remotion/src/components/` 为准。

本文件只写字段和「怎样生成」。检查项与阈值的判定在 [validate.md](validate.md)，规范原文在 [RULES.md](RULES.md)，步骤顺序在 [pipeline.md](pipeline.md)。

顶层三个键：`meta`、`assets`、`scenes`。没有顶层 `cover`。封面规格在 `meta.covers`（与同目录 `covers.json` 内容相同），渲染读取的是 `covers.json`（`remotion.config.ts` 把 `@covers` 指到 `../covers.json`）。

## meta

degradation 实际使用的键：

`title`、`episode`、`slug`、`release`、`draft`、`provisional`、`provisionalTiming`、`pendingAudio`、`provisionalReason`、`timingSource`、`onsetRule`、`width`、`height`、`fps`、`durationInFrames`、`durationExceptions`、`style`、`font`、`monoFont`、`palette`、`safeArea`、`poster`、`boxShots`、`boxShotRule`、`mapShots`、`devtoolsShots`、`sampleDataLabel`、`uiPolicy`、`chapters`、`covers`、`discussionQuestion`、`description`、`nextEpisode`。

和闸门直接相关的几项：

- `timingSource`：一段说明，写 `voice.wav`、`words.json`、`script.md` 的 SHA-256 前缀，以及哪些帧按起音、哪些按画面计时（例如「点击波纹 20 帧长满」「地址栏每帧一字」）。
- `onsetRule.module` / `onsetRule.checker`：degradation 冻结稿写的是仓外路径 `/workspace/video-studio/episodes-codex/_shared/onset_rule.py` 与同目录的 `label_onset_strict.py`。仓内对应 `episodes/_shared/onset_rule.py` 与 `episodes/_shared/label_onset_strict.py`。检查器只 import 这一份算法。
- `onsetRule.window`：`[-6, 2]`。`onsetRule.frameFormula`：`max(1, floor(onsetLocal) − 2) + d`。
- `safeArea`：`margin` 80，`subtitleBand` `[900, 980]`，`contentMaxY` 880，`watermarkClearZone` `[1680, 30, 1880, 100]`。
- `palette`：`bg` `#0B1020`、`panel` `#111827`、`text` `#E5E7EB`、`muted` `#94A3B8`。这是 canvas 底色和浏览器框（与 `remotion/src/theme.ts` 的 `P` 一致），**不是**网页页身色。页身色不写进分镜，见下文「页身色」。
- `style` / `uiPolicy`：从 `script.md` 文首「画面约定」「示例数据约定」原样搬来，给人看，渲染不读。
- `sampleDataLabel`：`示例数据`。
- `devtoolsShots`：这一期是空数组。现行上限是 2 处，见 [RULES.md](RULES.md)。
- `boxShots`：允许方框加文字的镜头 id。这一期是镜 10、11、18、20。`boxShotRule` 是一句说明。`mapShots` 这一期为空。
- `durationExceptions`：`{shot, frames, max, reason}`。镜 1 为 314 帧，超过该期自己写的 300 帧上限，原因写在 `reason`。
- `poster`：`shotId` 为 null，`source` 为 `covers.poster`。海报用封面，不截正片帧。
- `discussionQuestion`：与镜 19 题干、`article.mdx` 讨论题逐字相同。
- `nextEpisode`：`episode`、`title`、`teaser`。没有下期就不写，不要编。

`chapters[]`：`id`、`title`、`accent`、`from`、`startSec`。

## assets

`new`、`reuse` 在这一期都是空数组。`procedural.description` 是一段说明，点名 `knoll-props.md`，并列出沿用属性：`ripples`、`backTabs`、`afterTabs`、`readAlong`、`dimPage`、`fadeOut`、`CornerBadge`、`CalloutTag`、`highlighted`、`pulse`、`strike`、`padLeft`、`dimFrom`，以及 rect 宽度状态。这些名字在这一期的实际位置：`readAlong` 是 `reveal.mode` 的取值（镜 19、20）；`dimPage` 只在 BrowserChrome 的 `stateKeyframes` 里（镜 19）；`pulse` 只在 `stateKeyframes` 里，和 `highlighted` 一起出现。不要因为说明文字把它们写成元素顶层字段。

## scenes[] 与 shots[]

`scenes[]`：`id`、`chapterId`、`title`、`accent`、`from`、`durationInFrames`、`shots`。

`shots[]`：`id`、`scriptShot`、`part`、`chapterId`、`from`、`durationInFrames`、`narration`、`subtitles`、`voice`、`timing`、`camera`、`boxShot`、`mapShot`、`frame`、`direction`、`scriptVisual`、`elements`、`animations`、`transition`。

这一期 `frame` 只有 `browser` 和 `canvas`（browser：镜 1、3、4、13、14、17、19；其余 canvas）。`camera` 全是 null。`part` 全是 null。`transition` 为 `{type: "fade", durationInFrames: 10}`。`scriptVisual` 是脚本「画面：」原文；`direction` 是写给制作的调度说明，挂词写成「「词」处……」。

`subtitles[]`：`text`、`from`、`to`。`from` / `to` 是镜头内帧，首条从 0 开始，末条到 `durationInFrames − 1`，前后相接。字幕拼起来与 `narration` 逐字对应（标点可按句切开）。

`voice[]`：`id`、`wavStart`、`wavEnd`、`localStart`、`localEnd`。`id` 对应 `words.json` 里该句的 `sentences[].id`。

`timing`：`source`、`wavFrom`、`wavTo`、`holdFrames`、`tailAfterSpeech`、`holdReason`。`source` 带配音和 `words.json` 的 SHA-256 前缀，如 `voice.wav 9e70470c + words.json 36bccee8`。

## elements[]

这一期出现过的类型是 `text` 和 `rect`。

共通：`id`、`type`、`x`、`y`、`w`、`h`、`z`。坐标是 1920×1080 画面坐标，框一律 `[x, y, w, h]` 的含义。

文字常见：`text`、`fontSize`、`color`、`align`、`fontWeight`、`background`、`appearFrame`、`cueText`、`cueOnset`、`sampleData`、`timingReason`、`timingRole`、`role`、`binding`。字幕元素是 `role: "subtitle"`、`binding: "subtitles"`、`text` 为空，由 `Main.tsx` 按当前帧填字幕。

`cueOnset`：`sentence`、`asrFrame`、`onsetLocal`、`rule`、`delay`。这一期 `rule` 的取值是 `pause/fricative/plosive`、`asr/continuous`、`pause/voiced`、`pause/fricative (low, h/f)`。

`timingRole` 在元素上只见到 `structural`（第 0 帧就在、不挂旁白的结构元素，如网页窗口、镜首即在的节点），配 `timingReason` 写原因。

按需出现、不是每个元素都有：`component`、`stateKeyframes`、`timerLog`、`outsidePage`、`overlayOk`、`disappearFrame`、`disappearCueText`、`pointsTo`、`conflict`、`highlighted`、`boxCard`、`reveal`、`sync`、`sharedNode`、`dimFrom`、`dimOpacity`、`fadeOut`、`padLeft`、`strike`、`strikeColor`、`questionText`、`radius`。

几项的实际写法：

- `timerLog[]`：`path`、`after`、`d`、`frame`、`why`。记录不按起音、按画面节奏定的帧（地址栏逐字输入、输完 3 帧回车、按下后 20 帧出下一页、镜 6 计数分档）。`path` 指向被定的字段，如 `stateKeyframes[2].frame`；`after` 是起算的挂词。只给人看。
- `pointsTo`：被指向元素的 `id`。镜 7–9 两条箭头文字 `a-search`「搜索页 →」、`a-checkout`「← 结算页」都写 `pointsTo: "svc-node"`。
- `sharedNode: true`：被多条箭头共用的那一个节点（镜 7–9 `svc-node`「红包服务」）。
- `reveal`：`{mode: "readAlong", source, frames}`，`frames` 是逐字出现帧（来自 `words.json` chars）。
- `sync`：一句说明，表示与哪个元素同帧变化（镜 6 计数与资源）。
- `conflict: true`：镜 1 开场冲突元素（第 0 帧全在）。
- `outsidePage: true`：页外角标，放在网页窗口外的深色底上。
- `boxCard: true`：方框加文字的说明卡，只在 `meta.boxShots` 的镜头里。
- `dimFrom` + `dimOpacity`：从该帧起压暗到该不透明度，等挂词再亮。
- `fadeOut`：淡出帧数。`padLeft`：深色条左内边距（px）。`questionText`：讨论题全文（给人看）。

`component` 这一期只有 `BrowserChrome`、`CalloutTag`、`CornerBadge`。

`BrowserChrome` 这一期的页型字段：`page`（`shopPrice`）、`title`、`url`、`showPadlock`、`sampleData`、`pageBlank`、`view`（`search` / `checkout` / `success`）、`search`、`checkout`、`success`、`buttonPressed`、`tabLoading`、`ripples`、`backTabs`、`afterTabs`、`scale`、`rowSize`、`buttonSize`、`headlineSize`、`boxes`。`boxes` 的值是 `[x, y, w, h]`，键如 `item0Button`、`coupon`、`total`、`button`、`headline`。`backTabs` / `afterTabs` 是当前标签左侧 / 右侧其他标签的标题数组；当前标签标题是 `title`。

`stateKeyframes[]` 至少有 `frame` 与 `state`。第 0 条是 `{frame: 0, state: "initial"}`。随状态变化的字段重复嵌在关键帧里。这一期关键帧里出现过：

- BrowserChrome：`url`、`title`、`view`、`pageBlank`、`search`、`checkout`、`ripples`、`backTabs`、`afterTabs`、`buttonPressed`、`tabLoading`、`dimPage`。
- 其他元素：`text`、`color`、`fontWeight`、`highlighted`、`pulse`、`strike`、`strikeColor`、`w`（rect 宽度状态）。
- 两类共有：`cueText` + `onsetLocal`（按起音的帧），或 `timerDriven: true`（按画面节奏的帧，对应 `timerLog`）。

`ripples[]` 这一期的实例：`id`、`bornFrame`、`center`、`r0`、`r1`、`growFrames`、`holdOpacity`、`color`。`center` 取 `boxes` 的键（如 `item0Button`），不写圆心坐标。`timingSource` 写明点击波纹 20 帧长满；实例里 `growFrames` 为 20。

## animations[]

`elementId`、`property`、`easing`、`keyframes`。这一期 `property` 为 `opacity` 或 `scale`，`easing` 为 `linear`。关键帧是 `{frame, value}`。入场常见写法：`appearFrame` 起 4 帧 opacity 0→1、scale 0.9→1；预压暗元素 opacity 从 `dimOpacity` 起。

## covers.json

顶层：`rule`、`title`、`seriesTag`、`conclusion`、`priceLine`、`layout`、`layoutReason`、`watermark`、`poster`、`sizes`。`layout` 这一期是 `single-window`，`layoutReason` 写一句为什么（双窗在 4:3 放不下）。

`sizes` 的键是 `16x9`、`4x3`、`3x4`。每个尺寸有 `width`、`height`、`bottom15Y`、`watermarkZone`、`elements`。4:3 另有 `centerRegion: [315, 1125]`，`width` 1440，`height` 1080，`bottom15Y` 918。封面坐标用该尺寸的画布坐标（16:9 1920×1080，4:3 1440×1080，3:4 1080×1440）。

`watermark`：`text`、`anchor`、`offset`、`fontSize`、`color`、`clearZone`。

`poster`：`source`（`3x4`）、`file`（`poster.jpg`）、`width`、`height`、`note`。

封面元素除分镜元素字段外，这一期还用了：

- `fill`、`radius`（`type: "pill"` 系列胶囊）、`secondLineColor`（两行标题的第二行颜色）。
- `priceLine: true` + `priceRole`（`big` / `small`）：价格行由同一 `y` 的几段 `text` 拼成；`priceRole` 只给人看。
- 封面里的 BrowserChrome 多三项：`frame: "browser"`、`coverStill: true`（静帧，不播状态）、`addressFit`（`fontSize`、`textWidth`、`available`、`font`，地址栏宽度的计算记录，只给人看）。

类型还有 `pill`。

EP.02 的 `episodes/https/remotion/scripts/verify-storyboard.tsx` 在 `shot.camera` 非空时读取 `keyframes[].frame` 和 `scale`。degradation 没有使用 `camera`，新分镜不要为了这个检查去补相机。该脚本的组件白名单含 `NotepadWindow`，与现行「无假应用窗」冲突，不要照抄。

## 页身色

网页页身（`*Page.tsx` 画的内容区）用 `episodes/_shared/theme/pageTheme.ts` 的 `PAGE`：`pageBg` `#0F172A`、`pageInk` `#E5E7EB`，另有 `muted` `#94A3B8`、`field` / `row` `#1E293B`、`border` `#334155`、`highlight` `#422006`、`highlightEdge` `#FBBF24`、`success` `#4ADE80`。degradation 的 `remotion/src/theme.ts` 转出这一份，`ShopPricePage.tsx` 等组件直接用。

分镜里没有页身色字段，不要新增 `pageBg`。分镜能影响的只有页外和 canvas 上的元素：文字 `background` 用 `meta.palette.bg` `#0B1020` 一类深色，强调色用这一期已有的值（如 `#86EFAC`、`#FDBA74`、`#22D3EE`、`#FDE68A` on `#7C2D12`）。不要写大面积浅色 `background` / `fill`（白、近白）；这一期浅色填充只有镜 6 资源横条 `#86EFAC`（800×28 级别）。

## 生成清单（EP.14 实际做法）

EP.13、EP.14 的分镜不是手写 JSON，而是由生成器算出来的。仓内的通用生成器在 `episodes/_shared/storyboard/`（`layout.py`、`make_covers.py`、`build_sb.py`、`validate.py`，说明见 [episodes/_shared/storyboard/README.md](../episodes/_shared/storyboard/README.md)）；每期只写一组期 spec（Python 模块，经 `--spec` 传入），引擎不含任何期内容。EP.14 的整套 spec 在 `episodes/_shared/storyboard/examples/degradation/`，重跑结果与冻结稿 storyboard `6265993b`、covers `8cb7aafb` 逐字节相同。其他共享件：`episodes/_shared/onset_rule.py`、`episodes/_shared/label_onset_strict.py`、`episodes/_shared/make_knoll_props.py` 和 `episodes/_shared/voice/`。新期照 EP.14 的 spec 另写一组，不要从旧期 `validate.py` 抄。

### 输入（都要先冻结，SHA-256 写进 `meta.timingSource`）

| 文件 | 来源 |
|---|---|
| `script.md` | 编剧／分镜。每镜四行：`frame：`、`画面：`、`旁白：`、`屏幕文字：`，外加标注表（镜号、挂在哪个词） |
| 旁白定稿 | 与 `script.md` 的「旁白：」逐字一致（spec 设 `NARRATION_FILE` 时另存一份 `N = (…)` 元组，EP.14 是 `episodes/_shared/storyboard/examples/degradation/narration.py`） |
| `voice.wav`、`words.json`、`voice/cues.json`、`voice/shot_frames.json` | `episodes/_shared/voice/`（见 [voice.md](voice.md)）。镜头绝对帧以 `words.json shots[]` / `shot_frames.json` 为准，分镜不改 |

### 脚本分工与顺序（`episodes/_shared/storyboard/`）

下面 `S=episodes/_shared/storyboard`，`EX` 是期 spec 目录，`EP` 是期目录（`--episode-dir`；输入不在期目录时用 `--inputs MAP.json` 或 `--input 名=路径` 指过去，路径相对仓根）。都在仓根下跑 `python3 -B`。

1. `python3 -B $S/make_covers.py --spec $EX/covers_spec.py --out covers.json`。三尺寸各自算框；记录 `layout` / `layoutReason`；BrowserChrome 写 `addressFit`。
2. `python3 -B $S/layout.py --spec $EX/layout_spec.py --episode-dir EP [--inputs MAP.json] --out layout.json`。每镜元素的位置、文字、状态。帧号不写死，写成三种之一：`{"$cue": 词, "d": n}`（按起音），`{"$timer": 词, "d": n, "why": …}`（按画面节奏，从该词起算），或纯整数。波纹 `bornFrame` 写 `"@"` = 取所在状态帧。
3. `python3 -B $S/build_sb.py --spec $EX/build_spec.py --episode-dir EP [--inputs MAP.json] --layout layout.json --covers covers.json --out storyboard.json`（`build-onsets.txt` 默认写在 `--out` 同目录，`--onsets-out` 可改）。读脚本、旁白、`words.json`、`voice.wav`、`layout.json`、`covers.json`，核对 spec `SHA` 里各输入的 SHA-256 前缀；整轨按原位置铺，不插停顿；`$cue` 帧用 `onset_rule.py` 算成 `max(1, floor(onsetLocal) − 2) + d` 并写 `cueText` / `cueOnset` / `onsetLocal`；`$timer` 帧写 `timerDriven` 与 `timerLog`；`covers.json` 原样嵌进 `meta.covers`；字幕照脚本原字切。
4. `python3 -B $S/validate.py --spec $EX/validate_spec.py --episode-dir EP [--inputs MAP.json] --storyboard storyboard.json --covers covers.json [--report validate.txt]`（有错误退出码 1；通用检查在引擎里，期特有的在 spec `checks(v)`），再跑 `python3 -B episodes/_shared/label_onset_strict.py --storyboard storyboard.json --wav voice.wav --words-json words.json`（期目录齐全时 `--dir EPDIR`）。判定条目见 [validate.md](validate.md)。
5. 冻结一次（见下）。
6. `knoll-props.md`：仓内用 `python3 episodes/_shared/make_knoll_props.py --dir EPDIR`（骨架）或 `--spec SPEC.py`，加 `--require-frozen` 要求冻结副本存在（EP.14 范例 `docs/examples/knoll_props_spec.degradation.py`）。只要 `storyboard.<sha8>.json` 存在，`make_knoll_props.py` 都会先断言它与 `storyboard.json` 逐字节相同。

改任何一处（文字、坐标、帧）都改期 spec（`layout_spec.py` / `covers_spec.py`），再从第 1 步重跑，不手改 `storyboard.json`。

### 冻结一次

- 一轮修改全部做完、检查全过之后，才复制 `storyboard.json` 为 `storyboard.<sha8>.json`（`sha8` = 全文 SHA-256 前 8 位），两者逐字节相同（`cmp`）。一轮只出一个新 sha。
- 上一冻结整套（分镜、封面、制作说明、脚本、生成脚本、检查报告）先备份到 `bak-<旧 sha8>/`，期目录里只留当前一份冻结副本。
- 冻结后对副本再跑一遍检查，`knoll-props.md` 写明依据的 sha8，以及「相对上一冻结的变化」和要重渲的镜号。

### 生成时就要满足的画面规则

规范原文在 [RULES.md](RULES.md)；下面是写 `layout.py` / `make_covers.py` 时落到字段上的做法。是否达标由 [validate.md](validate.md) 判。

- **一条主线。** 画面术语 2–3 个为止，术语元素的 `cueText` 就是口播里那个词，之前只出白话。
- **browser 还是 canvas。** 内容本身是网页、地址栏或 DevTools 的镜头写 `frame: "browser"`，用 `BrowserChrome` + `page`；讲解用的流程、对照、计数写 `frame: "canvas"`，canvas 里不放 `BrowserChrome`、不出 `shop.example`。不用 `NotepadWindow` 一类假应用窗，不画实物。
- **页身色。** 见上文「页身色」：页身走 `pageTheme.ts`，分镜不加页身字段、不写大面积浅色底。
- **示例。** 画面上的示例数字（价钱、计数、百分比）每段文字都带「（示例）」；每镜（片尾除外）一个 `id: "sample"` 的 `CornerBadge`「示例数据」，browser 镜放页外（`outsidePage: true`），不压说明卡、不压右上水印。域名只用 `.example`。
- **状态变化要有帧。** 脚本里写到的每个状态都要有一条 `stateKeyframes`（或独立元素的 `appearFrame`），不靠渲染端推断；同一元素状态帧严格递增。
- **点击到下一状态 ≥ 12 帧。** 带 `ripples` 的关键帧之后，下一条关键帧至少隔 12 帧，EP.14 取 20 帧（与 `growFrames` 20 一致）。点击本身已在挂词首帧时，把后续状态用 `$timer … d: 20` 往后放。
- **第 0 帧接上一镜。** 连续 browser 镜之间，第 0 帧的 `backTabs + title + afterTabs` 与 `view` 等于上一 browser 镜结尾；上一镜是 canvas 时，镜首就是该页面的初始状态，前 8 帧不再换 `view` / `pageBlank`（避免闪一帧）。不留旧标签：标签链只放旁白里真打开过的页。
- **地址栏与 `backTabs`。** 地址栏可用宽按 `episodes/degradation/remotion/src/components/BrowserChrome.tsx` 算（非 compact：窗宽 − 各标签宽 − 132，标签默认 `min(160, 0.2 × 窗宽)`；窗宽 < 600 走 compact），按原字号放得下目标网址并留 ≥ 24 px。标签越多可用越少：封面一律 `backTabs: []`、`afterTabs: []`。逐字输入写成每帧一条 `type<n>` 关键帧，`url` 为目标串前 n 个字符，输完再 `loaded`。
- **不缩字。** 渲染不自动缩小（溢出只打 `COPYFIT`），生成时按原字号算宽：每行字宽 ≤ 框宽 − 16 − `padLeft`；`CalloutTag` / `CornerBadge` 的 `w` 再加 12 px 余量。
- **「同一个」只画一个。** 旁白说「同一个 X 服务」时，只建一个节点（`sharedNode: true`），各条箭头 `pointsTo` 它。
- **标签挂在它说的东西下面。** 例如「保核心链路」放在核心链路那一侧元素正下方，x 对齐。子流程放在父节点下方，x 不小于父节点 x。
- **封面 4:3 安全区。** `sizes["4x3"]` 内容元素 x 在 `centerRegion` 315..1125、底边 y < 918（`bottom15Y`）；水印用 `watermarkZone`，不挪。封面网页首行（`boxes` 最小 y）离页头至少 24 px（`shopPrice` 页头 80，见 `browserLayout.ts` 的 `browserHeaderHeight`）。版式放不下就换版式，并写 `layoutReason`，不缩字。
- **起音。** 挂词帧走 `onset_rule.py`，差值落在 −6..+2；`d` 只在这个窗口里调。不挂旁白的结构元素写 `timingRole: "structural"` + `timingReason`。
