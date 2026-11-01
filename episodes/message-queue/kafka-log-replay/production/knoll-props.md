# 制作说明

身份：MQ03 / EP43 / kafka-log-replay，issue#311，总览#308。清洁工作区fetch后从9e44109511cac1b0fb54d8aa9383b9d7dfe9074b建立codex/mq03-20261030。新期Remotion按当前锁文件fresh安装，仅复用共享基础设施源码，不继承MQ02回执或冻结。

11镜22句，时长由真实冰糖配音决定。两分区四事件沿同一ID，P1背景进度固定2，P0沿poll/process/commit→独立组→整组停用/reset/restart→保留边界展开。max.poll.records=1与关闭自动提交固定，inactive时读取位置不存在，不把其已提交位置混成业务状态。

共享voice/prep/gen/build与句级装配负责实际PCM和时序，Kafka仅送模替换为卡夫卡，字幕保持原稿。public/audio/voice.wav必须为实体副本。声学/来源检查、逐字ASR和全片人工语义听辨的实际范围分开记录，不找用户代替质量检查。

制作默认沿MQ02已验证limited BT.709正文转换、同色资料adapter与完整附录流程，本期声明/来源/冻结清单/封面输入快照全部重新生成。任何写源修改须先停止预演/排队/编码，明确负责人停写后再冻结。

正式流程：来源预检及独立审稿→配音与声学时序→独立连续动态图/封面→文章图位定秒数→冻结真实输入→默认render含5秒资料列表→成片完整解码与实际编码图→图文截图与本地网页→PR/Release/Pages→普通canonical完整SHA及原生浏览器线上检查→completed关闭311/同步308。仅GitHub站点，无平台新发；技术通过不预记用户观看认可。

制作中再次fetch并整合主干72b841c1（v0.94.0）；保留“其他”分类与新站点指导，MQ03明确仍归message-queue。13项上游改动与本期模型、声音、动画、封面及共享渲染输入零交集，候选Release顺延v0.95.0；实际交集记录见qa/upstream-integration.json。
