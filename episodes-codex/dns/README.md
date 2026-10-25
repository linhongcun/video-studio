# dns · Codex重制工程

2026-10-24用户要求将EP01–14上一轮Cursor版按当天Codex规格与经验重新制作。本目录为制作工程，站点接入由root统一处理。公开资料见research.md；旁白、文章、读音和分镜各自入库。

使用仓内共享voice/prep.py、gen.py、build.py，不复制配音算法。选定takes见voice/picks.json与substitutions.md；assemble.py仅把共享整轨结果转成句级字幕、声学句首标签与分镜，不生成或重剪音频。

Python环境：/workspace/.venvs/video-studio。Remotion安装npm ci，随后npx tsc --noEmit、npm run covers、npm run render。工作区node_modules软链是安装加速，不入库；锁文件可独立复现。系统要求FFmpeg、Chromium与Noto Sans CJK SC。

检查与能力边界见qa-motion.md、qa-final.md。ASR模型端点被当前网络策略拒绝，未声称完成逐字ASR或人工听辨；冻结词时间是句边界与声学句首，不是逐字对齐。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。

## 查询全局导航重制（2026-10-24制作阶段记录）

以下保留当时的阶段记录；本批参考资料附录的当前入口见文末，原正文基线以本批固定Git提交及完整SHA为准。

保留原12镜、3200帧、音轨、脚本、words与逐句字幕。当前导航见`remotion/src/branch-map.ts`，复用`../_shared/branch-map/index.ts`；05–09保持固定角色的局部网络，解析器自行问根/TLD/权威并接回指引或地址。两处缓存短路分别保留，11镜明确另一个未到期时点。

本轮官方资料实读见`research-flow-map.md`。原发布输入通过`revisions/pre-flow-map.json`的基线Git路径、blob与完整SHA索引追溯；旧媒体及takes不复制。此阶段只制作小样，未重新冻结或正式全片编码。小样位于`/workspace/.video-studio-flow-audit/dns-remake/`，编辑结论由root统一安排。


## 参考资料附录制作入口（2026-10-25）

本批在已发布正文之后追加可暂停的静态参考资料卡，默认每页5秒。卡片内容来自本期 `references.json`，完整出处、章节及对应论点见 `references.md` 和配套文章；原脚本、分镜、配音、字幕及正文帧数保持，最终总帧数由附录清单和发布 `meta.json.finalVideoFrames` 声明。旧检查记录保留其历史范围，本轮进度与上线证据见 [首批记录](../../docs/reference-endcards/batch-1/README.md)。

`freeze.py` 在原有输入之外收录参考资料、来源核验记录和共享附录工具。先确认全部负责人停写并冻结，再执行渲染；只读复核使用 `python3 freeze.py --verify`。Pillow按 `../_shared/requirements-reference-appendix.txt` 固定版本安装；系统字体与Pillow/FFmpeg版本作为真实工具链指纹记录在附录产物中，不把系统绝对路径伪装为可移植仓库依赖。

在本期 `remotion/` 目录按锁文件安装依赖后，`npm run render` 依次输出：

1. `out/voice.mp4`：原正文画面与人声。
2. `out/body.mp4`：沿用原共享混音的正文成片。
3. `../video.mp4`：共享 `append_references.py` 将参考卡接在正文后，保留正文画面与AAC音轨，附录无新增旁白。

`revisions/reference-endcards/reference-appendix.json` 记录输入/输出完整SHA、原正文与附录区间、总帧数、每页资料及工具链；同目录 `reference-appendix-media-check.json` 记录实际编码验证，`references-01.png` 等是卡片原稿。首次补存量时先按批次基线保存或从固定Git提交提取原正文，不能将已含附录的 `video.mp4` 当作正文再次追加。共享工具拒绝无可追溯回执的未知覆盖。

只读源核对通过后，在本期 `remotion/` 目录运行 `npm run verify:references`，以共享工具复核最终成片的正文保留、片尾范围及完整解码；正文时序继续按原分镜核验，不将原只适用正文的帧数检查冒充最终附录检查。检查通过后再同步发布副本，保留原URL、创建/首发时间和平台历史链接。未执行全片人工听辨或逐字ASR的能力边界继续如实保留。
