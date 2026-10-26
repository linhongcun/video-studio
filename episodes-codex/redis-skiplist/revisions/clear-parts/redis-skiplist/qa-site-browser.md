# EP40单转场修订本地网页QA

结论：**通过，无阻断项**。实际候选0.72.3，fresh preview为`http://127.0.0.1:4324/video-studio/`。两视口各25项，共50项，已实际用view_image打开全部16张原始截图。未重复原90项矩阵。

新媒体完整SHA-256为`c570ad44437b4bb2157a321328c6b4a021b5cf32a0ce183b865cf3ed57b1100b`，4632帧/154.4秒；served完整MP4/海报、builtHTML/VTT字节匹配。四章按article优先规则保留原网页标题，id与SB实际起点正确，四次真实点击通过；SB制作内的新分段标签不冒充网页章节名。20条原cue文本和毫秒边界保持并实际加载。

两视口真实静音1x短播放。实际暂停930、955、1060、1262、1382五个转场帧均严格paint命中；02明确收束，03先分段提问，再无cursor展开稀疏上层，04才在upperhead重新出现查询游标。资料首帧独立在149.4秒严格命中4482，activeCues为空；真实nativeFullscreen暂停4558帧无字幕，资料原题和机构完整。

旧0.72.2/4323的1382严格取帧失败完整保留，未追认为0.72.3。现边界请求读取实际编码PTS46.066667，paint严格1382；不放宽±1、不改媒体。非边界仍用帧中心。正文cue检查用hidden模式保留activeCue信息、避免叠加原生字幕；默认mode仍disabled。

原createdAt、publishedAt`2026-10-26T16:48:01+08:00`、firstRelease`v0.72.0`保留；sourcePath指向本nested修订工程，footer为0.72.3。原878捕获清单保持原字节；新独立d5d698cc基线的47个其他公开slug/880文件逐SHA及membership保护通过，原492历史文件与139冻结输入逐SHA保持。当前slug仅12项白名单内6项改变，无额外文件。检查前后两次保护结果相同。

文章全文、references和六份封面图片SHA保持。文章/43行代码/真实复制与SVG复用原QA结果；同时证明CodeBlock、章节/目录/图形/页面组件、global/tokens CSS、Astro配置与原基线同字节，锁文件仅本包version两字段变化，浏览器/Playwright版本相同。三比例封面另引用原coverQA与binding，不归入旧90项海报检查。未重跑算法、clipboard或SVG DOM。

限制：1440×1000、390×844均为headless桌面Chromium，844×390横屏Fullscreen仅模拟，不是真机。音轨静音，未全片人工听辨或ASR；Fullscreen通过QA受信任按钮调用真实API。线上Release与Pages身份尚待部署成功后检查。生产媒体与146项清单SHA在本次复核后不变，未改producer/public文件。
