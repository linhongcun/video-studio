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

`mix_bgm.py` 还可选 `--lufs`（默认 −16）、`--offset`、`--wav`。`--mode duck` 在重制期的 `package.json` 里没有使用。

输出：

- `episodes/<slug>/remotion/out/voice.mp4` — 混音前
- `episodes/<slug>/video.mp4` — 成片
- `episodes/<slug>/remotion/out/mix-report.json` — `final_LUFS`、`true_peak_dBTP`

degradation 的成片帧数等于分镜 `durationInFrames`（5152），也等于 `words.json` 的 `durationFrames`。片尾句子在最后一镜里。`Main.tsx` 没有挂 `ChannelBranding`，不会在这 5152 帧后再加一段。`episodes/_shared/branding/spec.json` 的 `endCard.frames` 仍是 60，那是水印组件规范；这一期的工程没有调用它。不要在分镜总帧数之外再加 60 帧，除非该期 `timingSource` 写明要加。

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

degradation 目录里已有 `cover-16x9.jpg`、`cover-4x3.jpg`、`cover-3x4.jpg` 和 `poster.jpg`。本期 `package.json` 没有把 PNG 转成这些 JPG 的脚本。待补：见最新一期 knoll-props。不要改用下面的共享封面命令来生成 degradation 的封面。

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
