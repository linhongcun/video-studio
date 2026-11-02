# MQ05 / EP45 consumer-replay-v2

《消费幂等：已经处理过，为什么还会再来一遍？》；用户反馈修订#454，首发#313/v0.97.0历史保持。基线01cd181caf24d4a8ce846c0eb8faeeab8f0054e2，新目录独立制作，不修改旧生产、发布、封面、冻结或运行证据。

主问题是同一E01@P0offset0为何再次处理：单次生产→A内存position1/组committed0→外DB10已提交→A在Kafka提交前halt→B同组查询0/安装0/Fetch0→原记录再次交付→无防护20。前9/12镜、569/805旁白字（70.68%）解释Kafka WHY；根最终声轨正文4884帧/162.8秒，前九镜3432帧，实际时长占70.2703%。第10镜完整reset改早提交，显示DB0漏处理；11–12再reset，用同DB事务业务键+10，重复尝试skip后另Kafka提交1，收束log1/attempt2/effect1。不讲PG索引并发内部。

- script.md/plan.json：12镜24句，严格英文slug标题；独立编辑已通过，根已完成并接受最终24句声轨，作者未TTS或改写已审批脚本/计划。
- research.md/source-chain-notes.md/sources/：本轮fresh官方固定4.4.0源码/GET/精确原文；PG18.0只读必要本地事务/主键/INSERT合同。
- references.json与article-sources.json：4视频来源、6文章精确摘录，原题/机构/访问日齐；均不继承旧verified身份。
- build_model.py → model.json/model-verification.json：纯标准库有限教学模型，36快照94检查；不是Kafka/Postgres实测。运行命令`python3 build_model.py`。
- article.mdx/article-figure-plan.json：四章与10处SourceQuote齐，四Figure已按真实最终声音启用，整数帧1815/3040/3946/4872，seconds=frame/30；初稿/旧计划字节与限域差异留qa-editorial/actual-figure-timing。实际JPEG待正式成片后导出，结构验证不等于成片图片通过。
- pronunciation.md：向根提交读音要求；本作者不改TTS参数/声音算法。
- knoll-props.md：制作对象、状态与新路径接口；Main/package由mq_animation，公共薄包装由根安排制作角色。

本轮真实Kafka/PG三个分支在docs/archive/2026-11/mq05-consumer-replay/runtime/runs/recovery-20261102T065614.804079Z独立执行，91项断言通过。作者已读报告、实际stdout/网络Fetch实参/物理日志dump/依赖版本/命令/源码；详见research与qa-editorial/runtime-author-review.json。准备恢复值0实际用Admin.alterConsumerGroupOffsets，业务后提交1用consumer.commitSync，已在根授权下修前言/模型元数据，旁白不变。2026-10-30旧89项和旧批121项保留历史身份；早期幂等参数拒绝及Fetch证据未闭合候选均保留，不冒充全尝试成功。

独立编辑已批准script d21acba…/canonical旁白935cdf…；根正式接受最终voice e1fd676b51a059bc6e54b475aff3a696da4f260e1d6c1d2a686705600453622a，正文4884帧，真实board e6f332a51e9376d47f03f45974a4e5b0536322645c20ee542de05065bbe67479。作者此轮仅限域补文章四图位、图位计划与本README，批准的script/nar/model/plan/refs及声音/时序字节不动。Main实际自审与独立动态仍由制作/QA收束；根统一冻结、正式编码、JPEG导出与publication/GitHub交付，不预记成片或上线通过。
