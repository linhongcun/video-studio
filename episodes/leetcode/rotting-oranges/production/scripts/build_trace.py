#!/usr/bin/env python3
"""Build trace/main-example.json from rotting_oranges_trace.py and verify against solution.py & oracle."""
from __future__ import annotations

import json
import sys
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EP))

from rotting_oranges_trace import build_all_traces, per_source_oracle  # noqa: E402
from solution import Solution  # noqa: E402


def main() -> None:
    traces = build_all_traces()
    sol = Solution()
    for key in ('main', 'impossible', 'officialEx1', 'noFresh', 'noRotten'):
        run = traces[key]
        grid = run['initialGrid']
        got_sol = sol.orangesRotting(grid)
        got_oracle = per_source_oracle(grid)
        assert got_sol == run['result'] == got_oracle, (key, got_sol, run['result'], got_oracle)
    out = EP / 'trace/main-example.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(traces, ensure_ascii=False, indent=2) + '\n')
    print(f'Wrote {out.relative_to(EP)} ({len(traces["main"]["events"])} main events, verified against Solution & oracle)')


if __name__ == '__main__':
    main()
