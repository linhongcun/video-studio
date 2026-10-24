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
