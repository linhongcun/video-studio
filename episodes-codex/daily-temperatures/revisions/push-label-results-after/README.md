# Daily push标签遮挡定向修复

真实预检在global2753/2754发现第7天36的新push标签斜穿既有答案2/4。旧源、原冻结清单、真实失败PNG和原采样来源保存在`../push-label-results-before/`，没有用新源覆盖旧证据。

仅修改Main中的isPush分支：新标记固定在目标栈槽y826，沿用原p作淡入。填充框和文字始终在y792..860，避开日期和答案行；原连接线、pop动作、事件时序、trace、script、voice、words、storyboard均未修改。145项重新冻结和类型检查通过，只有Main这一冻结项改变，详情及全文SHA见source-change.json。

按独立审查者给定范围生成10个无字幕push短窗口、31个去重起/中/末及原失败点、6个09带字幕图，未重跑常规56帧或完整core片段，未编码正式整片。实际来源和每份输出完整SHA见recheck-manifest.json，媒体在remotion/out/qa-push-recheck。

制作自查实际打开两处原失败点（有/无字幕各一）及第6天和相等补例加入中间态，答案2/4可见，实体标签不再跨结果区。此自查不能代替独立复验，正式整片仍等待独立PASS。

片根qa-motion-current.json给后续MP4比较提供16个带字幕采样：6个本轮真实新源图，10个逐帧证明不受only-isPush修改影响的旧图；每项保留真实render来源与旧Main摘要，未把整份旧Main元数据追认成新源。
