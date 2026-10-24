# EP.22 / v0.50.0 发布记录

本期是Agent系列A01概念入口：同一笔合成退款咨询，展示请求、程序执行、结果回传与下一步选择。20镜40句、5章、5420帧，约3分1秒。只查询与给建议，不执行真实退款。

## 固定发布产物

- 站点：[EP.22](https://linhongcun.github.io/video-studio/episodes/agent-intro/)。
- Release：[v0.50.0](https://github.com/linhongcun/video-studio/releases/tag/v0.50.0)。
- 制作与线上核验的完整收尾记录：[issue #131](https://github.com/linhongcun/video-studio/issues/131)。本文件不预写未执行的线上结果；实际合并SHA、部署run、线上GET核验与关闭时间保存在该issue。
- 最终视频：11,999,892字节，SHA-256 44b21f36f6b99b4106141548a6bbc70c7556a394e4f1e819949b0e2af9be9b9c。
- 音轨：dd94b8b2963f099122a3e81d2bc066f18ff158ad9504c70cc2af291ca0360022。
- 最终分镜：2e29685585bbab493b3f44adcc60d3de4d7bc55b1556e7b22e4038df514eb469；171项冻结输入见source-sha256.json。

## 已执行的本地验证

媒体格式、完整解码、−16.0LUFS/−3.7dBTP、冻结输入与配音原位放置通过。73幅带字幕预演与74个实际MP4帧比对通过；独立查看18张正式MP4全分辨率图，无阻断。干净npm ci、TypeScript、静帧和正式站点构建通过。

源/站点/dist视频完整SHA一致。40条VTT精确采用分镜边界，5章锚点与真实frame/fps对应；浏览器全部实点，最大定位误差0.004283秒，桌面与390px手机无横向溢出或媒体错误。详见站点site-integration.json。

未执行逐字ASR、句内字级对齐或全片人工听辨，不将上述检查写成用户已观看认可。具体范围见qa-final.md、qa-final-independent.md与voice/substitutions.md。

只上GitHub站点，不进行抖音、B站或视频号新发；后续由用户分批安排其余选题。
