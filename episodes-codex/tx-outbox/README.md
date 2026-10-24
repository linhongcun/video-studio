# EP.21 · 可靠消息：Outbox

本片只用Outbox这一种做法，14镜28句、3499帧，约1分57秒。先共同保存订单与待办，再由独立程序转发，演示已发未标记的崩溃重发，最后用库存与唯一处理标记共同提交保护重复效果。各失败分支明确重置，不把消息系统和两数据库画成一笔原子事务。

实际阅读权威/原作者资料、文章及旁白见research.md、article.mdx、script.md。配音输入与能力边界见voice/substitutions.md及voice/qa.json。状态预演和实际编码须分别核验；本目录尚未声明用户已经观看认可。

配音、铺轨和起音复用episodes/_shared；真实时序与冻结使用episodes-codex/_shared/通用脚本。工程入口remotion，npm ci后运行npx tsc --noEmit、node scripts/qa.mjs；关键无字幕片选04、08、10、12。根任务确认所有输入停写后统一freeze/全片编码，不在此目录另写整轨算法。

三尺寸封面由Cover.tsx生成，4:3核心x315..1125/y<918，poster与3:4 JPEG相同。没有额外全局片尾。配乐Kevin MacLeod《Wallpaper》，CC BY 4.0。


## 成片与发布记录

v0.50.3流程导航修订已完成正式编码与独立媒体复核，完整SHA见[render-result.json](render-result.json)，实际范围/限制见[qa-final.md](qa-final.md)。原v0.47.0已被用户观看并提出结构反馈，旧输入通过[历史索引](revisions/v0.47.0.json)追溯；本版不预记用户认可。GitHub发布与线上核验后按#152收尾。
