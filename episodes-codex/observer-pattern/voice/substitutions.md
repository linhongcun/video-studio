# D02 产品交互与结构/Java修订配音

2026-10-25（北京时间）。本轮沿用原示例，按产品交互首屏、结构职责、原协作过程和Java短静卡重新编排。导演与独立概念审读通过、owner确认停写后，冻结全文脚本SHA-256为 `76ac04f108442603bcb4a3daf04bd7bb0f59883bd675d4a84b67552f189341bc`。正文24句中，仅5句新合成；其余19句按完整旁白文本和送模文本精确匹配原选定take，原始WAV、48kHzWAV及文本侧录都保持完整字节。完整映射见 `flow-reuse-provenance.json`，新请求仅列在 `jobs-flow-ui-java.json`。

## 选段与保留

新候选后缀为 `flow`；原录音原位保留，没有覆盖或删除。已逐文件核对72个历史take相关文件，其SHA-256均与 `revisions/flow-ui-java/baseline/voice-archive.json` 一致。具体选择在 `picks.json`，送模文本及所有选中原始音频转换为48kHz的PCM逐样本一致。共享 `common.load/common.cut` 负责裁尾，新增审计器只核对来源与波形，不复制裁尾或起音算法。

使用MiMo `mimo-v2.5-tts`、冰糖、自然适中的科普语气，未作词语替换或合成后变速。每句追加的“好。”仅用于共享隔离裁尾；字幕和旁白原文不改。原候选复用只表示录音字节与文本来源一致，不将其扩大为已完成语音识别或读音听辨。

候选信号标记为：[]。所选候选及归一后整轨均无≥0.50秒句内低信号标记。不存在裁尾/格式硬失败，详见 `flow-candidate-audit.json`。

## 有声正文与Java静卡

先用原共享build/assemble/whole/strict/check完成真正有声正文：5178帧。真实正文输入和WAV、words、storyboard、字幕已另存不可变 `revisions/flow-ui-java/voiced-body/`，不修改旧checker或伪标Python卡。

新增 `episodes-codex/_shared/append_java_endcard.py` 只在正文后追加150帧、240,000样本全零PCM，并声明 `meta.javaEndCard.kind = java-design-pattern`。末镜 `javaCardFrom` 为镜内局部帧，meta的from为全局帧。最终5328帧/177.600000秒，完整voice SHA-256为 `ba5cf6b558f84933beb50c56a9105248cabca039e1e37d6017125bc821c324f9`。

Java验证器在临时副本对真实正文运行未改的原checker，再逐字段核对最终仅有声明的时长、哈希和尾卡派生字段改变；正文PCM前缀、旁白句界、所有字幕不变，静卡区无字幕且新增声轨全零。最终仍用原whole与strict检查，最大铺轨偏移0帧。详见期根 `qa-java-endcard.json`。`voice/build.json`/`qa-timing.json`描述有声正文；最终长度和卡边界以Java报告、words与storyboard为准。

最终纯人声测得-16.0LUFS、4倍采样真峰值-2.10dBTP；最终混音由正式渲染另测，不能将此当成正式MP4已检查。24份归一后逐句PCM与最终声轨相应切片全部一致，见 `audio-qa.json`。

## 能力边界

当前没有可用ASR包/模型或转写工具，未执行逐字ASR、发音/变调听辨或全片人工听辨。words兼容字符字段仍只是句包络，只有句首起音由共享声学规则测量。波形/PCM保真、文本来源和时序检查不能证明实际读词、发音或观众理解正确。正式动画、实际编码与上线仍须独立检查；后续AAC一致性只证明采用了本轮音轨，不代替听辨。
