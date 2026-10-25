# cache-consistency Codex重制工程

2026-10-24，用户授权EP01–14按今天Codex制作规格和经验整体重制。本目录为独立新工程；公开依据见research.md，视觉设计见visual-direction.md，最终检查状态见qa-final.md。

共享配音命令均从仓根执行：prep.py → gen.py → build.py（各带--dir episodes-codex/cache-consistency），再运行本期assemble.py、共享selfcheck.py/place_v2.py/label_onset_strict.py。ASR能力限制单独记录；不重新请求已有选定takes。

运行依赖：FFmpeg、/usr/bin/chromium、Noto Sans CJK SC；Python依赖沿用仓内共享配音环境。

Remotion：在remotion目录npm ci、npx tsc --noEmit、npm run covers、npm run render。正式编码用flock /tmp/video-studio-render.lock串行协调有限资源，单次渲染并发2。开发node_modules软链不提交；锁文件可独立安装。配乐Kevin MacLeod《Wallpaper》，CC BY 4.0，目标−16 LUFS。

站点由root统一接入发布；本目录制作代理不修改episodes/。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。


## 第3批参考资料：当前默认入口

本批在已发布原片后补参考资料，不重新渲染正文或混音。不可变原片位于 `revisions/reference-endcards/body.mp4`，完整SHA和原帧数见同目录 `baseline.json`；`before-source-sha256.json`、修前文章/调研/入口快照保留原制作身份，不能重写这些历史记录来追认新引用段。原配音、字幕、分镜、动作与图标继续保持，当前新清单仅声明新资料尾卡及后续默认渲染所需输入。

`references.json`采用`presentation: original-title-quote`：来源保留完整原始题名及原语言；短引保持连续逐字原文并标明位置，内部`supports`只作研究映射。每页最多2项、默认5秒，给出暂停与配套图文提示。来源核验及本批状态见 [第3批记录](../../docs/reference-endcards/batch-3/README.md)，本节不预记资料、成片或发布已通过。

在本期 `remotion/` 执行 `npm run check:references`。全部生产输入停写后运行本期 `freeze.py`，再以`freeze.py --verify`只读核对。冻结器保留本片已有正文/声音/导航输入，并明确收录后补MySQL身份组件的源码、原图、许可及来源；使用Redis身份的片目还保留middleware目录及历史包装器，不回退到初版缺图标的清单。另纳入新原题名器、未改字节的旧媒体引擎、默认wrapper、发布检查器、Pillow版本锁、主题、当前资料/文章/package及`verification.evidence`、`titleEvidence.evidence`、可选`quotation.evidence`的全部实际文件。

后续完整制作的 `npm run render` 使用共享wrapper，先检查来源和冻结，再调用 `render:body`严格沿用本期原`render:voice`→`render:mix`闭环，把完整主体生成到`out/body.mp4`，最后追加新资料卡到`../video.mp4`。本批只从已验收不可变原片生成资料尾卡，不执行该正文编码步骤；可给新器明确指定`--body ../revisions/reference-endcards/body.mp4`。可选`render:references`面向已准备好且SHA核对相同的`out/body.mp4`，不能把含附录的最终文件当主体再次追加。

新媒体清单及逐帧/音频保留报告位于`revisions/reference-endcards/reference-appendix.json`和同目录媒体检查回执。接齐期根交付回执、`render-result.json.publicationMetadata`及实际发布总帧数后，在`remotion/`执行`npm run verify:references`，核对当前资料、冻结和最终媒体；该wrapper使用`out/body.mp4`，仅复用存量时须先准备与不可变原片SHA完全一致的副本。旧编码检查器的正文帧数断言只适用于正文副本，不拿它判定已加资料卡的最终成片。

实际查看所有资料页、精确首卡字幕边界和桌面/手机暂停及原生全屏后再接入站点。原创建/首发时间、链接和平台身份保留，ASR或全片人工听辨未执行时继续如实记录；本批发布进度以真实证据为准。
