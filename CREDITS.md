# Credits

## 背景音乐

视频（完整版）使用：

"Wallpaper" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
http://creativecommons.org/licenses/by/4.0/

- 曲目页面：https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100843
- 文件：`episodes/_shared/music/Wallpaper.mp3`（未改动原曲；混音时以固定音量（比旁白低约 12dB）铺底并做淡入淡出，见 `episodes/_shared/music/mix_bgm.py`）

## 配音

现行重制旁白使用 **Xiaomi MiMo TTS**（云端 API，模型 `mimo-v2.5-tts`，预置音色「冰糖」），北京小米移动软件有限公司提供：

- 接口文档：https://mimo.mi.com/docs/zh-CN/api/audio/tts （页面更新于 2026-07-17）；计费：语音合成使用指南标注「**限时免费**」：https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5 （页面更新于 2026-07-15），即非永久免费，以平台公示为准。
- 适用条款：《Xiaomi MiMo 服务协议》https://mimo.xiaomi.com/legal/terms-zh （生效日期 2026-06-15；官方页面需 JS 渲染，条文经第三方存档 https://termshub.cn/public/version/6675 核对，当前版本记为 2026-06-26），2026-10-12 查阅。
  - 说明：该协议**没有明确授予生成音频的商业使用权，也没有明确禁止**；第 5.1 条仅约定模型及其参数、算法等知识产权归小米，第 3.13 条约定计费与免费额度以平台公示为准、小米可调整。（另：《Xiaomi MiMo 桌面版服务协议》https://mimo.xiaomi.com/legal/service-agreement-zh 第 3.1 条限定桌面版"为非商业目的"使用，但该协议针对桌面软件，不是 API。）**我们于 2026-10-12 知悉并接受这一灰区。**
- 合成入口：`episodes/_shared/tts/mimo_say.py`，整轨构建与选段工具在 `episodes/_shared/voice/`；具体音轨、读法和送模文本记录在 `episodes-codex/<slug>/pronunciation.md` 与 `voice/substitutions.md`。API 密钥只从环境变量或已忽略文件读取，不进仓库。
- 各期背景音乐同为 Wallpaper，混音与署名同上。历史版本的制作记录可从 Git 历史追溯，不作为当前运行命令。
- 动画：Remotion，代码生成；音效为代码合成

## 地图数据

- 第五期世界地图底图：Natural Earth 1:110m Land（`ne_110m_land`），公有领域（public domain），https://www.naturalearthdata.com/about/terms-of-use/ ；当前地图轮廓实现见 `episodes-codex/cdn/remotion/src/landPaths.ts`，来源元数据与转换代码在 `episodes-codex/cdn/assets/map/`，受本期冻结清单保护
