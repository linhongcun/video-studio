# 从模板开一期

先读仓库根上的 [AGENTS.md](../../AGENTS.md)、[docs/RULES.md](../../docs/RULES.md) 和 [docs/pipeline.md](../../docs/pipeline.md)。本目录目前只有这份说明，没有可复制的 Remotion 工程。

## 当前授权范围

按 [docs/RULES.md](../../docs/RULES.md) 的 STATUS 推进用户交办或已确定的选题。2026-10-24 用户已持续授权：做好并完成检查后可自主合并 GitHub 主干、发布 Release、部署 Pages，收到反馈再修改重发，无需每期等待 widget 批准。资料、动画动态复核、时序、媒体和线上完整 SHA 检查继续执行，能力限制如实记录；平台新发须另行明确授权。

## 最短路径

先按根AGENTS的“开工前同步”检查工作区并同步最新主干，记录基线、删除/移动和依赖变化，再复制现行工程。当前机的旧node_modules缓存或软链不代表删除后的工程仍可从零构建；至少在保留的当前制作目录按锁文件安装依赖，其他新期再共享该有效位置。

参考当前制作工程 `episodes-codex/db-lock/`、`episodes-codex/db-transaction/`（已认可的第二版），以及本轮各期 README。创建 `episodes-codex/<slug>/`；站点目录仍为 `episodes/<slug>/`。只复用配音、冻结和渲染基础设施，按本期主题重新设计动作，镜数与时长不照搬前一期。

1. 实际读取核心公开资料，按 [docs/research-template.md](../../docs/research-template.md) 记录主张、访问日期和边界。先确认观众需要的前置概念；术语与支线按本期范围取舍。
2. 编写 `script.md`、`article.mdx`、`pronunciation.md` 和 `visual-direction.md`。同一对象、渐进揭示，让动作解释因果；先做关键连续过程的小样，再展开全片。用当前期的脚本结构，旧20镜EP.14仅作为历史范例。
3. 生成本期 `storyboard.json`、`covers.json` 和 `knoll-props.md`。结构参照 [分镜字段](../../docs/storyboard-schema.md)，画面与封面依当前 [RULES](../../docs/RULES.md)。不要因旧组件存在就恢复假应用窗或密集信息常驻。
4. 用共享 `episodes/_shared/voice/` 的 prep、gen、build 等真实脚本生成冰糖配音、比较候选并保留 picks。按本期组装脚本写入真实句级区间，使用共享起音与 `place_v2.py --mode whole`；public/audio/voice.wav 是实体副本。ASR或听辨未执行时如实记录，不把字符兼容包络当作逐字识别，也不伪造共享自检结果。
5. 完成预检与独立动态复核，停止写入后冻结实际输入（含选中takes、共享实现、全部渲染源码）。参照本轮 `http-request/freeze.py --verify` 等只读核对方式，在编码前后核对同一份清单。需要修订时先取消本期排队或编码，再检查、重新冻结和渲染。
6. 按当期 `remotion/package.json` 的真实脚本安装、类型检查、生成封面并渲染。完成完整解码、媒体指标、实际编码中间态及跨镜接续复核，记录执行者、具体范围和能力边界。
7. 将检查通过的同一份媒体接入站点，保留历史元数据并设置 `sourcePath` 指向本期 Codex 工程；文章章节锚点、真实章节起点与冻结字幕均须构建及浏览器核验。按 [publish.md](../../docs/publish.md) 合并、Release、部署，核对线上完整 SHA 后关闭本次制作 issue，更新案例记录。GitHub 已有持续授权，平台发布另行授权。

历史 EP.14 的20镜/5152帧回归输入固定在 `episodes/_shared/tests/fixtures/`，旧制作说明保留在 `docs/examples/`；不要用已更换为新片的 live 站点目录重跑旧golden。

算法题的顺序为题意→入手分析与选择依据→方法名称→完整过程→5秒Python卡。独立审稿分别复述“题目要什么”与“为何选择此法”，不能把两项合成一个题意检查；无需固定先讲暴力。见L034。
