# 渲染与封面

以各期 `remotion/package.json` 为准。下面的命令从现行 `package.json`、`episodes/_shared/music/mix_bgm.py` 和 `episodes/_shared/cover/render.mjs` 抄出。过时说法（每句 −21 LUFS、渲染器一律在正片后追加 2 秒片尾、`npm run typecheck`、`npm run still`）不要再执行：degradation、circuit-breaker、https、http-request 的 `package.json` 都没有 `typecheck` 和 `still`。

## 正片

参考 `episodes/degradation/remotion/package.json`：

```sh
cd episodes/degradation/remotion
npm ci
npm run render
```

`npm run render` 等于：

```sh
npm run render:voice
npm run render:mix
```

`render:voice`：

```sh
remotion render src/index.ts Main out/voice.mp4 --codec=h264 --crf=26 --bundle-cache=false
```

`render:mix`：

```sh
python3 ../../../episodes/_shared/music/mix_bgm.py \
  --in out/voice.mp4 \
  --bgm ../../../episodes/_shared/music/Wallpaper.mp3 \
  --mode constant --below 12 \
  --out ../video.mp4 \
  --report out/mix-report.json
```

人声文件要先放在 `remotion/public/audio/voice.wav`。`remotion.config.ts` 据此设置 `__HAS_VOICE_AUDIO__`。文件不存在时画面仍会出，但没有配音。

`remotion/public/audio/voice.wav` 必须是实体文件（或打包后仍有效的拷贝）。不要用相对软链指过去：Remotion bundle 时把 `public/` 拷进临时目录，相对软链在那里断掉，渲染时 `staticFile('audio/voice.wav')` 404，整片渲染失败（EP.14 出过一次）。用 `python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole` 放置，它按字节复制，目标若是软链会先删掉再写实体文件。手动放时用 `cp`，不要 `ln -s`。渲染前可以确认：

```sh
test -f remotion/public/audio/voice.wav && test ! -L remotion/public/audio/voice.wav && echo ok
```

`mix_bgm.py` 还可选 `--lufs`（默认 −16）、`--offset`、`--wav`。`--mode duck` 在重制期的 `package.json` 里没有使用。

输出：

- `episodes/<slug>/remotion/out/voice.mp4` — 混音前
- `episodes/<slug>/video.mp4` — 成片
- `episodes/<slug>/remotion/out/mix-report.json` — `final_LUFS`、`true_peak_dBTP`

degradation 的成片帧数等于分镜 `durationInFrames`（5152），也等于 `words.json` 的 `durationFrames`。片尾句子在最后一镜里。`Main.tsx` 没有挂 `ChannelBranding`，不会在这 5152 帧后再加一段。`episodes/_shared/branding/spec.json` 的 `endCard.frames` 仍是 60，那是水印组件规范；这一期的工程没有调用它。不要在分镜总帧数之外再加 60 帧，除非该期 `timingSource` 写明要加。

## 演示页页身色

浏览器壳和 DevTools 用各期 `theme.ts` 的 `P.*`，保持深色不动。壳里的网页页身（各期 `src/components/*Page.tsx`）用 `episodes/_shared/theme/pageTheme.ts` 的 `PAGE`：`bg` `#0F172A`、`ink` `#E5E7EB`，另有 `muted`、`field`、`row`、`border`、`highlight`、`highlightEdge`、`success`。别名 `pageBg` = `PAGE.bg`，`pageInk` = `PAGE.ink`。

引用方式：每期 `remotion/src/theme.ts` 转发一行，不要把色值抄进期目录：

```ts
// Demo page body (not chrome). See episodes/_shared/theme/pageTheme.ts.
export {PAGE, pageBg, pageInk} from '../../../_shared/theme/pageTheme';
```

`*Page.tsx` 从本期 `theme` 引入（参考 `episodes/degradation/remotion/src/components/ShopPricePage.tsx`）：

```ts
import {P, PAGE} from '../theme';
// 页身根节点
<div style={{position: 'absolute', inset: 0, background: PAGE.bg, color: PAGE.ink}}>
```

新增 `*Page.tsx` 必须这样用 `PAGE.bg` / `PAGE.ink`（或 `pageBg` / `pageInk`），输入框、卡片、行底用 `PAGE.field` / `PAGE.row` / `PAGE.border`。不要写死 `#FFFFFF`、`#F8FAFC` 一类大面积浅色底；高亮、成功色在深底上用 `PAGE.highlight*` / `PAGE.success`，不要沿用浅底时代的色值。要改配色只改 `pageTheme.ts`，改后受影响各期都要重渲并重新审片。提交前可以查：

```sh
rg -n -i "#fff(fff)?\b|#f8fafc" episodes/*/remotion/src/components/*Page.tsx
```

## 重制期封面

`episodes/degradation/remotion/src/Root.tsx` 注册 `Cover16x9`、`Cover4x3`、`Cover3x4`，尺寸来自 `covers.json` 的 `sizes`。`Cover.tsx` 用 `@covers` 读 `covers.json`。

出静帧并查看 `COPYFIT`：

```sh
cd episodes/degradation/remotion
node scripts/prep-stills.mjs /tmp/ep-stills frames.json --covers /tmp/ep-covers
```

`frames.json` 形如 `[{"name":"hook","frame":0}]`。封面 PNG 写到 `--covers` 目录，文件名 `Cover16x9.png`、`Cover4x3.png`、`Cover3x4.png`。

`node scripts/diagfit.mjs /tmp/ep-stills frames.json --covers` 同样会出封面，并打印 `COPYFIT`。

`bash still.sh` 对本期 `Root.tsx` 的每个 composition id 执行 `npx remotion still`，文件在 `stills/`。查溢出仍以 `prep-stills.mjs` / `diagfit.mjs` 的日志为准。

degradation 目录里已有 `cover-16x9.jpg`、`cover-4x3.jpg`、`cover-3x4.jpg` 和 `poster.jpg`。本期 `package.json` 没有把 PNG 转成这些 JPG 的脚本。各尺寸的框和价格行写在 [examples/knoll-props.degradation.md](examples/knoll-props.degradation.md) 第 4 节，那里没有转 JPG 的命令。不要改用下面的共享封面命令来生成 degradation 的封面。

`meta.json` 的 `poster` 在 degradation 是 `cover-16x9.jpg`。`covers.json` 的 `poster.file` 写的是 `poster.jpg`，并注明海报与 3:4 同一构图。两个字段同时存在，改海报时两处一起对，不要只改一处。

## 共享封面工程

只适用于分镜顶层有 `cover`，或 slug 写在 `covers/cover-spec.json` 里的期。`episodes/degradation/storyboard.json` 没有顶层 `cover`，`cover-spec.json` 也没有 `degradation`。对这种期运行下面的命令会退出并打印「没有 … 的 cover 节点」。

```sh
cd episodes/_shared/cover
npm ci
npm run covers -- <slug>
npm run covers -- <slug> --out <dir> --only Cover34
npm run covers -- <slug> --set-poster
```

合成 id 是 `Cover169`、`Cover43`、`Cover34`（`src/Root.tsx`）。输出 `cover-16x9.jpg`、`cover-4x3.jpg`、`cover-3x4.jpg`，JPG 控制在 2MB 以内。`--set-poster` 把该期 `meta.json` 的 `poster` 写成 `cover-16x9.jpg`，而且不能和 `--out` 一起用。

4:3 安全区不由这个工程计算。现行闸门见 [validate.md](validate.md)：x 315..1125、y < 918，且无 `COPYFIT`。
