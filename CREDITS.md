# Credits

## 背景音乐

视频（完整版）使用：

"Wallpaper" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
http://creativecommons.org/licenses/by/4.0/

- 曲目页面：https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100843
- 文件：`episodes/_shared/music/Wallpaper.mp3`（未改动原曲；混音时以固定音量（比旁白低约 12dB）铺底并做淡入淡出，见 `episodes/_shared/music/mix_bgm.py`）

## 其他

- 配音（第一期）：edge-tts（zh-CN-YunxiNeural）

## 配音（第二期《HTTPS 为什么安全？》）

仅第二期旁白使用本地开源语音合成，音色 `zm_yunxi`：

- **Kokoro-82M v1.0**（hexgrad）— 权重 Apache License 2.0：https://huggingface.co/hexgrad/Kokoro-82M （v1.0 发布于 2025-01-27）
  - 说明：据其模型卡，训练数据为宽松许可/无版权音频，**其中包括由大型厂商的闭源 TTS 模型生成的合成音频**；另含 CC BY 数据 Koniwa `tnc`（CC BY 3.0）与 SIWIS（CC BY 4.0）。我们知悉并接受这一数据来源上的不确定性。
- **sherpa-onnx**（k2-fsa）— Apache License 2.0：https://github.com/k2-fsa/sherpa-onnx ，用于在 CPU 上运行 Kokoro（打包模型 `kokoro-multi-lang-v1_0`）
- 获取方式：`bash episodes/_shared/tts/fetch_kokoro.sh`（下载模型并校验 SHA-256，模型文件不进仓库）；合成：`python3 episodes/tts_timing.py episodes/https --engine=kokoro --speed=1.18`
- 动画：Remotion，代码生成；音效为代码合成
