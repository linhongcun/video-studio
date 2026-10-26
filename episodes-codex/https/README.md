# https · Codex重制工程

2026-10-24用户要求将EP01–14上一轮Cursor版按当天Codex规格与经验重新制作。本目录为制作工程，站点接入由root统一处理。公开资料见research.md；旁白、文章、读音和分镜各自入库。

使用仓内共享voice/prep.py、gen.py、build.py，不复制配音算法。选定takes见voice/picks.json与substitutions.md；assemble.py仅把共享整轨结果转成句级字幕、声学句首标签与分镜，不生成或重剪音频。

Python环境：/workspace/.venvs/video-studio。Remotion安装npm ci，随后npx tsc --noEmit、npm run covers、npm run render。工作区node_modules软链是安装加速，不入库；锁文件可独立复现。系统要求FFmpeg、Chromium与Noto Sans CJK SC。

检查与能力边界见qa-motion.md、qa-final.md。ASR模型端点被当前网络策略拒绝，未声称完成逐字ASR或人工听辨；冻结词时间是句边界与声学句首，不是逐字对齐。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。

## 全局/局部导航返工（2026-10-24制作阶段记录）

以下保留当时的阶段记录；本批参考资料附录的当前入口见文末，原正文基线以本批固定Git提交及完整SHA为准。

2026-10-24，批次`flow-map-20261024/#199`。保留原音轨、脚本、words、字幕、12镜和3589帧，新增安全握手与接收验证的分层全局关系、核验失败后的正常情景重置及结尾回收。历史输入和当前媒体由[索引](revisions/pre-flow-map.json)关联基线`6765032`，没有复制大媒体。

本轮预演与完整动作窗口证据见[QA记录](qa-flow-map.json)。动画源已停写，等待独立编辑复核；未执行本轮最终冻结、完整正式编码或发布。原`qa-final.md`、`release.md`及`source-sha256.json`继续对应旧版，最终制作由主任务统一安排。共用导航只引用`../_shared/branch-map/index.ts`，没有改动共用实现。

独立编辑首轮发现07提前高亮“握手完成”出口，R1已将该边延后到local273协商落定。只重采受影响07关键帧与identity跨镜片；初版源和QA在`revisions/flow-map-before-r1/`保留，证据按旧/新指纹分组，等待重点复验。


## 首批参考资料附录（2026-10-25历史记录）

本批在已发布正文之后追加可暂停的静态参考资料卡，默认每页5秒。卡片内容来自本期 `references.json`，完整出处、章节及对应论点见 `references.md` 和配套文章；原脚本、分镜、配音、字幕及正文帧数保持，最终总帧数由附录清单和发布 `meta.json.finalVideoFrames` 声明。旧检查记录保留其历史范围，本轮进度与上线证据见 [首批记录](../../docs/reference-endcards/batch-1/README.md)。

`freeze.py` 在原有输入之外收录参考资料、来源核验记录和共享附录工具。先确认全部负责人停写并冻结，再执行渲染；只读复核使用 `python3 freeze.py --verify`。Pillow按 `../_shared/requirements-reference-appendix.txt` 固定版本安装；系统字体与Pillow/FFmpeg版本作为真实工具链指纹记录在附录产物中，不把系统绝对路径伪装为可移植仓库依赖。

在本期 `remotion/` 目录按锁文件安装依赖后，`npm run render` 依次输出：

1. `out/voice.mp4`：原正文画面与人声。
2. `out/body.mp4`：沿用原共享混音的正文成片。
3. `../video.mp4`：共享 `append_references.py` 将参考卡接在正文后，保留正文画面与AAC音轨，附录无新增旁白。

`revisions/reference-endcards/reference-appendix.json` 记录输入/输出完整SHA、原正文与附录区间、总帧数、每页资料及工具链；同目录 `reference-appendix-media-check.json` 记录实际编码验证，`references-01.png` 等是卡片原稿。首次补存量时先按批次基线保存或从固定Git提交提取原正文，不能将已含附录的 `video.mp4` 当作正文再次追加。共享工具拒绝无可追溯回执的未知覆盖。

