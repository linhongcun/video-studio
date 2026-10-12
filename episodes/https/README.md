# 第二期：HTTPS 为什么安全？（草稿，未发布）

`meta.json` 标记 `draft: true`：站点默认构建不列出、不生成页面（本地预览：`SHOW_DRAFTS=1 npm run build`）。

| 文件 | 负责 | 状态 |
|---|---|---|
| `plan.md` | Christopher Nolan | 已定 |
| `script.md` | Aaron Sorkin | 待导演审核后放入 |
| `article.mdx` | Aaron Sorkin | 待导演审核后放入 |
| `storyboard.json` | Hayao Miyazaki | 空骨架（`scenes: []`，meta 沿用第一期 1920×1080/30fps 规格） |
| `remotion/` | John Knoll | 工程骨架 |

## 渲染流程（同第一期）
1. 配音：`python3 ../tts_timing.py ./ --engine=mimo --gap=0.28`（Xiaomi MiMo TTS 冰糖；需 MIMO_API_KEY）→ `remotion/public/audio/<shotId>.wav` 与 `remotion/src/timing.json`
2. `cd remotion && npm ci && npm run render`：先渲染纯人声 `out/voice.mp4`，再用 `../../_shared/music/mix_bgm.py --mode constant --below 12` 混入 Wallpaper（Kevin MacLeod, CC BY 4.0，固定音量，比旁白低约 12dB，1s 淡入 / 2s 淡出，-16 LUFS）输出 `../video.mp4`
3. `python3 validate.py` 校验分镜
