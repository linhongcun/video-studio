# EP.20《两个订单，怎么撞成同一个号了？》全局唯一 ID · 镜头表

- 脚本：/workspace/sorkin-backup/global-id/script.md（v0.25.0 定稿）+ pronunciation.md；research：/workspace/nolan-backup/ep20/research.md（村长 9 项决定）。9 章 16 句 → **15 镜头**
- 时间：暂定（make_timing.py 4.3 字/秒）→ map_timing.py；**总 2649 帧 = 正片 2549 + 标签 hold 40 + 片尾 60**
- 定稿：Knoll /workspace/share/ep20/ narration.wav + timeline.json + words.json → `rm -f label_holds.json && sh realign.sh && python3 -B make_checks.py`（不带 FORCE_ESTIMATE）
- 物件：驿站（色）= 库 · 条码打印机 = 发号 · 色带（色深无刻度）= 时间先后 · 徽章 = 站标记 · 流水戳（点阵疏密）= 同一瞬间第几张 · 小本子 = 本机自增 · 火花 = 撞号 · 黄灯 = 停打 · 窗口 = 公共计数器
- 规矩：画面无数字 / 英文 / logo（字幕可含 MySQL / Redis / ID 原文）；只有右上「IT小村」；术语 ≥66；封面大字 ≥36；静止段 push-in

| 镜头 | 全片帧 | 停留（帧） | 术语标签（淡入全片帧） |
|---|---|---|---|
| hook-1 | 0–125 | — | — |
| hook-2 | 126–224 | — | — |
| signal-1 | 225–389 | — | — |
| bridge-1 | 390–526 | — | — |
| bridge-2 | 527–719 | — | — |
| autoinc-1 | 720–958 | — | — |
| autoinc-2 | 959–1064 | — | — |
| autoinc-3 | 1065–1210 | — | 自增 1121 |
| need-1 | 1211–1408 | — | — |
| snowflake-1 | 1409–1670 | — | — |
| snowflake-2 | 1671–1896 | — | — |
| snowflake-3 | 1897–2028 | 40 | 雪花算法 1939 |
| clock-1 | 2029–2192 | — | 时钟回拨 2072 |
| counter-1 | 2193–2378 | — | — |
| recap-1 | 2379–2648 | — | 全局唯一 ID 2538 |

## 各章画面
1. **hook** ①封面大字「两个订单」/「怎么撞成同一个号了？」+ 红蓝站 ②两站各吐一张一模一样的条码 → 火花撞号
2. **signal** 两站各抱一本小本子编号，互不知道
3. **bridge** ①四色分站（写散了）②红蓝各自撕小本子、打出条码（号没散）
4. **autoinc** ①本机服务器 + 小本子 ②两站各自往上加 → 打出同一个号 + 火花 ③自增标签：只管自己这台
5. **need** 多站 + 总台发号机变亮，人往窗口挤（不能挤回去）
6. **snowflake** ①打印机旁依次亮出色带 / 徽章 / 流水戳 ②两站打出不同条码（绿勾）③雪花算法标签
7. **clock** 墙钟被拨回（红弧）→ 黄灯停打，条码变暗；时钟回拨标签
8. **counter** 公共窗口 + 人群挤回；公共计数器小标签
9. **recap** 红蓝不同条码 + 绿勾 → 全局唯一 ID

## 待定
- 时长、hold 都是字数估算；配音定稿后重算
- 完整显示（Nolan 2026-10-15，村长改 63）：pop-in（12 帧）完成 → 镜头转场淡出开始（fade 12 / crossfade 8）≥63 帧。需 hold 的 1 处（Knoll 在该处插静音）：snowflake-3「雪花算法」40（原音 1989 帧 = 66.30 s），共 40 帧
