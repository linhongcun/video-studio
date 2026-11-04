# P06 网站独立检查入口

仅准备工具，尚未执行P06本地或线上验收。已读AGENTS、RULES、article-style、publish与cloud runtime/networking。只复用P08程序代码；没有复制旧结果、截图、帧号或媒体SHA。所有执行须先等待根代理宣布完整本地成片及site/dist构建ready；线上须再等待真实Release后的Pages成功。

本地命令（输出目录必须新建，失败结果保留）：

```bash
python3 episodes/puzzles/twelve-balls/production/qa/site-independent.py --out episodes/puzzles/twelve-balls/production/qa/site-local-native
python3 episodes/puzzles/twelve-balls/production/qa/site-reading-supplement.py --out episodes/puzzles/twelve-balls/production/qa/site-local-reading
python3 episodes/puzzles/twelve-balls/production/qa/site-color-compare.py --browser episodes/puzzles/twelve-balls/production/qa/site-local-native --out episodes/puzzles/twelve-balls/production/qa/site-local-native-color
python3 episodes/puzzles/twelve-balls/production/qa/site-body-fullscreen.py --primary episodes/puzzles/twelve-balls/production/qa/site-local-native --out episodes/puzzles/twelve-balls/production/qa/site-local-body-fullscreen
python3 episodes/puzzles/twelve-balls/production/qa/site-body-playing.py --primary episodes/puzzles/twelve-balls/production/qa/site-local-native --out episodes/puzzles/twelve-balls/production/qa/site-local-body-playing
```

每个本地网页工具独立建立随机空闲端口RangeHTTPServer，直接读取当前site/dist；开始强断言production/publication/dist实际video SHA=新receipt，不借旧preview。1440×1000、390×844模拟视口检查真实play/pause、rVFC PTS、默认native字幕off与显式TextTrack开关、30 cue逐字逐毫秒、5章、两Figure真实seek/两原图、亮暗正文与长题/五作者SourceQuote。手机引用每次先scrollTop=0，再发真实touch并记录delta；不溢出的面板明确不声称滚动。当前no-JS Chromium使用native popover，不称实体旧浏览器。

真实Fullscreen API同时断言fullscreenElement及video viewport geometry。844×390手机横屏观察附录、正文最长句、两Figure的暂停原生控件；正文另正常播放等待控件自然收起，不修改controls属性或CSS。暂停前先inline rVFC精确帧，全屏前后比较实际currentTime并保留Chrome微秒精度，不要求暂停后的新rVFC回调。字幕y835是待实看参数，不提前宣称解决所有视口。

Native色差是全1920×1080 Canvas对explicit limited709 accurate_rnd/full_chroma_int RGB24，固定阈值1.5/3/3不改；独立媒体的Pillow960 3/.015/8另列。图像和播放器截图必须view_image实际目视后再写结论。

线上在根代理提供真实post-Release Pages成功、实际版本及部署commit后，指定canonical base和新的site-online-*输出目录跑同入口（reading用--base-url），再跑：

```bash
python3 episodes/puzzles/twelve-balls/production/qa/site-verify-online.py --version ACTUAL_TAG --commit ACTUAL_FULL_SHA
```

完整普通HTTPS GET分开报告10个Pages端点（video/poster/两图/VTT/episode/series/library/RSS/changelog）及两个指定部署commit原始JSON；真实Release API另查。不开cache-busting、TLS bypass、route fulfillment或缓存回填。本地新Release之前changelog显示v0.103正常，不作为错误。firstRelease候选v0.104.0待根代理最终版本闸门确认，不硬造可用性。

能力边界：当前Chromium桌面/手机模拟，无物理手机或实体旧浏览器、逐字ASR、全片语义听辨或观众理解效果声明。
