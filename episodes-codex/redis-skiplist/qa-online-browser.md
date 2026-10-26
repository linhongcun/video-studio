# EP40线上浏览器smoke

结论：**通过，无阻断项**。在根确认Release后Pages run40299437706已success后执行，绑定首发与当前Release v0.72.0。实际URL为https://linhongcun.github.io/video-studio/episodes/redis-skiplist/。

单次canonical浏览器检查覆盖1440×1000桌面与390×844窄屏，均HTTP200、最终URL正确，实际视频1920×1080、154.4秒。两视口均完成静音1x短播放、四章真实点击，四章精确起点由实际SB推导；全部20条原生VTT文本和毫秒边界匹配。首资料帧在149.4秒精确请求，两次requestVideoFrameCallback都返回4482帧，暂停且activeCues为空，无media error。

已实际用view_image打开全部4张线上原始截图：桌面/窄屏播放器与资料首帧。输入55、有序基线与章节控件在场；两项原题和Redis署名完整，首资料帧没有原生字幕或控件遮住题名。

每视口实际观察到3次浏览器管理的MP4 Range读取消：1次preload=metadata完成后取消，2次在同阶段实际seeking事件中取消。每项均符合exactMP4、media、非空Range、ERR_ABORTED、实际生命周期/seek证据及后续readyState4成功播放或绘帧见证。没有意外网络失败、页面异常或console error；没有将其他失败宽泛豁免。完整原始失败与分类证据见JSON。网络观察在故意context关闭前结束。

传输继承本会话代理与CA，正常TLS验证；无自定义缓存头、query cache-busting或自动重试。冻结清单SHA在复核后未变。只写QA产物，没有改工具/生产源或更新issue。

限制：桌面headless Chromium模拟视口，不是真机；音轨静音，没有全片人工听辨或ASR。本次线上没有重跑本地90项或线上Fullscreen/文章矩阵。线上完整MP4/海报/VTT文件身份由根另做普通canonical GET核验，本smoke不代替该项。
