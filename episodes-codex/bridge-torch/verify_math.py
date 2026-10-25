#!/usr/bin/env python3
"""Exact, unrestricted verification of the four-person bridge puzzle.

Both directions allow one OR two movers. No fixed number of crossings or
special shuttle pattern is assumed. Only Python's standard library is used.
Run from any working directory; --output writes the auditable JSON certificate.
"""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
from hashlib import sha256
from heapq import heappop, heappush
from itertools import combinations, permutations
import json
from math import inf
from pathlib import Path
from zoneinfo import ZoneInfo


PERSON_IDS = ("A", "B", "C", "D")
TIMES = (1, 2, 5, 10)
FULL_MASK = (1 << len(TIMES)) - 1
START = (0, 0)  # right-bank mask, torch side: 0 left / 1 right
GOAL = (FULL_MASK, 1)
STATES = tuple((mask, side) for mask in range(FULL_MASK + 1) for side in (0, 1))

# These are legal example paths, not restrictions imposed on the search.
INTUITIVE_19 = ((0, 1), (0,), (0, 2), (0,), (0, 3))
DEMONSTRATION_17 = ((0, 1), (0,), (2, 3), (1,), (0, 1))
OTHER_OPTIMAL_17 = ((0, 1), (1,), (2, 3), (0,), (0, 1))


def describe_state(state):
    mask, side = state
    left_indices = tuple(i for i in range(4) if not mask & (1 << i))
    right_indices = tuple(i for i in range(4) if mask & (1 << i))
    return {
        "rightMask": mask,
        "torchSide": "left" if side == 0 else "right",
        "left": [PERSON_IDS[i] for i in left_indices],
        "right": [PERSON_IDS[i] for i in right_indices],
        "leftMinutes": [TIMES[i] for i in left_indices],
        "rightMinutes": [TIMES[i] for i in right_indices],
    }


def build_graph_by_mover_subsets():
    graph = {}
    for state in STATES:
        mask, side = state
        available = tuple(i for i in range(4) if bool(mask & (1 << i)) == bool(side))
        edges = []
        for size in (1, 2):
            for movers in combinations(available, size):
                changed_bits = sum(1 << person for person in movers)
                next_state = (mask ^ changed_bits, 1 - side)
                edges.append((next_state, max(TIMES[i] for i in movers), movers))
        graph[state] = tuple(edges)
    return graph


def independently_build_graph_by_state_pairs():
    """Separate construction: inspect all 32 x 32 possible state pairs."""
    graph = {state: [] for state in STATES}
    for source in STATES:
        old_mask, old_torch = source
        for target in STATES:
            new_mask, new_torch = target
            if old_torch == new_torch:
                continue
            changed = old_mask ^ new_mask
            if changed.bit_count() not in (1, 2):
                continue
            movers = tuple(i for i in range(4) if changed & (1 << i))
            if any(((old_mask >> i) & 1) != old_torch for i in movers):
                continue
            duration = sorted(TIMES[i] for i in movers)[-1]
            graph[source].append((target, duration, movers))
    return {state: tuple(edges) for state, edges in graph.items()}


def edge_set(graph):
    return {
        (source, target, duration, movers)
        for source, edges in graph.items()
        for target, duration, movers in edges
    }


def dijkstra(graph):
    distances = {START: 0}
    predecessors = defaultdict(list)
    queue = [(0, START)]
    while queue:
        elapsed, state = heappop(queue)
        if elapsed != distances[state]:
            continue
        for target, duration, movers in graph[state]:
            candidate = elapsed + duration
            old = distances.get(target, inf)
            if candidate < old:
                distances[target] = candidate
                predecessors[target] = [(state, movers)]
                heappush(queue, (candidate, target))
            elif candidate == old:
                predecessors[target].append((state, movers))
    return distances, predecessors


def floyd_warshall(graph):
    distances = {(a, b): (0 if a == b else inf) for a in STATES for b in STATES}
    for source, edges in graph.items():
        for target, duration, _ in edges:
            distances[(source, target)] = min(distances[(source, target)], duration)
    for middle in STATES:
        for source in STATES:
            for target in STATES:
                candidate = distances[(source, middle)] + distances[(middle, target)]
                if candidate < distances[(source, target)]:
                    distances[(source, target)] = candidate
    return distances


def route_record(graph, groups):
    state = START
    elapsed = 0
    steps = []
    for index, movers in enumerate(groups, 1):
        movers = tuple(sorted(movers))
        matching = [(target, duration) for target, duration, group in graph[state] if group == movers]
        if len(matching) != 1:
            raise ValueError(f"illegal crossing {movers} from {state}")
        target, duration = matching[0]
        elapsed += duration
        steps.append({
            "step": index,
            "movers": [PERSON_IDS[i] for i in movers],
            "moverMinutes": [TIMES[i] for i in movers],
            "direction": "left_to_right" if state[1] == 0 else "right_to_left",
            "minutes": duration,
            "elapsedMinutes": elapsed,
            "before": describe_state(state),
            "after": describe_state(target),
        })
        state = target
    if state != GOAL:
        raise ValueError(f"route does not reach the goal: {state}")
    return {"totalMinutes": elapsed, "crossingCount": len(steps), "initial": describe_state(START), "steps": steps}


