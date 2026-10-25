# EP05 CDN：地图与术语返工

本批补参考资料前的正文发布记录：[v0.50.3](https://github.com/linhongcun/video-studio/releases/tag/v0.50.3)已上线并核验通过（2026-10-24 22:24:22北京时间），见[发布记录](release.md)。

2026-10-24，用户观看v0.48.0后要求增加真实地理地图与CDN等技术名词；本轮保留同一图片主线，地图参与调度、未命中回源与命中短返。旧版输入/结果/检查在revisions/v0.48.0，旧发布事实不作为本轮完成证明。


复现：仓内episodes/_shared/voice/prep.py、gen.py（voice/jobs_map.json）、build.py；新选定takes保留，避免重请求不确定TTS。assemble.py生成真实句级边界/字幕/术语起音；共享selfcheck/place_v2/label_onset_strict与preflight.py检查；地图转换python assets/map/convert.py。remotion目录npm ci、tsc --noEmit、npm run covers、npm run render。

TMPDIR和QA大文件均使用本期remotion/out工作盘；flock /tmp/video-studio-render.lock串行较大预演与正式编码。freeze.py冻结地图原始GeoJSON/公开许可依据/元数据/转换脚本与src静态路径、选定音轨、脚本、共享实现等实际输入；freeze.py --verify只读核对。check-render.py对真实MP4测量解码/帧数/响度/完整SHA。

Natural Earth 110m land公有领域；源/许可/固定上游commit/SHA与投影在assets/map/source/metadata.json和assets/map/convert.py。配乐Kevin MacLeod《Wallpaper》CC BY4.0沿用共享。无运行时远端URL。

没有逐字ASR或完整独立人工听辨的结论；字幕来自原稿和实际句级边界，术语位于句首并使用共享声学起音规则。qa-motion、qa-final及qa-independent-*记录本轮实际完成范围；本地制作与检查已完成，站点发布和线上核验由root继续记录。


## 第2批参考资料接入（2026-10-25历史记录）

本期已接入统一的 `render_with_references.py` 默认入口。调研时同步维护 `references.json`，配套文章保留正式链接、固定实读版本和对应论点；先在本期 `remotion/` 运行 `npm run check:references`。Python附录依赖按 `../_shared/requirements-reference-appendix.txt` 固定版本安装，字体与FFmpeg按共享工具的真实环境要求准备。

所有生产输入停写后运行本期 `freeze.py`，以 `freeze.py --verify` 只读核对。清单保留原正文、声音、时序、封面及本期素材依赖，并收录参考资料、默认wrapper、追加器、Pillow版本锁、发布资料检查器和每项来源声明的实际核验JSON；文章、package与共享主题也属于冻结输入。渲染前后核对同一份清单，不把视频或生成回执当作编码前输入。

后续需要重新制作正文时，在 `remotion/` 运行 `npm run render`：默认wrapper先检查来源与冻结，随后调用 `render:body`，沿用本期既有的 `render:voice` → `render:mix`，将完整正文输出到 `out/body.mp4`，再自动追加参考资料得到 `../video.mp4`。`render:body`不调用默认`render`，避免递归。

本次存量补齐采用 [第2批记录](../../docs/reference-endcards/batch-2/README.md) 中的固定Git基线：原已发布MP4放到 `remotion/out/body.mp4`，只生成并追加资料卡，每页默认5秒、可暂停阅读，不执行正文重渲、重混音或重新请求配音。基线与原冻结/媒体身份分别保存于 `revisions/reference-endcards/baseline.json`、`body-source-sha256.json`、`body-render-result.json`；旧QA仍只证明原来执行过的检查范围。

原脚本、分镜、`words.json`、人声与字幕继续描述正文；最终总帧数、正文终点和资料页范围由实际 `reference-appendix.json` 及发布元数据声明。附录回执先由共享工具写入 `revisions/reference-endcards/`，交付副本位于本期根目录；`render-result.json.publicationMetadata`给出应同步到发布`meta.json`的`finalVideoFrames`与`referenceAppendix`。本批手动复用正文后也必须按实际结果接齐这些交付文件，不能用旧时长/旧哈希代替最终身份。

接齐后在 `remotion/` 运行 `npm run verify:references`：统一wrapper只读核对来源、冻结、真实最终媒体及交付回执，不重新渲染正文。旧正文编码检查器的帧数断言只用于对应正文副本，不直接用它判断已追加附录的最终`video.mp4`。实际查看所有资料页、精确首卡字幕边界以及桌面/手机原生播放器暂停和全屏效果，再同步发布副本；保留原URL、创建/首发时间、已有平台链接及未执行ASR/人工听辨的能力边界。本批制作和上线状态以批次证据为准，不预记已通过或已发布。


## 原始题名与原文短引：当前资料入口

本轮按用户要求使用 `presentation: original-title-quote`：卡片保留来源的实际完整原题名和原语言，原文短引保持连续逐字文本并标明位置；内部 `supports` 只用于研究映射，不作为原文上屏。每页最多2项、默认5秒，按实际页数记录最终帧数；不沿用旧单页附录的总时长。引用正文、核验记录与本轮状态见 [原题名修订](../../docs/reference-endcards/original-titles/README.md)，旧回执及修前文章/研究/资料清单已保存在 `revisions/original-titles/`，不覆盖或改写旧验收事实。

在本期 `remotion/` 运行 `npm run check:references` 检查当前资料。全部输入停写后使用本期 `freeze.py` 冻结、加 `--verify` 只读核对；清单保留原正文/声音/素材依赖，并加入 `append_references_original.py`、未改字节的旧媒体引擎 `append_references.py`、默认wrapper、发布检查器、Pillow版本锁、主题，以及 `verification`、`titleEvidence`、可选 `quotation` 声明的全部实际证据文件。

后续完整制作的 `npm run render` 使用统一wrapper，先检查来源及冻结，再调用 `render:body` 原有画面/混音流程生成 `out/body.mp4`，最后通过新原题名渲染器追加资料到 `../video.mp4`。本次修订只复用已核验的原 `out/body.mp4`，调用新器的 `render:references` 生成资料尾卡，不重渲正文或重新混音。原旁白、字幕、分镜和 `words.json` 继续表示正文时序；原体与旧最终视频不得混用，避免重复叠加资料卡。

`revisions/reference-endcards/reference-appendix.json` 与媒体检查回执记录实际新附录；最终交付副本位于本期根目录。接齐新的回执和 `render-result.json.publicationMetadata` 后，在 `remotion/` 运行 `npm run verify:references`，由默认wrapper核对来源、冻结、最终媒体及发布身份，不重新编码正文。最后实际查看所有新资料页、精确首卡字幕边界和播放器暂停/全屏；正文旧QA仅在原画面/声音确证保持的范围复用，不冒称本轮已通过、已上线或获用户观看认可。
