# Redis 跳表当前发布媒体

当前成片由原`redis-style`视觉正文做实际pc601→tv709像素转换，再追加同编码资料页。正文4557帧、资料150帧、总4707帧；完整AAC包/PCM和全部原presentationPTS保持。新清单独立绑定83项输入，原视觉、历史冻结与第一轮缺少完整颜色标记的失败结果保留。

入口为仓根执行 `python3 episodes-codex/_shared/redis-video-bt709/render-v2.py`，默认只打印计划；`--render`使用已冻结输入，已有最终片只读核验。实际Remotion源仍在现行层高修订的`src/redis-style/`。本次像素经过有损颜色转换，不能称作与转换前逐像素相同。

恢复新清单所需的三个ignored生成媒体时，使用本轮交付分支中的`redis-video-style-production-inputs.zip`，按ZIP内仓根相对路径解压并逐项核对完整SHA；[清单](../../../../docs/archive/2026-10/redis-video-style/production-inputs-manifest.json)和最终固定下载提交在[任务记录](../../../../docs/archive/2026-10/redis-video-style/README.md)。原基线视频按`redis-style/baseline-publication.json`的Git提交恢复，其他输入与字体均依新清单核对。

`render-result.json`、`normalization-check.json`及参考资料回执记录实际媒体身份、全部时间戳、声音和附录保真。当前公开副本为`episodes/redis-skiplist/video.mp4`。网页取色与可读性、发布实际状态另见任务记录，不预记ASR、全片听辨、真机或用户新观看结论。
