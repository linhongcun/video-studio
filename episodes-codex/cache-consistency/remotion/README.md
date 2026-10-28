# 当前 Redis 视觉入口

当前正文入口为 `src/redis-style/index.ts`，沿用 Redis 跳表的冷银灰、Redis 红与石墨文字。原 `src/index.ts`、模型、分镜、声音和旧冻结保留历史身份。

从仓根执行：

```bash
python3 episodes-codex/_shared/redis-cache-video/render.py cache-consistency --render
```

新媒体和冻结在 `../revisions/redis-style/`；已存在清单只读核对，已有最终视频使用 `--verify`，不覆盖旧记录。正文在完整AAC流拷贝前生成有限范围BT.709画面，资料页使用同一编码。

新三比例封面使用 `episodes-codex/_shared/redis-covers-v2/`；实际制作、检查和发布记录见仓库 `docs/archive/2026-10/redis-cache-style/`。
