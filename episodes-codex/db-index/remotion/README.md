# EP.15 数据库索引 · Remotion

本期的本地重制工程，成片读取上层目录的冻结 `storyboard.json` 和实体配音文件 `public/audio/voice.wav`。不读取、不覆盖已上线的 `episodes/db-index` 视频。

## 环境与命令

- Node.js 20+，Python 3，FFmpeg；系统中文字体 Noto Sans CJK SC。
- Chromium：当前运行环境为 `/usr/bin/chromium`，配置及脚本中显式指定。
- 在本目录运行 `npm ci` 安装锁定依赖；不依赖已清理的旧期工程目录。

```sh
npm ci
npm run stills
npm run covers
npm run render
```

`stills` 将首帧及各镜 65% 位置写入 `/tmp/db-index-stills/`；可给 `npm run stills -- /绝对输出目录`。

`covers` 在上层目录写出 16:9、4:3、3:4 的 PNG。4:3 构图内容全部位于 x315..1125，底边低于 y918；对应尺寸由 `../covers.json` 定义。

`render` 先写 `out/voice.mp4`，再通过仓库共享混音脚本，以《Wallpaper》为背景音乐混音，成片写入 `../video.mp4`。响度目标为 −16 LUFS、真峰值 −2 dBTP；实际测量见 `out/mix-report.json`。输出 1920×1080、30fps、H.264，CRF 20，并发 2。

## 数据与时间

- 镜头时长、字幕和术语时间：`../storyboard.json`。
- 配音从第 0 帧连续播放；没有隐式增加的片头或片尾时长。
- 每镜按 `id` 映射场景；`cueFrames.sentences` 为句首相对帧，`scanLabel` / `indexLabel` 为对应术语相对帧。
- 示例数据固定 8 条，订单号 7042 始终对应标识 06 的耳机订单；左右排列保持一致。
- 索引与标识的对应关系是教学结构示意，不表示物理地址、固定索引实现或真实执行性能。
- 04 镜逐行读到第 6 条匹配记录；05 镜继续读余下 2 条，符合查全部匹配记录的条件。
- 字幕来自真实句子音频边界，最多显示两行；逐字文本与旁白相同，没有伪造 ASR 精度。

最终检查以项目上层 QA 文档与预检报告为准。当前工程仅产出本地待审成片。
