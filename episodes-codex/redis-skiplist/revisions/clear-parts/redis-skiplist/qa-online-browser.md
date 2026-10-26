# EP40单转场修订线上有界浏览器QA

结论：**通过，无阻断项**。在根实际确认Release后Pages run40312953998 success后执行，Release为v0.72.3，首发身份仍v0.72.0。实际canonical地址为https://linhongcun.github.io/video-studio/episodes/redis-skiplist/。

桌面1440×1000与窄屏390×844均HTTP200，真实静音1x短播放成功，四章真实点击、article优先的原网页title/id及SB实际start全部匹配。20条原生cue全文与毫秒边界实际加载并匹配原时序。旧createdAt、publishedAt2026-10-26T16:48:01+08:00与firstRelease保留，canonical页面包含新的nestedsourcePath。

新转场暂停严格命中955、1060、1382：边界955/1382用实际编码PTS31.833333/46.066667，非边界1060用帧中心35.35；requestVideoFrameCallback分别返回预期帧，没有±1容差。资料4482独立精确请求149.4秒，两视口均无activeCue及media error。旧0.72.2失败与QA修正记录继续保留原身份。

实际用view_image查看了全部10张线上原始截图：两视口播放器、桥接、上层渐显、重新查询首帧与资料首帧。桥接明确结束前次查找，上层准备没有查询游标，重新查询时才在上层起点出现游标；资料列表原题及Redis署名完整，无残留原生字幕。

每视口观察到4次浏览器管理的MP4 Range读取消，完整分类证据留JSON；只有exactMP4/media/Range/ERR_ABORTED、实际同阶段seeking或metadata生命周期、以及后续成功播放/绘帧见证齐全才归类。意外网络失败、JS与console错误均为0。传输继承代理和CA、正常TLS验证，无缓存绕过或自动重试。

媒体本地SHA仍c570ad44437b4bb2157a321328c6b4a021b5cf32a0ce183b865cf3ed57b1100b，146项冻结清单SHA仍43191a8176f7f96529d641d6160f94e497c2d20131fa322e485908da02fee7d0。未修改producer/public或重跑本地50/旧90矩阵。

限制：headless桌面浏览器模拟宽度，不是真机；静音短播放不表示全片听辨或ASR。此次线上未重复Fullscreen、算法、clipboard或SVG；这些保持各自本地/复用证据范围。普通canonical完整MP4、海报与VTT文件GET由根另行核验，本smoke不代替或预称其结果。
