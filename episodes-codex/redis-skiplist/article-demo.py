#!/usr/bin/env python3
"""Two-level forward-link teaching model; no Redis service/RNG/benchmark claim."""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

BASE = [10, 20, 30, 40, 50, 60, 70, 80]


def initial_links():
    return [dict(zip(["HEAD", *BASE], [*BASE, None])),
            {"HEAD": 40, 40: 70, 70: None}]


def order(links, level):
    result = []
    node = links[level]["HEAD"]
    while node is not None:
        assert node in links[level] and node not in result
        result.append(node)
        node = links[level][node]
    return result


def locate(links, target):
    cursor = "HEAD"
    previous = [None, None]
    events = []
    for level in (1, 0):
        next_node = links[level][cursor]
        while next_node is not None:
            can_advance = next_node < target
            events.append({"level": level, "current": cursor,
                           "next": next_node, "canAdvance": can_advance})
            if not can_advance:
                break
            cursor = next_node
            next_node = links[level][cursor]
        previous[level] = cursor
    return previous, events


def public_snapshot(links):
    return {"levels": [order(links, level) for level in (0, 1)],
            "links": [[{"from": node, "to": nxt} for node, nxt in row.items()]
                      for row in deepcopy(links)]}


def demonstrate(model=None):
    links = initial_links()
    before = deepcopy(links)
    previous, events = locate(links, 55)
    assert previous == [50, 40]
    assert [e["next"] for e in events] == [40, 70, 50, 60]
    assert [e["current"] for e in events] == ["HEAD", 40, 40, 50]
    writes = []
    for level in (0, 1):
        pred = previous[level]
        successor = links[level][pred]
        links[level][55] = successor
        writes.append({"level": level, "node": 55, "to": successor})
        links[level][pred] = 55
        writes.append({"level": level, "node": pred, "to": 55})
    assert order(links, 0) == [10, 20, 30, 40, 50, 55, 60, 70, 80]
    assert order(links, 1) == [40, 55, 70]
    assert order(before, 0) == BASE and order(before, 1) == [40, 70]
    assert 55 not in before[0] and 55 not in before[1]
    assert before[0][50] == 60 and before[1][40] == 70
    assert links[0][55] == 60 and links[1][55] == 70
    linear = []
    node = before[0]["HEAD"]
    while node is not None:
        linear.append(node)
        if node >= 55:
            break
        node = before[0][node]
    assert linear == [10, 20, 30, 40, 50, 60]
    agreement = None
    if model:
        root = json.loads(model.read_text())
        identify = lambda n: "head" if n == "HEAD" else None if n is None else f"n{n}"
        for stage, observed in [("before", before), ("after", links)]:
            expected = root[stage]
            assert expected["levels"] == [[identify(n) for n in order(observed, l)]
                                          for l in (0, 1)]
            for level in (0, 1):
                for old_node, next_node in observed[level].items():
                    assert expected["nodes"][identify(old_node)]["forward"][level] == identify(next_node)
        assert root["search"]["predecessors"] == [identify(n) for n in previous]
        assert root["search"]["comparisonCount"] == len(events) == 4
        assert [e["candidateValue"] for e in root["search"]["events"]] == [40, 70, 50, 60]
        agreement = {"status": "passed", "sha256": hashlib.sha256(model.read_bytes()).hexdigest()}
    return {"status": "passed", "scope": "Distinct-score forward links only; not real Redis or RNG playback.",
            "before": public_snapshot(before), "events": events,
            "predecessors": previous, "pointerWrites": writes,
            "after": public_snapshot(links), "linearComparisons": len(linear),
            "skipComparisons": len(events), "modelAgreement": agreement,
            "snapshotsIndependent": True, "productionRedisRun": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path)
    args = parser.parse_args()
    print(json.dumps(demonstrate(args.model), ensure_ascii=False, indent=2))
