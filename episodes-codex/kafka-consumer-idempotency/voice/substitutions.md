# TTS文本与候选记录

旁白与字幕保持已独立审读的script.md。voice/params.json仅在送模文本把Kafka替换为卡夫卡；原句、字幕及字词数据不作该替换。共享prep附加的收尾提示由共享build按实际句界裁去，不进入正文。

只对初始源声学旗标生成同文候选，完整原始请求、a/b/c、未选候选及各阶段声音报告均保留。最终非a选择：

- `01-problem-1`：选择c。
- `08-waiting-1`：选择b。
- `10-skip-and-progress-2`：选择b。

最终选择的请求文本与各句sents.json.tts相同；没有因声学旗标认定漏字或错字，也未进行逐字ASR或全片实时人工语义听辨。具体信号与选段PCM范围见qa-voice各阶段报告。
