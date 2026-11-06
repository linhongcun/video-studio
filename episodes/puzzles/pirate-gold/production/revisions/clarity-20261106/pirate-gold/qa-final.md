# P09 清晰度修订验收

本地制作与站点接入已通过；GitHub发布与线上身份在部署后另记。

- 保留原14镜28句、4801帧正文及150帧资料列表，4951帧／165.033秒；1920×1080、30fps、limited BT.709。最终视频SHA-256：`3e23ce93a913352e7ffd743af4548d571d8ddb2b6276e908a5291426f109b09b`。
- 164项实际输入冻结，审查的Main／model／分镜与本轮编码输入逐项同SHA；原制作目录跟踪文件及旧冻结未改。见source-sha256.json、qa/historical-preservation.json。
- 类型、来源、句级字幕／音轨时序与整数模型核对通过。原WAV字节与正式音轨完整解码PCM均与旧发布版完全相同，不新增TTS。见qa/audio-preservation.json。
- 独立无字幕动态复核先拦截残影、抢先提示与叠字，修后39时点、2字幕帧、两段短片及05定向7帧通过；旧失败未覆盖。见qa/clarity-preflight-final.json。
- 实际MP4独立35点审图覆盖14镜、四次通过边界、3/5号0→1、4号1=1反对、98/0/1/0/1、字幕和资料首尾；原生尺寸另看6帧。见qa/final-media-independent-visual.json。
- 默认编码检查和资料入口复核通过：完整解码、全帧时间戳、AAC包及原正文帧保持，响度−16.0 LUFS、真峰−3.7 dBTP。见qa-encoded-media.json及reference-appendix-media-check.json。
- 文章正文及引用不变，3000／4365帧重新以明确709→601矩阵导出JPEG，主代理实际看过两图。站点构建、28条VTT和播放器HTML绑定通过，见qa/publication-stage.json、qa/article-image-export.json和qa/site-build-check.json。

本地目录检查最初被迁移前的未跟踪node_modules缓存影响；仅临时移开该缓存运行原检查器，65期／11系列通过后立即还原，未改检查器或跟踪数据。全仓密钥扫描仍有282项未改旧MQ材料命中，本轮变更按相同表达式无命中；原失败与本轮范围均保留，见qa/layout-check.json和qa/secret-scan-task.json。

限制：本轮未作全片实时观看、逐字ASR、全片语义听辨、浏览器交互／全屏或实体手机实测。声音与时序沿用且完整PCM相同；播放器共享实现未改，本次网站核对限构建、HTML和实际媒体/配图，线上将核完整HTTP资产身份。不预记用户观看认可或学习效果。
