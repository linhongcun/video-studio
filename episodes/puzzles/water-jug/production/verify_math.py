#!/usr/bin/env python3
"""Exact verification of the 3 L / 5 L water-jug model; no external code.

State: (litres in the 3 L jug, litres in the 5 L jug).
Each non-noop fill, empty, or maximal pour costs one operation.
The main goal is ONLY: the 5 L jug contains 4 L; the other jug may retain water.
"""

import argparse
from collections import defaultdict, deque
from datetime import datetime
from hashlib import sha256
from itertools import product
import json
from math import inf
from pathlib import Path
from zoneinfo import ZoneInfo


CAPACITIES = (3, 5)
START = (0, 0)
STATES = tuple(product(range(4), range(6)))
ACTIONS = ("fill3", "fill5", "empty3", "empty5", "pour3to5", "pour5to3")
DEMONSTRATION = ("fill5", "pour5to3", "empty3", "pour5to3", "fill5", "pour5to3")
EXPECTED_STATES = ((0, 0), (0, 5), (3, 2), (0, 2), (2, 0), (2, 5), (3, 4))


def transition(state, action):
    a, b = state
    source_litres = drain_litres = transferred = 0
    if action == "fill3":
        target = (3, b)
        source_litres = 3 - a
    elif action == "fill5":
        target = (a, 5)
        source_litres = 5 - b
    elif action == "empty3":
        target = (0, b)
        drain_litres = a
    elif action == "empty5":
        target = (a, 0)
        drain_litres = b
    elif action == "pour3to5":
        transferred = min(a, 5 - b)
        target = (a - transferred, b + transferred)
    elif action == "pour5to3":
        transferred = min(b, 3 - a)
        target = (a + transferred, b - transferred)
    else:
        raise ValueError(f"unknown operation: {action}")
    return target, source_litres, drain_litres, transferred


def independently_simulate_one_litre_at_a_time(state, action):
    """Independent transition construction, without using min() or transition()."""
    water = list(state)
    inflow = outflow = transferred = 0
    if action in ("fill3", "fill5"):
        index = 0 if action == "fill3" else 1
        while water[index] < CAPACITIES[index]:
            water[index] += 1
            inflow += 1
    elif action in ("empty3", "empty5"):
        index = 0 if action == "empty3" else 1
        while water[index] > 0:
            water[index] -= 1
            outflow += 1
    else:
        source, target = (0, 1) if action == "pour3to5" else (1, 0)
        while water[source] > 0 and water[target] < CAPACITIES[target]:
            water[source] -= 1
            water[target] += 1
            transferred += 1
    return tuple(water), inflow, outflow, transferred


def build_graph(operation):
    graph = {}
    for state in STATES:
        moves = []
        for action in ACTIONS:
            target, inflow, outflow, transferred = operation(state, action)
            if target != state:
                moves.append((target, action, inflow, outflow, transferred))
        graph[state] = tuple(moves)
    return graph


def bfs(graph):
    distances = {START: 0}
    predecessors = defaultdict(list)
    queue = deque([START])
    while queue:
        state = queue.popleft()
        for target, action, _, _, _ in graph[state]:
            candidate = distances[state] + 1
            if target not in distances:
                distances[target] = candidate
                predecessors[target] = [(state, action)]
                queue.append(target)
            elif candidate == distances[target]:
                predecessors[target].append((state, action))
    return distances, predecessors


def floyd_warshall(graph):
    distances = {(a, b): (0 if a == b else inf) for a in STATES for b in STATES}
    for source, moves in graph.items():
        for target, _, _, _, _ in moves:
            distances[(source, target)] = 1
    for middle in STATES:
        for source in STATES:
            for target in STATES:
                candidate = distances[(source, middle)] + distances[(middle, target)]
                if candidate < distances[(source, target)]:
                    distances[(source, target)] = candidate
    return distances


def shortest_action_sequences(predecessors, target):
    if target == START:
        return [()]
    return [
        prefix + (action,)
        for previous, action in predecessors[target]
        for prefix in shortest_action_sequences(predecessors, previous)
    ]


def stop_reasons(target, action):
    if action.startswith("fill"):
        return ["filled_jug_is_full"]
    if action.startswith("empty"):
        return ["emptied_jug_is_empty"]
    source, receiver = (0, 1) if action == "pour3to5" else (1, 0)
    return [
        reason
        for reason, holds in (
            ("pouring_source_jug_is_empty", target[source] == 0),
            ("receiving_jug_is_full", target[receiver] == CAPACITIES[receiver]),
        )
        if holds
    ]


