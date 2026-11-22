"""Real execution trace generator for LC.994 Rotting Oranges.

Every state snapshot is produced by executing the exact multi-source BFS
algorithm (and an independent per-source single-BFS oracle for contrast and
cross-checking) with deep-copied grids and queues per L050.
"""
from __future__ import annotations

from collections import deque
from typing import Any

DIRS = ((-1, 0, 'up'), (1, 0, 'down'), (0, -1, 'left'), (0, 1, 'right'))

MAIN_GRID = [
    [2, 1, 1, 1],
    [1, 0, 1, 0],
    [1, 1, 2, 0],
]
IMPOSSIBLE_GRID = [
    [2, 1, 1],
    [0, 1, 1],
    [1, 0, 1],
]
OFFICIAL_EX1_GRID = [
    [2, 1, 1],
    [1, 1, 0],
    [0, 1, 1],
]
NO_FRESH_GRID = [[0, 2]]
NO_ROTTEN_GRID = [[1, 0, 1]]


def single_source_distances(grid: list[list[int]], start: tuple[int, int]) -> list[list[int | None]]:
    """Run BFS from a single initial rotten orange and return rot minute per cell."""
    rows, cols = len(grid), len(grid[0])
    dist: list[list[int | None]] = [[None] * cols for _ in range(rows)]
    sr, sc = start
    if grid[sr][sc] != 2:
        return dist
    dist[sr][sc] = 0
    q: deque[tuple[int, int]] = deque([(sr, sc)])
    while q:
        r, c = q.popleft()
        for dr, dc, _ in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1 and dist[nr][nc] is None:
                dist[nr][nc] = (dist[r][c] or 0) + 1
                q.append((nr, nc))
    return dist


def per_source_oracle(grid: list[list[int]]) -> int:
    """Independent oracle: run BFS from each initial rotten orange and take cell-wise min."""
    rows, cols = len(grid), len(grid[0])
    best: list[list[int | None]] = [[None] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                d = single_source_distances(grid, (r, c))
                for i in range(rows):
                    for j in range(cols):
                        if d[i][j] is not None:
                            if best[i][j] is None or d[i][j] < best[i][j]:
                                best[i][j] = d[i][j]
    ans = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                if best[r][c] is None:
                    return -1
                if best[r][c] > ans:
                    ans = best[r][c]
    return ans


def trace_rotting_oranges(grid: list[list[int]]) -> dict[str, Any]:
    rows, cols = len(grid), len(grid[0])
    state = [row[:] for row in grid]
    rot_time: list[list[int | None]] = [
        [0 if state[r][c] == 2 else None for c in range(cols)] for r in range(rows)
    ]
    queue: deque[tuple[int, int]] = deque()
    fresh = 0
    initial_rotten: list[list[int]] = []
    for r in range(rows):
        for c in range(cols):
            if state[r][c] == 2:
                queue.append((r, c))
                initial_rotten.append([r, c])
            elif state[r][c] == 1:
                fresh += 1

    events: list[dict[str, Any]] = []

    def snap(kind: str, **extra: Any) -> None:
        events.append({
            'id': len(events),
            'kind': kind,
            'grid': [row[:] for row in state],
            'rotTime': [row[:] for row in rot_time],
            'queue': [[r, c] for r, c in queue],
            'fresh': fresh,
            'minutes': minutes,
            **extra,
        })

    minutes = 0
    snap('init', initialRotten=initial_rotten, initialFresh=fresh)

    while queue and fresh > 0:
        layer_size = len(queue)
        layer_batch = [[r, c] for r, c in list(queue)]
        snap('layer_start', layerMinute=minutes + 1, layerSize=layer_size, layerBatch=layer_batch)
        next_batch: list[list[int]] = []
        for idx_in_layer in range(layer_size):
            r, c = queue.popleft()
            remaining_in_layer = layer_size - idx_in_layer - 1
            checks: list[dict[str, Any]] = []
            infected_here: list[list[int]] = []
            for dr, dc, dname in DIRS:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < rows and 0 <= nc < cols):
                    checks.append({'dir': dname, 'to': [nr, nc], 'outcome': 'oob'})
                elif state[nr][nc] == 0:
                    checks.append({'dir': dname, 'to': [nr, nc], 'outcome': 'empty'})
                elif state[nr][nc] == 2:
                    checks.append({
                        'dir': dname,
                        'to': [nr, nc],
                        'outcome': 'already_rotten',
                        'existingMinute': rot_time[nr][nc],
                    })
                else:
                    state[nr][nc] = 2
                    rot_time[nr][nc] = minutes + 1
                    fresh -= 1
                    queue.append((nr, nc))
                    next_batch.append([nr, nc])
                    infected_here.append([nr, nc])
                    checks.append({'dir': dname, 'to': [nr, nc], 'outcome': 'rot'})
            snap(
                'expand',
                layerMinute=minutes + 1,
                source=[r, c],
                checks=checks,
                infected=infected_here,
                remainingInLayer=remaining_in_layer,
                nextLayerCount=len(next_batch),
            )
        minutes += 1
        snap('layer_end', completedMinute=minutes, newlyRotted=next_batch)

    result = minutes if fresh == 0 else -1
    stop_reason = 'all_rotten_initial' if (fresh == 0 and minutes == 0) else (
        'all_rotten_queue_nonempty' if (fresh == 0 and len(queue) > 0) else (
            'all_rotten_queue_empty' if fresh == 0 else 'queue_empty_fresh_remaining'
        )
    )
    remaining_fresh = [[r, c] for r in range(rows) for c in range(cols) if state[r][c] == 1]
    snap('result', value=result, stopReason=stop_reason, remainingFresh=remaining_fresh)

    return {
        'rows': rows,
        'cols': cols,
        'initialGrid': [row[:] for row in grid],
        'initialRotten': initial_rotten,
        'result': result,
        'stopReason': stop_reason,
        'events': events,
    }


def build_all_traces() -> dict[str, Any]:
    main_run = trace_rotting_oranges(MAIN_GRID)
    only_top_left = single_source_distances(MAIN_GRID, (0, 0))
    only_bottom_right = single_source_distances(MAIN_GRID, (2, 2))
    return {
        'main': main_run,
        'contrastSingleSource': {
            'grid': [row[:] for row in MAIN_GRID],
            'fromTopLeft': only_top_left,
            'fromBottomRight': only_bottom_right,
            'combinedMin': main_run['events'][-1]['rotTime'],
        },
        'impossible': trace_rotting_oranges(IMPOSSIBLE_GRID),
        'officialEx1': trace_rotting_oranges(OFFICIAL_EX1_GRID),
        'noFresh': trace_rotting_oranges(NO_FRESH_GRID),
        'noRotten': trace_rotting_oranges(NO_ROTTEN_GRID),
    }
