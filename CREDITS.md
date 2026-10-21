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

## 配音（第二期《HTTPS 为什么安全？》、第三期《输入网址后，怎么找到服务器？》、第四期《网站怎么记住你已经登录？》、第五期《网站离你那么远，为什么还这么快？》、第六期《一台服务器忙不过来，怎么办？》）

第二期、第三期旁白使用 **Xiaomi MiMo TTS**（云端 API，模型 `mimo-v2.5-tts`，预置音色「冰糖」），北京小米移动软件有限公司提供：

- 接口文档：https://mimo.mi.com/docs/zh-CN/api/audio/tts （页面更新于 2026-07-17）；计费：语音合成使用指南标注「**限时免费**」：https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5 （页面更新于 2026-07-15），即非永久免费，以平台公示为准。
- 适用条款：《Xiaomi MiMo 服务协议》https://mimo.xiaomi.com/legal/terms-zh （生效日期 2026-06-15；官方页面需 JS 渲染，条文经第三方存档 https://termshub.cn/public/version/6675 核对，当前版本记为 2026-06-26），2026-10-12 查阅。
  - 说明：该协议**没有明确授予生成音频的商业使用权，也没有明确禁止**；第 5.1 条仅约定模型及其参数、算法等知识产权归小米，第 3.13 条约定计费与免费额度以平台公示为准、小米可调整。（另：《Xiaomi MiMo 桌面版服务协议》https://mimo.xiaomi.com/legal/service-agreement-zh 第 3.1 条限定桌面版"为非商业目的"使用，但该协议针对桌面软件，不是 API。）**我们于 2026-10-12 知悉并接受这一灰区。**
- 合成：`python3 episodes/tts_timing.py episodes/https --engine=mimo --gap=0.28`（`episodes/_shared/tts/mimo_say.py`，API 密钥只从环境变量或仓库外文件读取，不进仓库）
- 第三期合成：`python3 episodes/tts_timing.py episodes/dns --engine=mimo --gap=0.28`（同一模型与音色「冰糖」，条款情况同上）；第三期背景音乐同为 Wallpaper（固定音量，比旁白低约 12dB，1s 淡入 / 2s 淡出，-16 LUFS）
- 第四期合成：`python3 episodes/tts_timing.py episodes/cookie-session --engine=mimo --gap=0.28`（同一模型与音色「冰糖」，条款情况同上；读法表 `episodes/cookie-session/tts_lexicon.json`）；背景音乐同为 Wallpaper（固定音量，比旁白低约 12dB，-16 LUFS）
- 第五期合成：同一模型 `mimo-v2.5-tts` 与音色「冰糖」，条款情况同上（读法表 `episodes/cdn/pronunciation.md`）；背景音乐同为 Wallpaper（固定音量，比旁白低约 12dB，-16 LUFS）
- 第六期合成：同一模型 `mimo-v2.5-tts` 与音色「冰糖」，条款情况同上（读法表 `episodes/load-balancing/pronunciation.md`）；背景音乐同为 Wallpaper（固定音量，比旁白低约 12dB，-16 LUFS）
- 动画：Remotion，代码生成；音效为代码合成

## 地图数据

- 第五期世界地图底图：Natural Earth 1:110m Land（`ne_110m_land`），公有领域（public domain），https://www.naturalearthdata.com/about/terms-of-use/ ；文件见 `episodes/cdn/remotion/data/ne_110m_land.geojson`、`episodes/cdn/remotion/public/assets/ne_110m_land.svg`，转换脚本 `episodes/cdn/remotion/scripts/build-land.py`
