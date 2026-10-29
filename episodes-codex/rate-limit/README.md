# EP.11《抢票时，为什么总提示系统繁忙？》

> 当前系列视觉入口：[`remotion/src/peak-style/index.ts`](remotion/src/peak-style/index.ts)。正文与资料页沿现行深青蓝／亮青／暖黄封面；通过[共享制作入口](../_shared/peak-video/README.md)先预检、冻结，再生成完整成片。新产物位于 `revisions/peak-style/`；下文原入口保留历史身份，不用旧命令覆盖当前发布视频。

2026-10-24用户授权EP01–14按今天Codex规格重制，本期为全新制作工程。只在本目录产出，不改线上旧文件；站点接入和发布由root统一完成。

- research.md记录实际读取的官方正文、日期与边界。
- script.md、article.mdx、pronunciation.md和visual-direction.md记录同一主线与逐镜因果。
- 已完成本地成片与核验，见delivery.json和qa-final.md。全片12镜、24句、3271帧、约109.0秒，1920×1080、30fps。
- 配音冰糖，使用仓内共享prep/gen/build；一条短尾候选保留a/b对比，选段见voice/picks.json、tail-comparison.json和substitutions.md。
- words.json是句级时序和声学句首起音，不是逐字ASR；能力边界如实保留。
- 冻结清单source-sha256.json包含实际脚本、选定takes、共享实现和全部Remotion输入。
- 动态小样、成片和媒体核验分别记录在qa-motion.md、qa-final.md和render-result.json。

复现：在remotion目录npm ci、npx tsc --noEmit、npm run covers、npm run render。工作区可使用EP01的集中node_modules软链；它不入库。运行渲染时Python需要numpy（使用/workspace/.venvs/video-studio/bin加入PATH），系统需要FFmpeg、Chromium和Noto Sans CJK SC。

配音复现保留原takes避免重复调用非确定性TTS：共享voice/build.py --dir episodes-codex/rate-limit，再运行本期assemble.py、共享selfcheck.py、place_v2.py --mode whole、label_onset_strict.py，然后本期freeze.py与verify.py。

最终视频video.mp4、三种封面、captions.srt供root接入同名站点slug。平台历史投稿不自动重发。

独立实际编码图审结果见qa-independent-encoded.md；所有能力限制如实记在qa-final.md。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。


## 第4批参考资料（历史资料样式）

本批只在已发布原片后追加参考资料。不可变完整原片位于`revisions/reference-endcards/body.mp4`，原始SHA及帧数见同目录`baseline.json`；`before-source-sha256.json`、修前文章/调研/冻结器/package等快照保持历史字节。当前原脚本、配音、字幕、分镜、动作及已有身份图标不重制，不把新资料段或新入口的冻结清单追认为旧原片的实际编码输入。

`references.json`使用`presentation: original-title-quote`：保留完整原始题名和原语言，短引采用连续逐字原文并标明位置；内部`supports`不作为文献原句上屏。每页最多2项、默认5秒，完整出处在文章中保留。当前来源与实际进度见 [第4批记录](../../docs/reference-endcards/batch-4/README.md)，不预记资料或成片已通过。

先在本期`remotion/`执行`npm run check:references`，全部输入停写后使用本期`freeze.py`，再以`freeze.py --verify`只读核对。冻结保留原片现有全部生产依赖：导航片继续收录branch-map，MQ继续收录后补middleware源码、原SVG、许可、来源及包装器；不回退旧冻结历史。新输入另含新原题名器、未改字节的旧媒体引擎、默认wrapper、发布检查器、Pillow版本锁、主题、当前资料/文章/package与`verification.evidence`、`titleEvidence.evidence`及可选`quotation.evidence`实际文件。

后续完整制作的`npm run render`经共享wrapper先检查来源和冻结，再调用`render:body`原有`render:voice`→`render:mix`闭环，将完整正文生成到`out/body.mp4`，最后追加资料到`../video.mp4`。本片既有编码/并发参数保持；本批不执行正文编码或重新混音，只由根代理消费上述已验收原片生成尾卡。可选`render:references`面向已准备且SHA核对相同的`out/body.mp4`，不能把含附录的最终文件再次当成正文。

根级交付回执、`render-result.json.publicationMetadata`及发布总帧数按实际附录结果接齐后，`npm run verify:references`可验证来源、冻结、最终媒体和交付身份。其普通wrapper从`out/body.mp4`读取正文，本批该副本已按不可变原片SHA准备。已由追加器完成的全量帧/PTS/AAC/PCM保真检查按真实执行范围记录，不为重复验证而重渲或再次混音；旧正文检查器的帧数断言只用于正文副本。

实际查看所有资料页、精确首卡字幕边界、桌面/手机暂停和原生全屏后再接入站点。原创建/首发时间与历史平台链接保留，ASR或全片人工听辨未执行时如实记录；旧QA只在原体完整保真得到证明的范围复用。


## 题名与作者：当前资料入口

本轮资料卡采用`presentation: title-author`，按完整原始题名和作者/机构列示。仅在来源本身已有`author`时使用该字段，否则使用既有`organization`，不补造个人姓名。原题名、机构、原文摘录、定位及核验文件保留在`references.json`和配套文章中；本轮只切换显示方式，不改研究结论或正文。

默认资料渲染器为共享`append_references_bibliography.py`，早先两份渲染器保持历史字节并继续作为冻结依赖。新卡按实际排版分页，每页默认5秒；修前回执、来源清单、入口及输入身份保存在本实际制作目录的`revisions/title-author/`，不重写旧验收结果。候选资料卡同在该修订目录生成，通过检查后再接入既有最终产物与回执位置；本轮进度由根任务记录。

当前冻结入口为`freeze.py`，加`--verify`只读核对。冻结清单在原有正文、声音、图标、导航和历史来源输入之外收录新渲染器，既有wrapper、发布检查器、两份旧渲染器及证据仍保留。默认正文构建、混音、并发和已有代码卡顺序均沿用实际package；本批只消费基线已验收的完整正文生成资料卡，不运行正文prepare、TTS、重渲或重混音。

资料生成后按新回执同步最终总帧数、媒体SHA及发布映射；实际复核题名/署名、分页、首卡字幕边界、暂停及原生全屏。原脚本、配音、字幕、分镜、动作和文章/研究均保持本轮基线字节，旧技术验收只按原体保真范围复用，不预记新版已获观看认可。
