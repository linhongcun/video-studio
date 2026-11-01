# Redis 跳表当前视觉入口

当前正文使用 `src/redis-style/index.ts`，延续 Redis 系列封面的冷银灰、Redis 红和石墨文字。`src/index.ts` 是原层高修订的历史入口；原模型、层高选项、分镜和声音继续保持。

原视觉制作与冻结在 [`../../../redis-style/`](../../../redis-style/)。当前发布媒体还经过独立的 [`../../../redis-style-bt709-v2/`](../../../redis-style-bt709-v2/) 色彩派生，以免实际浏览器把银灰底显示成白色。原视觉产物和冻结保持；实际渲染入口以两阶段共享工具为准：

```bash
# 从仓根执行
python3 episodes-codex/_shared/redis-video/render.py redis-skiplist --render
python3 episodes-codex/_shared/redis-video-bt709/render-v2.py --render
```

共享说明：[`redis-video/README.md`](../../../../../_shared/redis-video/README.md) 与 [`redis-video-bt709/README-v2.md`](../../../../../_shared/redis-video-bt709/README-v2.md)。先按各入口准备或只读核对冻结输入，不能覆盖已经存在的最终媒体。发布状态与验收记录见仓库 `docs/archive/2026-10/redis-video-style/`。
