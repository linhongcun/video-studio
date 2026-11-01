# height-choice 最终媒体 QA 准备

状态：最终源已选定并实际执行 --prepare-plan；151项完整冻结已核验，尚未执行正式成片检查。当前正文4557帧、31张正文计划图，加正文末和一页资料首中末预计35张。

所有输出仅本revision。旧flat/clear-parts目录、已发布媒体与历史QA不改写。当前正式身份为Main390ad829、SB64e7a5ce和新WAVe63140e9；帧号已按实际新句窗计算。“层高”cue为07局部1帧，reset在局部221帧，预分配渐显起于局部268帧、完整态在326帧。

声音分别处理17句精确raw/48k/request复用和3句新选中take（07两句、09首句）。本轮必须具备正常fresh qa-voice/qa-voice-takes/必要pause-review和current input-provenance；旧审计只保留历史身份。fresh全局归一化可以改变17句normalized PCM的gain，不要求旧PCM或整轨字节相同。

关键画面以新Main与新SB选取：

- 保留02结束→03转场卡→无查询游标的真实结构渐显→04同55重查。
- 真实前进/原40下降/底层50停位。
- 新07独立height1.after：55仅底层端口、50→55→60完成，上层仍40→70、全跳表仍两层。
- 实际“层高”起音邻帧；第二句从完整height1反例明确reset到共同before：8个原节点、无55。
- 预先选2层的新55在未接入状态渐显，不能表现为已接好的1层节点升层；07→08连贯。
- 原四次指针写邻帧与09新因果提示；最后图连续且有序。
- 实际正文末、新appendix起点及每页资料首/中/末，title-author原题机构正确且无字幕残留。

正式执行保留完整decode、全PTS/H2641080p30、AAC payload/PTS/DTS/duration/size、全PCM、当前新源波形/逐句漂移/固定延迟/响度数值检查，原checker与阈值不变。收到最终冻结和完整MP4 SHA后才运行；实际decoded PNG必须真正看过再写视觉gate。没有ASR、全片人工听审或实时全片观看宣称。

两个入口AST/--help及实际fresh source适配器已通过只读准备核验。实际发生4次TTS生成，最终选中3句：07-1取d、07-2和09-1取c；17原声源逐项SHA核验通过。没有媒体decode、ASR或听辨执行。正式检查继续等待制作方成片完成通知与完整MP4 SHA。
