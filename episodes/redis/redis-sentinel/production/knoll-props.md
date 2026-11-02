# EP50 Sentinel 制作说明

使用本期独立真实配音与13镜/26句分镜，正文4439帧、147.9666667秒；默认尾随两项原题/Redis机构资料共150帧，最终帧数以正式媒体回执为准。cold-silver/Redis-red来自不可变redis-video/style-v1.json，正文真实EP50；封面由新redis-covers-v3生成，实际字体/图形/安全区及SHA见covers/cover-style.json和covers.json，不复用旧EA封面身份。

Main.tsx直接读取本期storyboard.json、model.json和model-timing.json。41个有限教学阶段：五已知Sentinel固定，故障确认2与多数授权3分开；授权票只从Sentinel到执行者候选；投票条件对照显式回到投票前；priority0筛选先于进度比较；晋升命令与INFO角色观测分步；客户端向Sentinel查地址后直连Redis。角色、票数、选中状态来自同一模型，移动消息不附带横穿节点的文字。

节点坐标跨镜稳定。第一镜是问题预览，第二镜明确回到故障前部署；第08是独立条件对照；第12是异步复制窗口的独立边界示例，旧主离线字节仍保留。模型检查与真实进程实验分开，实际运行的传播视图尚未完全收敛不能写成全体一致实测。

音轨通过未修改的shared prep/gen/build/assemble/place工具产出；选中a候选和原rawWAV/请求文本保留。声学测量与来源/拼接结构不等于ASR、全片人工听辨或用户观看结论。烧录字幕独立于模型运动层，不跨入无旁白资料区。资料追加器复用不可变布局/媒体引擎，选本期冷银灰配色，并对资料视频同样执行真实limitedBT709编码。

最终媒体在根任务负责人完成独立动态闸门后冻结与编码；全片render-final.sh持有/tmp/video-studio-render.lock，不能发布remotion/out/body.mp4代替video.mp4。正式编码前后均只读核对同一输入清单；有变更先停任务并重新审受影响区间，不重写旧清单认可旧编码。
