# Redis 缓存应用场景视觉入口

当前两期为EP.08服务端缓存与EP.09缓存一致性，正文与资料页沿Redis跳表的冷银灰、Redis红、石墨文字和原始标记。字体/配色/标记为不可变style-v1快照，不读取增长中的封面catalog；真实EP、题名和场景标识随单集传入，旧系列身份和冻结仍保留历史字节。

每期新视觉入口为`remotion/src/redis-style/index.ts`，新媒体和冻结独立放`revisions/redis-style/`。原数据、模型、分镜、台词、字幕与源码不覆盖；完整发布基线AAC直接复用，不运行prepare/TTS/混音脚本。EP.08正文3491帧、资料150帧，总3641；EP.09正文3464帧、资料150帧，总3614，均1920×1080/30fps。

```bash
node episodes-codex/_shared/redis-cache-video/qa.mjs server-cache --out-dir work/redis-cache-style/preflight/server-cache
python3 episodes-codex/_shared/redis-cache-video/render.py server-cache --font-inputs
python3 episodes-codex/_shared/redis-cache-video/render.py server-cache --freeze
python3 episodes-codex/_shared/redis-cache-video/render.py server-cache --render
python3 episodes-codex/_shared/redis-cache-video/render.py server-cache --verify
```

对cache-consistency使用相同命令替换slug。默认只输出计划；正式编码前先逐镜0/.5/.98实际DOM/PNG预检与独立审查，再首次写入新清单。QA支持`--frames 0,100`与`--scale 1`定向复查，不改原动画或加入生产审计钩子。实际字体解析为冻结输入；已有清单只读核对，不能重写追认。

从原发布Git提交恢复基线至`work/redis-cache-style/baseline/<slug>.mp4`，先核对完整SHA与替换前baseline-publication.json。新无声Remotion画面输出full-range BT.601，经清单中明确记录的真实pc601→tv709像素转换、yuv420p与逐帧setparams，确认range/matrix/primaries/transfer后再流拷贝完整原AAC。资料图仍由已验证原题/机构排版生成，只将PNG编码改为同一limited BT.709。没有给原片重贴标签，也没有把转换后画面说成原像素相同。

完整原AAC包载荷/PTS/DTS/duration与解码PCM必须相同；原发布片与新最终片的全部presentationPTS/duration按精确分数逐帧相同。追加引擎完整解码新正文/最终片，证明正文帧与PTS不被附加资料改变。实际网页取色、全屏及字幕/文章回看另作独立检查，不能凭ffmpeg截图宣称浏览器颜色正确。

新冻结绑定原源码/import闭包、当前制作/发布文章与快照、实际保存的来源证据、旧清单、原标记来源/许可、实际字体和编码命令/工具版本。媒体核心与旧Redis/趣味推理引擎均不改写，只在私有函数命名空间复用。原文实读日期保持，不预记本轮官网GET、全片听辨、ASR、真机或用户新观看结论。实际制作与发布状态写入本轮任务归档。
