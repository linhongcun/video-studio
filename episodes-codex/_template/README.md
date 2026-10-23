# 从模板开一期

先读仓库根上的 [AGENTS.md](../../AGENTS.md)、[docs/RULES.md](../../docs/RULES.md) 和 [docs/pipeline.md](../../docs/pipeline.md)。本目录目前只有这份说明，没有可复制的 Remotion 工程。

## 现在不要开

[docs/RULES.md](../../docs/RULES.md) 的 STATUS：EP.14 之后暂停。恢复之前停在这里，不要新建 `episodes-codex/<slug>-v1/`，也不要改 `episodes/` 里的成片。

## 恢复之后的最短路径

参考实现是 `episodes/degradation`。分镜里的 `meta.slug` 为 `degradation-v1`，站点目录名仍是 `degradation`。内部制作名用 `<slug>-v1`，进站点的目录用 `<slug>`。

1. 按 [docs/research-template.md](../../docs/research-template.md) 写公开出处。片中一条主线；多出来的事实只进文章。
2. 照 `episodes/degradation/script.md`、`article.mdx`、`pronunciation.md` 的结构写这三份。不要先写比喻。
3. 照 [docs/storyboard-schema.md](../../docs/storyboard-schema.md) 写 `storyboard.json` 和 `covers.json`。`knoll-props.md` 不在本仓。待补：见最新一期 knoll-props。页型从 `episodes/degradation/remotion/src/components/` 里已有的组件选，不要新造假应用窗。
4. 用 [docs/voice.md](../../docs/voice.md) 的 `mimo_say.py` 逐句合成。整轨、`words.json` 和 `voice/shot_frames.json` 的铺轨脚本不在本仓，缺了就停。
5. 冻结 SHA-256，做 [docs/validate.md](../../docs/validate.md) 的预检，再按 [docs/render.md](../../docs/render.md) 渲染。
6. Nolan 与 Deming 审成片，村长 widget 批准之后，把站点需要的 `meta.json`、`article.mdx`、`video.mp4`、封面放进 `episodes/<slug>/`，按 [docs/publish.md](../../docs/publish.md) 发版。

工程文件以 `episodes/degradation/remotion/package.json` 的脚本为准：`npm ci` 然后 `npm run render`。不要运行根 README 旧文里的 `npm run typecheck` 或 `npm run still`，那两个脚本不在这期的 `package.json` 里。
