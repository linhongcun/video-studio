# 从模板开一期

先读仓库根上的 [AGENTS.md](../../AGENTS.md)、[docs/RULES.md](../../docs/RULES.md) 和 [docs/pipeline.md](../../docs/pipeline.md)。本目录目前只有这份说明，没有可复制的 Remotion 工程。

## 当前授权范围

按 [docs/RULES.md](../../docs/RULES.md) 的 STATUS 推进用户交办或已确定的选题。2026-10-24 用户已持续授权：做好并完成检查后可自主合并 GitHub 主干、发布 Release、部署 Pages，收到反馈再修改重发，无需每期等待 widget 批准。资料、动画动态复核、时序、媒体和线上完整 SHA 检查继续执行，能力限制如实记录；平台新发须另行明确授权。

## 最短路径

参考实现是 `episodes/degradation`。分镜里的 `meta.slug` 为 `degradation-v1`，站点目录名仍是 `degradation`。内部制作名用 `<slug>-v1`，进站点的目录用 `<slug>`。

1. 按 [docs/research-template.md](../../docs/research-template.md) 写公开出处。片中一条主线；多出来的事实只进文章。
2. 照 `episodes/degradation/script.md`、`article.mdx`、`pronunciation.md` 的结构写这三份。不要先写比喻。
3. 照 [docs/storyboard-schema.md](../../docs/storyboard-schema.md) 写 `storyboard.json` 和 `covers.json`。制作说明从 [docs/knoll-props.template.md](../../docs/knoll-props.template.md) 抄一份再填，写法对照 [docs/examples/knoll-props.degradation.md](../../docs/examples/knoll-props.degradation.md)。页型从 `episodes/degradation/remotion/src/components/` 里已有的组件选，不要新造假应用窗。
4. 配音按 [episodes/_shared/voice/README.md](../../episodes/_shared/voice/README.md)：`prep.py` → `cue_tests.py` → `gen.py`（要 `MIMO_API_KEY`）→ 选 take 与听辨（人或代理判断，写 `voice/picks.json`）→ `sh episodes/_shared/voice/run.sh EPDIR`（`selfcheck` 退出码 1 就停）。整轨在手之后：`python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole`（整轨放第 0 帧，校验后原样复制到 `remotion/public/audio/voice.wav`，实体文件）。
5. 制作说明：`python3 episodes/_shared/make_knoll_props.py --dir EPDIR`（或 `--spec`）。冻结 SHA-256，跑 `python3 episodes/_shared/label_onset_strict.py --dir EPDIR`（退出码 1 即未过），再做 [docs/validate.md](../../docs/validate.md) 的其余预检，按 [docs/render.md](../../docs/render.md) 渲染。
6. 完成动态表达和实际成片复核，记录执行者、结果及能力限制；按持续授权把站点需要的 `meta.json`、`article.mdx`、冻结 `video.mp4`、封面放进 `episodes/<slug>/`，按 [docs/publish.md](../../docs/publish.md) 合并、发 Release、部署并核验线上完整 SHA。无需逐期用户批准，平台发布另行授权。

工程文件以 `episodes/degradation/remotion/package.json` 的脚本为准：`npm ci` 然后 `npm run render`。不要运行根 README 旧文里的 `npm run typecheck` 或 `npm run still`，那两个脚本不在这期的 `package.json` 里。
