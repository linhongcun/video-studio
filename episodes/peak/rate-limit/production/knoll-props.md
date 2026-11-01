# 制作说明

本期工程以episode.json、script.md与visual-direction.md驱动；Main.tsx逐镜实现因果动画，非说明文字幻灯片。深色全屏canvas直接表达抽象请求、记录和状态；无假浏览器、实物设备和比喻道具。

配音只使用共享实现；术语全部位于独立句首，按共享声学起音-2帧出现。句级字幕原文不改，长句允许换行而非缩小字。分镜保持0帧原位整轨，holdFrames为0。

封面依据covers.json三个尺寸独立布局，4:3内容严格在x315..1125与y<918，水印另区。

冻结source-sha256.json包含所有实际输入及选中takes；渲染前后核对。动态与最终媒体检查见qa-motion.md和qa-final.md，未做能力不冒称通过。