只读源核对通过后，在本期 `remotion/` 目录运行 `npm run verify:references`，以共享工具复核最终成片的正文保留、片尾范围及完整解码；正文时序继续按原分镜核验，不将原只适用正文的帧数检查冒充最终附录检查。检查通过后再同步发布副本，保留原URL、创建/首发时间和平台历史链接。未执行全片人工听辨或逐字ASR的能力边界继续如实保留。


## 原始题名与原文短引（历史资料样式）

本轮按用户要求使用 `presentation: original-title-quote`：卡片保留来源的实际完整原题名和原语言，原文短引保持连续逐字文本并标明位置；内部 `supports` 只用于研究映射，不作为原文上屏。每页最多2项、默认5秒，按实际页数记录最终帧数；不沿用旧单页附录的总时长。引用正文、核验记录与本轮状态见 [原题名修订](../../docs/reference-endcards/original-titles/README.md)，旧回执及修前文章/研究/资料清单已保存在 `revisions/original-titles/`，不覆盖或改写旧验收事实。

在本期 `remotion/` 运行 `npm run check:references` 检查当前资料。全部输入停写后使用本期 `freeze.py` 冻结、加 `--verify` 只读核对；清单保留原正文/声音/素材依赖，并加入 `append_references_original.py`、未改字节的旧媒体引擎 `append_references.py`、默认wrapper、发布检查器、Pillow版本锁、主题，以及 `verification`、`titleEvidence`、可选 `quotation` 声明的全部实际证据文件。

后续完整制作的 `npm run render` 使用统一wrapper，先检查来源及冻结，再调用 `render:body` 原有画面/混音流程生成 `out/body.mp4`，最后通过新原题名渲染器追加资料到 `../video.mp4`。本次修订只复用已核验的原 `out/body.mp4`，调用新器的 `render:references` 生成资料尾卡，不重渲正文或重新混音。原旁白、字幕、分镜和 `words.json` 继续表示正文时序；原体与旧最终视频不得混用，避免重复叠加资料卡。

`revisions/reference-endcards/reference-appendix.json` 与媒体检查回执记录实际新附录；最终交付副本位于本期根目录。接齐新的回执和 `render-result.json.publicationMetadata` 后，在 `remotion/` 运行 `npm run verify:references`，由默认wrapper核对来源、冻结、最终媒体及发布身份，不重新编码正文。最后实际查看所有新资料页、精确首卡字幕边界和播放器暂停/全屏；正文旧QA仅在原画面/声音确证保持的范围复用，不冒称本轮已通过、已上线或获用户观看认可。


## 题名与作者：当前资料入口

本轮资料卡采用`presentation: title-author`，按完整原始题名和作者/机构列示。仅在来源本身已有`author`时使用该字段，否则使用既有`organization`，不补造个人姓名。原题名、机构、原文摘录、定位及核验文件保留在`references.json`和配套文章中；本轮只切换显示方式，不改研究结论或正文。

默认资料渲染器为共享`append_references_bibliography.py`，早先两份渲染器保持历史字节并继续作为冻结依赖。新卡按实际排版分页，每页默认5秒；修前回执、来源清单、入口及输入身份保存在本实际制作目录的`revisions/title-author/`，不重写旧验收结果。候选资料卡同在该修订目录生成，通过检查后再接入既有最终产物与回执位置；本轮进度由根任务记录。

当前冻结入口为`freeze.py`，加`--verify`只读核对。冻结清单在原有正文、声音、图标、导航和历史来源输入之外收录新渲染器，既有wrapper、发布检查器、两份旧渲染器及证据仍保留。默认正文构建、混音、并发和已有代码卡顺序均沿用实际package；本批只消费基线已验收的完整正文生成资料卡，不运行正文prepare、TTS、重渲或重混音。

资料生成后按新回执同步最终总帧数、媒体SHA及发布映射；实际复核题名/署名、分页、首卡字幕边界、暂停及原生全屏。原脚本、配音、字幕、分镜、动作和文章/研究均保持本轮基线字节，旧技术验收只按原体保真范围复用，不预记新版已获观看认可。
