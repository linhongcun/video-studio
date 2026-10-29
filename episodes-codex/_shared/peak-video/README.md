# 高并发、高可用、高性能系列正文视觉入口

EP.11限流、EP.12幂等、EP.13熔断与EP.14降级沿用现有封面的深青蓝、亮青、暖黄及Noto字体。共享`style-v1.json`保存独立配色、字体与原封面样式SHA，不读取增长中的封面目录。真实EP、场景标识与原机制动作由单集传入。

新入口为各期`remotion/src/peak-style/index.ts`，新媒体、当前发布文章快照与冻结放在`revisions/peak-style/`。旧入口、模型、分镜、台词、字幕、配音和历史清单保留原字节；不运行prepare、TTS或混音。四期均为1920×1080、30fps：

| slug | 正文帧 | 资料帧 | 总帧 |
| --- | ---: | ---: | ---: |
| rate-limit | 3271 | 150 | 3421 |
| idempotency | 2998 | 150 | 3148 |
| circuit-breaker | 2926 | 150 | 3076 |
| degradation | 3134 | 150 | 3284 |

```bash
python3 episodes-codex/_shared/peak-video/render.py rate-limit
python3 episodes-codex/_shared/peak-video/render.py rate-limit --font-inputs
node episodes-codex/_shared/peak-video/qa.mjs rate-limit --out-dir work/peak-video-style/preflight/rate-limit
python3 episodes-codex/_shared/peak-video/render.py rate-limit --freeze
python3 episodes-codex/_shared/peak-video/render.py rate-limit --render
python3 episodes-codex/_shared/peak-video/render.py rate-limit --verify
```

其余三期替换slug。默认只输出计划；正式编码前先完成来源检查、逐镜0/.5/.98实际DOM与PNG预检及独立审查，再写入新清单。QA可用`--frames 0,100`及`--scale 1`定向复查，从实际`data-peak-canvas`矩形校准字幕与文字位置，不修改生产动画或注入审计钩子。首次冻结前允许尚未写入baseline-publication；已有清单须先只读验证，不能改写追认。

原发布基线从固定Git提交恢复至`work/peak-video-style/baseline/<slug>.mp4`，核对完整SHA与发布回执；冻结时将原元数据和回执保存为`baseline-publication.json`。新无声Remotion正文的实际full-range BT.601画面经明确记录的pc601→tv709像素转换、yuv420p及逐帧setparams归一化。确认流和首个实际解码帧的range/matrix/primaries/transfer后，流拷贝完整原AAC；资料PNG编码采用相同limited BT.709。

完整原AAC包载荷、PTS、DTS、duration与解码PCM必须相同；原发布片和最终片全部presentationPTS/duration按精确分数逐帧相同。既有追加引擎完整解码新正文和最终片，证明追加资料没有改变正文帧或时间。当前附录保留资料原题和作者/机构，每页最多四项、默认五秒。

新清单绑定原源码及实际import闭包、原制作文章、当前发布文章及其快照、原参考证据及其保存文件、旧冻结、原封面样式、实际字体文件、编码命令和运行工具版本。媒体核心和旧附录引擎只在私有函数命名空间复用，不改其文件或模块全局。已有来源日期保持；本轮官网GET、人工听辨、ASR、真机及用户观看结论仅在实际执行后另记。浏览器取色、全屏、字幕与文章回看须另作真实检查，不能从编码标签或截图代推。
