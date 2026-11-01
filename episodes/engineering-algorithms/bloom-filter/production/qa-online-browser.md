# 布隆过滤器：正式线上浏览器smoke

结论：修正媒体读取生命周期分类后，正式canonical页面两视口smoke通过，4张新截图均已实际查看。首轮误把浏览器主动取消旧媒体读取当成产品错误的失败报告、原工具、Range/媒体事件诊断及精确工具差异均保留。没有修改产品、媒体、元数据、150项冻结输入或本地86项报告。

- 页面： https://linhongcun.github.io/video-studio/episodes/bloom-filter/ 。Release v0.71.0，Release后Pages run40249567063成功后才执行。
- 实际使用继承的session代理与正常CA验证，ignore_https_errors=false，无忽略证书参数、自定义缓存头、cache-busting或自动重试。
- Chromium154，1440×1000与390×844均canonical200；真实静音1×短播放、共8次章节点击seek成功。
- 两视口各载入26条native cue；末cue结束191.366秒。精确首卡5741/30秒实际绘制5741帧并暂停，activeCues均为空，video.error均null。
- 每视口观察到3次同一canonical MP4的media ERR_ABORTED，共6次。记录具体Range、请求/取消阶段、loadedmetadata/suspend等真实事件和后续成功播放/绘帧见证，均可解释为metadata读取结束或主动seek关闭旧读取。未解释请求失败、文档/VTT/脚本/证书或页面/console错误均为0；没有全局忽略失败。
- 原题和资料主体未被原生控件遮住；390内嵌画面较小。本轮不扩写为真实手机、全片人工听辨、ASR、线上Fullscreen或教学效果认可。完整媒体SHA和其他入口的10项ordinary canonical GET由独立线上内容核验记录支持。

## 工具归档

实际执行位置仍为`/tmp/bloom-online-browser-smoke.py`；执行后才复制到`qa-tools/bloom-online-browser-smoke.py`，两者和报告中工具SHA均为`00a88f5036bb6f0ed6a5adc97c3d7ec05b2c445290ea6156791db7b03d2956a2`。没有把归档路径冒称执行原路径。

详细事件、取消次数、实际时间和4张截图SHA见qa-online-browser.json；原失败/诊断/工具差异见qa-revisions/online-browser/media-abort/。
