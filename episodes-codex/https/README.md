# https · Codex重制工程

2026-10-24用户要求将EP01–14上一轮Cursor版按当天Codex规格与经验重新制作。本目录为制作工程，站点接入由root统一处理。公开资料见research.md；旁白、文章、读音和分镜各自入库。

使用仓内共享voice/prep.py、gen.py、build.py，不复制配音算法。选定takes见voice/picks.json与substitutions.md；assemble.py仅把共享整轨结果转成句级字幕、声学句首标签与分镜，不生成或重剪音频。

Python环境：/workspace/.venvs/video-studio。Remotion安装npm ci，随后npx tsc --noEmit、npm run covers、npm run render。工作区node_modules软链是安装加速，不入库；锁文件可独立复现。系统要求FFmpeg、Chromium与Noto Sans CJK SC。

检查与能力边界见qa-motion.md、qa-final.md。ASR模型端点被当前网络策略拒绝，未声称完成逐字ASR或人工听辨；冻结词时间是句边界与声学句首，不是逐字对齐。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。

## 全局/局部导航返工（待独立复核）

2026-10-24，批次`flow-map-20261024/#199`。保留原音轨、脚本、words、字幕、12镜和3589帧，新增安全握手与接收验证的分层全局关系、核验失败后的正常情景重置及结尾回收。历史输入和当前媒体由[索引](revisions/pre-flow-map.json)关联基线`6765032`，没有复制大媒体。

本轮预演与完整动作窗口证据见[QA记录](qa-flow-map.json)。动画源已停写，等待独立编辑复核；未执行本轮最终冻结、完整正式编码或发布。原`qa-final.md`、`release.md`及`source-sha256.json`继续对应旧版，最终制作由主任务统一安排。共用导航只引用`../_shared/branch-map/index.ts`，没有改动共用实现。

独立编辑首轮发现07提前高亮“握手完成”出口，R1已将该边延后到local273协商落定。只重采受影响07关键帧与identity跨镜片；初版源和QA在`revisions/flow-map-before-r1/`保留，证据按旧/新指纹分组，等待重点复验。
