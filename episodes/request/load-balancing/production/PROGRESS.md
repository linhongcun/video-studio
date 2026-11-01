# EP06 制作断点（2026-10-24）

新脚本、实读调研、文章、读音、定制动画、配音和封面均完成；最终无声动态预检与补验通过，输入已停写冻结92项。总计3186帧。不要重做TTS，不要为认可旧MP4重写冻结清单。

正式编码统一批处理06→07：工具会话36415，命令`flock /tmp/video-studio-render.lock /workspace/.venvs/video-studio/bin/python /tmp/render_ep67.py`。EP06已完成正式编码与自审，SHA见render-result.json，EP12独立图审也已完成并通过，qa-final.md已归档；EP07也已完成并通过独立图审，同一批处理已退出并释放锁。该脚本逐期在渲染前后只读校验冻结输入，并要求冻结清单字节不变；npm渲染日志在本期render.log，完整解码/指标日志在verify.log。

每期媒体检查后自动调用`python3 /tmp/ep67_extract_final.py load-balancing`，从真实MP4解码关键帧到`qa-evidence/final/`并写frames.json。该步骤只产证据，不自动声明视觉/听辨通过。

恢复后先查已运行的进程、日志、video.mp4和render-result.json，不要重复开渲染抢锁。若只是排队，正常等待；Node进程名可能为MainThread。只复核已编码实际帧后更新qa-final.md并通知root及EP12组独立图审。实际正片核对02末→03首应用甲位置、05唯一分配、08两次失败后暂停、10两次成功后恢复且新请求随后进入。

已知能力边界：无逐字ASR及完整独立人工听辨。字幕采用实测句界，标签只用声学句首。站点/GitHub接入交由root，子组不改全局、不提交或发布。
