# EP40本地站点浏览器复核

结论：**通过，无阻断项**。仅覆盖本地fresh build与所列截图，不代替线上核验、真机或全片听辨。

实际执行地址为`http://127.0.0.1:4322/video-studio/`，候选版本0.72.0；未使用旧4321。单次运行两个独立浏览器context：1440×1000桌面、390×844窄屏，各45项，共90项通过。完整日志、输入SHA和原始截图见同名JSON及`qa-site-browser-evidence/`。

实际视频为1920×1080、4632帧/154.4秒，MP4完整SHA-256为`1c78a906545d3eb9b25df0d6c7c104c5d8de3f248440cbb3bb9ed1467db2150e`。完整served视频/海报与发布副本一致，20条native VTT文本及毫秒边界完整匹配。四章起点从实际SB推导，真实点击均跳转正确；字幕初始mode为disabled，测试为核查cue而主动开启。

两视口均真实执行静音1x短播放，并从正文尾跨入资料区直到ended。首资料帧严格在149.4秒请求，requestVideoFrameCallback均报告4482帧，无activeCue；首帧+0.1ms、中间4557帧和末4631帧也严格匹配。真实Fullscreen API进入成功，暂停4558帧且无字幕；窄屏全屏只模拟844×390横屏。

文章四章目录、单张SVG、实际43行Python全文通过。网页code.textContent、data-code和隔离context真实剪贴板均精确等于文章fence；复用已有且绑定相同文章/源码SHA的执行证据，没有重跑其他算法。代码instant滚动后等待双rAF，窄屏pre从scrollLeft0到42到达右侧，横向滚动留在代码容器内，整页无横向溢出。工程算法三课顺序、当前课、首页/学习/系列/内容库入口、创建/修改日期与RSS通过，无JS或意外外部请求错误。对origin/main278f69a7的931个既有episodes文件逐个Git blob比较，无变化。

已实际用view_image打开12张原始截图：两宽度的播放器、精确首资料帧、Fullscreen、代码顶部、代码末尾右侧和SVG。资料两项原题与Redis署名完整；Fullscreen中可读且未被控件遮住，SVG关系和代码首尾正确。正文截图开启native字幕是本次测试状态，不是默认caption模式。其余6张资料首帧+0.1ms/中/末截图仅由工具检查paint与cue，本审者没有另行打开。

限制：headless桌面Chromium模拟宽度，不是真机或物理旋转；音频静音，未作全片人工语义听辨或ASR；真实全屏通过受信任的QA临时按钮调用video.requestFullscreen，不是点浏览器chrome。本报告不宣称线上Release或Pages已核验。原冻结清单和最终视频在复核后SHA不变，未修改生产输入。
