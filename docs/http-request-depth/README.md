# EP.01：从流程概览补到机制细节

2026-10-25用户实际观看旧版后指出内容太简单，要求增加TCP三次握手等技术细节。返工由[#283](https://github.com/linhongcun/video-studio/issues/283)跟踪，保留同一商品页与原URL。

新版用四段主线组织找地址、建连接、取资源、画页面，重点展开TCP的三报文、两端独立起始序号、确认号加一以及第三次确认的作用；随后区分TLS和HTTP，用HTTP/1.1报文节选解释路径、Host、成功状态和内容类型。资源请求复用连接，结构/样式再连接到布局绘制；HTTP/2与HTTP/3只交代会改变流程的边界。

修前媒体由Git基线追溯，原稿和技术检查范围保存在[本期修前记录](../../episodes-codex/http-request/revisions/technical-depth-v2/startup.json)。旧机器/视觉检查通过不等于用户认为深度足够，本轮独立稿审见[稿审](../../episodes-codex/http-request/qa-editorial-depth.md)。

开工已同步40adfbf4；编码前整合1aad9cc2的EP.20命名与标签更新，再整合8d037aa3之前的v0.68.0日期版本功能与归档记录，与本期生产输入无交集；保留新createdAt并用实际ISO时间记录本次updatedAt。候选版本顺延为v0.68.1，实际发版以最终Release为准。文稿、配音、真实动态、正式成片、网站及线上核验按各自实际证据记录，不预写用户已观看认可新版。

网站工具只处理本期内容：`sync-site.py`复制通过复核的正式产物，`verify-site.py`检查本地媒体、字幕、章节与双视口实际播放器，`verify-online.py`接收明确tag、部署运行及保留基线，核对线上完整文件和实际Release条目。平台历史链接保留，本轮不重发平台。

收尾时并行EP.20已发布v0.68.1，因此本期最终保留`2ca6e1e0661bbb2b9683f7909de5c0949272ec04`并顺延为[v0.68.2](https://github.com/linhongcun/video-studio/releases/tag/v0.68.2)。旧本地候选的QA、实际HTML/VTT与截图原样保存于`candidates/v0.68.1/`；新版EP01的13份完整文件、VTT与播放器/日期源码SHA保持，明确复用原候选真实播放、34句native字幕与28次章节/正文seek检查，另完成新候选双视口标题/日期/结构/解码海报/卡片检查。EP20新媒体和文章逐字节按最终保留基线纳入构建；EP01未重拷、修改时间仍为实际`2026-10-25T19:38:59+08:00`。详见[当前本地QA](qa-site.json)和[构建记录](build-receipt.json)。

PR #288已合并`f1fe833c70ee0a6c9e3296ba2710b77f05a34823`，附注tag与Release绑定该提交；[Release后手动部署40190399664](https://github.com/linhongcun/video-studio/actions/runs/40190399664)同head成功。北京时间2026-10-25 19:53:15首轮9次完整HTTPS GET（9,691,106字节）核验通过：视频9,161,920字节、完整SHA-256 `593c528daae0aca8540d9daa34e53455fce6776fcdc330ff3ff705564234a1c6`与制作/canonical/tag一致；海报、34句字幕精确时序、七章精确帧起点/锚点、日期/JSON-LD/RSS首发、媒体/源码/原生控件、系列/库/首页及本次Release自己的日志项均正确，日志只关联EP01。详见[线上核验](online-verification.md)、[完整JSON](online-verification.json)、[真实尝试](online-attempts.json)、[Release](release.json)与[部署](deployment.json)。本地changelog读取失败曾按既有逻辑降级外链，没有冒充正式日志检查。上线通过不表示用户已观看认可新版。