def optimal_move_sequences(predecessors, state=GOAL):
    if state == START:
        return [()]
    return [
        path + (movers,)
        for previous, movers in predecessors[state]
        for path in optimal_move_sequences(predecessors, previous)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write exact verification and lower-bound certificate as JSON")
    args = parser.parse_args()

    graph = build_graph_by_mover_subsets()
    independent_graph = independently_build_graph_by_state_pairs()
    edges = edge_set(graph)
    independent_edges = edge_set(independent_graph)
    assert edges == independent_edges
    assert len(STATES) == 32
    assert len(edges) == 112
    assert Counter(len(movers) for _, _, _, movers in edges) == {1: 64, 2: 48}
    assert all((target, source, minutes, movers) in edges for source, target, minutes, movers in edges)

    distances, predecessors = dijkstra(graph)
    independent_distances = floyd_warshall(independent_graph)
    assert len(distances) == 30
    assert set(STATES) - set(distances) == {(0, 1), (FULL_MASK, 0)}
    assert distances[START] == 0
    assert distances[GOAL] == 17
    assert all(distances.get(state, inf) == independent_distances[(START, state)] for state in STATES)
    assert all(source in distances and target in distances for source, target, _, _ in edges)

    # A complete lower-bound certificate, independently checkable without
    # trusting the shortest-path implementation: w >= phi(v) - phi(u).
    slacks = [minutes + distances[source] - distances[target] for source, target, minutes, _ in edges]
    assert len(slacks) == 112 and min(slacks) >= 0

    expected = route_record(graph, DEMONSTRATION_17)
    other = route_record(graph, OTHER_OPTIMAL_17)
    intuitive = route_record(graph, INTUITIVE_19)
    assert expected["totalMinutes"] == other["totalMinutes"] == 17
    assert intuitive["totalMinutes"] == 19
    assert [step["elapsedMinutes"] for step in expected["steps"]] == [2, 3, 13, 15, 17]
    assert [step["elapsedMinutes"] for step in intuitive["steps"]] == [2, 3, 8, 9, 19]
    assert [step["elapsedMinutes"] for step in other["steps"]] == [2, 4, 14, 15, 17]

    sequences = optimal_move_sequences(predecessors)
    assert len(sequences) == 2
    assert set(sequences) == {DEMONSTRATION_17, OTHER_OPTIMAL_17}
    all_optimal_paths = [route_record(graph, groups) for groups in sequences]
    assert all(path["totalMinutes"] == 17 for path in all_optimal_paths)

    # Every possible order of the fastest-person escort idea costs 19.
    escort_cases = []
    for order in permutations((1, 2, 3)):
        moves = []
        for index, companion in enumerate(order):
            moves.append((0, companion))
            if index != len(order) - 1:
                moves.append((0,))
        record = route_record(graph, moves)
        assert record["totalMinutes"] == 19
        escort_cases.append({"companionOrderMinutes": [TIMES[i] for i in order], "totalMinutes": 19})
    assert len(escort_cases) == 6

    certificate = [
        {**describe_state(state), "potential": distances[state]}
        for state in sorted(distances)
    ]
    result = {
        "status": "passed",
        "executedAt": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "executor": "/root/puzzle_batch_a",
        "verifierSha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "model": {
            "people": [{"id": identifier, "minutes": minutes} for identifier, minutes in zip(PERSON_IDS, TIMES)],
            "stateEncoding": "(rightMask, torchSide), bit i is 1 iff person i is right; side 0=left,1=right",
            "start": describe_state(START),
            "goal": describe_state(GOAL),
            "moveRule": "one or two people on the torch's bank cross completely together; torch crosses with them; duration=max(person times)",
            "allowsOneOrTwoMoversInBothDirections": True,
            "assumedFixedNumberOfCrossings": False,
            "allowsTorchTeleportOrMidBridgeRelay": False,
        },
        "exactGraphChecks": {
            "syntacticStateCount": len(STATES),
            "reachableStateCount": len(distances),
            "unreachableSyntacticStates": [describe_state(state) for state in sorted(set(STATES) - set(distances))],
            "directedLegalMoveCount": len(edges),
            "onePersonDirectedMoves": 64,
            "twoPersonDirectedMoves": 48,
            "independentStatePairsChecked": len(STATES) ** 2,
            "independentEdgeConstructionMatches": True,
            "reverseEdgeChecksPassed": True,
            "dijkstraFloydWarshallDistancesMatchAtEveryState": True,
        },
        "conclusions": {
            "shortestMinutes": distances[GOAL],
            "goalReachableWithin16Minutes": False,
            "optimalPathCount": len(sequences),
            "fastestPersonEscortMinutes": 19,
            "fastestPersonEscortCompanionOrdersChecked": len(escort_cases),
        },
        "routes": {
            "intuitive19": intuitive,
            "demonstration17": expected,
            "otherOptimal17": other,
            "allOptimalPaths": all_optimal_paths,
            "fastestPersonEscortOrders": escort_cases,
        },
        "lowerBoundCertificate": {
            "definition": "phi(state)=the integer potential in reachableStatePotentials",
            "startPotential": distances[START],
            "goalPotential": distances[GOAL],
            "inequality": "phi(v) <= phi(u) + duration for every legal directed edge u->v",
            "edgesChecked": len(slacks),
            "minimumEdgeSlack": min(slacks),
            "allInequalitiesPassed": True,
            "whyThisProvesLowerBound": "summing duration >= phi(v)-phi(u) along any start-to-goal walk telescopes to total >= 17-0",
            "reachableStatePotentials": certificate,
        },
        "scopeLimits": [
            "Exact verification of this fixed four-person bank-to-bank model; not a claim about arbitrary times, capacities or relay rules.",
            "No random sampling: every state and legal move of this model is represented.",
            "Does not inspect animation, audio, encoded media, web pages or user understanding.",
            "Reads no external code or network resources at execution time.",
        ],
    }
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
        print(json.dumps({
            "status": "passed",
            "output": str(args.output),
            "shortestMinutes": 17,
            "reachableStates": 30,
            "directedMoves": 112,
            "optimalPaths": 2,
            "edgeCertificateChecks": 112,
            "verifierSha256": result["verifierSha256"],
        }, ensure_ascii=False))
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
