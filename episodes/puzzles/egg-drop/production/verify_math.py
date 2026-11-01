#!/usr/bin/env python3
"""Independent exact QA for P05's two-egg threshold strategies.

This standard-library program verifies threshold identification, not animation,
speech, learner understanding, or a randomized expected number of trials.
"""

import argparse
from collections import Counter
from datetime import datetime
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from zoneinfo import ZoneInfo


FLOORS = 100
DECREASING_POINTS = (14, 27, 39, 50, 60, 69, 77, 84, 90, 95, 99, 100)
TEN_POINTS = tuple(range(10, 101, 10))
INFINITY = 10 ** 9


def simulate(n, threshold, points):
    """Run an explicit physical test sequence and retain all possible F values.

    The first intact egg follows the supplied checkpoints. After it breaks,
    the other egg scans upward from the last known-safe floor. A known upper
    breaking boundary may identify F without dropping again from that floor.
    """
    assert 0 <= threshold <= n
    assert points and points[-1] == n
    assert tuple(sorted(set(points))) == tuple(points)
    assert all(1 <= floor <= n for floor in points)
    candidates = set(range(n + 1))
    egg_intact = {1: True, 2: True}
    events = []

    def test(egg, floor, stage):
        nonlocal candidates
        assert egg_intact[egg], "A broken egg was reused"
        assert len(candidates) > 1, "An unnecessary test after exact identification"
        before = sorted(candidates)
        assert before[0] < floor <= before[-1], "Test must split live candidates"
        broke = floor > threshold
        candidates = {f for f in candidates if (f < floor) == broke}
        if broke:
            egg_intact[egg] = False
        after = sorted(candidates)
        assert after and threshold in candidates
        assert after == list(range(after[0], after[-1] + 1))
        events.append({
            "drop": len(events) + 1,
            "egg": egg,
            "stage": stage,
            "floor": floor,
            "broke": broke,
            "highestSafeFBefore": [before[0], before[-1]],
            "highestSafeFAfter": [after[0], after[-1]],
            "remainingEggs": sum(egg_intact.values()),
            "remainingOf14DropBudget": 14 - len(events) - 1,
        })
        assert any(egg_intact.values()) or len(candidates) == 1
        return broke

    for floor in points:
        if len(candidates) == 1:
            break
        if test(1, floor, "checkpoint"):
            # The candidate set now ends at floor - 1. Testing the already
            # known breaking floor again would waste the final egg.
            for fine_floor in range(min(candidates) + 1, floor):
                if len(candidates) == 1:
                    break
                if test(2, fine_floor, "linear"):
                    break
            break

    assert candidates == {threshold}, (threshold, candidates)
    trace = tuple((e["egg"], e["floor"], e["broke"]) for e in events)
    return {
        "F": threshold,
        "inferredF": next(iter(candidates)),
        "drops": len(events),
        "remainingEggs": sum(egg_intact.values()),
        "events": events,
        "trace": trace,
    }


def strategy_report(points):
    results = [simulate(FLOORS, f, points) for f in range(FLOORS + 1)]
    assert len({r["trace"] for r in results}) == FLOORS + 1
    maximum = max(r["drops"] for r in results)
    return {
        "checkpoints": list(points),
        "gaps": [b - a for a, b in zip((0,) + tuple(points[:-1]), points)],
        "thresholdsChecked": len(results),
        "allExactlyIdentified": True,
        "distinctObservableTraces": len(results),
        "maximumDrops": maximum,
        "worstThresholds": [r["F"] for r in results if r["drops"] == maximum],
        "dropCountDistribution": dict(sorted(Counter(r["drops"] for r in results).items())),
        "dropCountByF": [r["drops"] for r in results],
        "edgeCases": {"F0": results[0], "F100": results[-1]},
    }


@lru_cache(maxsize=None)
def interval_minimax(eggs, low, high):
    """Independent optimal decision-tree search on F in inclusive [low, high].

    A split at actual floor x produces [low, x-1] with one fewer egg on
    break, and [x, high] with the same eggs on survival. The two outcomes
    cover every candidate exactly once. This does not read strategy points.
    """
    assert 0 <= low <= high
    if low == high:
        return 0
    if eggs == 0:
        return INFINITY
    if eggs == 1:
        # Skipping any next floor risks breaking the only egg while leaving
        # two F candidates indistinguishable. Ascending tests attain this.
        return high - low
    return 1 + min(max(interval_minimax(eggs - 1, low, x - 1),
                       interval_minimax(eggs, x, high))
                   for x in range(low + 1, high + 1))


