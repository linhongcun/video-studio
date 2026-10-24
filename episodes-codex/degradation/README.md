# EP.14 Codex重制工程

2026-10-24 用户授权重制EP01–14，本期按今天EP15–17的因果动画经验重新制作。

本工程重写脚本、文章和动态画面，权威来源核验在research.md；逐镜观看顺序在visual-direction.md，配音选段与能力边界在voice/substitutions.md。

复现：仓内共享voice/prep.py → gen.py → build.py；本期assemble.py建立真实句边界与声学起音；共享selfcheck.py、place_v2.py --mode whole、label_onset_strict.py通过后freeze.py。Remotion中执行npm ci、npx tsc --noEmit、npm run covers、npm run render。不要重新请求已选中的非确定性TTS来代替冻结音轨。

source-sha256.json与verify-freeze.py核对实际输入；动态检查、成片指标及完成状态以后续QA记录为准。

背景音乐：Kevin MacLeod《Wallpaper》，CC BY 4.0；复用仓内共享混音，成片目标−16 LUFS。check-inputs.py检验实际冻结输入的时序/字幕/哈希，verify-freeze.py检验输入字节。

本地成片已完成并复核：3134帧，104.467秒。视频SHA-256 `4b589fd0cbf55f2c336d3f6e62f3a25225d49eacf79181709fab8430835a2245`。检查执行范围、能力限制与实际编码证据见[qa-final.md](qa-final.md)、[qa-independent.md](qa-independent.md)、[render-result.json](render-result.json)。本制作代理未改站点、提交或发布。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。
