from collections import deque


class Solution:
    def orangesRotting(self, grid: list[list[int]]) -> int:
        rows, cols = len(grid), len(grid[0])
        state = [row[:] for row in grid]
        queue = deque()
        fresh = 0
        for r in range(rows):
            for c in range(cols):
                if state[r][c] == 2:
                    queue.append((r, c))
                elif state[r][c] == 1:
                    fresh += 1
        minutes = 0
        while queue and fresh > 0:
            for _ in range(len(queue)):
                r, c = queue.popleft()
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and state[nr][nc] == 1:
                        state[nr][nc] = 2
                        fresh -= 1
                        queue.append((nr, nc))
            minutes += 1
        return minutes if fresh == 0 else -1
