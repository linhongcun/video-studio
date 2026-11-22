"""Comprehensive unit & oracle tests for LC.994 Rotting Oranges."""
from __future__ import annotations

import itertools
import json
import random
import sys
import unittest
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EP))

from rotting_oranges_trace import (  # noqa: E402
    IMPOSSIBLE_GRID,
    MAIN_GRID,
    NO_FRESH_GRID,
    NO_ROTTEN_GRID,
    OFFICIAL_EX1_GRID,
    build_all_traces,
    per_source_oracle,
    single_source_distances,
    trace_rotting_oranges,
)
from solution import Solution  # noqa: E402


class TestRottingOranges(unittest.TestCase):
    def setUp(self) -> None:
        self.sol = Solution()

    def test_official_examples_and_boundaries(self) -> None:
        cases = [
            ('official_ex1', OFFICIAL_EX1_GRID, 4),
            ('official_ex2', IMPOSSIBLE_GRID, -1),
            ('official_ex3', NO_FRESH_GRID, 0),
            ('main_two_source', MAIN_GRID, 3),
            ('no_rotten_with_fresh', NO_ROTTEN_GRID, -1),
            ('single_empty', [[0]], 0),
            ('single_fresh', [[1]], -1),
            ('single_rotten', [[2]], 0),
            ('all_empty', [[0, 0], [0, 0]], 0),
            ('all_rotten', [[2, 2], [2, 2]], 0),
            ('two_sources_same_cell_min1', [[2, 1, 2]], 1),
            ('four_corners_meet_center', [[2, 1, 2], [1, 1, 1], [2, 1, 2]], 2),
            ('diagonal_blocked', [[2, 0], [0, 1]], -1),
        ]
        for name, grid, expected in cases:
            with self.subTest(case=name):
                copy_before = [row[:] for row in grid]
                got = self.sol.orangesRotting(grid)
                self.assertEqual(grid, copy_before, 'Solution must not mutate input grid')
                self.assertEqual(got, expected)
                self.assertEqual(per_source_oracle(grid), expected)
                self.assertEqual(trace_rotting_oranges(grid)['result'], expected)

    def test_exhaustive_small_grids(self) -> None:
        # Exhaustively test 8 small grid shapes with m, n <= 3 and <= 6 cells: 1x1, 1x2, 2x1, 1x3, 3x1, 2x2, 2x3, 3x2 (1,614 grids).
        for rows, cols in ((1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2), (2, 3), (3, 2)):
            for cells in itertools.product((0, 1, 2), repeat=rows * cols):
                grid = [list(cells[r * cols:(r + 1) * cols]) for r in range(rows)]
                self.assertEqual(self.sol.orangesRotting(grid), per_source_oracle(grid))

    def test_random_grids_against_per_source_oracle(self) -> None:
        rng = random.Random(9942026)
        for _ in range(3000):
            rows = rng.randint(1, 6)
            cols = rng.randint(1, 6)
            grid = [[rng.choice((0, 1, 1, 1, 2)) for _ in range(cols)] for _ in range(rows)]
            expected = per_source_oracle(grid)
            self.assertEqual(self.sol.orangesRotting(grid), expected)

    def test_main_trace_invariants(self) -> None:
        traces = build_all_traces()
        main = traces['main']
        self.assertEqual(main['result'], 3)
        self.assertEqual(main['stopReason'], 'all_rotten_queue_nonempty')
        # Verify single-source contrast: (2,1) is 3 from (0,0) alone, 1 from (2,2)
        d_tl = single_source_distances(MAIN_GRID, (0, 0))
        d_br = single_source_distances(MAIN_GRID, (2, 2))
        self.assertEqual(d_tl[2][1], 3)
        self.assertEqual(d_br[2][1], 1)
        self.assertEqual(d_tl[1][2], 3)
        self.assertEqual(d_br[1][2], 1)
        # Verify final event has fresh == 0 while queue still holds (0, 3)
        last = main['events'][-1]
        self.assertEqual(last['kind'], 'result')
        self.assertEqual(last['fresh'], 0)
        self.assertEqual(last['queue'], [[0, 3]])
        # Verify collision skips at minute 2 on (0,2) and (2,0)
        m2_expands = [e for e in main['events'] if e['kind'] == 'expand' and e.get('layerMinute') == 2]
        self.assertEqual([e['source'] for e in m2_expands], [[1, 0], [0, 1], [1, 2], [2, 1]])
        skip_12 = [ch for ch in m2_expands[2]['checks'] if ch['to'] == [0, 2]][0]
        self.assertEqual(skip_12['outcome'], 'already_rotten')
        self.assertEqual(skip_12['existingMinute'], 2)
        skip_21 = [ch for ch in m2_expands[3]['checks'] if ch['to'] == [2, 0]][0]
        self.assertEqual(skip_21['outcome'], 'already_rotten')
        self.assertEqual(skip_21['existingMinute'], 2)
        # Verify deep-copy immutability across events (L050)
        self.assertEqual(main['events'][0]['grid'], MAIN_GRID)
        self.assertEqual(main['events'][0]['fresh'], 7)
        # Verify impossible trace leaves (2,0) fresh
        imp = traces['impossible']
        self.assertEqual(imp['result'], -1)
        self.assertEqual(imp['events'][-1]['remainingFresh'], [[2, 0]])

    def test_solution_json_matches_solution_py(self) -> None:
        sol_json = EP / 'solution.json'
        if sol_json.is_file():
            data = json.loads(sol_json.read_text())
            self.assertEqual(data['lines'], (EP / 'solution.py').read_text().splitlines())


if __name__ == '__main__':
    unittest.main()
