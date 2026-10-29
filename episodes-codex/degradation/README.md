# EP.14 Codex重制工程

> 当前系列视觉入口：[`remotion/src/peak-style/index.ts`](remotion/src/peak-style/index.ts)。正文与资料页沿现行深青蓝／亮青／暖黄封面；通过[共享制作入口](../_shared/peak-video/README.md)先预检、冻结，再生成完整成片。新产物位于 `revisions/peak-style/`；下文原入口保留历史身份，不用旧命令覆盖当前发布视频。

2026-10-24 用户授权重制EP01–14，本期按今天EP15–17的因果动画经验重新制作。

本工程重写脚本、文章和动态画面，权威来源核验在research.md；逐镜观看顺序在visual-direction.md，配音选段与能力边界在voice/substitutions.md。

复现：仓内共享voice/prep.py → gen.py → build.py；本期assemble.py建立真实句边界与声学起音；共享selfcheck.py、place_v2.py --mode whole、label_onset_strict.py通过后freeze.py。Remotion中执行npm ci、npx tsc --noEmit、npm run covers、npm run render。不要重新请求已选中的非确定性TTS来代替冻结音轨。

source-sha256.json与verify-freeze.py核对实际输入；动态检查、成片指标及完成状态以后续QA记录为准。

背景音乐：Kevin MacLeod《Wallpaper》，CC BY 4.0；复用仓内共享混音，成片目标−16 LUFS。check-inputs.py检验实际冻结输入的时序/字幕/哈希，verify-freeze.py检验输入字节。

本地成片已完成并复核：3134帧，104.467秒。视频SHA-256 `4b589fd0cbf55f2c336d3f6e62f3a25225d49eacf79181709fab8430835a2245`。检查执行范围、能力限制与实际编码证据见[qa-final.md](qa-final.md)、[qa-independent.md](qa-independent.md)、[render-result.json](render-result.json)。本制作代理未改站点、提交或发布。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。

## 第8批参考资料名单与当前入口

本批为已验收的完整原片追加`title-author`参考资料名单，每页最多4项、默认5秒，仅显示完整原题与明确作者或机构。原旁白、字幕、分镜及现有视觉依赖保持；不运行装配、TTS、正文渲染或混音。基线`61d3b984a594578a67bc34aa374cccd0326cd9d6`的Git完整原片已逐字节保存在`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`，本批直接消费该body并另做实际追加媒体保真检查。

当前冻结入口为本期`freeze.py`，保留旧清单全部84个key与既有共享依赖；旧article/research/package及freeze记录通过`revisions/reference-endcards/`下before快照核对，其余按原路径核对。当前清单声明实际资料与新入口依赖，不声称它已重现旧MP4。原实质输入校验保留；storyboard、words、带SHA的分镜快照及placeholder只读检查，不再重写。来源JSON及其中记录的原始补证文件分别按完整SHA纳入冻结，技术实读日期与本轮题名/署名补查范围按来源记录区分。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/degradation
python3 episodes-codex/degradation/freeze.py
python3 episodes-codex/degradation/freeze.py --verify
```

默认`npm run render`调用共享bibliography wrapper，先核对来源和冻结，再运行`render:body`及附录。`render:body`保留本期原voice→mix闭环、编码参数与concurrency=1，只把mix输出改到`out/body.mp4`；`npm run render:references`从该完整body单独追加名单。`npm run verify:references`用于后续完整交付核验，会检查最终媒体；本批入口审计只执行只读freeze与wrapper.verify_freeze，不重复整片解码。旧正文QA和发布事实按原记录保留，最终总帧数以新receipt、render-result和发布metadata为准。进度见[第8批记录](../../docs/reference-endcards/batch-8/README.md)，不预记尚未完成的媒体或线上结果。
