独立实际 DOM 审查通过。最终231张真实PNG各有一条Chromium DOM记录，执行64,366个断言，0失败；所有19项被绑定源在渲染前后保持一致。

检查读取真实SVG值字形、节点端口、实线/虚线、forward路径和箭头tip、实际cursor矩形与移动圆点。实际链与合法快照逐项一致，55出现时机、四写提交帧3113/3204/3560/3651和字幕窗口均核对；不导入制作算法，不使用Scene.state自证。几何容差为0.06 CSS像素，提交帧无容差。

actual路径按曲线采样核是否穿过其他节点，未把整条曲线AABB重叠当穿框。旧直线匀速假设失败与修正保留于qa-revisions/independent-checker-v1。完整数值和源SHA见qa-dom-independent.json；最终视觉和媒体范围见qa-preflight.json。
