#!/usr/bin/env python3
"""Fixed 16-bit Bloom teaching demo; no product or probability benchmark."""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


def positions(key: str) -> list[int]:
    return [
        int.from_bytes(sha256(f"{seed}:{key}".encode("utf-8")).digest()[:8], "big") % 16
        for seed in range(3)
    ]


class BloomDemo:
    def __init__(self) -> None:
        self.bits = [0] * 16

    def add(self, key: str) -> None:
        for index in positions(key):
            self.bits[index] = 1

    def query(self, key: str) -> tuple[bool, list[int]]:
        checked = []
        for index in positions(key):
            checked.append(index)
            if self.bits[index] == 0:
                return False, checked
        return True, checked

    def ones(self) -> list[int]:
        return [index for index, value in enumerate(self.bits) if value == 1]


def demonstrate() -> dict:
    expected = {
        "sku101": [3, 14, 15], "sku205": [0, 3, 12],
        "sku001": [12, 2, 15], "sku067": [14, 0, 15],
    }
    mapping = {key: positions(key) for key in expected}
    assert mapping == expected
    bloom = BloomDemo()
    assert bloom.ones() == []
    bloom.add("sku101")
    after101 = bloom.ones()
    assert after101 == [3, 14, 15]
    bloom.add("sku205")
    assert bloom.ones() == [0, 3, 12, 14, 15]
    catalog = {"sku101", "sku205"}
    queries = []
    for key in expected:
        maybe, checked = bloom.query(key)
        queries.append({"key": key, "positions": mapping[key], "checked": checked,
                        "possiblyPresent": maybe, "catalogContains": key in catalog})
    assert bloom.query("sku001") == (False, [12, 2])
    assert bloom.query("sku067") == (True, [14, 0, 15])
    assert all(bloom.query(key)[0] for key in catalog)

    # Invalid experiment: this is NOT a supported deletion operation.
    wrong = deepcopy(bloom)
    for index in positions("sku101"):
        wrong.bits[index] = 0
    remaining_catalog = catalog - {"sku101"}
    assert "sku205" in remaining_catalog
    assert wrong.ones() == [0, 12]
    assert wrong.query("sku205") == (False, [0, 3])

    # Separate maintenance scenario: new real item, stale filter, then repair.
    new_catalog = catalog | {"sku001"}
    maintained = deepcopy(bloom)
    stale = maintained.query("sku001")
    assert "sku001" in new_catalog and stale == (False, [12, 2])
    maintained.add("sku001")
    assert maintained.ones() == [0, 2, 3, 12, 14, 15]
    assert maintained.query("sku001") == (True, [12, 2, 15])

    return {
        "scope": "Fixed teaching example; not Redis/Guava internals or a production FPP measurement.",
        "bitCount": 16, "hashCount": 3, "mapping": mapping,
        "snapshots": {"empty": [], "after101": after101, "after205": bloom.ones(),
                      "wronglyCleared101": wrong.ones(),
                      "afterCorrectlyAdding001": maintained.ones()},
        "queries": queries,
        "invalidDeletion": {"remainingCatalog": sorted(remaining_catalog),
                            "query205": {"possiblyPresent": False, "checked": [0, 3]},
                            "classification": "invalid clearing causes false negative"},
        "staleInsertion": {"catalogContains001": True, "possiblyPresent": stale[0],
                           "checked": stale[1], "classification": "stale filter is unsafe"},
        "correctInsertion": {"catalogContains001": True, "possiblyPresent": True,
                             "checked": [12, 2, 15]},
        "productionFPPMeasured": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, help="Optional film-model agreement check")
    args = parser.parse_args()
    result = demonstrate()
    if args.model:
        model = json.loads(args.model.read_text())
        assert result["bitCount"] == model["bitCount"]
        assert result["hashCount"] == model["hashCount"]
        assert result["mapping"] == {item["key"]: item["positions"] for item in model["items"]}
        assert result["snapshots"] == model["snapshots"]
        assert model["catalogInitially"] == ["sku101", "sku205"]
        for query in result["queries"]:
            if query["key"] in model["catalogInitially"]:
                assert query["possiblyPresent"] is True
        assert result["queries"][2]["checked"] == model["expected"]["negative001"]["checked"]
        assert result["queries"][3]["checked"] == model["expected"]["positive067"]["checked"]
        result["filmModelAgreement"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2))
