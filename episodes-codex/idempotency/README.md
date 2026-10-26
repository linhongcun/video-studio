# EP.12 Codex重制工程

2026-10-24 用户授权重制EP01–14，本期按今天EP15–17的因果动画经验重新制作。

本工程重写脚本、文章和动态画面，权威来源核验在research.md；逐镜观看顺序在visual-direction.md，配音选段与能力边界在voice/substitutions.md。

复现：仓内共享voice/prep.py → gen.py → build.py；本期assemble.py建立真实句边界与声学起音；共享selfcheck.py、place_v2.py --mode whole、label_onset_strict.py通过后freeze.py。Remotion中执行npm ci、npx tsc --noEmit、npm run covers、npm run render。不要重新请求已选中的非确定性TTS来代替冻结音轨。

source-sha256.json与verify-freeze.py核对实际输入；动态检查、成片指标及完成状态以后续QA记录为准。

背景音乐：Kevin MacLeod《Wallpaper》，CC BY 4.0；复用仓内共享混音，成片目标−16 LUFS。check-inputs.py检验实际冻结输入的时序/字幕/哈希，verify-freeze.py检验输入字节。

本地成片已完成并复核：2998帧，99.933秒。视频SHA-256 `93167c788f97ec666be2ff42f011d4506a8205f84c343a40a4b27acc3e64ce3d`。检查执行范围、能力限制与实际编码证据见[qa-final.md](qa-final.md)、[qa-independent.md](qa-independent.md)、[render-result.json](render-result.json)。本制作代理未改站点、提交或发布。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。

## 第12批参考资料与当前入口

本批从基线`f3610e244f9e23e7a9075e406bbc990ba53b7699`的完整Git发布原片追加`title-author`参考资料，每页最多4项、默认5秒。原MP4已核对完整SHA和总帧数，保存为`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；本批直接使用这些原片，不重渲正文、混音或TTS。原完整body共2998帧，无代码卡，原收尾和字幕范围保持。

原84项声明全部现存，按原路径或article/research/freezer/package四份before快照逐项核对；旧源与旧引擎原路径及字节保持。新freeze.py只写当前清单，分镜快照/placeholder只读核对，不调用旧写入型冻结器。当前新增清单说明真实入口与附录输入，不声称已据此重现原MP4；旧QA与历史制作事实保留原意。

来源全部停写后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/idempotency
python3 episodes-codex/idempotency/freeze.py
python3 episodes-codex/idempotency/freeze.py --verify
```

默认`npm run render`经共享bibliography wrapper检查来源和冻结，再生成完整body并追加资料。当前render:body保留原voice→mix闭环。默认mix只改输出到`out/body.mp4`，其余混音参数及concurrency=1保留。`npm run render:references`从完整body单独追加；`npm run verify:references`用于后续完整交付核验。最终总帧数由新receipt/render-result与发布meta声明，正文SB/words范围不改。生产整合结果见[入口报告](../../docs/archive/2026-10/reference-endcards-batch-12/production-entry-check.json)，[本批记录](../../docs/archive/2026-10/reference-endcards-batch-12/README.md)只按真实完成状态更新。