def route_record(actions):
    state = START
    states = [state]
    source_total = drain_total = 0
    steps = []
    for index, action in enumerate(actions, 1):
        target, inflow, outflow, transferred = transition(state, action)
        assert target != state
        assert (target, inflow, outflow, transferred) == independently_simulate_one_litre_at_a_time(state, action)
        assert all(0 <= value <= capacity for value, capacity in zip(target, CAPACITIES))
        assert sum(target) - sum(state) == inflow - outflow
        reasons = stop_reasons(target, action)
        assert reasons
        source_total += inflow
        drain_total += outflow
        assert source_total - drain_total == sum(target)
        steps.append({
            "step": index,
            "action": action,
            "before": list(state),
            "after": list(target),
            "jug3DeltaLitres": target[0] - state[0],
            "jug5DeltaLitres": target[1] - state[1],
            "sourceInflowLitres": inflow,
            "drainOutflowLitres": outflow,
            "interJugTransferLitres": transferred,
            "stopReasons": reasons,
            "totalWaterBeforeLitres": sum(state),
            "totalWaterAfterLitres": sum(target),
            "cumulativeSourceLitres": source_total,
            "cumulativeDrainLitres": drain_total,
            "massBalancePassed": True,
        })
        state = target
        states.append(state)
    return {
        "operationCount": len(actions),
        "actions": list(actions),
        "states": [list(value) for value in states],
        "steps": steps,
        "finalState": list(state),
        "fiveLitreJugHasExactlyFour": state[1] == 4,
        "combinedTotalIsFour": sum(state) == 4,
        "waterAccounting": {
            "sourceLitres": source_total,
            "drainLitres": drain_total,
            "finalTotalLitres": sum(state),
            "finalJug3Litres": state[0],
            "finalJug5Litres": state[1],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write auditable JSON verification and certificate")
    args = parser.parse_args()

    # Check all 24 integer states and all six attempted operations, including
    # noops, before removing noops from the shortest-path graph.
    for state, action in product(STATES, ACTIONS):
        actual = transition(state, action)
        assert actual == independently_simulate_one_litre_at_a_time(state, action)
        target, inflow, outflow, transferred = actual
        assert target in STATES
        assert sum(target) - sum(state) == inflow - outflow
        if action.startswith("pour"):
            assert inflow == outflow == 0
            assert (target == state) == (transferred == 0)
            if target != state:
                assert stop_reasons(target, action)

    graph = build_graph(transition)
    independent_graph = build_graph(independently_simulate_one_litre_at_a_time)
    assert graph == independent_graph
    assert sum(len(moves) for moves in graph.values()) == 106
    distances, predecessors = bfs(graph)
    independent_distances = floyd_warshall(independent_graph)
    assert len(distances) == 16
    assert all(distances.get(state, inf) == independent_distances[(START, state)] for state in STATES)
    assert all(a in (0, 3) or b in (0, 5) for a, b in distances)
    assert {state for state in STATES if state not in distances} == set(product((1, 2), (1, 2, 3, 4)))

    reachable_edges = [
        (source, target, action)
        for source in distances
        for target, action, _, _, _ in graph[source]
    ]
    assert len(reachable_edges) == 58
    assert all(target in distances for _, target, _ in reachable_edges)
    main_goals = sorted(state for state in distances if state[1] == 4)
    combined_goals = sorted(state for state in distances if sum(state) == 4)
    assert main_goals == [(0, 4), (3, 4)]
    assert combined_goals == [(0, 4), (3, 1)]
    assert min(distances[state] for state in main_goals) == 6
    assert min(distances[state] for state in combined_goals) == 7

    demo = route_record(DEMONSTRATION)
    assert demo["states"] == [list(state) for state in EXPECTED_STATES]
    assert demo["operationCount"] == 6
    assert demo["fiveLitreJugHasExactlyFour"] and not demo["combinedTotalIsFour"]
    assert [step["interJugTransferLitres"] for step in demo["steps"] if step["action"].startswith("pour")] == [3, 2, 1]
    assert demo["waterAccounting"] == {"sourceLitres": 10, "drainLitres": 3, "finalTotalLitres": 7, "finalJug3Litres": 3, "finalJug5Litres": 4}
    combined_example = route_record(DEMONSTRATION + ("empty3",))
    assert combined_example["operationCount"] == 7 and combined_example["combinedTotalIsFour"]

    best_main_goals = [state for state in main_goals if distances[state] == 6]
    best_sequences = [sequence for state in best_main_goals for sequence in shortest_action_sequences(predecessors, state)]
    assert best_sequences == [DEMONSTRATION]

    # Feasible potentials certify a lower bound independently of trusting BFS.
    slacks = [1 + distances[source] - distances[target] for source, target, _ in reachable_edges]
    assert len(slacks) == 58 and min(slacks) >= 0
    layers = [
        {"operations": level, "states": [list(state) for state in sorted(distances) if distances[state] == level]}
        for level in range(max(distances.values()) + 1)
    ]
    assert all(state[1] != 4 for state, level in distances.items() if level < 6)

    result = {
        "status": "passed",
        "executedAt": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "executor": "/root/puzzle_batch_a",
        "verifierSha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "model": {
            "capacitiesLitres": list(CAPACITIES),
            "stateEncoding": "[water in 3 L jug, water in 5 L jug]",
            "start": list(START),
            "mainGoal": "the 5 L jug contains exactly 4 L; the 3 L jug may contain water",
            "sourceAndDrainAllowed": True,
            "actions": list(ACTIONS),
            "pourRule": "pour until the source jug is empty or the receiving jug is full, whichever happens first",
            "operationCost": 1,
            "noopsExcludedFromSearch": True,
        },
        "exactGraphChecks": {
            "syntacticIntegerStateCount": len(STATES),
            "attemptedStateActionPairsChecked": len(STATES) * len(ACTIONS),
            "allIntegerStatesNonNoopDirectedOperations": 106,
            "reachableStateCount": len(distances),
            "reachableNonNoopDirectedOperations": len(reachable_edges),
            "unreachableInteriorStates": [list(state) for state in sorted(set(STATES) - set(distances))],
            "independentOneLitreSimulationMatchesEveryOperation": True,
            "bfsFloydWarshallDistancesMatchAtEveryIntegerState": True,
            "allCapacityStopAndMassBalanceChecksPassed": True,
        },
        "conclusions": {
            "minimumOperationsForFiveLitreJugFour": 6,
            "shortestMainGoalRouteCount": len(best_sequences),
            "mainGoalStates": [{"state": list(state), "distance": distances[state]} for state in main_goals],
            "differentCombinedTotalFourGoal": {
                "minimumOperations": 7,
                "states": [{"state": list(state), "distance": distances[state]} for state in combined_goals],
                "notTheVideoGoal": True,
            },
        },
        "demonstration": demo,
        "differentCombinedTotalFourExample": combined_example,
        "bfsLayers": layers,
        "lowerBoundCertificate": {
            "definition": "phi(state) is the integer in reachableStatePotentials",
            "inequality": "phi(target) <= phi(source) + 1 for every legal non-noop operation",
            "startPotential": distances[START],
            "minimumMainGoalPotential": min(distances[state] for state in main_goals),
            "minimumCombinedGoalPotential": min(distances[state] for state in combined_goals),
            "edgesChecked": len(slacks),
            "minimumEdgeSlack": min(slacks),
            "allInequalitiesPassed": True,
            "reachableStatePotentials": [{"state": list(state), "potential": distances[state]} for state in sorted(distances)],
            "whyThisProvesLowerBound": "sum 1 >= phi(next)-phi(current) along any route; the sum telescopes, so reaching any main-goal state costs at least 6 operations",
        },
        "scopeLimits": [
            "Exact complete finite-state verification for 3 L and 5 L, empty start, full-fill/full-empty/maximal-pour rules only.",
            "Integers are exhaustive here: every permitted operation preserves integer volumes starting at zero.",
            "One-litre unit simulation is an independent verifier, not permission to stop a real pouring operation after one litre.",
            "Operation count is not elapsed time, amount of water consumed, or a general GCD theorem.",
            "No random sampling or external-code execution; does not inspect production visuals, voice, media or web pages.",
        ],
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
        print(json.dumps({"status": "passed", "output": str(args.output), "reachableStates": 16, "reachableOperations": 58, "mainGoalMinimumOperations": 6, "differentCombinedGoalMinimumOperations": 7, "sourceLitres": 10, "drainLitres": 3, "finalTotalLitres": 7, "verifierSha256": result["verifierSha256"]}, ensure_ascii=False))
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
