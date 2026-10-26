#!/usr/bin/env python3
"""Independent audit of the one-hash core and separately rebuilt k=2 example.

No producer module is imported. SHA positions use a hexadecimal prefix and
integer masks are checked against a set-based oracle. Counts describe bounded
deterministic checks, never an empirical production false-positive rate.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo


D = Path(__file__).resolve().parent
COUNTS: Counter[str] = Counter()


def verify(value: bool, category: str, detail=None) -> None:
    COUNTS[category] += 1
    if not value:
        raise AssertionError((category, detail))


def locations(key: str, bits: int, seeds: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(int(hashlib.sha256((str(seed)+":"+key).encode("utf-8")).hexdigest()[:16], 16) % bits
                 for seed in seeds)


def insert(mask: int, selected: tuple[int, ...]) -> int:
    for position in selected:
        mask |= 1 << position
    return mask


def probe(mask: int, selected: tuple[int, ...]) -> tuple[bool, list[int]]:
    read = []
    for position in selected:
        read.append(position)
        if not mask & (1 << position):
            return False, read
    return True, read


def set_positions(mask: int, bits: int) -> list[int]:
    return [position for position in range(bits) if mask & (1 << position)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review_fixture(model: dict) -> dict:
    verify(model["bitCount"] == 8 and model["hashCount"] == 1, "fixture-configuration")
    verify(model["hash"]["seeds"] == [22] and model["hash"]["modulus"] == 8,
           "fixture-configuration")
    verify(model["inserted"] == ["A", "B"], "fixture-ground-truth")
    expected_primary = {"A": (3,), "B": (3,), "C": (3,), "D": (7,)}
    expected_both = {"A": (3, 2), "B": (3, 1), "C": (3, 5), "D": (7, 5)}
    primary = {key: locations(key, 8, (22,)) for key in expected_primary}
    both = {key: locations(key, 8, (22, 0)) for key in expected_both}
    verify(primary == expected_primary and both == expected_both, "actual-sha-derived-positions")
    for item in model["items"]:
        key = item["key"]
        verify(tuple(item["singlePositions"]) == primary[key] == tuple(item["positions"]),
               "model-primary-position", key)
        verify(tuple(item["comparisonPositions"]) == both[key], "model-secondary-position", key)
        for evidence in item["hashEvidence"]:
            payload = str(evidence["seed"]) + ":" + key
            digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            prefix = digest[:16]
            unsigned = int(prefix, 16)
            verify(evidence["payload"] == payload, "model-hash-evidence-payload", key)
            verify(evidence["sha256Hex"] == digest, "model-hash-evidence-digest", key)
            verify(evidence["first8Hex"] == prefix, "model-hash-evidence-prefix", key)
            verify(evidence["first8UnsignedDecimal"] == str(unsigned), "model-hash-evidence-unsigned", key)
            verify(evidence["position"] == unsigned % 8, "model-hash-evidence-modulus", key)

    a = insert(0, primary["A"])
    ab = insert(a, primary["B"])
    verify(set_positions(a, 8) == [3] == model["snapshots"]["afterA"], "primary-state")
    verify(set_positions(ab, 8) == [3] == model["snapshots"]["afterB"], "primary-state")
    verify(ab == a, "shared-bit-not-counter")
    verify(model["snapshots"]["empty"] == [], "primary-state")
    for key, expected in model["queries"].items():
        actual = probe(ab, primary[key])
        verify(actual == (expected["result"], expected["checked"]), "primary-query-and-trace", key)
        verify(expected["truthContains"] == (key in {"A", "B"}), "primary-query-ground-truth", key)
        if "stopsAt" in expected:
            verify(not actual[0] and actual[1][-1] == expected["stopsAt"], "primary-query-stop", key)
    verify(probe(ab, primary["C"])[0] and "C" not in {"A", "B"}, "actual-false-positive-C")
    verify(probe(ab, primary["D"]) == (False, [7]), "actual-zero-rejection-D")

    wrong = ab & ~(1 << 3)
    verify(set_positions(wrong, 8) == model["snapshots"]["wronglyClearedA"] == [], "invalid-clear-state")
    deletion = model["wrongDeletion"]
    verify(deletion["clearedPosition"] == 3 and deletion["remainingTruth"] == ["B"], "invalid-clear-ground-truth")
    verify(probe(wrong, primary["B"]) == (False, [3]), "invalid-clear-harms-B")
    verify(probe(wrong, primary["B"]) == (deletion["queryB"]["result"], deletion["queryB"]["checked"]),
           "invalid-clear-declared-trace")

    comparison = model["comparison"]
    verify(comparison["hashCount"] == 2 and comparison["seeds"] == [22, 0]
           and comparison["bitCount"] == 8 and comparison["inserted"] == ["A", "B"], "rebuilt-configuration")
    rebuilt_a = insert(0, both["A"])
    rebuilt_ab = insert(rebuilt_a, both["B"])
    verify(comparison["snapshots"]["empty"] == [], "rebuilt-state")
    verify(set_positions(rebuilt_a, 8) == comparison["snapshots"]["afterA"] == [2, 3], "rebuilt-state")
    verify(set_positions(rebuilt_ab, 8) == comparison["snapshots"]["afterB"] == [1, 2, 3], "rebuilt-state")
    for key, expected in comparison["queries"].items():
        actual = probe(rebuilt_ab, both[key])
        verify(actual == (expected["result"], expected["checked"]), "rebuilt-query-and-trace", key)
        verify(expected["truthContains"] == (key in {"A", "B"}), "rebuilt-query-ground-truth", key)
        if "stopsAt" in expected:
            verify(not actual[0] and actual[1][-1] == expected["stopsAt"], "rebuilt-query-stop", key)
    verify(probe(rebuilt_ab, both["C"]) == (False, [3, 5]), "rebuilt-excludes-this-C")
    verify(probe(rebuilt_ab, both["D"]) == (False, [7]), "rebuilt-D-stops-before-second-probe")

    h = locations("H", 8, (22, 0))
    verify(h == (1, 1) == tuple(model["guardCounterexample"]["positions"]), "guard-H-mapping")
    old_h, new_h = probe(ab, h[:1]), probe(rebuilt_ab, h)
    verify(old_h == (False, [1]) and new_h == (True, [1, 1]), "acceptance-not-pointwise-improvement")
    verify(old_h == (model["guardCounterexample"]["single"]["result"], model["guardCounterexample"]["single"]["checked"])
           and new_h == (model["guardCounterexample"]["double"]["result"], model["guardCounterexample"]["double"]["checked"]),
           "guard-H-declared-query")
    verify(model["guardCounterexample"]["truthContains"] is False, "guard-H-ground-truth")
    invalid_configuration_examples = {key: probe(ab, both[key]) for key in ("A", "B")}
    for key, actual in invalid_configuration_examples.items():
        verify(not actual[0], "querying-old-state-with-new-rules-is-unsafe", key)
    return {
        "primaryLocations": {key: list(value) for key, value in primary.items()},
        "comparisonLocations": {key: list(value) for key, value in both.items()},
        "singleFinalOnes": set_positions(ab, 8), "rebuiltFinalOnes": set_positions(rebuilt_ab, 8),
        "singleC": probe(ab, primary["C"]), "rebuiltC": probe(rebuilt_ab, both["C"]),
        "singleD": probe(ab, primary["D"]), "rebuiltD": probe(rebuilt_ab, both["D"]),
        "wrongDeletionB": probe(wrong, primary["B"]),
        "guardH": {"positions": list(h), "single": old_h, "rebuilt": new_h},
        "invalidNewRulesOnOldBits": invalid_configuration_examples,
        "interpretation": "C and H witness that these two realized acceptance sets are incomparable; no rate estimate follows.",
    }


def property_review() -> list[dict]:
    rows = []
    bits_options = (1, 2, 8, 17, 64)
    seed_options = ((22,), (22, 0), (22, 0, 1, 2))
    counts = (0, 1, 2, 8, 32, 128)
    members = [f"inserted:{i}" for i in range(126)] + ["元素甲", "元素乙:UTF8"]
    outsiders = [f"absent:{i}" for i in range(256)]
    verify(set(members).isdisjoint(outsiders), "property-inputs-disjoint")
    for bits in bits_options:
        for seeds in seed_options:
            member_positions = [locations(key, bits, seeds) for key in members]
            outsider_positions = [locations(key, bits, seeds) for key in outsiders]
            for value in member_positions + outsider_positions:
                verify(len(value) == len(seeds) and all(0 <= position < bits for position in value),
                       "property-hash-range")
            mask = 0
            oracle: set[int] = set()
            previous_count = 0
            for count in counts:
                for selected in member_positions[previous_count:count]:
                    prior = mask
                    mask = insert(mask, selected)
                    oracle.update(selected)
                    verify(prior & mask == prior, "property-insertion-never-clears")
                    verify(insert(mask, selected) == mask, "property-repeat-insertion-idempotent")
                    verify(probe(mask, selected)[0], "property-new-member-never-rejected")
                previous_count = count
                verify(set(set_positions(mask, bits)) == oracle, "property-independent-set-oracle")
                for selected in member_positions[:count]:
                    verify(probe(mask, selected)[0], "property-retained-member-never-rejected")
                accepted_absent = 0
                for selected in outsider_positions:
                    result, visited = probe(mask, selected)
                    verify(result is all(position in oracle for position in selected), "property-query-result-oracle")
                    first_zero = next((i for i, position in enumerate(selected) if position not in oracle), None)
                    correct_prefix = list(selected if first_zero is None else selected[:first_zero+1])
                    verify(visited == correct_prefix, "property-zero-short-circuit")
                    accepted_absent += int(result)
                rows.append({"bits": bits, "seeds": list(seeds), "insertions": count,
                             "setBits": len(oracle), "absentProbeCount": len(outsiders),
                             "acceptedAbsentWitnessCount": accepted_absent,
                             "meaning": "Deterministic witnesses only, not an error-rate measurement."})
    return rows


def main() -> None:
    model = json.loads((D / "model.json").read_text())
    fixture = review_fixture(model)
    matrix = property_review()
    report = {
        "status": "passed", "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
        "checkedAtBeijing": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "scope": "Independent logical model and bounded deterministic properties; no audio, animation, encoded media or product execution.",
        "inputs": {name: sha(D / name) for name in ("model.json", "script.md", "plan.json")},
        "checkerSHA256": sha(Path(__file__)), "assertionsExecuted": sum(COUNTS.values()),
        "assertionsByCategory": dict(sorted(COUNTS.items())), "fixture": fixture,
        "configurationCount": 15, "insertionCheckpointsPerConfiguration": 6, "propertyMatrix": matrix,
        "reasoning": [
            "k=1 retains the standard set-bit/query-same-positions structure and is a valid simplest Bloom case.",
            "Insertion never clears markers, so a correctly inserted element cannot encounter an unset selected bit under unchanged rules and intact state.",
            "A/B/C collide at3; D probes an untouched7. A set bit stores no identity, so C remains a concrete false positive.",
            "The k=2 example is rebuilt from empty using the original A/B set. C probes3 then5 and is excluded, but H changes from rejected to accepted.",
            "Adding probe locations also adds marked bits; neither per-query improvement nor a lower measured error rate is implied by this example.",
        ],
        "limitations": [
            "The SHA-derived teaching hash is not Redis or Guava's internal implementation.",
            "H and C are counterexample witnesses, not evidence of either population false-positive rate.",
            "Changing query rules without rebuilding can reject known members; no-false-negative claims require unchanged rules and complete correct insertion.",
            "No audio, rendering, visual readability, website or encoded-film check was performed.",
        ],
    }
    (D / "qa-model.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (D / "qa-model.md").write_text(
        "# 单哈希核心修订：独立模型复核\n\n"
        f"状态：通过。实际执行{report['assertionsExecuted']:,}项断言，覆盖15种位数/哈希配置、各6个插入量检查点。\n\n"
        "独立实现未导入制作代码，以SHA-256十六进制前缀求位置，整数位图与集合oracle交叉检查。"
        "A/B/C的H1均为3、D为7；H2为A2/B1/C5/D5，全部摘要、无符号十进制及取模证据一致。"
        "单位置插入共享、D遇0排除、C碰撞误判、清3误伤B，以及另建双位置数组完整重插A/B后排除C均通过。\n\n"
        "特别验证H→1/1：单位置状态会排除H，双位置重建状态却会放行H；和C一起证明本例不能推出逐查询改善。"
        "新规则直接查询旧位图还会错排除A/B，支持重建与配置一致性的前提。"
        "性质矩阵包含重复位置、UTF-8键、幂等/单调、已插入元素不漏判及遇0短路；未用样例估算误判率。\n\n"
        "本报告仅覆盖逻辑模型，实际来源和逐句技术审批另见qa-technical-independent，未检查声音、动画或成片。\n"
    )
    print(json.dumps({"status": report["status"], "assertionsExecuted": report["assertionsExecuted"],
                      "configurationCount": report["configurationCount"], "modelSHA256": report["inputs"]["model.json"]}))


if __name__ == "__main__":
    main()
