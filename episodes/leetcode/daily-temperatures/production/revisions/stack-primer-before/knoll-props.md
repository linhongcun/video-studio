# 制作说明 · LC.739 每日温度

阶段：内容及源码审稿，未生成配音或媒体，不可发布。内部EP35，片内只展示LC.739；计划批次首发v0.69.0，实际发布身份由root收尾。

- 唯一代码：solution.py；展示：solution.json；文章代码逐字同源。
- 真实数据：research/verify_solution.py执行唯一代码，research/trace.json保存完整事件；Main/data只安排事件顺序。
- 镜头：14镜28句4章；script.md是旁白真源，plan.json提供章节与句首术语挂词。
- 占位时序：build_draft.py只用于文稿排布；meta.provisionalTiming、pendingAudio、draft均为true，不保存伪造voice或words。
- 片尾：最后150帧完整静态Python卡，固定36字号，提示暂停；正式配音后由prepare_code_endcard.py声明真实卡起点。
- 封面：covers.json三尺寸布局，Cover.tsx绘制相同气温子例；4:3内容区位于315..1125且底边<918。
- 共享实现：TTS、整轨、起音、混音继续用episodes/_shared与episodes-codex/_shared；没有复制或修改共享算法。
- 资产：全部程序化SVG，未使用第三方图片、音效或天气服务；教学示例不代表真实预报。

后续在root授权后生成voice，做句级装配、共享铺轨和起音核对，再以真实时序独立检查连续事件与跨镜。全部写入停止后冻结输入；渲染使用flock /tmp/video-studio-render.lock与TMPDIR=/workspace/daily-tmp，再做成片与站点检查。

ASR、全片人工听辨、实际视频及封面检查在本阶段均未执行，不能记为通过。算法验证和TypeScript类型检查只支持相应范围，不替代编辑、动态或声音复核。
