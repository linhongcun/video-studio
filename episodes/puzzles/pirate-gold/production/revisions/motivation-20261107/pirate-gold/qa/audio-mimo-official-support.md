# 新04两句音频理解调用依据

核验时间：2026-11-07 UTC。只为核对既有的两句新配音，不生成TTS。

官方页：[小米MiMo开放平台：音频理解](https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/multimodal-understanding/audio-understanding)。通过公开网页搜索与正文提取工具实际读取，页内显示更新时间2026-04-22。

读取到的相关原文与示例：

> 当前仅支持 `mimo-v2.5`，`mimo-v2-omni` 模型。

> Base64 编码传入：将音频转换为 Base64 编码字符串后再传入。

> 请在 Base64 编码前携带前缀：`data:{MIME_TYPE};base64,$BASE64_AUDIO`

文档示例端点为 `POST https://api.xiaomimimo.com/v1/chat/completions`，使用 `api-key: $MIMO_API_KEY` 和 `Content-Type: application/json`。用户消息的音频项是 `{"type":"input_audio","input_audio":{"data":"data:{MIME_TYPE};base64,$BASE64_AUDIO"}}`，另附文本任务。支持格式列有WAV；Base64单音频上限50MB。本次两段实际输入分别约1.02MB与1.19MB的PCM WAV；只送入音频及通用逐字转写指令，没有送入脚本、字幕、预期内容或参考转写。

同次搜索还找到了官方语音识别页面 `https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/Speech-Recognition`，但正文提取返回 `empty_content`，所以没有猜测或调用该页面未读到的模型、端点或参数。

执行前实际读取 `/etc/codex/network-policy.json` 与云环境状态：网络为restricted，`api.xiaomimimo.com`在已配置允许列表，策略状态`enforced`、观察状态当前，`MIMO_API_KEY`为`ready`。请求沿用继承的代理、CA与既有环境变量；没有输出密钥，没有申请新权限或更改网络。没有安装/下载ASR模型；当前默认Python无whisper、faster_whisper、transformers、vosk或torch模块，常用workspace模型缓存也无模型。

实际API结果保存在 `audio-asr-04-responses.json`，只保留响应状态、错误或文本、用量与输入SHA等必要证据，不保存请求音频Base64或认证头。两次`mimo-v2.5`原始400均保留；后备尝试严格限定官方另列的`mimo-v2-omni`，先第一句，失败即停止；只有第一句成功才请求第二句。

官方文档声明不等于该账户当前实际可用；最终以请求证据为准。模型转写即使成功也不等于人工听辨、声调检查或逐字时间对齐。
