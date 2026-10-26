# EP40 网页QA工具准备

结论：工具已准备，语法与`--help`通过；**尚未执行浏览器检查**。未运行旧dist、未build/copy/publish，未改生产源码。

本期固定EP40 / redis-skiplist / 20条原生字幕，四章goal、search、insert、boundary的时间从实际SB推导。正文4482帧，首资料帧严格检查4482；附录时长与总片长等最终meta，不使用当前尚未接附录的SB总长冒充成片。firstRelease暂取v0.72.0，执行前由root最终确认。

本地一次运行覆盖1440桌面与390窄屏：实际1x播放、真实章节点击、20条VTT全文与边界、精确资料帧paint/无字幕、原生Fullscreen API、文章SVG、完整Python复制与滚动、四章目录、三课入口、日期/RSS。代码以本期实际43行fence为准，DOM code/data-code/clipboard全文精确一致，复用research已执行且绑定相同article/snippet的报告。复制只给隔离浏览器context剪贴板权限；代码滚动明确instant并等待双rAF再取rect。

线上工具仍只做canonical小范围smoke，继承代理与CA，无缓存绕过或自动重试。媒体取消仅在exactMP4、media、Range、ERR_ABORTED、同一seek阶段的实际seeking或preload生命周期，以及后续成功证据均齐全时分类；意外失败继续阻断。

等待root通知正式成片、freeze、publishCopy和fresh build完成后再执行。本地运行后将实际查看关键桌面/窄屏播放器、首资料帧、Fullscreen及代码截图，另写真实执行范围；在线运行再等成功部署与run ID。完整执行计划、工具SHA和当前规划输入见同名JSON。
