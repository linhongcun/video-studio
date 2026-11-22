# LC.994 腐烂的橘子 · 调研与资料核验

核验日期：2026-11-22（Asia/Shanghai）。本文件记录真实访问公开资料的原题、出处、适用边界与本期教学范围；逐字证据保存在 [source-evidence.json](research/source-evidence.json)。

## 来源清单

| 编号 | 机构 | 原始题名 | 访问与版本 | 公开链接 | 支持的核心论点 |
| --- | --- | --- | --- | --- | --- |
| R1 | LeetCode | Rotting Oranges | 官方题面，2026-11-22访问 | https://leetcode.cn/problems/rotting-oranges/description/ | `m x n` 网格取值 `0/1/2`；每分钟向 4 方向相邻新鲜橘子扩散；返回最少分钟数，不可能返回 `-1`；官方三例与 `1 <= m, n <= 10` 约束 |
| R2 | Python Software Foundation | collections — Container datatypes | Python 3.15.2 documentation，2026-11-22访问 | https://docs.python.org/3/library/collections.html#collections.deque | `collections.deque` 在两端提供近似 `O(1)` 的 `append` / `popleft`，避免列表 `pop(0)` 的 `O(n)` 内存搬移 |
| R3 | Wikipedia | Breadth-first search | 英文条目，2026-11-22访问 | https://en.wikipedia.org/wiki/Breadth-first_search | 广度优先搜索借助队列先展开当前深度层的全部节点，再推进到下一深度层 |

## 教学范围与适用边界

- **前置概念**：二维数组行列下标 `(r, c)`、上下左右四邻方向、队列的先进先出（在视频第 03 镜结合按层推进就地解释，不预设观众已背诵多源 BFS 模板）。
- **核心问题**：多个烂橘子同时开始扩散，为什么要先把所有初始烂橘子一起放进队列？
- **贯穿教学主例**：`3 × 4` 双源网格 `[[2,1,1,1],[1,0,1,0],[1,1,2,0]]`，初始烂橘子在 `(0,0)` 与 `(2,2)`，初始新鲜橘子 7 个，空位 3 个。
  - 若只从 `(0,0)` 单独推进，`(2,1)` 和 `(1,2)` 会被算成 3 分钟，忽略了 `(2,2)` 在第 1 分钟就传染它们。
  - 双源同入队后：第 1 分钟腐烂 4 个（`fresh: 7→3`）；第 2 分钟两路波纹在 `(0,2)` 和 `(2,0)` 相遇，体现“入队即改 2”去重与最早到达性质（`fresh: 3→1`）；第 3 分钟腐烂最后一个 `(0,3)`（`fresh: 1→0`），此时队列仍含 `[(0,3)]` 非空，直接展示 `while queue and fresh > 0` 防止多算成 4 分钟。
- **重置与边界**：第 07 镜明确重置为官方示例 2 `[[2,1,1],[0,1,1],[1,0,1]]` 演示空位斜向隔离返回 `-1`；第 08 镜覆盖官方示例 3 `[[0,2]] → 0`、无烂橘子 `[[1,0,1]] → -1`、官方示例 1 `[[2,1,1],[1,1,0],[0,1,1]] → 4`。
- **核验范围边界**：以上来源仅证明题面规则、队列接口复杂度与 BFS 按层定义；主例多源过程与边界正确性由 `solution.py`、`rotting_oranges_trace.py` 与独立逐源 BFS oracle 交叉测试核验，不冒充官方题解。
