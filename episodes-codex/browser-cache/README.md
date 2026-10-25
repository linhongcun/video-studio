# EP.07《同一个网页，第二次打开为什么快这么多？》Codex重制

2026-10-24用户明确要求将EP01–14上一轮Cursor版，按今天EP15–17的规范与经验进行Codex重制。本目录是独立的新制作工程，站点接入由主协调者在检查通过后处理。

主线：同一张图片，能直接复用就少传一次。调研见research.md；脚本、文章、读音表与visual-direction.md分别保留内容、边界和逐镜动态设计。Main.tsx用连续对象和状态变化解释过程，关闭字幕与声音后仍可观察请求/内容路径。

复现配音使用仓内共享工具：

```sh
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/prep.py --dir episodes-codex/browser-cache
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/gen.py --dir episodes-codex/browser-cache
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/build.py --dir episodes-codex/browser-cache
/workspace/.venvs/video-studio/bin/python episodes-codex/browser-cache/assemble.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/selfcheck.py --dir episodes-codex/browser-cache
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir episodes-codex/browser-cache --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/label_onset_strict.py --dir episodes-codex/browser-cache
```

保留选定takes和picks.json，复现时不要重新请求非确定性的TTS替代已检查音轨。词时间兼容文件明确使用句级包络，只有句首实测声学起音；没有内部逐字ASR对齐。主协调者已检查环境，faster-whisper及本地模型均不可用，官方模型端点被策略拒绝；此限制不伪称识别通过或完整人工听辨。

在本期remotion目录执行npm ci、npx tsc --noEmit、npm run covers和npm run render。Python需要numpy、scipy、soundfile，系统需要FFmpeg、/usr/bin/chromium及Noto Sans CJK SC。工作区node_modules软链不入库；package-lock.json保留独立安装依据。

关键预演在remotion目录运行：

```sh
flock /tmp/video-studio-render.lock node scripts/motion-qa.mjs /tmp/ep07-codex-motion --shots=03,04,05,06,07,08,09 --flow=06-09
```

正式编码前运行freeze.py，冻结脚本、文章、调研、读音、全部Remotion源码及脚本、选定配音takes、整轨、时间数据和共享实现。编码后用verify.py核对输入未变及实际MP4。动态与最终复核实际范围见qa-motion.md和qa-final.md。

配乐沿用Kevin MacLeod《Wallpaper》，CC BY 4.0。混音调用共享mix_bgm.py，目标−16 LUFS、真峰值−2 dBTP。发布只覆盖GitHub站点，平台新发仍按原授权边界处理。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。


## 参考资料附录制作入口（2026-10-25）

本批在已发布正文之后追加可暂停的静态参考资料卡，默认每页5秒。卡片内容来自本期 `references.json`，完整出处、章节及对应论点见 `references.md` 和配套文章；原脚本、分镜、配音、字幕及正文帧数保持，最终总帧数由附录清单和发布 `meta.json.finalVideoFrames` 声明。旧检查记录保留其历史范围，本轮进度与上线证据见 [首批记录](../../docs/reference-endcards/batch-1/README.md)。

`freeze.py` 在原有输入之外收录参考资料、来源核验记录和共享附录工具。先确认全部负责人停写并冻结，再执行渲染；只读复核使用 `python3 freeze.py --verify`。Pillow按 `../_shared/requirements-reference-appendix.txt` 固定版本安装；系统字体与Pillow/FFmpeg版本作为真实工具链指纹记录在附录产物中，不把系统绝对路径伪装为可移植仓库依赖。

在本期 `remotion/` 目录按锁文件安装依赖后，`npm run render` 依次输出：

1. `out/voice.mp4`：原正文画面与人声。
2. `out/body.mp4`：沿用原共享混音的正文成片。
3. `../video.mp4`：共享 `append_references.py` 将参考卡接在正文后，保留正文画面与AAC音轨，附录无新增旁白。

`revisions/reference-endcards/reference-appendix.json` 记录输入/输出完整SHA、原正文与附录区间、总帧数、每页资料及工具链；同目录 `reference-appendix-media-check.json` 记录实际编码验证，`references-01.png` 等是卡片原稿。首次补存量时先按批次基线保存或从固定Git提交提取原正文，不能将已含附录的 `video.mp4` 当作正文再次追加。共享工具拒绝无可追溯回执的未知覆盖。

只读源核对通过后，在本期 `remotion/` 目录运行 `npm run verify:references`，以共享工具复核最终成片的正文保留、片尾范围及完整解码；正文时序继续按原分镜核验，不将原只适用正文的帧数检查冒充最终附录检查。检查通过后再同步发布副本，保留原URL、创建/首发时间和平台历史链接。未执行全片人工听辨或逐字ASR的能力边界继续如实保留。
