# D03业务边界修订：站点工具

当前工具用于已发布D03的内容修订。`firstRelease`永久保留v0.63.0、`publishedAt`保留原日，EP31/顺序3/源码入口等身份不变。新patch仅是revision release，由根任务在最终同步main并查tag后确定；不再使用首次交付或未发布候选替换流程。

旧v0.63.0站点QA、截图日志、相关四份非生产QA工具与旧published meta，已从精确提交`5a5594fb13e1acdab28981d0bc67fb305754ebbd`逐字节归档至`revisions/business-boundary-v2/previous-site/`，原路径→归档路径及SHA见其中`archive-path-map.json`。未递归旧候选目录，也未复制整份配音/Remotion/Java生产树。旧报告不能改名成新修订检查。

媒体门之前只准备工具，不复制新MP4或构建。实际媒体通过后：

1. `python3 episodes-codex/adapter-pattern/site-integrate.py --approved --release vX.Y.Z`，需要时传实际`--updated-at YYYY-MM-DD`。保留历史首发、发布日期和身份，更新当前title/summary/updatedAt/真实帧数。复制14份检查通过同SHA的发布文件与当前source/render/mix报告，不复制WAV/PNG/制作树。D01、D02、Skills、P04核心数据及全部其他meta前后保持原字节。
2. `node episodes-codex/adapter-pattern/site-qa.cjs`：一次最终build、一次当前历史路径回归，1440浅色/390深色全部四章实际seek及短静音播放。镜数/cue数从本期config和冻结SB读取（本轮计划10镜20句），不沿用旧24句。Java卡150帧，完整加载且showing的轨道在首/中/尾均需0活动cue，实际解码后暂停导出卡帧；页面截图恢复默认字幕状态。
3. 核对原生SVG computed字号/锚点/bbox、无整页溢出、正文#java及卡片所用完整Java源/原AdapterDemo依赖链接。Java源名从java-card.json.sourceFile读取，不把节选误作完整程序。核对D01–D03目录/前后课、其他课程数据保持。当前发布页数动态读取；新Skills和Agent方向存在，已退agent-intro/agent-tool-execution仍缺。
4. 实际打开新截图后单独记准确查看范围。仅浏览器恢复且输入/构建产物指纹均未变时可`--reuse-build`；不同候选需先明确归档，不能覆盖旧文件后虚称复用原证据。
5. 根发布revision Release并完成其后Pages部署，再运行`python3 episodes-codex/adapter-pattern/site-verify-online.py`：11个普通canonical GET，完整视频流SHA不保存远端媒体；核对poster/VTT/章节/Java与源码/三期目录/系列/资料库/RSS/真实revision条目。Agent首页入口使用正确`learn/#agent`，不是series入口。报告分别保存revisionRelease、firstRelease、publishedAt和updatedAt，不把修订版本当首发版本。

本地短静音播放、包络或页面检查不代表全片听辨、ASR、用户认可或学习效果测量。旧v0.63已收到纠正性观看反馈；新修订检查未执行前不预写通过。构建日志保留原始gzip与只去尾空格的可读副本。
