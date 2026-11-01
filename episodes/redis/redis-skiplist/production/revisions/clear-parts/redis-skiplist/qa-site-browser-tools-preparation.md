# EP40单转场修订网页QA准备

状态：工具语法/help通过，等待最新发布基线和v0.72.3 fresh build。未改producer/public或媒体，未改旧878项捕获清单。首发仍v0.72.0，publishedAt仍2026-10-26T16:48:01+08:00。

实际0.72.2/4323首次本地运行停在严格1382帧：算术46.0666666667被浏览器截为46.066666，paint回1381。失败报告及当时工具真实字节留在qa-revisions/site-browser-boundary-pts；不能追记为0.72.3通过。只修QA边界请求采用实际编码PTS46.066667，仍要求paintedFrame1382，不放宽±1；资料4482继续单独精确149.4验证。尚未重跑旧preview。

检查保持有界：两视口的新片播放/身份、五个转场暂停、20原cue、4482无字幕、nativeFullscreen、新sourcePath和保留日期。网页按article优先的旧四章标题，不宣称SB制作标签同步成为网页标题。未变文章/43code/SVG与封面按精确SHA、旧QA及同runtime证明复用，不重新凑90项。

root将另给d5d698cc最新公开资产基线和明确incoming-path审计，再适配保护读取；原492顶层历史继续逐SHA保护。线上只等Release后Pages成功通知再执行。完整状态及工具SHA见同名JSON。
