# Redis应用场景当前视觉修订

正文及资料页沿用Redis跳表的冷银灰、Redis红、石墨文字与原始标记；新三比例封面使用redis-covers-v2。实际源为同一Remotion目录的`src/redis-style/index.ts`，保留原模型/分镜/配音与历史冻结，旧源码与原生产封面不覆盖。

`source-sha256.json`记录本轮原源及真实import闭包、当前发布文章快照、已保留来源、字体、编码与颜色转换命令/版本。新正文先实际转换为有限范围BT.709再复制完整原AAC，资料页同编码；像素经有损转换，完整声音和原presentationPTS保持。`baseline-publication.json`按固定Git提交与完整SHA绑定原发布片，`article.mdx`保留当前发布文稿原字节，正式截图从最终视频生成。

从仓根使用 `python3 episodes-codex/_shared/redis-cache-video/render.py cache-consistency`，默认只打印计划；`--render`使用已冻结输入，已有成片只读核对`--verify`。不运行旧prepare/TTS/混音或旧封面命令覆盖本轮产物。实际制作、独立检查和发布状态见仓库`docs/archive/2026-10/redis-cache-style/`，不预记ASR、全片听辨、真机或用户新观看结论。