def capacity_table(max_moves=15):
    """Max unknown floors resolved by moves/eggs, independent of minimax DP."""
    rows = [[0, 0, 0]]
    for moves in range(1, max_moves + 1):
        previous = rows[-1]
        rows.append([0, previous[0] + 1 + previous[1],
                     previous[1] + 1 + previous[2]])
    assert all(row[1] == moves for moves, row in enumerate(rows))
    assert all(row[2] == moves * (moves + 1) // 2 for moves, row in enumerate(rows))
    return rows


def branch_budgets(points):
    rows = []
    last_safe = 0
    for used, first_break_floor in enumerate(points, 1):
        gap = first_break_floor - last_safe
        rows.append({
            "firstEggDropNumber": used,
            "previousKnownSafeFloor": last_safe,
            "firstBreakingFloor": first_break_floor,
            "gap": gap,
            "candidateFIntervalAfterBreak": [last_safe, first_break_floor - 1],
            "candidateFCount": gap,
            "secondEggUntestedFloors": list(range(last_safe + 1, first_break_floor)),
            "maximumSecondEggDrops": gap - 1,
            "totalWorstDropsIfFirstBreakHere": used + gap - 1,
        })
        last_safe = first_break_floor
    return rows


def verify():
    decreasing = strategy_report(DECREASING_POINTS)
    fixed_ten = strategy_report(TEN_POINTS)
    assert decreasing["maximumDrops"] == 14
    assert fixed_ten["maximumDrops"] == 19
    assert decreasing["edgeCases"]["F0"]["drops"] == 2
    assert decreasing["edgeCases"]["F100"]["drops"] == 12
    budgets = branch_budgets(DECREASING_POINTS)
    assert all(r["totalWorstDropsIfFirstBreakHere"] <= 14 for r in budgets)
    assert all(r["totalWorstDropsIfFirstBreakHere"] == 14 for r in budgets[:11])
    assert budgets[-1]["totalWorstDropsIfFirstBreakHere"] == 12
    example = simulate(100, 31, DECREASING_POINTS)
    assert [(e["floor"], e["broke"]) for e in example["events"]] == [
        (14, False), (27, False), (39, True), (28, False),
        (29, False), (30, False), (31, False), (32, True)]
    assert example["drops"] == 8 and example["inferredF"] == 31
    assert example["events"][2]["highestSafeFAfter"] == [27, 38]
    assert example["events"][2]["remainingEggs"] == 1
    assert budgets[2]["maximumSecondEggDrops"] == 11
    capacities = capacity_table()
    optimal_by_n = [interval_minimax(2, 0, n) for n in range(107)]
    assert optimal_by_n[100] == 14
    for n, minimum in enumerate(optimal_by_n):
        by_capacity = next(m for m, row in enumerate(capacities) if row[2] >= n)
        assert minimum == by_capacity
    assert [(n, optimal_by_n[n]) for n in (91, 92, 100, 105, 106)] == [
        (91, 13), (92, 14), (100, 14), (105, 14), (106, 15)]
    first_costs = {floor: 1 + max(interval_minimax(1, 0, floor - 1),
                                 interval_minimax(2, floor, 100))
                   for floor in range(1, 101)}
    optimal_first = [floor for floor, cost in first_costs.items() if cost == 14]
    assert optimal_first == list(range(9, 15))
    assert capacities[13][2] == 91 and capacities[14][2] == 105
    assert 91 + 1 < 101 <= 105 + 1
    stats = interval_minimax.cache_info()
    return {
        "status": "passed",
        "checkedAtBeijing": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "executor": "Codex /root/egg_math",
        "verifierSHA256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "model": {"floors": 100, "highestSafeFRange": [0, 100],
                  "possibleThresholdStates": 101, "identicalDeterministicEggs": True,
                  "unbrokenEggReusable": True, "brokenEggConsumed": True,
                  "objective": "minimize the guaranteed worst-case drops, not an average"},
        "decreasing": decreasing,
        "fixedTen": fixed_ten,
        "decreasingBreakBudgets": budgets,
        "exampleF31": example,
        "optimality": {"intervalMinimaxAt100": 14,
                       "independentNRangeChecked": [0, 106],
                       "independentNCount": 107,
                       "capacityRecurrence": "C(e,m)=C(e-1,m-1)+1+C(e,m-1)",
                       "capacityRows": [{"moves": m, "oneEggFloors": row[1],
                                         "twoEggFloors": row[2],
                                         "twoEggThresholdStates": row[2] + 1}
                                        for m, row in enumerate(capacities)],
                       "twoEgg13MovesFloors": 91, "twoEgg14MovesFloors": 105,
                       "optimalFirstFloorsAt100": optimal_first,
                       "intervalDPStates": stats.currsize,
                       "intervalDPCacheHits": stats.hits,
                       "lowerBoundScope": "arbitrary adaptive strategies, not only fixed checkpoints"},
        "limits": ["Finite exhaustive threshold checks verify the concrete routes.",
                   "The written recurrence proof establishes the general lower bound.",
                   "This program does not verify animation, narration or learner comprehension."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("qa-math.json"))
    args = parser.parse_args()
    report = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "thresholdsPerStrategy": 101,
                      "decreasingWorst": report["decreasing"]["maximumDrops"],
                      "fixedTenWorst": report["fixedTen"]["maximumDrops"],
                      "intervalOptimalAt100": report["optimality"]["intervalMinimaxAt100"],
                      "exampleDrops": report["exampleF31"]["drops"],
                      "report": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
