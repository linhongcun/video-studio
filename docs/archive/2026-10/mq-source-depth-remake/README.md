# MQ01–MQ04实现原理重制

2026-10-30，北京时间。用户授权重制已发布四期MQ，增加实现深度并保持容易理解；本轮优先于继续MQ05。任务[#443](https://github.com/linhongcun/video-studio/issues/443)，系列[#308](https://github.com/linhongcun/video-studio/issues/308)。从clean最新`923305b49cea1b18d7fc7e4dd8ac70ad830bc673`建立`codex/mq01-04-source-remake-20261030`。

| 稳定身份 | 本轮核心实现因果 | 新制作目录 | 当前阶段 |
|---|---|---|---|
| MQ01 / EP10 / message-queue | 日志保存消息数据，消费者读取后另执行业务 | `episodes-codex/message-queue/revisions/source-depth-v2/` | 审稿通过，配音与动画制作中 |
| MQ02 / EP42 / kafka-consumer-groups | classic Range分配表计算、同步和安装后限制成员读取 | `episodes-codex/kafka-consumer-groups/revisions/source-depth-v2/` | 审稿通过，配音与动画制作中 |
| MQ03 / EP43 / kafka-log-replay | 持久恢复位置加载为内存位置，再成为Fetch起点读取原字节 | `episodes-codex/kafka-log-replay/revisions/source-depth-v2/` | 审稿通过，配音与动画制作中 |
| MQ04 / EP44 / kafka-send-confirmation | 分区缓冲与结果完成，发送身份/序列让Broker识别重传 | `episodes-codex/kafka-send-confirmation/revisions/source-depth-v2/` | 审稿通过，配音与动画制作中 |

每片保留一个问题和可追踪事件。先用动作说明结构和判断，必要名称随后引入；代码按需，不以源码截图、类名或术语数量验收。脚本与分镜独立通过实现因果及可懂性审查后才配音；真实时序下再审实际动态，全部负责人停写后冻结、编码。核心原理留正文，完整调用链及旁支留研究与图文。

保留原EP、slug、题名、创建/首发时间与已有平台链接，旧封面继续使用。旧#309–#312的completed状态和真实交付不改写；本轮新任务完成上线后再关闭#443。开工[基线](baseline.json)保存四期1972个Gitblob和137份既有清单所涉及8435个实际文件的SHA/mtime；新修订不覆盖旧冻结输入。

固定Apache Kafka/Java4.4.0及官方commit`1156b2752aaa28eafc0b4c4d387e63356793268d`，各期按其实际协议和配置限定主张。单节点最小真实运行只验证明确记录的路径，不代替三副本故障、生产幂等丢响应或外部业务实验。实际范围见[最小运行报告](runtime/README.md)：单节点RF1已观察生产确认与日志、classic动态Range组读取、position/committed与重开恢复；原静态组运行及仅补动态组的不同输入分别保留，未重跑的position不追认为新run。未验证三副本故障、真实业务或MQ04丢回应。

四期配音前独立因果与可懂性审查已通过，审批对应旁白SHA见[审稿记录](qa/editorial-approvals.json)；当前正生成新配音和动画，尚未完成正式媒体、站点替换或部署。来源事实、有限教学模型、真实实验、声画与站点检查分别留证；没有执行逐字ASR、全片人工语义听辨、物理手机或学习效果实验时如实记录。仅GitHub主干与本站，无外部平台重发。
