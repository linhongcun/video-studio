# height-choice 最终编码声轨核验

结论：passed。使用本轮fresh源/整轨审计与实际新WAV执行完整20句编码波形数值核验；未进行ASR、逐字听辨或全片人工听审。

- 最终MP4 SHA-256：`0edf23150bb3a3a00950ebb99547e09e9ede6ba9326e22d46e73d5e2e50f24f9`
- 冻结清单：`c2607a0506a616bca777fa90af111ad092856995bb40fe344afcffd65e781813`；151项冻结输入前后未变。
- 新WAV：`e63140e9dbb8c0a9a841212563c090cf3aa199eeccf417077dc6c0a441d04b4b`，7291200样本、4557正文帧。17句仅在raw/48k/request层精确复用；实际4次TTS生成选中3句（07-1d、07-2c、09-1c），其来源与freshGeneration/selectedFreshSentences/mixedSource、当前pick及新源审计逐项SHA一致。未假定旧normalized PCM或旧整轨相同。
- 本轮正文与最终视频的7122个AAC包payload/PTS/DTS/duration/size完全一致；解码立体声PCM均7291904样本、SHA相同。
- 源信号全部覆盖；未混音偏移0样本，AAC尾垫704样本；整轨相关系数0.9999778281，逐句最低0.9999698115。
- 最终混音延迟95样本（1.979167ms）；20句偏移漂移最大0样本。已知旁白/音乐双源模型整轨相关系数0.9998544284，逐句最低0.9998045300；语音窗旁白相对音乐RMS为11.730949dB。
- 实际最终响度-16.01LUFS，真峰值-3.71dBTP。固定数值checker/阈值保持，失败项0。

本轮fresh源审计保留5项低能量区间标记，整轨仍保留4项标记；没有清空旗标或据此判断发音/自然度。波形相关不能识别口播词义，双源回归不是盲声源分离。

详细结果见`qa-encoded-voice-content.json`、`qa-encoded-voice-content.numerical.json`及`qa-encoded-body-gate.json`。实际图、连续预检、浏览器和原生字幕边界分别记录。
