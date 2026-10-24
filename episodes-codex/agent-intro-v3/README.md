# Agent A01 V3：开头直接呈现退款咨询

用户认为V2开头的内部流程框仍陌生，建议用对话框或对应功能的交互界面，先让人知道使用场景。本轮只改01镜0–236帧：首帧完整用户问句，订单/规则查询反馈，4秒AI反问；237帧起仍回到首次查询的原讲解。

实际视频：2864帧、95.466667秒、5,776,564字节，SHA-256为5c751c841497dc01a2bc076d07de8c9cec90f94d54358b925e504a712b977661。canonical slug仍agent-intro，源码入口改为本目录的remotion；V2/v0.50.5历史保持。

## 局部制作

所有22句旁白、voice.wav、四章和字幕时序不变。只用Remotion原参数渲染首237帧；237正是旧片闭合GOP的IDR，因此复制后2627个视频包，并从原片整体复制4476个已混音AAC包。没有调用TTS、重混音或重新渲染其他场景。

从仓根执行：

```sh
python3 episodes-codex/agent-intro-v3/freeze.py
```

在remotion目录执行：

```sh
npm run render
```

实际命令先render:opening（0–236、muted），再调用compose-revision.py。合成脚本校验126项冻结输入、AVC配置、IDR和时间轴；check-splice.py验证候选的尾视频包、完整音频包、PCM、边界及解码，通过后才成为video.mp4。输出存在时拒绝覆盖，避免无意替换已验文件。V2原片作为显式冻结输入保留。

## 实际检查

UI小样23个状态、首镜连续片、0/60/120/150/236/237及去掉题名后的功能区经过独立检查；237帧PNG与V2第二镜首帧字节相同。正式成片另核受影响区间，见qa-final-independent.md。

qa-splice.json证明尾2627个视频包与全部4476个AAC包（包括PTS/DTS、时长、priming和末包）不变；PCM SHA仍为e97780ba8cc1641d2731410056aa86f42c8aa6f120615783fc460d8a91221dd1。235–239帧连续，整片2864帧。23预演与24实际帧比对通过，最大平均RGB差1.8718；格式、冻结哈希及完整解码通过。细节见qa-final.md。

封面字节复用，既有22条VTT和4章不变；站点接入范围见episodes/agent-intro/site-integration.json。实际合并、Release、部署、线上完整SHA与关闭状态在issue #131收尾。

界面是合成订单8124的功能示例，没有真实模型或退款接口执行。没有新增听辨或ASR；旧音轨检查范围不因复用而扩大，实际抽帧不冒称全片实时观看或用户已认可V3。
