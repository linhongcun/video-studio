#!/usr/bin/env python3
"""Deterministic, single-owner teaching data; no network or media dependencies."""

from __future__ import annotations

import argparse
from bisect import bisect_left
from collections import Counter
import json
from pathlib import Path


SPACE = 100
HASHES = [5, 13, 27, 34, 46, 56, 64, 78, 86, 95]
NODES_BEFORE = [
    {"id": "A", "position": 20},
    {"id": "B", "position": 50},
    {"id": "C", "position": 85},
]
NODES_AFTER = [*NODES_BEFORE, {"id": "D", "position": 70}]
VNODE_POSITIONS = {"A": [5, 38, 72], "B": [15, 48, 82], "C": [28, 60, 94]}
VNODE_D_POSITIONS = [10, 34, 88]


def physical_tokens(nodes: list[dict]) -> list[dict]:
    return [dict(node, physicalId=node["id"]) for node in nodes]


def validate_tokens(tokens: list[dict], space: int) -> list[dict]:
    if type(space) is not int or space <= 0 or not tokens:
        raise ValueError("A positive integer space and a nonempty ring are required")
    positions, identifiers = set(), set()
    for token in tokens:
        position = token["position"]
        if type(position) is not int or not 0 <= position < space:
            raise ValueError("Token positions must be integers inside the fixed space")
        if position in positions or token["id"] in identifiers:
            raise ValueError("This teaching model requires unique token positions and IDs")
        if not isinstance(token["physicalId"], str) or not token["physicalId"]:
            raise ValueError("Every token must name exactly one physical owner")
        positions.add(position)
        identifiers.add(token["id"])
    return sorted(tokens, key=lambda token: token["position"])


def owners_for_space(tokens: list[dict], space: int = SPACE) -> list[str]:
    """Binary-search the clockwise successor, including a token at the key hash."""
    ordered = validate_tokens(tokens, space)
    positions = [token["position"] for token in ordered]
    return [
        ordered[bisect_left(positions, hash_value) % len(ordered)]["physicalId"]
        for hash_value in range(space)
    ]


def ring_state(tokens: list[dict], space: int = SPACE) -> dict:
    ordered = validate_tokens(tokens, space)
    owners = owners_for_space(ordered, space)
    intervals = []
    for index, token in enumerate(ordered):
        previous = ordered[index - 1]["position"]
        intervals.append({
            "tokenId": token["id"],
            "physicalId": token["physicalId"],
            "startExclusive": previous,
            "endInclusive": token["position"],
            "wraps": previous >= token["position"],
            "count": (token["position"] - previous) % space or space,
        })
    counts = Counter(owners)
    return {
        "tokens": ordered,
        "owners": owners,
        "intervalCounts": {node: counts[node] for node in sorted(counts)},
        "intervals": intervals,
    }


def transition(before: dict, after: dict, key_hashes: list[int]) -> dict:
    changed = [
        hash_value for hash_value, (old, new) in enumerate(zip(before["owners"], after["owners"]))
        if old != new
    ]
    keys = [f"K{index:02d}" for index, value in enumerate(key_hashes, 1) if value in changed]
    transfers = Counter((before["owners"][value], after["owners"][value]) for value in changed)
    return {
        "changedPositions": changed,
        "changedPositionCount": len(changed),
        "changedKeyIds": keys,
        "changedSampleCount": len(keys),
        "sampleCount": len(key_hashes),
        "transfers": [
            {"from": old, "to": new, "count": count}
            for (old, new), count in sorted(transfers.items())
        ],
    }


def build_model() -> dict:
    vnodes_before = [
        {"id": f"{physical}{index}", "physicalId": physical, "position": position}
        for physical, positions in VNODE_POSITIONS.items()
        for index, position in enumerate(positions, 1)
    ]
    vnodes_after = [*vnodes_before, *[
        {"id": f"D{index}", "physicalId": "D", "position": position}
        for index, position in enumerate(VNODE_D_POSITIONS, 1)
    ]]
    rings = {
        "before": ring_state(physical_tokens(NODES_BEFORE)),
        "after": ring_state(physical_tokens(NODES_AFTER)),
        "virtualBefore": ring_state(vnodes_before),
        "virtualAfter": ring_state(vnodes_after),
    }
    keys = [
        {
            "id": f"K{index:02d}", "hash": value,
            "modBefore": "ABC"[value % 3], "modAfter": "ABCD"[value % 4],
            "ringBefore": rings["before"]["owners"][value],
            "ringAfter": rings["after"]["owners"][value],
            "virtualBefore": rings["virtualBefore"]["owners"][value],
            "virtualAfter": rings["virtualAfter"]["owners"][value],
        }
        for index, value in enumerate(HASHES, 1)
    ]
    hot_key = keys[5]
    hot_owner = hot_key["virtualAfter"]
    return {
        "schemaVersion": 1,
        "space": SPACE,
        "scope": {
            "illustrativeHashes": True,
            "singleOwner": True,
            "fixedHashSpace": True,
            "existingTokenPositionsStayFixedDuringJoin": True,
            "collisionPolicy": "Distinct token positions are a precondition; collisions are not simulated.",
            "successorRule": "First token at position >= key hash; wrap to the first token.",
            "intervalConvention": "(predecessor position, token position]",
            "virtualNodesAreSeparatePreconfiguredExample": True,
            "virtualExampleRelationship": "Not an in-place conversion of the A20/B50/C85 ring.",
            "interpretation": "Mapping changes only; no replication, failure detector, data migration, or traffic benchmark.",
        },
        "keys": keys,
        "nodesBefore": NODES_BEFORE,
        "nodesAfter": NODES_AFTER,
        "vnodesBefore": vnodes_before,
        "vnodesAfter": vnodes_after,
        "rings": rings,
        "modulo": {
            "nodeOrderBefore": ["A", "B", "C"],
            "nodeOrderAfter": ["A", "B", "C", "D"],
            "changedKeyIds": [key["id"] for key in keys if key["modBefore"] != key["modAfter"]],
            "changedSampleCount": sum(key["modBefore"] != key["modAfter"] for key in keys),
            "sampleCount": len(keys),
            "sampleOnly": True,
        },
        "ringJoin": dict(transition(rings["before"], rings["after"], HASHES), addedPhysicalNode="D"),
        "ringRemoval": dict(transition(rings["after"], rings["before"], HASHES), removedPhysicalNode="D"),
        "virtualJoin": dict(transition(rings["virtualBefore"], rings["virtualAfter"], HASHES), addedPhysicalNode="D"),
        "virtualRemoval": dict(transition(rings["virtualAfter"], rings["virtualBefore"], HASHES), removedPhysicalNode="D"),
        "hotKey": {
            "id": hot_key["id"], "hash": hot_key["hash"],
            "ring": "virtualAfter", "owner": hot_owner, "ownerCount": 1,
            "illustrativeRequests": 10000,
            "requestsByPhysicalNode": {node: 10000 if node == hot_owner else 0 for node in "ABCD"},
            "sampleOnly": True,
            "interpretation": "Repeated requests for the same key retain one physical owner; virtual tokens do not split a hot key.",
        },
    }


def serialized_model() -> str:
    return json.dumps(build_model(), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check model.json without rewriting it")
    args = parser.parse_args()
    target = Path(__file__).with_name("model.json")
    content = serialized_model()
    if args.check:
        if not target.exists() or target.read_text() != content:
            raise SystemExit("FAIL: model.json differs from the deterministic generator")
        print("PASS: model.json matches its deterministic generator")
    else:
        target.write_text(content)
        print(f"Wrote {target}")


if __name__ == "__main__":
    main()
