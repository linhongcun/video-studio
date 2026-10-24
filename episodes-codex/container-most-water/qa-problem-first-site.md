# 题意优先开头：网站局部复验

- 最终站点版本0.54.2；firstRelease保持v0.49.0。首轮0.54.1实测数据在JSON中原样保留。
- 首轮构建82页、29索引页；当前learning-path完整检查按约定仅执行一次，通过，包含新版学习方向和内容索引导航。
- 1440单尺寸：标题、原生controls、4章节精确起点与实际seek通过；浏览器媒体时长224.469秒。
- 44句新VTT文本与每条起止帧和新SB一致（毫秒序列化容差）；SHA为 `3623191215620ca66a070e458765831cf9029014a8cbc78ce79c5f77794b7b3c`。
- 末卡开始于219.466667秒，仍150帧/5秒；CC showing时activeCues=0，可暂停。
- 实际查看前两镜浏览器解码帧，先说明输入、任务、约束和返回结果。

## 总时长显示边界修正

- LC3首轮页面显示2:51：170.966667秒先舍入到一位小数变为171.0，导致显示多一秒。主任务将computeChapters改为保留精确finalFrames/fps。
- 修后仅重构建一次并局部复验LC3：页面显示2:50，原生浏览器时长170.986秒；保留新学习站设计。未重跑已通过的两页seek、字幕、LC11或完整learning-path。

实际截图：

- /tmp/leetcode-problem-first-site/container-most-water-opening-01.png
- /tmp/leetcode-problem-first-site/container-most-water-opening-02.png
- /tmp/leetcode-problem-first-site/container-most-water-paused-code-card.png
- /tmp/leetcode-problem-first-site/container-most-water-new-learning-site-1440.png

范围：只做两页1440局部检查和一次显示修正复验，沿用既有390与算法证据；不声称全片人工听辨。本地Release读取采用既有外链降级，联合线上核验另行执行。
