# EP45 MQ05 consumer-replay-v2 制作接口

12镜/24句；最终真实声音与分镜未产生，不填写估计声轨SHA或将placeholder叫作测得时序。根负责TTS/words/board/covers/冻结/正式render/publication；作者内容接口为script/plan/model，Main/package由mq_animation独占。本修订位于production/revisions/consumer-replay-v2，所有ROOT按AGENTS向上寻找，不能把旧episodes-codex或仓外ignored旧工程当依赖。

## 对象与状态

同一条E01/order7042/account17/+10，orders/P0offset0。三个固定空间：Kafka日志与组points持久committed，当前拥有者A或B的内存position，外部数据库已提交积分与业务键。甲乙先后接手，非两个稳定同组拥有者。日志不搬走，不画producer重发。

model.json.snapshots是全量状态，按id查表。log.records与producerSendCount/appendCount始终1，consumer.owner最多一个；activefalse时position/committedLoaded/fetchOffset都为null。consumer.returned保留完整事件及原offset；db.points是已提交值，pendingPoints/pendingKeys只在本地事务open时存在，businessAttemptCount与effectCount分别计业务尝试与效果，不能用poll次数代替。

plan逐镜modelStages与resetFrom明确。01为DB10/组0的问题快照，02回看首次读取前已有唯一记录的共同起点，仅高亮单记录，不造模型外0→1追加；03Fetch0→position1；04读位置和恢复值分开；05DBCOMMIT10；06halt清内存；07查询0/收到0/安装0三步；08Fetch0/原E01@0/position1；09业务再提交20；10reset DB0/组0后先commit1/halt/B Fetch1空；11reset同起点后本地key+10同事务提交，再halt/B Fetch0；12skip/commit1/log1attempt2effect1。

## 必须由动作兑现的因果

收到committed0时不能提前显示Bposition0；安装后才有Fetch0。poll返回应用前本地position已1；该值不能标成Broker保存的组读取位置。数据库COMMIT完成前不能把pending10/20叫已完成积分。A退出清内存后再显示B，且原日志/组值/DB已提交状态保留。

10/11分支先明确完整reset a-polled：DB0、无key、组0、Aposition1、log1。不得从旧20现场跳成10或在未标记DB10上凭空增加key。第11镜有足够时间依次展示同事务暂存/提交→halt→B恢复读取；若真实声音不足以读清，再与根讨论内容或拆镜，不能压成1帧完成。结尾依据当前guard-final模型收回log1/attempt2/effect1。

沿当前不可变Kafka暖炭灰/橙/冰蓝style-v1与产品标识，不重画旧封面。箭头只穿面板间空隙、需要可读state DOM；正文字幕默认开启并支持showSubtitlesfalse/hideSubtitlestrue真关字幕预演。额外data属性建议model-state/owner/position/committedLoaded/fetchOffset/groupCommitted/dbpoints/businessAttemptCount/effectCount/sourceRecords，供实际独立DOM投影。

## 文章与资料

四图采用article/consumer-replay-01-commit-gap.jpg、02-fetch-zero、03-early-commit、04-idempotent-result，同名站点Figure URL，不覆盖publication旧图。当前frame/secondsnull，根最终真实voice后才能定整数帧/seconds=frame/30并在编码前启用。

references.json title-author四项一页默认5秒：KafkaConsumer.java/Apache Kafka、ConsumerUtils.java/Apache Kafka、AbstractFetch.java/Apache Kafka、Transactions/PostgreSQL Global Development Group。不得只渲正文；默认入口须做实际BT709 limited像素转换、混音与原题/机构附录。资料不叠原文、版本、链接或暂停提示，完整证据在文章与研究。

冻结清单由根最终填写，须包括本期真实内容、来源原文/题名证据、article-sources、最终图位计划、所有实际import共享视觉/代码、字体账本、声音与时序；不是继承旧冻结回执。有限模型与本轮真实运行分开：新独立run recovery-20261102T065614.804079Z三分支91断言通过，作者已读实际范围，见research/qa-editorial/runtime-author-review.json；初始0用Admin显式设置并查实，业务后1用consumer.commitSync。声音/预演/成片/播放器/站点检查均按后续真实执行记录，不以实测替代动态检查。
