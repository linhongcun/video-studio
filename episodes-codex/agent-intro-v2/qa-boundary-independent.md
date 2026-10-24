# Agent A01 V2：独立变更边界与冻结设计检查

检查者：repair_issue_sources（独立边界复核）。日期：2026-10-24（北京时间）。

检查范围：本轮文档差异、canonical 元数据、新制作目录的配置与音频/时序薄包装，以及冻结清单生成逻辑。**这是制作中的只读边界检查，不是预演或成片验收。** 未观看V2动态预演或最终MP4，未进行配音听辨、ASR、响度测量、线上发布或媒体部署核验；不预写这些项目通过，也不代表用户已经认可新版。

## 旧版冻结产物保持

- 对 episodes-codex/agent-intro/source-sha256.json 中171项逐一检查当前文件SHA-256：171项均存在且一致，0项缺失、0项变化。
- git diff --name-only -- episodes-codex/agent-intro 的结果为空；本轮制作输入位于新目录 episodes-codex/agent-intro-v2/，没有覆写旧目录的冻结文件。
- 另核对旧版 video.mp4 的工作区Git对象与HEAD中的对象一致；该文件的SHA-256为 44b21f36f6b99b4106141548a6bbc70c7556a394e4f1e819949b0e2af9be9b9c。
- canonical目录 episodes/agent-intro/ 后续用于新片上线，与旧制作目录及v0.50.0历史保留是不同职责。检查时新版媒体尚未接入；这里不声称canonical新版媒体已通过核验。

## 文档与授权边界

- docs/RULES.md 的本轮增量是开头主题、具体问题、逐镜因果和结尾回应要求，没有修改GitHub站点或平台发布授权。
- docs/pipeline.md 将叙事检查放在脚本冻结之前，并说明首2/5/15秒是本期检查标准，不把单期镜数或时间点扩成所有片子的固定结构。
- docs/production-memory.md 明确记录用户观看V1后的负面反馈，保留旧版实际检查与发布记录，未把V1事实/媒体检查写成用户理解或认可的证据。
- docs/successful-practices.md 只补充事实检查的适用范围，没有把尚未完成的V2改法提前记作已验证成功经验。
- canonical元数据仍保留EP.22、slug agent-intro、firstRelease v0.50.0及空platforms；sourcePath改为新制作目录，不新增平台发布事项。

## L021的事实与状态（检查时暂编L019，合入并行主干后顺延）

L021与主任务转交的用户反馈一致：主线模糊、开头铺垫多、像流水账，需要先给主题、悬念或方向。关于原因的文字明确标为“复盘判断”，未冒充用户原话或观众实验结果。

量化回看以V1实际storyboard核对：第08镜首次正式订单查询从1799帧开始，即59.97秒；第14镜首次明确引入“智能体”从3272帧开始，即109.07秒。因此记录中的“约60秒”和“约109秒”有实际时序依据。V1开头的旁白也确实将“可以申请但订单未变化”作为冲突，与正文只提供申请建议的任务边界产生叙事错位。

L021明确写出新版尚待制作与观看验证；V2教学审核也区分文本审核与真实2/5/15秒、无字幕动态及最终编码检查，没有预写媒体或用户观看结论。

## 薄包装与算法复用

- 本期 assemble.py 通过runpy调用 episodes-codex/_shared/assemble_sentence_episode.py，再添加本期标题、示例状态、动作描述与实际句边界字段；不复制TTS、裁尾、铺轨或起音算法。
- 共享装配器导入 episodes/_shared/onset_rule.py 的Rule；没有在本期另存Rule实现。
- voice/audit-takes.py 导入共享 voice/common.py 的cut和load。其额外逻辑是选定候选的文本、PCM/raw转换及信号包络审计，不生成或改写候选音频；报告明示不构成发音或ASR通过。
- 本期freeze.py通过runpy调用共享freeze_sentence_episode.py，再把本期实际薄包装、音频审计、渲染/QA脚本、jobs和输入冻结记录追加到清单；未修改共享音频数值来适配单期。

## 冻结清单覆盖设计

静态检查确认共享冻结器与本期追加层共同覆盖：

- 实际script、article、research、pronunciation、plan、episode-config、visual-direction和knoll-props。
- storyboard、words、covers、整轨voice.wav及实体public音频；共享冻结器还核对公共音频字节一致、配音/脚本SHA和帧数关系。
- voice/params.json、picks.json、sents.json、build.json、substitutions.md和旁白SHA记录。
- 按picks选择的每一句wav和txt.json，以及对应存在的raw.wav；本期音频审计另外要求选定raw文件存在并核对其转换结果。
- 实际Remotion源码、占位分镜快照、package/lock、配置，以及本期remotion/scripts下的实际渲染/QA脚本。
- 本期assemble.py、freeze.py、voice/audit-takes.py、voice/jobs*.json和voice/input-freeze.json。
- 实际共享装配/冻结/检查实现、共享TTS、prep/gen/build/common、唯一起音算法、主题、混音脚本和配乐。

这是对冻结逻辑的覆盖检查；检查时尚未生成最终V2媒体，未执行本期最终冻结或编码检查。最终负责人停写后仍须实际运行冻结、核对清单，编码前后再复核，不能用本报告代替。

## 已同步主任务的收尾项

1. 检查时package.json曾声明stills命令指向不存在的scripts/stills.mjs。已向主任务报告，主任务转交渲染负责人修正；此处记录发现，未在本报告中预写修复结果。
2. 检查时canonical元数据的finalVideoFrames=5420、targetDuration=181仍是旧片值。主任务确认正在等待V2实际分镜/成片后由站点负责人更新；上线前必须替换为真实值并核验字幕和章节，不以当前临时值发布。

未扩大平台发布授权。本报告仅证明上述检查范围及发现，不宣称V2制作、成片或上线已经完成。
