# EP40 参考资料显示策略适配

已通过有界元数据保留检查，待独立复核及新资料卡预览。采用 `title-author`，每页最多4项、默认5秒；本期2项均显示 Redis 机构，共150帧。引文、定位、版本和核验日仍保留在研究记录，视频列表只显示原题和机构。

旧 full script `704f43aaf70d731b59b1d5bc36e124fdd6c03107d5baf0ff6ea2915391a76169` → 新 `24f4e02ec755765f571283f88e58018211a631e45666029a1145d135b3706b2c`。只改非口播前言的一处片尾说明，20句旁白与全部 TTS 请求字节不变。旧 script、SB66da、words、来源记录与旧审批原字节在归档中。

新 storyboard `ed3c07262aaa9d630c87584b41ade69b4e149220bcfc361cd1618958bb9a2d4f`，唯一变动是 `meta.timingSource`；10镜完整 scenes、所有句窗/cue/字幕、封面、4482帧、30fps及1920×1080完全相同。共享 assemble 原始输出也保留；其中10个历史 shot.timing.source 被有界恢复为真实原始704f生成身份，避免改写历史来源。新 words 仅改 scriptSha256。

配音及实体公开 WAV SHA 均为 `0c48b0538985b74cce8e31e8ed6f45196ae03d6b2cdc09886b26eba2b9932805`；字幕SRT及168项约束文件逐字节相同。未重新 TTS、build、铺轨、冻结、正式渲染或发布。旧两份 TTS 审批和声轨/正文报告保留其实际旧 SHA，未改写成新 SHA 审批。

新模式来源检查、bibliography 验证、三入口语法/帮助与三层 renderer 冻结输入声明均实际通过。独立帧复现、资料卡实看和最终编码属于后续独立闸门。完整 SHA、原始快照、命令回执和字段差异见同名 JSON。
