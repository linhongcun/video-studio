# cookie-session · 原题与原文短引

本轮固定正文复核日期：2026-10-25（北京时间）。原题按文档frontmatter／RFC题名／首个H1逐字保留；短引选取完整原句，不以内部supports或译名替代原文。

本轮GET状态、全文SHA、题名及原句位置见[核验记录](../../docs/reference-endcards/original-titles/sources-core.json)。正式入口与固定版本同时保留，原有canonical访问记录未冒充本轮重新访问。

## R1 · Using HTTP cookies

- 作者／机构：MDN Web Docs
- 年份／版本：持续维护文档 · 2026-10-25核验
- 原题位置：frontmatter title · line 2
- 正式文档：<https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies>
- 固定原文：<https://github.com/mdn/content/blob/13ef67a4ffbdb929415dfa1b3d65ab1aa9ebe5da/files/en-us/web/http/guides/cookies/index.md>

> The browser sends the cookie containing the session ID along with the corresponding request to indicate that it still thinks the user is signed in.

原句位置：What cookies are used for · line 18。原始文件行号：18–18。

内部论点对应（制作解释，不作为原文引句）：

- 登录成功后可用Cookie保存会话ID，后续合适请求携带ID，由服务器检查会话是否有效
- Set-Cookie指示浏览器保存Cookie，后续Cookie请求字段传回；删除Cookie需要匹配其命名与作用范围

## R2 · Session Management Cheat Sheet

- 作者／机构：OWASP
- 年份／版本：持续维护文档 · 2026-10-25核验
- 原题位置：H1 · line 1
- 正式文档：<https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html>
- 固定原文：<https://github.com/OWASP/CheatSheetSeries/blob/cec51594b191eec97ec36f93d1e08c7945dfe598/cheatsheets/Session_Management_Cheat_Sheet.md>

> When a session expires, the web application must take active actions to invalidate the session on both sides, client and server.

原句位置：Session Expiration · line 313。原始文件行号：313–313。

内部论点对应（制作解释，不作为原文引句）：

- 会话编号应不可预测、无业务含义且不包含敏感账户数据；编号含义与关联状态由服务器保存
- 会话过期或退出时服务端必须使会话失效，只删除浏览器Cookie不能替代服务端撤销
