# MQ01 · Kafka入门重制

现行独立修订基于d7a5d768，保留EP.10、message-queue URL、原标题、创建与首发身份。用户将MQ系列统一Kafka并明确同步重制本片后换封面。旧root及mq-intro均保留为历史；本目录不继承旧RabbitMQ图义或验收结论。

12镜24句，当前正文3697帧/123.233秒。2句旧take精确复用、22句新配；实际provenance和声音检查见qa-voice.md。独立动态图义、实际编码与发布回执按完成阶段补齐；未执行逐字ASR、全片人工听审或真实Kafka集群实验不写通过。

本机Python为/workspace/.venvs/video-studio/bin/python，新Remotion目录按自身锁fresh npm ci。prepare/assemble只是共享句级工具的薄入口，语音和真实句窗已装配，后续不能为元数据追认而重新合成或重装配。storyboard-metadata-adaptation.json仅补covers/palette、证明全部scenes/声音/时序保持。

制作前来源预检：

```bash
node site/scripts/check-references.mjs --sources episodes-codex/message-queue/revisions/kafka-intro/message-queue
```

所有输入停写、独立预检通过后：

```bash
/workspace/.venvs/video-studio/bin/python episodes-codex/message-queue/revisions/kafka-intro/message-queue/freeze.py
bash episodes-codex/message-queue/revisions/kafka-intro/message-queue/render-final.sh
```

默认render使用_shared/kafka-video/render.py，复用canonical来源/冻结/body/full-media检查并选择不可变Kafka配色资料卡；不会修改旧引擎。正文混音在remotion/out/body.mp4，最终video.mp4含5秒参考附录；发布必须取最终媒体及真实render-result.publicationMetadata。

封面使用_shared/kafka-covers/render.py，当前源接入Kafka元数据后才允许--install；不向旧RabbitMQ片只贴Kafka名称。正文引用style-v1和冻结背景副本，不引用可增长的catalog。实际源文件、输入/输出SHA、预演差异、成片和站点检查集中在docs/archive/2026-10/kafka-series-style/。

站点仍episodes/message-queue，Kafka系列仍message-queue分类路径。新片/图文接入时保留历史日期与平台链接，仅更新真实修改日期、媒体范围、来源及sourcePath。GitHub按持续授权发布，外平台作品未重发。
