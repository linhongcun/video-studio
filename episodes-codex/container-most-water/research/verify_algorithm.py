#!/usr/bin/env python3
"""Reproduce the article algorithm and teaching-number verification.

Run from any directory:
    python3 episodes-codex/container-most-water/research/verify_algorithm.py

Uses only the Python standard library. The oracle enumerates every pair and
therefore does not rely on the two-pointer exclusion rule being verified.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
from pathlib import Path


EPISODE = Path(__file__).resolve().parents[1]
REPORT = EPISODE / "research" / "algorithm-verification.json"
EXAMPLES = (
    [2, 3, 10, 5, 7, 8, 9],
    [1, 8, 6, 2, 5, 4, 8, 3, 7],
    [1, 1],
    [0, 0],
    [0, 3, 0],
    [10, 2, 10],
)


def brute_force(height):
    return max(
        (right - left) * min(height[left], height[right])
        for left in range(len(height))
        for right in range(left + 1, len(height))
    )


def teaching_trace(height):
    """Record the documented moves; the brute-force function is the oracle."""
    left, right, best = 0, len(height) - 1, 0
    trace = []
    while left < right:
        width = right - left
        shorter = min(height[left], height[right])
        area = width * shorter
        best = max(best, area)
        trace.append(
            dict(left=left, right=right, width=width, shorter=shorter,
                 area=area, best=best)
        )
        if height[left] <= height[right]:
            left += 1
        else:
            right -= 1
    return best, trace


def main():
    article = (EPISODE / "article.mdx").read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)\n```", article, re.S)
    assert len(blocks) == 1, "Expected exactly one article Python implementation"
    code = blocks[0]
    namespace = {}
    exec(compile(code, str(EPISODE / "article.mdx") + ":python", "exec"), namespace)
    solve = namespace["Solution"]().maxArea

    exhaustive = 0
    for length in range(2, 9):
        for height in itertools.product(range(4), repeat=length):
            expected = brute_force(height)
            assert solve(list(height)) == expected, height
            traced, trace = teaching_trace(height)
            assert traced == expected, height
            assert len(trace) == length - 1, height
            exhaustive += 1

    rng = random.Random(11)
    for _ in range(400):
        height = [rng.randint(0, 10_000) for _ in range(rng.randint(2, 100))]
        assert solve(height) == brute_force(height), height

    examples = []
    for height in EXAMPLES:
        answer, trace = teaching_trace(height)
        assert answer == solve(height) == brute_force(height)
        examples.append(dict(height=height, answer=answer, trace=trace))

    assert [row["area"] for row in examples[0]["trace"]] == [12, 15, 36, 24, 14, 5]
    assert examples[0]["answer"] == 36
    assert examples[1]["answer"] == 49
    report = {
        "method": "Extract the article Python implementation, compare with independent full pair enumeration, and verify the teaching trace and n-1 advances.",
        "exhaustive": {"height_values": [0, 1, 2, 3], "lengths": list(range(2, 9)), "cases": exhaustive},
        "random": {"seed": 11, "cases": 400, "length_range": [2, 100], "height_range": [0, 10000]},
        "examples": examples,
        "verdict": "pass",
        "articleCodeSha256": hashlib.sha256(code.encode()).hexdigest(),
        "articleCodeExtractedAndExecuted": True,
        "articleCodeExhaustiveCases": exhaustive,
        "reproduce": "python3 episodes-codex/container-most-water/research/verify_algorithm.py",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": "pass", "exhaustive_cases": exhaustive, "random_cases": 400, "report": str(REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
