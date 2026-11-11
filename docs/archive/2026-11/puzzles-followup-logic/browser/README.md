# P06/P10本地播放器复核

2026-11-11。当前状态：两期新媒体的实际本地浏览器复核完成。Chromium154在桌面亮色与触摸手机视口暗色中完成44项功能动作，12张截图留证；独立实际查看6张代表图，见[browser-local-v1.json](browser-local-v1.json)与[browser-visual-review.json](browser-visual-review.json)。

全局Playwright和`/usr/bin/chromium`已实际找到，Chromium版本为154.0.8037.57，无需安装依赖。`browser-check.cjs`默认只输出计划；本轮已在两期新发布资产、站点构建及preview就位后执行（实际端口4174）：

```sh
node docs/archive/2026-11/puzzles-followup-logic/browser/browser-check.cjs --execute --base http://127.0.0.1:4174/video-studio/ --run browser-local-v1
```

执行前从实际publication元数据、分镜、文章和新render-result读取时长、章节、Figure时间与讲解镜头，核对发布MP4和新修订完整SHA。P06选择12镜、P10选择03/04镜的实际时序采样，不硬编码旧时刻。两期分别检查桌面亮色与触摸手机视口暗色的真实播放/暂停、章节与配图回看、呈现帧回调、深链、原生字幕默认关闭、水平边界，以及桌面原生fullscreen进入退出。

执行记录写入同目录唯一run名的JSON及截图子目录，失败保留，后续重跑使用新run名。两期完整媒体SHA分别与新修订render-result、publication完全一致：P06为`7ee68c46527cfe4b20ad5c76eb0a5dd4f7626227401f96f9cfd4cf95096e1f2b`，7101帧／236.7秒；P10为`a8bfe657f39ff9b08688ffd410775829ef593c116deb54cdb7612b825b4e018d`，6512帧／217.0667秒。两图实际回看为P06的100／116秒、P10的87.7／156.2秒。

代表桌面fullscreen截图的说明与烧录字幕可读；手机内嵌暂停截图中原生控件遮盖底部字幕，初始页面图保留瞬时seek转圈。23项媒体请求中止均为`net::ERR_ABORTED`，实际加载、播放进度、呈现帧与跳转检查通过，未发现pageerror；不把请求中止改记为从未发生，也不把功能检查扩大为所有控件状态下字幕无遮挡。部分呈现帧回调先于seek完成，回调原始readyState/seeking照实保存；截图前另外等待seek结束与readyState至少2。

范围限本地构建站点和Chromium模拟视口；不证明线上浏览器动作、实体手机、其他引擎、全片实时观看、语义听辨或ASR。线上HTTP媒体身份由批次交付另行核验。
