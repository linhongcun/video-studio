# P06 provenance说明更新后的定向身份补充

核验日期：2026-11-11 UTC。原[audio-check.json](audio-check.json)、[README.md](README.md)及原音频检查脚本保持原字节。本补充只处理制作人在冻结前更新`input-provenance.json`的`scope`说明，不重做信号分析，也不覆盖原回执。

结论：确认provenance仅`scope`一项变化；此前核验的音频输入及装配结果全部保持，原有界音频检查仍适用于当前冻结输入。当前provenance也与本轮冻结清单内的对应SHA一致。

| 身份 | 完整SHA-256 |
|---|---|
| 原音频报告绑定的provenance | `4723ea6769261f2966f20ba96a67df01c32f81cd8df064e3d40de9f96f3924d7` |
| 当前provenance | `9c2df7510d90ed7e4764f31561b245fefb216e9e3aa5ba45f82701d015fbd3f4` |
| 当前冻结清单source-sha256.json | `54ea607932572d1eebaed85f6169d0c42c4520313edf862c1e2686757f158d6f` |

制作人提供了初始化时`scope`的完整原文。独立检查在内存中将当前JSON仅此字段恢复为该原文，按原序列化格式重建，所得完整SHA恰好等于原报告记录的`4723ea67…3924d7`。因此这一结论不只依赖制作人的“仅改说明”陈述，也不依赖不完整的旧快照；`voiceReuse`及其余字段、顺序与原序列化字节均得到该重建哈希约束。旧说明及当前说明的完整内容保存在[补充JSON](provenance-supplement.json)。重建未写回制作目录。

另对181项文件身份执行定向SHA复核：脚本、jobs、build元数据、整轨、共享裁尾实现，2句新take的6份输入及2份实配句WAV，以及28句复用输入在新／旧制作目录中的168份文件。全部与原音频回执记录一致；当前冻结清单中存在的相应条目均匹配。新／复用句ID与计数也与当前`voiceReuse`一致。原3份QA产物执行前后SHA保持。

影响范围仅为provenance制作状态说明由待审草稿更新成已完成独立稿审、28旧＋2新及共享装配的实际范围。整轨仍为`4cc091cbd9f0b66d105f7819c3b299ba39b89ec67293a25ae0b2d1a5d1d64c2c`；不影响此前新句信号、裁尾长度、整轨PCM切片或复用take身份的结论。

可从仓根执行`python docs/archive/2026-11/puzzles-followup-logic/audio/twelve-balls/check-provenance-supplement.py`复查；它只写本目录独立补充JSON，不运行原检查脚本、不改旧QA或制作源。本次没有TTS、ASR、重新配音或语义听辨；语义与读音仍未验证。2026-11-07的三个历史400仍是历史限制，没有被记成本轮新请求。
