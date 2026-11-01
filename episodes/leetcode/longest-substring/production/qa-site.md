# LC.3 网站接入与局部验证

- 结果：通过。站点/首发版本 0.53.0，公开标签 LC.3，内部期号23。
- 正式构建80页、29搜索索引页；现有 `check-learning-path.mjs --complete --built` 仅执行一次并通过，保留事务、Agent、策略模式与已有Release规则。
- 视频5078帧，画面时长169.266667秒；浏览器读取169.28秒，页面显示2:49。源、构建与HTTP视频完整SHA一致：`c8adbb517ccba5296a3b019cb48ea4a3695c47c861f27e325cef1ea76e342043`。
- 1440浅色与390深色的新片页：标题、LC.3、源码入口、文章、原生controls和四章节锚点正常，无脚本错误或横向溢出。
- 四章精确起点0、37.833333333333336、72.7、126.46666666666667秒，两个尺寸均实际点击seek通过。
- 36句VTT与冻结分镜逐句一致，HTTP与构建字节一致；SHA为 `0bcfb90d0e8c7eb5a74c242e6a5b88cd41490cbd3491737890b8b3db03987785`。最后cue序列化至164.267秒；精确静音卡起点为4928/30=164.2666666667秒，差异来自毫秒舍入。
- 实际开启CC：旧旁白段activeCues=1；166秒代码卡activeCues=0，约1秒静音播放与暂停后仍为0。完整Python卡已实际截图查看；卡片150帧/5秒。
- LeetCode系列两期按LC.11→LC.3排列；首页新卡、系列筛选2条、RSS LC.3条目和正确Remotion源码入口均通过。

实际截图：

- /tmp/longest-substring-site-qa/complete-python-frame-1440.png
- /tmp/longest-substring-site-qa/lc3-player-1440-light.png
- /tmp/longest-substring-site-qa/complete-python-frame-390.png
- /tmp/longest-substring-site-qa/lc3-player-390-dark.png

范围：仅新增课程1440/390局部验证与既有回归一次，未重复旧课程响应式矩阵、全片听辨或算法验证。本地GitHub Releases获取仍使用既有外链降级，线上Release与更新日志另行核验。
