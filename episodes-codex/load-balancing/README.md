# EP.06《一台服务器忙不过来，怎么办？》Codex重制

2026-10-24用户明确要求将EP01–14上一轮Cursor版，按今天EP15–17的规范与经验进行Codex重制。本目录是独立的新制作工程，站点接入由主协调者在检查通过后处理。

主线：同一批请求，分给可用的应用实例。调研见research.md；脚本、文章、读音表与visual-direction.md分别保留内容、边界和逐镜动态设计。Main.tsx用连续对象和状态变化解释过程，关闭字幕与声音后仍可观察请求/内容路径。

复现配音使用仓内共享工具：

```sh
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/prep.py --dir episodes-codex/load-balancing
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/gen.py --dir episodes-codex/load-balancing
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/build.py --dir episodes-codex/load-balancing
/workspace/.venvs/video-studio/bin/python episodes-codex/load-balancing/assemble.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/selfcheck.py --dir episodes-codex/load-balancing
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir episodes-codex/load-balancing --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/label_onset_strict.py --dir episodes-codex/load-balancing
```

保留选定takes和picks.json，复现时不要重新请求非确定性的TTS替代已检查音轨。词时间兼容文件明确使用句级包络，只有句首实测声学起音；没有内部逐字ASR对齐。主协调者已检查环境，faster-whisper及本地模型均不可用，官方模型端点被策略拒绝；此限制不伪称识别通过或完整人工听辨。

在本期remotion目录执行npm ci、npx tsc --noEmit、npm run covers和npm run render。Python需要numpy、scipy、soundfile，系统需要FFmpeg、/usr/bin/chromium及Noto Sans CJK SC。工作区node_modules软链不入库；package-lock.json保留独立安装依据。

关键预演在remotion目录运行：

```sh
flock /tmp/video-studio-render.lock node scripts/motion-qa.mjs /tmp/ep06-codex-motion --shots=01,04,05,06,08,09,10,11 --flow=08-10
```

正式编码前运行freeze.py，冻结脚本、文章、调研、读音、全部Remotion源码及脚本、选定配音takes、整轨、时间数据和共享实现。编码后用verify.py核对输入未变及实际MP4。动态与最终复核实际范围见qa-motion.md和qa-final.md。

配乐沿用Kevin MacLeod《Wallpaper》，CC BY 4.0。混音调用共享mix_bgm.py，目标−16 LUFS、真峰值−2 dBTP。发布只覆盖GitHub站点，平台新发仍按原授权边界处理。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。
