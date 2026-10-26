# EP.21 · 可靠消息：Outbox

本片只用Outbox这一种做法，14镜28句、3499帧，约1分57秒。先共同保存订单与待办，再由独立程序转发，演示已发未标记的崩溃重发，最后用库存与唯一处理标记共同提交保护重复效果。各失败分支明确重置，不把消息系统和两数据库画成一笔原子事务。

实际阅读权威/原作者资料、文章及旁白见research.md、article.mdx、script.md。配音输入与能力边界见voice/substitutions.md及voice/qa.json。状态预演和实际编码须分别核验；本目录尚未声明用户已经观看认可。

配音、铺轨和起音复用episodes/_shared；真实时序与冻结使用episodes-codex/_shared/通用脚本。工程入口remotion，npm ci后运行npx tsc --noEmit、node scripts/qa.mjs；关键无字幕片选04、08、10、12。根任务确认所有输入停写后统一freeze/全片编码，不在此目录另写整轨算法。

三尺寸封面由Cover.tsx生成，4:3核心x315..1125/y<918，poster与3:4 JPEG相同。没有额外全局片尾。配乐Kevin MacLeod《Wallpaper》，CC BY 4.0。


## 成片与发布记录

v0.51.0流程导航修订已完成正式编码与独立媒体复核，完整SHA见[render-result.json](render-result.json)，实际范围/限制见[qa-final.md](qa-final.md)。原v0.47.0已被用户观看并提出结构反馈，旧输入通过[历史索引](revisions/v0.47.0.json)追溯；本版不预记用户认可。GitHub发布与线上核验后按#152收尾。

## 第8批参考资料名单与当前入口

本批为已验收的完整原片追加`title-author`参考资料名单，每页最多4项、默认5秒，仅显示完整原题与明确作者或机构。原旁白、字幕、分镜及现有视觉依赖保持；不运行装配、TTS、正文渲染或混音。基线`61d3b984a594578a67bc34aa374cccd0326cd9d6`的Git完整原片已逐字节保存在`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`，本批直接消费该body并另做实际追加媒体保真检查。

当前冻结入口为本期`freeze.py`，保留旧清单全部149个key与既有共享依赖；旧article/research/package记录通过`revisions/reference-endcards/`下before快照核对，其余按原路径核对。当前清单声明实际资料与新入口依赖，不声称它已重现旧MP4。原实质输入校验保留；storyboard、words、带SHA的分镜快照及placeholder只读检查，不再重写。来源JSON及其中记录的原始补证文件分别按完整SHA纳入冻结，技术实读日期与本轮题名/署名补查范围按来源记录区分。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/tx-outbox
python3 episodes-codex/tx-outbox/freeze.py
python3 episodes-codex/tx-outbox/freeze.py --verify
```

默认`npm run render`调用共享bibliography wrapper，先核对来源和冻结，再运行`render:body`及附录。`render:body`保留本期原voice→mix闭环、编码参数与concurrency=2，只把mix输出改到`out/body.mp4`；`npm run render:references`从该完整body单独追加名单。`npm run verify:references`用于后续完整交付核验，会检查最终媒体；本批入口审计只执行只读freeze与wrapper.verify_freeze，不重复整片解码。旧正文QA和发布事实按原记录保留，最终总帧数以新receipt、render-result和发布metadata为准。进度见[第8批记录](../../docs/reference-endcards/batch-8/README.md)，不预记尚未完成的媒体或线上结果。
