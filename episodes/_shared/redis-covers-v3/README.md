# Redis 新期封面模板

EP50 Sentinel、EP51 Cluster 自动故障转移与 EP52 近似 LRU 的三比例封面。沿用已发布 Redis 系列的冷银灰、冰白、Redis 红、石墨字色、原始 Redis 标记、字体和固定版式；`style-v1.json`、`background.png` 保持 v2 原字节。旧 v1/v2 输入与既有发布封面不改写。

catalog 只声明本批三个真实 EP 与完整原题，不另起 R 号。Sentinel 图把选负责人的票与负责人挑数据副本分开；Cluster 的授权来自持槽主节点、接收者是原主的副本；LRU 以显式教学示例区分全局最旧与候选池当前最旧，候选池只画有效条目的节选，未把节选数当作真实容量。

尺寸为 1920×1080、1080×1440、1440×1080，4:3 保持原竖版等比居中，内容在 x315..1125、y<918。生成器用实际 Chromium 字体检查全部字框、图形及组间距，另做三位 EP 与长文字排版压力样例。渲染报告保存完整输入、字体与 SVG/PNG/JPEG SHA；这些检查不代替独立实际审图。

```bash
python3 episodes/_shared/redis-covers-v3/render.py --out-dir /workspace/work/redis-batch/covers/candidates
```

默认只生成候选。独立审图通过后可由负责人使用同一输出目录加 `--install` 安装已审字节；安装操作会重新核对所有输入、真实字体和图像 SHA，并拒绝覆盖任何既有冻结输入。它只写 catalog 中声明的新期制作封面与发布封面，不为旧片重新渲染或安装。

本 README 是制作输入；后续实际制作、审查与发布状态写任务归档，不回写本文件追认。
