# MQ05 consumer-replay-v2：从保存的0重读同一条记录

当前使用root最终接受实际声轨：4884帧/162.8秒，voiceSHA256=e1fd676b51a059bc6e54b475aff3a696da4f260e1d6c1d2a686705600453622a；storyboardSHA256=e6f332a51e9376d47f03f45974a4e5b0536322645c20ee542de05065bbe67479。实际每句localStart/localEnd只提供声学句包络，不冒称句内字词强制对齐。旧6073帧Prevoice估计板、原90图及窄修/短片继续保持原身份，不转记真实时序。正式src/index.ts只注册Main并读取实际D/storyboard，拒绝估计板/缺音轨时序；另独立Prevoice entry供历史复现，不作缺省回退。

EP45 / slug kafka-consumer-idempotency / MQ05，保留原身份与封面，正文共用不可变Kafka style-v1。页身暖炭灰#211D1B、面板#302823、前景#FFF1E8、次字#C3ADA0；写入/业务动作橙#FFAE73、位置/恢复请求冰蓝#93CCE5，成功保护绿#90D3AB、重复加分/漏处理红#F78E82。Kafka标记只在Kafka容器，业务数据库使用数据库身份符号；不借用unique索引并发图或锁动画。文字不使用边线低对比色作前景。

首镜只建立订单7042、会员17已加10分与同一积分事件又被处理的冲突，不先显示20完成，也不先铺consumer/committed等术语。第二镜显式回看首次读取前：原日志已有唯一E01@orders/P0 offset0、恢复0、积分0。模型从已追加起点开始，故只高亮唯一原记录与“追加1次”，不新增无模型的生产者发送动画。

之后三个稳定空间：[90,430,490,355]Kafka原日志与该组持久恢复位置；[710,430,490,355]当前唯一拥有者的本地内存；[1340,430,490,355]外部业务数据库。原记录一直留在第一空间的同一offset；拉取返回仅移动副本圆点。甲内存1与Kafka保存0分开，数据库COMMIT只改积分，不联动Kafka提交。退出后中间内存清空，左右两份持久状态保留；新乙接手同一容器，不并排放两个稳定同组P0拥有者。07查询→收到committed0但本地position仍未安装→安装position0三态必须各有停留，08再将本地0变成Fetch0参数，响应仍是原offset0。

全局四段方向：同一条原记录／读取与恢复／退出后再读取／避免重复效果。01–09主讲恢复因果，09无防护数据库第二次提交后才20。10单独显式reset回a-polled：唯一原日志仍在，甲内存下一读取位置1/组0/积分0/无key，只改变提交顺序。Kafka先提交1，退出后乙恢复1/Fetch1空，不删除offset0、不把漏业务说成丢日志。11再回同一a-polled起点，从积分0无key开始，在同一DB事务中暂存points:E01和+10，COMMIT同帧变10+key，之后退出/查询0/安装0/Fetch0再次交付。不能在旧20或无标记10现场凭空补标记。12乙尝试第二次、命中稳定业务键后跳过，保持10分，再显式提交Kafka1；最终只按模型收回日志1/尝试2/效果1，不泛化ExactlyOnce外部保证。

主源码从model.snapshots与plan.modelStages同源读取。sceneTiming(s)只按实际每句localStart/localEnd布置阶段，stateAt导出当前snapshot；任何段长变化都由真实board驱动，未声称句内字词对齐。DB未提交pendingPoints和pendingKeys只作“拟写/拟登记”，已提交积分与processedKeys只在模型COMMIT后出现。完成态标题和脚注按真实当前模型值/阶段守卫，不在计划说明中提前宣告完成。移动圆点在y414保留通道，静态路径标签y363；不带长文本穿过日志、标题或数字。

可读DOM：data-model-state/branch/reset-from/client-owner/client-active/client-position/committed-loaded/fetch-offset/returned/group-committed/db-points/processed-keys/db-transaction/db-effect/producer-send-count/log-append-count/log-records。原记录data-log-record/event-id/offset/partition，移动体data-moving-body与record-copy的data-moving-record。所有文字data-text/data-copyfit；默认Main烧录字幕，showSubtitles:false与hideSubtitles:true同时覆盖时不渲染字幕。独立QA应对inputProps及resolvedcomposition.props共同关闭，并实际解码看图，不靠文件名推断无字幕。

嵌套src到episodes/_shared为7层相对路径；theme和middleware-identity均指现行实际目录，不引用旧episodes-codex/ignored缓存。fresh npm ci按4.0.534锁安装；依赖/命令记录在remotion/dependency-install.json。src/placeholders预建仅供canonical freeze生成派生快照，不作为正式Main的缺省输入。薄包装由publication代理提供；默认render实际limitedBT709转换+混音+同色title-author资料。root最终声明字体、style、identity等实际冻结依赖；作者不自行freeze/正式整片编码或改旧输入。


实际时序第11镜按根确认作压缩复演：完整plan/model仍保留9阶段；Main选择reset、DBpending、DBcommit、halt、Bposition-installed、Bfetch、Bpolled共7个既有快照，不改模型和旁白。DBpending在第二句.04开始，COMMIT在.55、退出.82，B恢复0在.88、Fetch在.94，记录响应在句后tail送达；甲退出到乙取得P0不暗示主动LeaveGroup或立即通知/选举协议，标签明确不推定检测和分配时长。省略的查询/收到恢复值两中间态已在第07镜完整展示，并在本镜标“沿前述恢复链压缩复演”。第12镜统计收束保守到第二句.80；效果、提交完成词依模型值显示，未提前出现。

当前4Figure实际整数帧1815/3040/3946/4872，秒数严格frame/30，研究作者已据此限域更新MDX。作者已逐张打开4个实际源PNG，正式编码后仍须按这些n抽JPEG逐张复核，不把预演PNG当成已生成的文章JPEG。当前selfQA报告在remotion/qa-actual-*，独立动态、最终附录/媒体/网站另行审查。
