# EP04 公开资料核验

访问日期：2026-10-24（北京时间）。本次通过联网阅读工具打开正文，读取对应章节，以下为独立概括。旧视频和内部记忆不作为引用。

1. MDN，Using HTTP cookies（持续维护）
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies
   实际读取 What cookies are used for、Creating removing updating cookies 正文：典型登录由服务器验证凭据，再返回含会话 ID 的 Cookie；后续请求带上该 ID，由服务器检查有效性。服务器响应通过 Set-Cookie 写入；发送行为受域、路径、安全等属性影响。删除 Cookie 要用匹配属性并设置过期。支持镜1–3、5–8、10–11。
2. OWASP，Session Management Cheat Sheet（持续维护）
   https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
   已打开正文并检查 Session ID Properties、Cookies、Session Expiration 章节：会话标识应不可预测且不包含敏感账户数据；服务端保存含义与状态；退出或过期必须服务端失效。Cookie 的传输和脚本访问保护依赖正确设置属性。支持镜4、9–11。

## 主张与边界

- 本片只演示服务器会话加 Cookie 的常见实现，不说这是所有网站唯一方案；令牌方案留在文章。
- HTTP 请求不会自动继承上一请求的应用登录状态；会话机制在多次请求间建立关联。不是说持久连接不能复用。
- 示例编号显示“会话甲”，只帮助追踪同一对象，不代表生产系统的熵、长度或格式；真实会话 ID 必须难猜。
- Cookie 不是密码保险箱，也不等于服务器会话。服务器仍须每次检查有效性与访问权限。
- HTTPS、Secure、HttpOnly、SameSite 与 CSRF 是文章边界补充，不在短片同时展开。
- 不声称关掉浏览器就一定退出；浏览器的会话恢复和服务端有效期各自有规则。

## 2026-10-25 片尾参考资料补充核验

本轮重新GET并读取下列固定正文，日期2026-10-25（北京时间）。正式站点本轮不可达的事实、实际HTTP 200响应、全文SHA及逐论点短引分别记于[本片证据](../../docs/reference-endcards/batch-2/sources-cookie-session.json)。历史正文与旧访问记录保留，不以旧状态冒充本轮核验。

- R1 MDN Web Docs，《Using HTTP cookies》（持续维护文档 · 2026-10-25核验）：<https://github.com/mdn/content/blob/13ef67a4ffbdb929415dfa1b3d65ab1aa9ebe5da/files/en-us/web/http/guides/cookies/index.md>。实读What cookies are used for；Creating, removing, and updating cookies／Creating cookies／Removal: defining the lifetime of a cookie；对应：登录成功后可用Cookie保存会话ID，后续合适请求携带ID，由服务器检查会话是否有效；Set-Cookie指示浏览器保存Cookie，后续Cookie请求字段传回；删除Cookie需要匹配其命名与作用范围。
- R2 OWASP，《Session Management Cheat Sheet》（持续维护文档 · 2026-10-25核验）：<https://github.com/OWASP/CheatSheetSeries/blob/cec51594b191eec97ec36f93d1e08c7945dfe598/cheatsheets/Session_Management_Cheat_Sheet.md>。实读Session ID Entropy；Session ID Content (or Value)；Expire and Max-Age Attributes；Session Expiration；对应：会话编号应不可预测、无业务含义且不包含敏感账户数据；编号含义与关联状态由服务器保存；会话过期或退出时服务端必须使会话失效，只删除浏览器Cookie不能替代服务端撤销。

Security属性、浏览器恢复与其他会话机制属于文章边界说明；片尾只映射视频里的编号传递、服务器查找及有效性检查，不把这些文章拓展记为视频已经展开。
