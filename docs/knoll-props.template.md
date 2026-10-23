# Knoll 制作说明模板

复制本文件为当期的 `knoll-props.md`。EP.14 的完整写法见 [examples/knoll-props.degradation.md](examples/knoll-props.degradation.md)。

分镜 `assets.procedural.description` 可以点名这份说明。写进这里的文字、颜色、坐标和帧号必须与冻结的 `storyboard.json`、`covers.json` 逐字一致。渲染代码不写死这些值。

EP.14 范例的文首写「由 `make_knoll_props.py` 从分镜生成」。该脚本不在本仓，不要去跑。本模板用手填。

## 文首（必填）

```markdown
# EP.{N} {slug}-v{n} {这一版画面在回答什么}

依据：storyboard.json {sha256 前缀}；covers.json {sha256 前缀}。若有冻结副本，写文件名，并注明是否逐字节相同。
script {sha} / voice {sha} / words {sha} / cues {sha} / shot_frames {sha}，{总帧} 帧，{镜数} 镜。镜头绝对帧按 Knoll 所定。
所有帧号从本镜第 0 帧算。画面坐标是 1920×1080。封面用该尺寸的画布坐标（16:9 为 1920×1080，4:3 为 1440×1080，3:4 为 1080×1440）。
```

没有的哈希写「无」，不要编一个。

### 只给人看、渲染时忽略的字段

列出本期渲染不读的字段。EP.14 的清单是：

`cueLog` `timerLog` `cueOnset` `onsetLocal` `timingReason` `timingRole` `appearTimer` `dimFromCue` `overlayOk` `conflict` `sampleData` `questionText` `boxCard` `timerDriven` `outsidePage` `sync` `cueText` `disappearCueText` `addressFit` `coverStill`

本期渲染若读取其中某个字段，从清单删掉，并写进对应页型表。

`strike` 与 `strikeColor` 是渲染属性：文字中线删除线，线宽 = fontSize × 0.08，颜色缺省取 `color`。用到的镜号写在这一段。没用到就写「本期不用」。

## 本版相对 {上一冻结 sha} 的变化（必填）

先写要不要重渲：哪些镜、哪些封面，哪一镜不动。再按条写改动，必改和可选分开。每条包含镜号、元素 id、框 `[x, y, w, h]`、对齐或状态，以及挂词帧有没有改。

相对上一冻结没有差异时写「无」。不要省略这一节。

## 相对上一期的变化——Knoll 必读（必填）

- 新页型：`page` 名、组件名、有哪些 `view`。被取代的旧页型点名。
- 本期明确不用的组件（例如不开 DevTools）。
- 同镜多窗口、标签是切换还是新开、波纹 `center` 指向 `boxes` 的哪个键。
- 页外角标的位置（右缘、y、是否 `outsidePage: true`）。
- 段长例外，与 `meta.durationExceptions` 一致：`[{shot, frames, max, reason}]`。没有则写「无」。
- 沿用的属性名。只列本期元素里真的出现的。

## 0. 画面类型 `frame`（必填）

| 镜 | id | frame | 绝对帧 | 帧数 | 方框 |
|---|---|---|---|---|---|
| {n} | {id} | `"browser"` 或 `"canvas"` | {from}–{to} | {frames} | 是，或留空 |

`frame` 只写本期 `storyboard.json` 里出现过的值。`canvas` 镜是全屏干净底色，不画外框、标签页、地址栏和网址。`browser` 镜才用下一节的页型。

## 1. 页型与状态帧（有 browser 镜则必填）

每种 `page` 一小节。先给字段表：

| 字段 | 类型 | 含义 |
|---|---|---|
| `view` | 本期允许的取值 | 各取值画什么 |
| {视图对象} | 形状 | 画在 `boxes` 的哪些键 |

状态帧用本镜帧，不写绝对帧。每一条：

- 镜 {n} `{page 或 page2}` [{x},{y},{w},{h}] scale={n}：初始 view、url、title，以及该视图要画的对象。`backTabs` / `afterTabs`。
  - 帧 {local}（{状态名}，对「{cueText}」）{这一帧相对上一状态的补丁}

逐字输入单独写：起止帧、每帧一字、`url` 取目标字符串的前几个字符。

标签怎样从上一镜接过来，写在该页型小节末尾。

没有 browser 镜时，这一节写「无」。

## 2. 页外角标与叠字（必填）

一行一个元素，按镜号排：

- 镜 {n} `{id}` {组件名或 None} [{x},{y},{w},{h}] fs={fontSize} color={#RRGGBB} bg={#RRGGBB} appear={帧} text='{与分镜逐字相同}'

有消失或状态帧时再加 `disappear`、`fadeOut`、`states=[[帧, "状态"]]`。`outsidePage: true` 的角标在行内注明。没有叠字就写「无」。

## 3. 计数与同步（必填）

同帧变化的计数、条宽写在这里：

- 镜 {n} `{id}`（与谁同帧）帧 [{f}, …] → [{显示文字或宽度}, …]

没有这种元素就写「无」。

## 4. 封面 `covers.json`（必填）

写 sha256 前缀、有哪些尺寸、`poster` 取哪一档。然后每个尺寸一行：画布宽高、`bottom15Y`、窗口 `[{x},{y},{w},{h}]`、内容是否落在 4:3 的 x 315..1125 且 y < 918。

主标题或价格行的每一段单独写：文案、框、字号、颜色。`priceLine: true` 的段注明 `priceRole`（big / small），并写明 `priceRole` 只给人看。

版式原因与 `covers.json` 的 `layoutReason` 一致，写一句。

## 5. 方框加文字镜 / 讨论题 / 下期（必填）

- boxShots = [{镜头 id}, …]。写明占全部镜头的比例，与 `meta.boxShots` 一致。
- discussionQuestion = '{与分镜逐字相同}'
- nextEpisode = {"episode": {n}, "title": "{标题}", "teaser": "{预告}"}

没有下期就写 `nextEpisode` 缺省，不要编预告。

## 字段约定

- 框一律 `[x, y, w, h]`，单位像素。
- 颜色写 `#RRGGBB`。分镜没有的色值不要在说明里补。
- 状态帧挂词写成「对「{cueText}」」，花括号里的字与分镜 `cueText` 相同。
- `ripples[].center` 取 `boxes` 里的键，不写死圆心坐标。`growFrames` 与 `meta.timingSource` 里写的波纹时长一致。
- 只在这一期出现的新属性，在第 1 节写类型和画法。沿用属性只在「Knoll 必读」点名。
