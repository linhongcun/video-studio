# 片尾参考资料 · 题名与署名简表

本轮根据新的展示偏好，将现有17支资料片尾统一改为简洁单列：只保留“参考资料”标题、完整原始题名与作者/机构；无原文摘录、定位、版本/日期、URL、额外提示或大卡片。当前37项来源均无已登记个人author，按已核验organization署名，不猜测撰作者。完整链接、原文和证据仍保留配套文章与研究，来源对象逐项保持。

每页最多4项、5秒。现有17片全部一页；HTTP请求、HTTPS、CDN由两页减为一页，其余资料时长保持。所有讲解、声音、字幕、已有代码卡、封面和正文动画保持，不重新配音或整条渲染。

|视频|资料项|最终帧数|
|---|---:|---:|
|[布隆过滤器：为什么能确定不存在，却只能说可能存在？](https://linhongcun.github.io/video-studio/episodes/bloom-filter/)|2|4720|
|[同一个网页，第二次打开为什么快这么多？](https://linhongcun.github.io/video-studio/episodes/browser-cache/)|2|2796|
|[后台改了价格，页面怎么还是旧的？](https://linhongcun.github.io/video-studio/episodes/cache-consistency/)|2|3614|
|[网站离你那么远，为什么还这么快？](https://linhongcun.github.io/video-studio/episodes/cdn/)|3|4139|
|[一个服务出故障，为什么整个网站没跟着崩？](https://linhongcun.github.io/video-studio/episodes/circuit-breaker/)|2|3076|
|[一致性哈希：多加一台机器，为什么只改部分数据的归属？](https://linhongcun.github.io/video-studio/episodes/consistent-hashing/)|2|6031|
|[网站怎么记住你已经登录？](https://linhongcun.github.io/video-studio/episodes/cookie-session/)|2|3494|
|[每日温度：还要等几天，才会更暖？](https://linhongcun.github.io/video-studio/episodes/daily-temperatures/)|2|5472|
|[输入网址后，怎么找到服务器？](https://linhongcun.github.io/video-studio/episodes/dns/)|2|3350|
|[两枚鸡蛋、100层楼，怎样保证14次内找到答案？](https://linhongcun.github.io/video-studio/episodes/egg-drop/)|1|5719|
|[浏览器输入网址后发生了什么？](https://linhongcun.github.io/video-studio/episodes/http-request/)|4|5556|
|[HTTPS 为什么安全？](https://linhongcun.github.io/video-studio/episodes/https/)|3|3739|
|[一台服务器忙不过来，怎么办？](https://linhongcun.github.io/video-studio/episodes/load-balancing/)|2|3336|
|[订单已提交，为什么还没处理完？](https://linhongcun.github.io/video-studio/episodes/message-queue/)|2|3250|
|[观察者模式：订单变了，谁该收到通知？](https://linhongcun.github.io/video-studio/episodes/observer-pattern/)|2|4592|
|[抢票时，为什么总提示系统繁忙？](https://linhongcun.github.io/video-studio/episodes/rate-limit/)|2|3421|
|[数据库明明有数据，为什么还要再存一份？](https://linhongcun.github.io/video-studio/episodes/server-cache/)|2|3641|

开工clean同步07d4c491/v0.71.1，保留Bloom单位置最新修订，实际制作目录是single-hash-core下的nested工程，未使用顶层旧多位置版本。其原ignored body缺失，按已发布前4570帧无损恢复，并将帧/PTS、AAC包及PCM指纹与旧媒体证明逐字核对；容器SHA差异单列，不伪称旧字节相同。Observer 4442帧核心及Java卡原文件保留，最终输出继续为video-with-references.mp4。

新增append_references_bibliography.py复用保留的两版旧引擎/原题校验与媒体算法，不复制视频拼接或声音逻辑。两版旧渲染器字节保持；新回执精确绑定bibliography原题/credit、单列四项layout、研究quotations以及真实媒体SHA，quotesRendered=false不等于删除调研证据。存在author就必须非空字符串，否则用organization。Node门禁兼容历史原题/摘录记录，但新默认入口只接受title-author；历史固定SHA豁免未扩大。

17期旧2159项输入全保留，新2176项冻结及只读检查通过；只改显示模式、实际渲染入口/冻结依赖和必要包脚本，正文article/research与所有render:body/voice/mix保持。真实短正文CLI迁移、两页到一页、不重复附加、幂等/篡改拒绝与默认入口10项测试通过，Node78项通过。17份新成片完整解码/连续PTS、原全部正文像素/时间戳与AAC/PCM比较通过，且逐项匹配历史保真指纹。未知旧输出被引擎保护拒绝时，使用其真实已归档旧receipt精确复制作为迁移前身份，不改旧证明追认新片。

新模板与调研/分镜/冻结/默认渲染/发布规范同步。全站构建17份实际资料附录/30片固定未换媒体存量通过，剩余存量不预记完成。实际图片、代表播放器和最终线上检查按各自真实报告记录；未重新GET未变的引用原文或改写来源对象，无全片听辨/ASR，不预记用户认可或传播效果。仅GitHub站点，不重发外部平台。

证据入口：startup.json、production-entry-check.json、media-results.json、delivery.json、各期revisions/title-author中的before快照/迁移receipt/媒体检查及Bloom body-recovery.json。旧视频和QA按其原提交追溯，不改为新格式结果。

## 最终本地验收

17页/37项、68张实际MP4尾帧（各body末帧和卡首/中/末）全部逐张查看，17页卡首末MD5与producer报告一致。所有完整题名/署名正确，无引文、日期、定位、编号、暂停提示、截断或原字幕带入；包括HTTP四项、最长TLS题名、长机构、Bloom当前单位置末镜，以及原Java/Python卡。见qa-independent.json。

17片本地built/完整文件/原章节和字幕检查通过；六片代表作完成desktop真实1倍速尾段到ended、mobile原生全屏，13张必要浏览器图实际查看通过。详见local-verification.json、qa-browser.json及visual-review.json。QA只兼容Bloom既有“资料依据”/脚注原格式，原文章未改；模拟手机/静音播放、旧代码卡原生控件遮挡范围如实保留，不宣称真机、全片听辨或重新检查所有旧代码行。正式线上69次GET在Release后另行执行。
