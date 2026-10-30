# Kafka MQ05 / EP45

《消费幂等：已经处理过，为什么还会再来一遍？》；issue313；基线f01411f7e2a2d1cef480cd0f6b73d4c29d7169f3。来源、脚本、模型和文章已通过配音前独立编辑。根已接受最终5497帧实测声轨；新Main通过类型检查，源作者已实际审查逐镜关键帧、字幕帧和关键短窗，等待独立动态审查，尚未冻结或正式编码。

核心是唯一键的并发仲裁与登记/积分同一本地事务。Kafka恢复仅解释同E01为什么重来。固定E01/order7042/account17/+10，逻辑业务points；Kafka4.4.0 classic、手动提交、单条poll；PostgreSQL18.0 Read Committed。

- `outline-source-map.md` / `script.md` / `plan.json`：四章14镜28句、真实执行映射与明确reset分支。`qa-editorial/draft-identity.json`记录确切旁白和脚本SHA。
- `research.md` / `references.json` / `article-sources.json` / `sources/`：本轮固定commit实际GET、原题、机构、精确连续原文和边界。4项片尾来源预检已通过；额外5项文章执行短引。
- `python3 build_model.py`：90项有限状态/应用负向检查、33快照；本轮结果在`model-verification.json`。模型不是真实Broker/数据库实验。
- 独立真实运行：`docs/archive/2026-10/mq05-07-implementation/runtime/runs/mq05-20261030T152318.187770Z/`，89实际断言；研究已限定读取的实际输出与未覆盖分支。
- `article.mdx` / `article-figure-plan.json`：文章可独立阅读，4个Figure已按最终实测时序固定整数帧563/3001/3368/4565与seekTo。已看源预演图；最终JPEG需正式成片后按整数帧提取核验，未预认成片图验收。
- Remotion只复用当前保留的生产入口/锁图并实际fresh npm ci，无旧takes/QA/冻结/媒体回执冒作新结果。Main新写14镜并通过真实TypeScript类型检查；自预演记录见`qa/self-review.json`，范围不包括全片人工听辨或新手学习研究。独立动态审查另由QA完成。

配音、冻结和最终渲染由根统一控制。获得独立编辑与根放行后才调用共享voice工具；本目录`prepare.py`和`assemble.py`仅转发共享算法，`render.py`默认接完整来源检查/冻结核对/真实limited BT.709转换与title-author资料页。不会直接交付缺资料的正文片。根负责新封面审图和站点/git发布，本代理不修改既有四期或共享生产文件。
