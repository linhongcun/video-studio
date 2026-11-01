#!/usr/bin/env python3
"""Independent, deterministic review of the Bloom teaching model.

This checker imports no episode production or article implementation. Integer
bit operations are checked against a set-of-positions oracle. Hash positions
use hexadecimal decoding rather than the producer's int.from_bytes expression.
The configuration matrix is a bounded property check, not a product benchmark.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


D = Path(__file__).resolve().parent
COUNTS: Counter[str] = Counter()


def check(condition: bool, category: str, detail: object = None) -> None:
    COUNTS[category] += 1
    if not condition:
        raise AssertionError((category, detail))


def positions(key: str, m: int, k: int) -> tuple[int, ...]:
    return tuple(
        int(hashlib.sha256((str(seed) + ":" + key).encode("utf-8")).hexdigest()[:16], 16) % m
        for seed in range(k)
    )


def add(mask: int, locations: tuple[int, ...]) -> int:
    for location in locations:
        mask |= 1 << location
    return mask


def query(mask: int, locations: tuple[int, ...]) -> tuple[bool, list[int]]:
    visited: list[int] = []
    for location in locations:
        visited.append(location)
        if mask & (1 << location) == 0:
            return False, visited
    return True, visited


def ones(mask: int, m: int) -> list[int]:
    return [index for index in range(m) if mask & (1 << index)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_review(model: dict) -> dict:
    check(model["bitCount"] == 16 and model["hashCount"] == 3, "fixture", "configuration")
    check(model["hash"]["seeds"] == [0, 1, 2], "fixture", "seeds")
    check(model["hash"]["algorithm"] == "SHA-256" and model["hash"]["modulus"] == 16,
          "fixture", "hash definition")
    expected_locations = {
        "sku101": (3, 14, 15), "sku205": (0, 3, 12),
        "sku001": (12, 2, 15), "sku067": (14, 0, 15),
    }
    calculated = {key: positions(key, 16, 3) for key in expected_locations}
    for key, expected in expected_locations.items():
        check(calculated[key] == expected, "fixture", (key, calculated[key]))
    declared = {item["key"]: tuple(item["positions"]) for item in model["items"]}
    check(declared == calculated, "fixture", "declared locations")
    check(model["catalogInitially"] == ["sku101", "sku205"], "fixture", "catalog")

    empty = 0
    first = add(empty, calculated["sku101"])
    both = add(first, calculated["sku205"])
    erased = both
    for location in calculated["sku101"]:
        erased &= ~(1 << location)
    repaired = add(both, calculated["sku001"])
    states = {"empty": empty, "after101": first, "after205": both,
              "wronglyCleared101": erased, "afterCorrectlyAdding001": repaired}
    for name, mask in states.items():
        check(ones(mask, 16) == model["snapshots"][name], "fixture", name)
    check(ones(both, 16) == [0, 3, 12, 14, 15], "fixture", "normal final state")
    check(add(both, calculated["sku205"]) == both, "fixture", "shared bit stays one")

    observed = {
        "negative001": query(both, calculated["sku001"]),
        "known101": query(both, calculated["sku101"]),
        "positive067": query(both, calculated["sku067"]),
        "wrongDeletion205": query(erased, calculated["sku205"]),
        "stale001": query(both, calculated["sku001"]),
        "afterCorrectlyAdding001": query(repaired, calculated["sku001"]),
    }
    for name, (result, trace) in observed.items():
        expected = model["expected"][name]
        check(result is expected["result"], "fixture", (name, "result"))
        if "checked" in expected:
            check(trace == expected["checked"], "fixture", (name, "trace"))
        if "stopsAt" in expected:
            check(not result and trace[-1] == expected["stopsAt"], "fixture", (name, "stop"))
    check(observed["negative001"] == (False, [12, 2]), "fixture", "do not probe 15 after zero")
    check(observed["positive067"] == (True, [14, 0, 15]), "fixture", "actual all-one result")
    check("sku067" not in model["catalogInitially"], "fixture", "false positive ground truth")
    check({14, 15} <= set(calculated["sku101"]) and 0 in calculated["sku205"],
          "fixture", "067 has marks from two other keys")
    check(3 in calculated["sku101"] and 3 in calculated["sku205"], "fixture", "shared position")
    check("sku205" in model["catalogInitially"] and not observed["wrongDeletion205"][0],
          "fixture", "wrong clear hurts a retained key")
    changed_catalog = set(model["catalogInitially"]) | {"sku001"}
    check("sku001" in changed_catalog and not observed["stale001"][0],
          "fixture", "stale filter contradicts new catalog")
    for key in changed_catalog:
        check(query(repaired, calculated[key])[0], "fixture", ("after repair", key))
    return {
        "positions": {key: list(value) for key, value in calculated.items()},
        "states": {name: ones(mask, 16) for name, mask in states.items()},
        "queryResults": {name: {"result": result, "checked": trace}
                         for name, (result, trace) in observed.items()},
        "explicitCounterexamples": [
            "sku067 is absent but all three tested positions are set.",
            "Destructively clearing sku101 changes shared position 3 and wrongly rejects sku205.",
            "Adding sku001 only to the catalog leaves the old filter unsafe; adding its marks repairs membership.",
        ],
    }


def property_matrix() -> list[dict]:
    rows: list[dict] = []
    capacities = (1, 2, 7, 16, 31, 64, 127)
    hash_counts = (1, 2, 3, 5, 8)
    checkpoints = (0, 1, 2, 8, 32, 128)
    inserted_keys = [f"member:{i:04d}" for i in range(126)] + ["商品一零一", "商品:205:目录"]
    absent_keys = [f"not-in-catalog:{i:04d}" for i in range(256)]
    for m in capacities:
        for k in hash_counts:
            member_locations = [positions(key, m, k) for key in inserted_keys]
            outsider_locations = [positions(key, m, k) for key in absent_keys]
            check(set(inserted_keys).isdisjoint(absent_keys), "matrix-domain", (m, k))
            for locations in member_locations + outsider_locations:
                check(len(locations) == k and all(0 <= loc < m for loc in locations),
                      "hash-range", (m, k, locations))
            mask = 0
            oracle: set[int] = set()
            already_added = 0
            for n in checkpoints:
                while already_added < n:
                    locations = member_locations[already_added]
                    before = mask
                    mask = add(mask, locations)
                    oracle.update(locations)
                    check(before & mask == before, "insert-monotonicity", (m, k, already_added))
                    check(add(mask, locations) == mask, "duplicate-insert-idempotence", (m, k, already_added))
                    check(query(mask, locations)[0], "new-member-no-false-negative", (m, k, already_added))
                    already_added += 1
                check(set(ones(mask, m)) == oracle, "independent-state-oracle", (m, k, n))
                for index, locations in enumerate(member_locations[:n]):
                    check(query(mask, locations)[0], "retained-member-no-false-negative", (m, k, n, index))
                positives = 0
                for index, locations in enumerate(outsider_locations):
                    result, trace = query(mask, locations)
                    expected = all(location in oracle for location in locations)
                    check(result is expected, "absent-query-oracle", (m, k, n, index))
                    missing = next((i for i, loc in enumerate(locations) if loc not in oracle), None)
                    wanted_trace = list(locations if missing is None else locations[:missing + 1])
                    check(trace == wanted_trace, "query-short-circuit-prefix", (m, k, n, index))
                    positives += int(result)
                rows.append({
                    "bitCount": m, "hashCount": k, "insertions": n,
                    "setBits": len(oracle), "absentProbeCount": len(absent_keys),
                    "syntheticFalsePositiveCount": positives,
                    "interpretation": "Deterministic witness count only; not a theoretical or production false-positive rate.",
                })
    return rows


def main() -> None:
    model = json.loads((D / "model.json").read_text())
    fixture = fixture_review(model)
    matrix = property_matrix()
    report = {
        "status": "passed",
        "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
        "checkedAtBeijing": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "reviewer": "Independent model-review agent",
        "scope": "Logical model and bounded deterministic properties; no animation, audio, final media or product runtime.",
        "inputs": {"model.json": sha(D / "model.json"), "script.md": sha(D / "script.md")},
        "checkerSHA256": sha(Path(__file__)),
        "implementationIndependence": "No production/article imports; hexadecimal SHA digest and integer bitmap checked against set union/membership oracle.",
        "assertionsExecuted": sum(COUNTS.values()), "assertionsByCategory": dict(sorted(COUNTS.items())),
        "fixture": fixture,
        "configurationCount": 35, "checkpointsPerConfiguration": 6,
        "matrix": matrix,
        "reasoning": [
            "Insertion is a bitwise OR and cannot clear any existing mark.",
            "A correctly inserted element's fixed probe positions remain set, so it cannot be rejected while state/configuration are preserved.",
            "An unset probe position proves the queried key was not fully inserted under these rules; all set positions contain no key ownership and are not proof of membership.",
            "Increasing the set of marks can only retain or increase acceptance for a fixed probe distribution; it does not establish a strict increase per insertion or a production probability.",
        ],
        "limitations": [
            "The teaching SHA-256 mapping is not Redis, Guava or Cassandra's internal hash implementation.",
            "The four teaching keys and synthetic matrix are not a production probability experiment.",
            "The no-false-negative property requires complete insertion, stable query rules and no destructive clearing or corruption.",
            "No audio, timing, visuals, encoded media, site behavior or Redis/Guava/Cassandra execution was checked here.",
        ],
    }
    (D / "qa-model.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (D / "qa-model.md").write_text(
        "# 布隆过滤器独立模型复核\n\n"
        f"状态：通过。实际执行{report['assertionsExecuted']:,}项断言，覆盖35种位数/哈希数组合，每组6个插入量检查点。\n\n"
        "独立实现未导入制作或文章程序：以SHA-256十六进制前缀求位置，用整数位图执行插入/查询，并与集合oracle比对。"
        "四键映射、位图快照、001在12→2处遇0停止、067实际假阳性、错误清位误伤205、001未同步与补写恢复均符合模型。\n\n"
        "多容量检查覆盖1、2、7、16、31、64、127位以及1、2、3、5、8路哈希，含同键重复落点、重复插入、UTF-8键、状态单调、已插入键不漏判及查询短路顺序。"
        "各组未插入探针的放行数仅为确定输入的见证，不估计线上误判率。\n\n"
        "结论限定为普通只置1结构在正确插入、稳定规则和完好状态下的性质。来源复核另见qa-source-independent；未检查配音、动画、正式媒体、网页或产品运行。"
        "本报告按输入完整SHA记录实际版本，后续改稿或改模型须判断影响范围。\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "assertionsExecuted": report["assertionsExecuted"],
                      "configurationCount": 35, "modelSHA256": report["inputs"]["model.json"]}))


if __name__ == "__main__":
    main()
