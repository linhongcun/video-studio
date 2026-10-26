#!/usr/bin/env python3
"""Reproducible single-position Bloom teaching example, not a production library."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


def position(key: str, seed: int = 22) -> int:
    digest = sha256(f"{seed}:{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % 8


def build(keys, seeds=(22,)):
    bits = [0] * 8
    for key in keys:
        for seed in seeds:
            bits[position(key, seed)] = 1
    return bits


def query(bits, key, seeds=(22,)):
    checked = []
    for seed in seeds:
        index = position(key, seed)
        checked.append(index)
        if bits[index] == 0:
            return {"result": False, "checked": checked, "stopsAt": index}
    return {"result": True, "checked": checked}


def ones(bits):
    return [index for index, value in enumerate(bits) if value == 1]


def demonstrate():
    first = {key: position(key) for key in "ABCD"}
    second = {key: position(key, 0) for key in "ABCD"}
    assert first == {"A": 3, "B": 3, "C": 3, "D": 7}
    assert second == {"A": 2, "B": 1, "C": 5, "D": 5}
    single = build("AB")
    assert ones(build("A")) == ones(single) == [3]
    queries = {key: {**query(single, key), "truthContains": key in "AB"}
               for key in "ABCD"}
    assert queries["D"]["result"] is False and queries["C"]["result"] is True
    assert all(queries[key]["result"] for key in "AB")

    # Invalid clearing experiment; this is NOT a supported deletion method.
    wrong = single.copy()
    wrong[position("A")] = 0
    assert ones(wrong) == [] and query(wrong, "B")["result"] is False

    # Separate complete rebuild of the SAME A/B set under the two-position rule.
    double = build("AB", seeds=(22, 0))
    double_queries = {key: {**query(double, key, seeds=(22, 0)), "truthContains": key in "AB"}
                      for key in "ABCD"}
    assert ones(double) == [1, 2, 3]
    assert all(double_queries[key]["result"] for key in "AB")
    assert double_queries["C"] == {"result": False, "checked": [3, 5],
                                    "stopsAt": 5, "truthContains": False}

    # Review guard only: more positions do not improve every individual query.
    assert [position("H"), position("H", 0)] == [1, 1]
    assert query(single, "H")["result"] is False
    assert query(double, "H", seeds=(22, 0))["result"] is True
    return {
        "status": "passed", "scope": "Fixed teaching logic; no production FPP measurement.",
        "bitCount": 8, "hashCount": 1, "firstPositions": first, "secondPositions": second,
        "snapshots": {"empty": [], "afterA": ones(build("A")),
                      "afterB": ones(single), "wronglyClearedA": ones(wrong)},
        "queries": queries, "wrongDeletionQueryB": query(wrong, "B"),
        "comparison": {"seeds": [22, 0], "inserted": ["A", "B"],
                       "snapshots": {"empty": [], "afterA": ones(build("A", (22, 0))),
                                     "afterB": ones(double)}, "queries": double_queries},
        "guardCounterexample": {"key": "H", "positions": [1, 1],
                                "single": query(single, "H"),
                                "double": query(double, "H", (22, 0)), "truthContains": False},
        "productionFPPMeasured": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, help="Optional production-model agreement check")
    args = parser.parse_args()
    result = demonstrate()
    if args.model:
        model = json.loads(args.model.read_text())
        assert model["bitCount"] == result["bitCount"] and model["hashCount"] == 1
        assert model["hash"]["seeds"] == [22]
        assert result["snapshots"] == model["snapshots"]
        assert result["queries"] == model["queries"]
        for item in model["items"]:
            assert item["positions"] == [result["firstPositions"][item["key"]]]
            assert item["comparisonPositions"] == [result["firstPositions"][item["key"]],
                                                    result["secondPositions"][item["key"]]]
        assert result["comparison"]["snapshots"] == model["comparison"]["snapshots"]
        assert result["comparison"]["queries"] == model["comparison"]["queries"]
        assert result["wrongDeletionQueryB"] == model["wrongDeletion"]["queryB"]
        assert result["guardCounterexample"] == model["guardCounterexample"]
        result["modelAgreement"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2))
