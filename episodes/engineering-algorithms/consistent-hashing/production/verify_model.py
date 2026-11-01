#!/usr/bin/env python3
"""Check teaching data against a distance oracle and exhaustive small rings."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import model


HERE = Path(__file__).resolve().parent
COUNTS: Counter = Counter()


def require(condition: bool, message: str) -> None:
    COUNTS["assertions"] += 1
    if not condition:
        raise AssertionError(message)


def oracle_owners(tokens: list[dict], space: int) -> list[str]:
    """Independent oracle: minimize clockwise distance, without sort/bisect."""
    return [
        min(tokens, key=lambda token: (token["position"] - value) % space)["physicalId"]
        for value in range(space)
    ]


def interval_points(start: int, end: int, space: int) -> set[int]:
    # Direct inequalities, including a full ring when start == end.
    return {
        value for value in range(space)
        if (start < value <= end if start < end else value > start or value <= end)
    }


def changed_points(before: list[str], after: list[str]) -> set[int]:
    return {index for index, (old, new) in enumerate(zip(before, after)) if old != new}


def token(identifier: str, position: int, physical: str | None = None) -> dict:
    return {"id": identifier, "position": position, "physicalId": physical or identifier}


def check_fixture(data: dict) -> None:
    require(data["space"] == 100, "fixed hash space")
    expected_nodes = [{"id": "A", "position": 20}, {"id": "B", "position": 50}, {"id": "C", "position": 85}]
    require(data["nodesBefore"] == expected_nodes, "locked original node positions")
    require(data["nodesAfter"] == [*expected_nodes, {"id": "D", "position": 70}], "join never moves an existing node")
    expected_hashes = [5, 13, 27, 34, 46, 56, 64, 78, 86, 95]
    require([key["hash"] for key in data["keys"]] == expected_hashes, "fixed ten-key fixture")
    expected_rows = [
        ("C", "B", "A", "A"), ("B", "B", "A", "A"),
        ("A", "D", "B", "B"), ("B", "C", "B", "B"),
        ("B", "C", "B", "B"), ("C", "A", "C", "D"),
        ("B", "A", "C", "D"), ("A", "C", "C", "C"),
        ("C", "C", "A", "A"), ("C", "D", "A", "A"),
    ]
    for index, (key, expected) in enumerate(zip(data["keys"], expected_rows), 1):
        require(key["id"] == f"K{index:02d}", "stable key IDs")
        require(tuple(key[field] for field in ("modBefore", "modAfter", "ringBefore", "ringAfter")) == expected, f"hard-coded independent row {index}")
    require(data["modulo"]["changedSampleCount"] == 8, "modulo sample changes 8/10")
    require(data["modulo"]["changedKeyIds"] == ["K01", "K03", "K04", "K05", "K06", "K07", "K08", "K10"], "exact modulo changed keys")
    require(data["ringJoin"]["changedKeyIds"] == ["K06", "K07"], "ring changes exactly K06/K07")
    require(data["ringJoin"]["changedSampleCount"] == 2, "ring sample changes 2/10")
    require(data["ringJoin"]["changedPositions"] == list(range(51, 71)), "join interval is exactly (50,70]")
    require(data["ringRemoval"]["changedPositions"] == list(range(51, 71)), "removal reverses D ownership only")
    for value, old, new in [(0, "A", "A"), (20, "A", "A"), (50, "B", "B"), (51, "C", "D"), (70, "C", "D"), (71, "C", "C"), (85, "C", "C"), (86, "A", "A"), (99, "A", "A")]:
        require(data["rings"]["before"]["owners"][value] == old, f"before boundary {value}")
        require(data["rings"]["after"]["owners"][value] == new, f"after boundary {value}")
    require(data["scope"]["virtualNodesAreSeparatePreconfiguredExample"] is True, "virtual nodes are a separate example")
    expected_virtual = {"A": [5, 38, 72], "B": [15, 48, 82], "C": [28, 60, 94]}
    for physical, positions in expected_virtual.items():
        require([item["position"] for item in data["vnodesBefore"] if item["physicalId"] == physical] == positions, f"locked virtual positions: {physical}")
        require([item for item in data["vnodesAfter"] if item["physicalId"] == physical] == [item for item in data["vnodesBefore"] if item["physicalId"] == physical], f"virtual join preserves existing tokens: {physical}")
    expected_counts = {
        "before": {"A": 35, "B": 30, "C": 35},
        "after": {"A": 35, "B": 30, "C": 15, "D": 20},
        "virtualBefore": {"A": 33, "B": 30, "C": 37},
        "virtualAfter": {"A": 27, "B": 25, "C": 31, "D": 17},
    }
    require([item["position"] for item in data["vnodesAfter"] if item["physicalId"] == "D"] == [10, 34, 88], "locked new virtual positions")
    for name, state in data["rings"].items():
        expected = oracle_owners(state["tokens"], 100)
        require(len(state["owners"]) == 100 and state["owners"] == expected, f"all positions match independent oracle: {name}")
        require(state["intervalCounts"] == expected_counts[name], f"independent counts: {name}")
        coverage = Counter()
        for interval in state["intervals"]:
            points = interval_points(interval["startExclusive"], interval["endInclusive"], 100)
            require(len(points) == interval["count"], f"interval endpoint/count: {name}")
            require(all(expected[value] == interval["physicalId"] for value in points), f"interval physical owner: {name}")
            coverage.update(points)
        require(coverage == Counter({value: 1 for value in range(100)}), f"disjoint and exhaustive interval coverage: {name}")
        for key in data["keys"]:
            field = {"before": "ringBefore", "after": "ringAfter", "virtualBefore": "virtualBefore", "virtualAfter": "virtualAfter"}[name]
            require(key[field] == expected[key["hash"]], f"key matches full-space vector: {name}/{key['id']}")
    require(data["virtualJoin"]["transfers"] == [{"from": "A", "to": "D", "count": 6}, {"from": "B", "to": "D", "count": 5}, {"from": "C", "to": "D", "count": 6}], "virtual transfers come from three physical nodes")
    require(data["virtualJoin"]["changedPositionCount"] == 17, "virtual join changes 17/100 integer positions")
    require(data["virtualJoin"]["changedPositions"] == [*range(6, 11), *range(29, 35), *range(83, 89)], "three exact virtual intervals")
    require(data["virtualRemoval"]["changedPositions"] == data["virtualJoin"]["changedPositions"], "removing all D tokens reverses exactly their intervals")
    hot = data["hotKey"]
    expected_owner = oracle_owners(data["rings"][hot["ring"]]["tokens"], 100)[hot["hash"]]
    require(hot["owner"] == expected_owner and hot["ownerCount"] == 1, "hot key keeps one physical owner")
    require(sum(hot["requestsByPhysicalNode"].values()) == hot["illustrativeRequests"], "illustrative traffic conserved")
    require([node for node, count in hot["requestsByPhysicalNode"].items() if count] == [expected_owner], "virtual tokens do not split one key's traffic")


def exhaustive_single_token_rings() -> None:
    for space in range(2, 10):
        for size in range(1, space + 1):
            for positions in combinations(range(space), size):
                tokens = [token(f"N{position}", position) for position in positions]
                before = model.owners_for_space(tokens, space)
                require(before == oracle_owners(tokens, space), "exhaustive distance oracle")
                require(before == model.owners_for_space(list(reversed(tokens)), space), "input order is irrelevant")
                COUNTS["singleTokenTopologies"] += 1
                COUNTS["basePositionComparisons"] += space
                for added_position in set(range(space)) - set(positions):
                    added = token(f"N{added_position}", added_position)
                    after = model.owners_for_space([*tokens, added], space)
                    require(after == oracle_owners([*tokens, added], space), "joined ring distance oracle")
                    predecessor = max((position for position in positions if position < added_position), default=max(positions))
                    expected_change = interval_points(predecessor, added_position, space)
                    require(changed_points(before, after) == expected_change, "fresh physical node changes exactly its predecessor interval")
                    require(all(after[value] == added["physicalId"] for value in expected_change), "all changed keys go to the new node")
                    require(all(before[value] == oracle_owners(tokens, space)[added_position] for value in expected_change), "all taken keys formerly belonged to the old successor")
                    COUNTS["singleNodeJoins"] += 1
                if size > 1:
                    for removed in tokens:
                        remaining = [item for item in tokens if item["id"] != removed["id"]]
                        after = model.owners_for_space(remaining, space)
                        require(after == oracle_owners(remaining, space), "removed ring distance oracle")
                        require(changed_points(before, after) == {value for value, owner in enumerate(before) if owner == removed["physicalId"]}, "removal changes only and all keys owned by the removed physical node")
                        COUNTS["singleNodeRemovals"] += 1


def exhaustive_virtual_rings() -> None:
    for space in range(3, 8):
        for size in range(1, min(3, space) + 1):
            for positions in combinations(range(space), size):
                for physical_ids in product("AB", repeat=size):
                    tokens = [token(f"T{index}", position, physical_ids[index]) for index, position in enumerate(positions)]
                    before = model.owners_for_space(tokens, space)
                    require(before == oracle_owners(tokens, space), "virtual physical mapping oracle")
                    COUNTS["virtualTopologies"] += 1
                    for position in set(range(space)) - set(positions):
                        predecessor = max((point for point in positions if point < position), default=max(positions))
                        allowed = interval_points(predecessor, position, space)
                        for destination in ("A", "C"):
                            joined = [*tokens, token("new-token", position, destination)]
                            after = model.owners_for_space(joined, space)
                            require(after == oracle_owners(joined, space), "virtual join distance oracle")
                            changed = changed_points(before, after)
                            require(changed <= allowed, "virtual token may only change its own interval")
                            require(all(after[value] == destination for value in allowed), "new token has exactly one configured physical owner")
                            if destination == "C":
                                require(changed == allowed, "new physical owner takes the complete added-token interval")
                            COUNTS["virtualTokenJoins"] += 1
                    if size > 1:
                        for removed in tokens:
                            remaining = [item for item in tokens if item["id"] != removed["id"]]
                            after = model.owners_for_space(remaining, space)
                            require(after == oracle_owners(remaining, space), "virtual-token removal oracle")
                            require(all(before[value] == removed["physicalId"] for value in changed_points(before, after)), "virtual-token removal changes no key owned by another physical node")
                            COUNTS["virtualTokenRemovals"] += 1
                    for physical in set(physical_ids):
                        remaining = [item for item in tokens if item["physicalId"] != physical]
                        if not remaining:
                            continue
                        after = model.owners_for_space(remaining, space)
                        require(after == oracle_owners(remaining, space), "whole-physical-node removal oracle")
                        require(changed_points(before, after) == {value for value, owner in enumerate(before) if owner == physical}, "removing all physical-node tokens changes exactly that node's keys")
                        COUNTS["virtualPhysicalNodeRemovals"] += 1


def invalid_topologies() -> None:
    cases = [([], 10), ([token("A", 2), token("B", 2)], 10), ([token("A", -1)], 10), ([token("A", 10)], 10), ([token("A", 0)], 0)]
    for tokens, space in cases:
        try:
            model.owners_for_space(tokens, space)
        except ValueError:
            COUNTS["rejectedInvalidTopologies"] += 1
        else:
            raise AssertionError("Undefined empty/colliding/out-of-space ring must not be accepted")


def main() -> None:
    data = json.loads((HERE / "model.json").read_text())
    checks = []
    tasks = [
        ("fixture_and_all_100_positions", lambda: check_fixture(data)),
        ("exhaustive_single_token_rings_spaces_2_to_9", exhaustive_single_token_rings),
        ("exhaustive_virtual_rings_spaces_3_to_7_up_to_3_tokens", exhaustive_virtual_rings),
        ("invalid_topologies_are_explicitly_rejected", invalid_topologies),
        ("deterministic_json_matches_generator", lambda: require((HERE / "model.json").read_text() == model.serialized_model(), "model.json matches deterministic generation")),
    ]
    for name, operation in tasks:
        try:
            operation()
            checks.append({"name": name, "status": "pass"})
        except Exception as error:
            checks.append({"name": name, "status": "fail", "error": f"{type(error).__name__}: {error}"})
    report = {
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checkedAt": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "executor": "Codex independent mathematical-model subagent",
        "scope": "Deterministic illustrative ownership only; not a Redis/Cassandra deployment, data migration, load benchmark, media, audio, or learning-effect check.",
        "oracle": "Production uses sorted successor + bisect_left; independent oracle minimizes modular clockwise distance, and interval expectations use direct inequalities.",
        "checks": checks,
        "counts": dict(COUNTS),
        "fixture": {
            "moduloChangedKeys": data["modulo"]["changedSampleCount"],
            "ringChangedKeys": data["ringJoin"]["changedSampleCount"],
            "sampleCount": 10,
            "integerPositionCounts": {name: state["intervalCounts"] for name, state in data["rings"].items()},
            "virtualTransferCounts": data["virtualJoin"]["transfers"],
        },
        "sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in ("model.py", "model.json", "verify_model.py")},
        "limitations": [
            "Exhaustive checks cover the stated finite topology ranges, not every possible hash space or real product implementation.",
            "Integer interval counts are exact for this 100-position example; physical load and traffic are not measured.",
            "8/10 and 2/10 are sample results, not universal migration percentages or a claimed theoretical expectation.",
            "Virtual tokens use a separate preconfigured example and do not demonstrate an in-place conversion from the single-token ring.",
        ],
    }
    (HERE / "qa-model.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    lines = [
        "# 一致性哈希模型独立核验", "", f"结果：**{report['status'].upper()}**。检查时间：{report['checkedAt']}。", "",
        "只核验示意数学模型与供动画读取的数据，不代表产品实测、数据迁移、请求负载测试、音视频复核或观众学习效果。", "",
        "## 固定输入与结论", "",
        "- 空间为整数0…99；顺时针选择第一个位置≥键哈希值的token，尾部回绕；每键单份物理归属。",
        "- 原环A@20、B@50、C@85保持不动，加入D@70只接管(50,70]：50仍属B，70属于D，71仍属C。86…99回绕A。",
        "- 同批10个键：取余3→4改变8个；原环加入D仅K06(56)、K07(64)由C改归D，共2个。比例仅属于这组样本。",
        "- 虚拟节点是另一组预先配置示例，不是把原环原地转换。新D@10/34/88分别接管(5,10]、(28,34]、(82,88]，从B/A/C取得5/6/6个整数点。",
        "- 虚拟节点加入前A33/B30/C37，加入后A27/B25/C31/D17；不承诺正好均匀。",
        "- 热键K06(56)在虚拟新环仍单独归C；模型中的10000次示意请求全部归同一物理节点，不是流量实测。", "",
        "## 独立方法与覆盖", "",
        "生产模型采用排序后继与二分查找；核验oracle独立最小化模空间顺时针距离，不调用生产查找。区间期待值另用开闭端点不等式求集合。", "",
    ]
    lines.extend(f"- `{check['name']}`：{check['status']}" + (f"；{check['error']}" if "error" in check else "") for check in checks)
    lines.extend(["", "覆盖计数：", "", *[f"- {name}: {count}" for name, count in report["counts"].items()], "", "## 文件指纹", ""])
    lines.extend(f"- `{name}`：`{digest}`" for name, digest in report["sha256"].items())
    lines.extend(["", "## 能力边界", "", *[f"- {item}" for item in report["limitations"]], ""])
    (HERE / "qa-model.md").write_text("\n".join(lines))
    print(json.dumps({"status": report["status"], "counts": report["counts"], "modelSha256": report["sha256"]["model.json"]}))
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
