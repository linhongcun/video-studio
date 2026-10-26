# EP.01 HTTP请求：技术细节重制

2026-10-25用户观看旧版后认为内容太简单，要求增加TCP三次握手等机制。现有正文以17镜34句、5406帧（180.2秒）沿同一商品页说明三报文、序号与确认、第三次作用、TCP/TLS/HTTP职责、具体HTTP/1.1报文和页面渲染；连接复用及HTTP/3作为边界。

修前稿、真实技术检查与媒体身份由[修前记录](revisions/technical-depth-v2/startup.json)及Git基线追溯。旧检查通过不代表用户认可旧版深度，新版发布也不等于已获观看认可。

## 本轮生产

配音使用仓内共享voice/prep.py、gen.py、build.py；picks为32个depth与2个depthb，保留24个历史选段。读音和取舍在voice/substitutions.md。整轨与public实体音轨字节一致，句级真实时序与声学起音不冒充逐字ASR或人工听辨。具体报告见voice/depth-timing-report.json。

本期assemble.py将共享整轨的真实边界装配为words、storyboard与字幕，不重剪声音。Remotion按production.json的slug与cueFrames读取，三个报文字段和终态有独立检查。公开来源与版本核对见research.md，独立稿审见qa-editorial-depth.md。

依赖按当前remotion/package-lock.json独立npm ci安装，未复用已删除工程软链。运行环境需FFmpeg、Chromium、Noto Sans CJK SC以及Python numpy/scipy/soundfile；本次Python在/workspace/.venvs/video-studio。

## 冻结、预检与渲染

所有生产源停写、真实动态复核完成后，在仓根执行：

```sh
python3 episodes-codex/http-request/freeze.py
python3 episodes-codex/http-request/freeze.py --verify
python3 episodes-codex/http-request/preflight.py
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/http-request
```

在remotion目录执行npx tsc --noEmit、npm run covers、npm run render。正式渲染使用共享/tmp/video-studio-render.lock。render由本期package先编码H.264再调用共享混音；audit_encoded.py核对冻结输入、5406实际解码帧、格式和响度，并输出正式MP4采样。最终视觉与完整线上文件另验。

本轮无逐字ASR、全片人工听辨或初学者学习实验；所有检查按实际执行范围记录。站点仍使用episodes/http-request，历史平台URL保留，本轮只更新GitHub站点。发布与线上结果见release.md及docs/http-request-depth/，实际状态以最新证据为准。


## 第2批参考资料接入（2026-10-25历史记录）

本期已接入统一的 `render_with_references.py` 默认入口。调研时同步维护 `references.json`，配套文章保留正式链接、固定实读版本和对应论点；先在本期 `remotion/` 运行 `npm run check:references`。Python附录依赖按 `../_shared/requirements-reference-appendix.txt` 固定版本安装，字体与FFmpeg按共享工具的真实环境要求准备。

所有生产输入停写后运行本期 `freeze.py`，以 `freeze.py --verify` 只读核对。清单保留原正文、声音、时序、封面及本期素材依赖，并收录参考资料、默认wrapper、追加器、Pillow版本锁、发布资料检查器和每项来源声明的实际核验JSON；文章、package与共享主题也属于冻结输入。渲染前后核对同一份清单，不把视频或生成回执当作编码前输入。

后续需要重新制作正文时，在 `remotion/` 运行 `npm run render`：默认wrapper先检查来源与冻结，随后调用 `render:body`，沿用本期既有的 `render:voice` → `render:mix`，将完整正文输出到 `out/body.mp4`，再自动追加参考资料得到 `../video.mp4`。`render:body`不调用默认`render`，避免递归。

本次存量补齐采用 [第2批记录](../../docs/reference-endcards/batch-2/README.md) 中的固定Git基线：原已发布MP4放到 `remotion/out/body.mp4`，只生成并追加资料卡，每页默认5秒、可暂停阅读，不执行正文重渲、重混音或重新请求配音。基线与原冻结/媒体身份分别保存于 `revisions/reference-endcards/baseline.json`、`body-source-sha256.json`、`body-render-result.json`；旧QA仍只证明原来执行过的检查范围。

原脚本、分镜、`words.json`、人声与字幕继续描述正文；最终总帧数、正文终点和资料页范围由实际 `reference-appendix.json` 及发布元数据声明。附录回执先由共享工具写入 `revisions/reference-endcards/`，交付副本位于本期根目录；`render-result.json.publicationMetadata`给出应同步到发布`meta.json`的`finalVideoFrames`与`referenceAppendix`。本批手动复用正文后也必须按实际结果接齐这些交付文件，不能用旧时长/旧哈希代替最终身份。

接齐后在 `remotion/` 运行 `npm run verify:references`：统一wrapper只读核对来源、冻结、真实最终媒体及交付回执，不重新渲染正文。旧正文编码检查器的帧数断言只用于对应正文副本，不直接用它判断已追加附录的最终`video.mp4`。实际查看所有资料页、精确首卡字幕边界以及桌面/手机原生播放器暂停和全屏效果，再同步发布副本；保留原URL、创建/首发时间、已有平台链接及未执行ASR/人工听辨的能力边界。本批制作和上线状态以批次证据为准，不预记已通过或已发布。


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
