# MQ05 / EP45 consumer-replay-v2

《消费幂等：已经处理过，为什么还会再来一遍？》；用户反馈修订#454，首发#313/v0.97.0历史保持。基线01cd181caf24d4a8ce846c0eb8faeeab8f0054e2，新目录独立制作，不修改旧生产、发布、封面、冻结或运行证据。

主问题是同一E01@P0offset0为何再次处理：单次生产→A内存position1/组committed0→外DB10已提交→A在Kafka提交前halt→B同组查询0/安装0/Fetch0→原记录再次交付→无防护20。前9/12镜、569/805旁白字（70.68%）解释Kafka WHY；真实声音时长份额之后另核。第10镜完整reset改早提交，显示DB0漏处理；11–12再reset，用同DB事务业务键+10，重复尝试skip后另Kafka提交1，收束log1/attempt2/effect1。不讲PG索引并发内部。

- script.md/plan.json：12镜24句，严格英文slug标题；未TTS，不造board或测得时长。
- research.md/source-chain-notes.md/sources/：本轮fresh官方固定4.4.0源码/GET/精确原文；PG18.0只读必要本地事务/主键/INSERT合同。
- references.json与article-sources.json：4视频来源、6文章精确摘录，原题/机构/访问日齐；均不继承旧verified身份。
- build_model.py → model.json/model-verification.json：纯标准库有限教学模型，36快照94检查；不是Kafka/Postgres实测。运行命令`python3 build_model.py`。
- article.mdx/article-figure-plan.json：四章与SourceQuote齐，新consumer-replay-*四图位等待最终声音整数帧；未正式看图、不能冻结或发布占位。
- pronunciation.md：向根提交读音要求；本作者不改TTS参数/声音算法。
- knoll-props.md：制作对象、状态与新路径接口；Main/package由mq_animation，公共薄包装由根安排制作角色。

本轮真实Kafka/PG三个分支在docs/archive/2026-11/mq05-consumer-replay/runtime/runs/recovery-20261102T065614.804079Z独立执行，91项断言通过。作者已读报告、实际stdout/网络Fetch实参/物理日志dump/依赖版本/命令/源码；详见research与qa-editorial/runtime-author-review.json。准备恢复值0实际用Admin.alterConsumerGroupOffsets，业务后提交1用consumer.commitSync，已在根授权下修前言/模型元数据，旁白不变。2026-10-30旧89项和旧批121项保留历史身份；早期幂等参数拒绝及Fetch证据未闭合候选均保留，不冒充全尝试成功。

当前待独立编辑审批确切整稿/旁白SHA后根TTS；根统一封面安装、冻结、正式编码、配图导出与publication/GitHub交付。本目录不预记任何声音、动态、成片或上线通过。
