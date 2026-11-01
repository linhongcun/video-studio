# clear-parts 最终编码声轨核验

结论：passed。新成片实际数值核验已执行；源配音及历史审计按精确身份复用，没有新 TTS、源听辨、ASR 或全片人工听审。

- 最终 MP4 SHA-256：`c570ad44437b4bb2157a321328c6b4a021b5cf32a0ce183b865cf3ed57b1100b`
- 新冻结清单 SHA-256：`43191a8176f7f96529d641d6160f94e497c2d20131fa322e485908da02fee7d0`；146 项输入前后未变。
- 当前 20 句旁白与冻结配音请求文本相同；63 个原 raw/take 文件、20 个 normalized 句文件及 WAV 与原声源逐字节相同，四份历史审计在 `provenance/original` 保留原 SHA 和原能力限制。当前关联由 `qa-voice-reuse-provenance.json` 独立绑定，未改写历史审计为 fresh pass。
- 本轮正文与最终视频的 7005 个 AAC 包 payload、PTS、DTS、duration、size 完全相同；解码立体声 PCM 均为 7172096 样本且 SHA 相同。
- 源 WAV 7171200 样本全部覆盖；未混音偏移 0，AAC 尾垫 896 样本；整轨相关系数 0.9999776205，逐句最低 0.9999698115。
- 混音偏移 95 样本（1.979167 ms）；20 句偏移漂移最大 0 样本。已知双源模型整轨相关系数 0.9998522628，逐句最低 0.9998109146；语音窗旁白高于音乐 RMS 11.708640 dB。
- 最终响度 -16.02 LUFS；真峰值 -3.71 dBTP。沿用固定数值 checker 和原阈值，失败项为 0。

5 项源低能量区间标记、4 项整轨标记继续保留，没有通过清空标记获取 passed。波形一致性无法证明措辞、发音或自然度；已知音乐回归也不是盲声源分离。实际画面、浏览器播放及原生字幕边界分别记录。

详细结果：`qa-encoded-voice-content.json`、`qa-encoded-voice-content.numerical.json`、`qa-encoded-body-gate.json`。
