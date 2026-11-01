# EP.17 MySQL视觉修订

当前制作入口：`episodes-codex/db-lock/remotion/src/mysql-style/index.ts`，范围为MySQL 8.4 · InnoDB。系列显示名为MySQL，内部database与旧链接保留。

本修订读取原分镜、模型、字幕与配音时序，正文改用墨绿/薄荷绿家族，原参考资料题名与机构署名保持。发布稿快照为本目录`article.mdx`；旧制作稿、原src及旧冻结清单不改写。

正式MP4为`episodes/db-lock/video.mp4`，SHA-256：`31b9cd29e376f42e72676fdfca5fc90b4ef8352190f44488dd9e740cb0c36f6f`，3607帧（30fps），正文3457帧后追加150帧参考资料。完整基线AAC载荷、时间戳与解码PCM相同。`baseline-publication.json`记录旧发布身份，`baseline-audio-check.json`记录全音轨核对，`source-sha256.json`为本轮独立输入。

从仓根按[共享入口](../../../_shared/mysql-video/README.md)执行预检、冻结、渲染与只读验证。恢复旧音轨时必须按baseline-publication的Git提交及SHA提取，不能以当前新版MP4替代。

实际终审、网站检查与发布状态见[本轮记录](../../../../docs/archive/2026-10/mysql-video-style/README.md)。本轮未重新录音、未进行新ASR或全片人工听辨，不将原研究日期改成新的官网实读。
