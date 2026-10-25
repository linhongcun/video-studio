# EP.01：从流程概览补到机制细节

2026-10-25用户实际观看旧版后指出内容太简单，要求增加TCP三次握手等技术细节。返工由[#283](https://github.com/linhongcun/video-studio/issues/283)跟踪，保留同一商品页与原URL。

新版用四段主线组织找地址、建连接、取资源、画页面，重点展开TCP的三报文、两端独立起始序号、确认号加一以及第三次确认的作用；随后区分TLS和HTTP，用HTTP/1.1报文节选解释路径、Host、成功状态和内容类型。资源请求复用连接，结构/样式再连接到布局绘制；HTTP/2与HTTP/3只交代会改变流程的边界。

修前媒体由Git基线追溯，原稿和技术检查范围保存在[本期修前记录](../../episodes-codex/http-request/revisions/technical-depth-v2/startup.json)。旧机器/视觉检查通过不等于用户认为深度足够，本轮独立稿审见[稿审](../../episodes-codex/http-request/qa-editorial-depth.md)。

开工已同步40adfbf4；编码前整合1aad9cc2的EP.20命名与标签更新，再整合8d037aa3之前的v0.68.0日期版本功能与归档记录，与本期生产输入无交集；保留新createdAt并用实际ISO时间记录本次updatedAt。候选版本顺延为v0.68.1，实际发版以最终Release为准。文稿、配音、真实动态、正式成片、网站及线上核验按各自实际证据记录，不预写用户已观看认可新版。

网站工具只处理本期内容：`sync-site.py`复制通过复核的正式产物，`verify-site.py`检查本地媒体、字幕、章节与双视口实际播放器，`verify-online.py`接收明确tag、部署运行及保留基线，核对线上完整文件和实际Release条目。平台历史链接保留，本轮不重发平台。
