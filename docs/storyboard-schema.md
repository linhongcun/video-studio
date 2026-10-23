# 分镜字段

从 `episodes/degradation/storyboard.json` 和 `episodes/degradation/covers.json` 归纳。该分镜 `meta.slug` 是 `degradation-v1`。没有出现的字段不要加。`assets.procedural.description` 点名 `knoll-props.md`；空白模板是 [knoll-props.template.md](knoll-props.template.md)，EP.14 全文范例是 [examples/knoll-props.degradation.md](examples/knoll-props.degradation.md)。`episodes/degradation/` 里没有这份期文件。组件行为以范例和 `episodes/degradation/remotion/src/components/` 为准。

顶层三个键：`meta`、`assets`、`scenes`。没有顶层 `cover`。封面规格在 `meta.covers`，渲染读取的是同目录 `covers.json`（`remotion.config.ts` 把 `@covers` 指到 `../covers.json`）。

## meta

degradation 实际使用的键：

`title`、`episode`、`slug`、`release`、`draft`、`provisional`、`provisionalTiming`、`pendingAudio`、`provisionalReason`、`timingSource`、`onsetRule`、`width`、`height`、`fps`、`durationInFrames`、`durationExceptions`、`style`、`font`、`monoFont`、`palette`、`safeArea`、`poster`、`boxShots`、`boxShotRule`、`mapShots`、`devtoolsShots`、`sampleDataLabel`、`uiPolicy`、`chapters`、`covers`、`discussionQuestion`、`description`、`nextEpisode`。

和闸门直接相关的几项：

- `onsetRule.module` / `onsetRule.checker`：degradation 冻结稿写的是仓外路径 `/workspace/video-studio/episodes-codex/_shared/onset_rule.py` 与同目录的 `label_onset_strict.py`。仓内起音模块是 `episodes/_shared/onset_rule.py`。`label_onset_strict.py` 仍不在本仓。
- `onsetRule.window`：`[-6, 2]`。`onsetRule.frameFormula`：`max(1, floor(onsetLocal) − 2) + d`。
- `safeArea`：`margin` 80，`subtitleBand` `[900, 980]`，`contentMaxY` 880，`watermarkClearZone` `[1680, 30, 1880, 100]`。
- `devtoolsShots`：这一期是空数组。现行上限是 2 处，见 [RULES.md](RULES.md)。
- `boxShots`：允许方框加文字的镜头 id。这一期是镜 10、11、18、20。
- `durationExceptions`：`{shot, frames, max, reason}`。镜 1 为 314 帧，超过该期自己写的 300 帧上限，原因写在 `reason`。
- `poster`：`shotId` 为 null，`source` 为 `covers.poster`。海报用封面，不截正片帧。

`chapters[]`：`id`、`title`、`accent`、`from`、`startSec`。

## assets

`new`、`reuse` 在这一期都是空数组。`procedural.description` 是一段说明，点名 `knoll-props.md`，并列出沿用属性：`ripples`、`backTabs`、`afterTabs`、`readAlong`、`dimPage`、`fadeOut`、`CornerBadge`、`CalloutTag`、`highlighted`、`pulse`、`strike`、`padLeft`、`dimFrom`，以及 rect 宽度状态。`readAlong`、`dimPage`、`pulse` 没有出现在这一期的元素实例里，不要因为说明文字就加进新分镜。

## scenes[] 与 shots[]

`scenes[]`：`id`、`chapterId`、`title`、`accent`、`from`、`durationInFrames`、`shots`。

`shots[]`：`id`、`scriptShot`、`part`、`chapterId`、`from`、`durationInFrames`、`narration`、`subtitles`、`voice`、`timing`、`camera`、`boxShot`、`mapShot`、`frame`、`direction`、`scriptVisual`、`elements`、`animations`、`transition`。

这一期 `frame` 只有 `browser` 和 `canvas`。`camera` 全是 null。`part` 全是 null。`transition` 为 `{type: "fade", durationInFrames: 10}`。

`subtitles[]`：`text`、`from`、`to`。`from` / `to` 是镜头内帧，首条可以从 0 开始。字幕拼起来与 `narration` 逐字对应（标点可按句切开）。

