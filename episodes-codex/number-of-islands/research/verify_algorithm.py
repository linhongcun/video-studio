"""Compare the real iterative solver and its AST observation with an independent DSU."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import sys
import time

sys.dont_write_bytecode = True
from generate_demo_trace import EP, Runners, generate_demo, sha


def dsu_partition(grid):
    """Only right/down undirected land edges are merged; no traversal/DFS solver."""
    rows, cols = len(grid), len(grid[0])
    parent = {r * cols + c: r * cols + c
              for r in range(rows) for c in range(cols) if grid[r][c] == "1"}
    size = {key: 1 for key in parent}

    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    def union(left, right):
        a, b = find(left), find(right)
        if a == b:
            return
        if size[a] < size[b]:
            a, b = b, a
        parent[b] = a
        size[a] += size[b]

    for r in range(rows):
        for c in range(cols):
            key = r * cols + c
            if key not in parent:
                continue
            if c + 1 < cols and key + 1 in parent:
                union(key, key + 1)
            if r + 1 < rows and key + cols in parent:
                union(key, key + cols)
    labels = {(key // cols, key % cols): find(key) for key in parent}
    return len(set(labels.values())), labels


def verify_case(runners, grid, expected=None):
    before = tuple(tuple(row) for row in grid)
    oracle_count, roots = dsu_partition(grid)
    assert tuple(tuple(row) for row in grid) == before, "Oracle mutated input"
    result, observer, summary = runners.run(grid)
    assert result == oracle_count, (grid, result, oracle_count)
    if expected is not None:
        assert result == expected, (result, expected)
    # A mere equal total could hide different partitions; require a bijection.
    actual_to_oracle, oracle_to_actual = {}, {}
    for cell, island_id in observer.discovered.items():
        root = roots[cell]
        assert actual_to_oracle.setdefault(island_id, root) == root
        assert oracle_to_actual.setdefault(root, island_id) == island_id
    assert len(actual_to_oracle) == len(oracle_to_actual) == result
    assert tuple(tuple(row) for row in grid) == before
    summary["inputUnchanged"] = True
    summary["dsuCount"] = oracle_count
    summary["componentPartitionBijection"] = True
    return summary


def rows(strings):
    return [list(row) for row in strings]


def snake_grid():
    grid = [["0"] * 300 for _ in range(300)]
    for r in range(300):
        if r % 2 == 0:
            grid[r] = ["1"] * 300
        else:
            grid[r][299 if (r // 2) % 2 == 0 else 0] = "1"
    return grid


def main():
    started = time.perf_counter()
    runners = Runners()
    source_sha = runners.source_sha
    exhaustive_started = time.perf_counter()
    totals = Counter()
    result_histogram = Counter()
    for mask in range(1 << 16):
        grid = [["1" if mask & (1 << (r * 4 + c)) else "0" for c in range(4)]
                for r in range(4)]
        summary = verify_case(runners, grid)
        totals.update({key: summary["actionCounts"].get(key, 0)
                       for key in ["mark", "push", "pop", "neighbor_check"]})
        result_histogram[summary["islands"]] += 1
    exhaustive_seconds = time.perf_counter() - exhaustive_started

    named = [
        ("official-example-1", rows(["11110", "11010", "11000", "00000"]), 1),
        ("official-example-2", rows(["11000", "11000", "00100", "00011"]), 3),
        ("single-water", [["0"]], 0),
        ("single-land", [["1"]], 1),
        ("one-row-alternating", [["1" if c % 2 == 0 else "0" for c in range(300)]], 150),
        ("one-column-alternating", [["1" if r % 2 == 0 else "0"] for r in range(300)], 150),
        ("one-row-solid", [["1"] * 300], 1),
        ("one-column-solid", [["1"] for _ in range(300)], 1),
        ("300-square-all-water", [["0"] * 300 for _ in range(300)], 0),
        ("300-square-all-land", [["1"] * 300 for _ in range(300)], 1),
        ("300-square-checkerboard", [["1" if (r + c) % 2 == 0 else "0"
                                      for c in range(300)] for r in range(300)], 45000),
        ("300-square-diagonal", [["1" if r == c else "0" for c in range(300)]
                                    for r in range(300)], 300),
        ("water-hole-and-separate-center", rows(["11111", "10001", "10101", "10001", "11111"]), 2),
        ("orthogonal-bridge", rows(["11011", "11111", "00000"]), 1),
        ("diagonal-only", rows(["10", "01"]), 2),
        ("long-induced-snake", snake_grid(), 1),
    ]
    boundary_results = []
    for name, grid, expected in named:
        case_started = time.perf_counter()
        summary = verify_case(runners, grid, expected)
        item = dict(name=name, rows=len(grid), cols=len(grid[0]), expected=expected,
                    actual=summary["islands"], landCells=summary["landCells"],
                    actionCounts=summary["actionCounts"], maxStackDepth=summary["maxStackDepth"],
                    inputUnchanged=True, componentPartitionBijection=True,
                    everyLandDiscoveredPushedPoppedExpandedExactlyOnce=True,
                    elapsedSeconds=round(time.perf_counter() - case_started, 6))
        if name == "long-induced-snake":
            degree_counts = Counter()
            for r, row in enumerate(grid):
                for c, value in enumerate(row):
                    if value == "1":
                        degree_counts[sum(0 <= r + dr < 300 and 0 <= c + dc < 300
                                          and grid[r + dr][c + dc] == "1"
                                          for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)])] += 1
            assert summary["landCells"] == 45150
            assert degree_counts == {1: 2, 2: 45148}
            assert grid[0][0] == "1" and grid[0][1] == "1" and grid[1][0] == "0"
            item["pathProof"] = dict(
                landCells=45150, connectedComponents=1, degreeCounts=dict(degree_counts),
                firstRowMajorSeedIsEndpoint=True, simplePathVertices=45150,
                pythonRecursionLimitObserved=sys.getrecursionlimit(),
                exceedsObservedRecursionLimit=45150 > sys.getrecursionlimit(),
                recursiveSolverExecuted=False,
                inference="Connected undirected graph with two degree-1 vertices and all other degrees2 is a simple path; DFS from its endpoint would need45150 nested cell visits.",
            )
        boundary_results.append(item)

    rng = random.Random(20020261025)
    random_started = time.perf_counter()
    random_cases = 300
    for _ in range(random_cases):
        height, width = rng.randint(1, 40), rng.randint(1, 40)
        probability = rng.choice([0.05, 0.2, 0.5, 0.8, 0.95])
        grid = [["1" if rng.random() < probability else "0" for _ in range(width)]
                for _ in range(height)]
        verify_case(runners, grid)
    random_seconds = time.perf_counter() - random_started

    trace = generate_demo(runners)
    trace_file = EP / "research/demo-trace.json"
    trace_file.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n")
    runners.check_source_unchanged()
    report = dict(
        status="passed", checkedAtUTC=datetime.now(timezone.utc).isoformat(),
        elapsedSeconds=round(time.perf_counter() - started, 6),
        solverSHA256=source_sha,
        sourcesSHA256={name: sha((EP / name).read_bytes()) for name in [
            "solution.py", "solution.json", "research/verify_algorithm.py",
            "research/generate_demo_trace.py", "research/demo-trace.json"]},
        oracle="Independent union-find: land singleton sets, merge right/down land edges only, count distinct roots; require component-label/root bijection.",
        actualSolverExecutedUnmodified=True,
        observer=dict(
            originalASTPreservedAfterRemovingOnlyTaggedCallbacks=True,
            originalASTSHA256=hashlib.sha256(runners.original_ast.encode()).hexdigest(),
            insertedCallbackSites=runners.insertions,
            allCasesRunBothUnmodifiedAndObservedSolver=True,
            allLandMarkedPushedPoppedExpandedExactlyOnce=True,
            allWaterNeverMarked=True,
            actualNeighborOrderChecked="right, down, left, up",
            inputDeepSnapshotsUnchangedForOracleAndBothSolvers=True,
            summaryModeAvoidsWholeSeenCopies=True,
        ),
        exhaustive4x4=dict(cases=65536, allMasksFrom=0, allMasksThrough=65535,
                           elapsedSeconds=round(exhaustive_seconds, 6),
                           resultsHistogram=dict(sorted(result_histogram.items())),
                           aggregateActions=dict(totals)),
        namedBoundaryAndStressCases=boundary_results,
        seededRandom=dict(cases=random_cases, seed=20020261025, rowsAndCols="1..40",
                          landProbabilities=[0.05, 0.2, 0.5, 0.8, 0.95],
                          elapsedSeconds=round(random_seconds, 6)),
        actualOfficialExample2Trace=dict(path="research/demo-trace.json",
                                        events=len(trace["events"]), result=trace["result"],
                                        summary=trace["summary"]),
        totalCases=65536 + len(named) + random_cases,
        limitations=[
            "Finite exhaustive4x4 and listed larger cases validate implementation; they do not enumerate every grid up to300x300 or replace the connectivity argument.",
            "The long-path recursion depth is a graph-theoretic inference; no recursive DFS or intentional RecursionError was run.",
            "Only the small official example stores detailed snapshots; stress cases use summary observation of the same real source.",
            "No animation, audio, pronunciation, viewer learning or user acceptance is verified here.",
        ],
    )
    report_file = EP / "research/algorithm-verification.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(dict(status="passed", totalCases=report["totalCases"],
                          exhaustive4x4=65536, namedCases=len(named), randomCases=random_cases,
                          elapsedSeconds=report["elapsedSeconds"],
                          demoTraceEvents=len(trace["events"]), traceSHA256=sha(trace_file.read_bytes()))))


if __name__ == "__main__":
    main()
