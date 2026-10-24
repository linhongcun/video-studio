# dns · Codex重制工程

2026-10-24用户要求将EP01–14上一轮Cursor版按当天Codex规格与经验重新制作。本目录为制作工程，站点接入由root统一处理。公开资料见research.md；旁白、文章、读音和分镜各自入库。

使用仓内共享voice/prep.py、gen.py、build.py，不复制配音算法。选定takes见voice/picks.json与substitutions.md；assemble.py仅把共享整轨结果转成句级字幕、声学句首标签与分镜，不生成或重剪音频。

Python环境：/workspace/.venvs/video-studio。Remotion安装npm ci，随后npx tsc --noEmit、npm run covers、npm run render。工作区node_modules软链是安装加速，不入库；锁文件可独立复现。系统要求FFmpeg、Chromium与Noto Sans CJK SC。

检查与能力边界见qa-motion.md、qa-final.md。ASR模型端点被当前网络策略拒绝，未声称完成逐字ASR或人工听辨；冻结词时间是句边界与声学句首，不是逐字对齐。

## 站点发布

[v0.48.0](https://github.com/linhongcun/video-studio/releases/tag/v0.48.0)已完成站点部署与线上文件核验，见[发布记录](release.md)。

## 查询全局导航重制（待独立编辑复核）

保留原12镜、3200帧、音轨、脚本、words与逐句字幕。当前导航见`remotion/src/branch-map.ts`，复用`../_shared/branch-map/index.ts`；05–09保持固定角色的局部网络，解析器自行问根/TLD/权威并接回指引或地址。两处缓存短路分别保留，11镜明确另一个未到期时点。

本轮官方资料实读见`research-flow-map.md`。原发布输入通过`revisions/pre-flow-map.json`的基线Git路径、blob与完整SHA索引追溯；旧媒体及takes不复制。此阶段只制作小样，未重新冻结或正式全片编码。小样位于`/workspace/.video-studio-flow-audit/dns-remake/`，编辑结论由root统一安排。