`voice[]`：`id`、`wavStart`、`wavEnd`、`localStart`、`localEnd`。`id` 对应 `words.json` 里该句的 `sentences[].id`。

`timing`：`source`、`wavFrom`、`wavTo`、`holdFrames`、`tailAfterSpeech`、`holdReason`。`source` 带配音和 `words.json` 的 SHA-256 前缀。

## elements[]

这一期出现过的类型是 `text` 和 `rect`。

共通：`id`、`type`、`x`、`y`、`w`、`h`、`z`。

文字常见：`text`、`fontSize`、`color`、`align`、`fontWeight`、`background`、`appearFrame`、`cueText`、`cueOnset`、`sampleData`、`timingReason`、`timingRole`、`role`、`binding`。字幕元素是 `role: "subtitle"`、`binding: "subtitles"`、`text` 为空，由 `Main.tsx` 按当前帧填字幕。

`cueOnset`：`sentence`、`asrFrame`、`onsetLocal`、`rule`、`delay`。这一期 `rule` 的取值是 `pause/fricative/plosive`、`asr/continuous`、`pause/voiced`、`pause/fricative (low, h/f)`。

`timingRole` 在元素上只见到 `structural`。

按需出现、不是每个元素都有：`component`、`stateKeyframes`、`outsidePage`、`overlayOk`、`disappearFrame`、`disappearCueText`、`pointsTo`、`conflict`、`highlighted`、`boxCard`、`reveal`、`sync`、`sharedNode`、`dimFrom`、`dimOpacity`、`fadeOut`、`padLeft`、`strike`、`strikeColor`、`questionText`、`radius`。

`component` 这一期只有 `BrowserChrome`、`CalloutTag`、`CornerBadge`。

`BrowserChrome` 这一期的页型字段：`page`（`shopPrice`）、`title`、`url`、`showPadlock`、`sampleData`、`pageBlank`、`view`、`search`、`checkout`、`success`、`buttonPressed`、`tabLoading`、`ripples`、`backTabs`、`afterTabs`、`scale`、`rowSize`、`buttonSize`、`headlineSize`、`boxes`。`boxes` 的值是 `[x, y, w, h]`。

`stateKeyframes[]` 至少有 `frame` 与 `state`。随状态变化的页面字段会重复嵌在关键帧里（如 `checkout`、`ripples`、`pageBlank`、`url`），并可以带 `cueText`、`onsetLocal`。

`ripples[]` 这一期的实例：`id`、`bornFrame`、`center`、`r0`、`r1`、`growFrames`、`holdOpacity`、`color`。`timingSource` 写明点击波纹 20 帧长满；实例里 `growFrames` 为 20。

## animations[]

`elementId`、`property`、`easing`、`keyframes`。这一期 `property` 为 `opacity` 或 `scale`，`easing` 为 `linear`。关键帧是 `{frame, value}`。

## covers.json

顶层：`rule`、`title`、`seriesTag`、`conclusion`、`priceLine`、`layout`、`layoutReason`、`watermark`、`poster`、`sizes`。

`sizes` 的键是 `16x9`、`4x3`、`3x4`。每个尺寸有 `width`、`height`、`bottom15Y`、`watermarkZone`、`elements`。4:3 另有 `centerRegion: [315, 1125]`，`width` 1440，`height` 1080，`bottom15Y` 918。

`watermark`：`text`、`anchor`、`offset`、`fontSize`、`color`、`clearZone`。

`poster`：`source`（`3x4`）、`file`（`poster.jpg`）、`width`、`height`、`note`。

封面元素除分镜元素字段外，这一期还用了 `fill`、`secondLineColor`、`priceLine`、`priceRole`。类型还有 `pill`。

EP.02 的 `episodes/https/remotion/scripts/verify-storyboard.tsx` 在 `shot.camera` 非空时读取 `keyframes[].frame` 和 `scale`。degradation 没有使用 `camera`，新分镜不要为了这个检查去补相机。该脚本的组件白名单含 `NotepadWindow`，与现行「无假应用窗」冲突，不要照抄。
