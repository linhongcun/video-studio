"""Verify observable behavior and export the exact teaching data as JSON."""

import hashlib
import ast
import difflib
import importlib.util
import inspect
import json
import platform
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

from pricing import (RULES_EXTENDED, RULES_V1, RULES_V2, before_checkout,
                     checkout, select_rule)

HERE = Path(__file__).resolve().parent


def reject(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError("invalid input was accepted")


def trace(name, rules):
    chosen = select_rule(name, rules)
    events = [{"step": "caller_selects", "selected": name,
               "implementation": chosen.__name__}]

    def observed_rule(total):
        events.append({"step": "rule_called", "total_cents": total,
                       "implementation": chosen.__name__})
        result = chosen(total)
        events.append({"step": "rule_returns", "payable_cents": result})
        return result

    events.append({"step": "checkout_called", "total_cents": 10_000})
    result = checkout(10_000, observed_rule)
    events.append({"step": "checkout_returns", "payable_cents": result})
    return {"selected": name, "total_cents": 10_000,
            "payable_cents": result, "events": events}


def main():
    equivalence_cases = 0
    for total in range(50_001):
        for name in RULES_V1:
            actual = checkout(total, select_rule(name, RULES_V1))
            assert actual == before_checkout(total, name), (total, name)
            assert type(actual) is int and 0 <= actual <= total
            equivalence_cases += 1

    oracle_cases = 0
    for total in [0, 1, 9, 19, 99, 101, 999, 1_001, 9_999, 10_000, 12_345]:
        for rate, name, rules in [
            (90, "member", RULES_V1), (80, "campaign", RULES_V1),
            (75, "campaign", RULES_V2),
        ]:
            expected = int((Decimal(total) * Decimal(rate) / Decimal(100))
                           .to_integral_value(rounding=ROUND_FLOOR))
            assert checkout(total, select_rule(name, rules)) == expected
            oracle_cases += 1

    bad_total_cases = 0
    for total in [-1, 10_000.0, "10000", True, None]:
        for name in RULES_V1:
            reject(lambda total=total, name=name:
                   checkout(total, select_rule(name, RULES_V1)))
            reject(lambda total=total, name=name:
                   before_checkout(total, name))
            bad_total_cases += 2

    for rules in [RULES_V1, RULES_V2, RULES_EXTENDED]:
        reject(lambda rules=rules: select_rule("missing", rules))
        reject(lambda rules=rules: select_rule(None, rules))
    reject(lambda: before_checkout(10_000, "missing"))

    for result in [-1, 10_001, 9_000.0, True]:
        reject(lambda result=result: checkout(10_000, lambda _: result))

    before_hash = hashlib.sha256(inspect.getsource(checkout).encode()).hexdigest()
    v1 = trace("campaign", RULES_V1)
    v2 = trace("campaign", RULES_V2)
    assert v1["payable_cents"] == 8_000
    assert v2["payable_cents"] == 7_500
    assert before_hash == hashlib.sha256(inspect.getsource(checkout).encode()).hexdigest()
    for name in ["ordinary", "member"]:
        assert checkout(10_000, select_rule(name, RULES_V1)) == checkout(
            10_000, select_rule(name, RULES_V2))

    for total, expected in [(0, 0), (999, 0), (1_000, 0), (1_001, 1), (10_000, 9_000)]:
        assert checkout(total, select_rule("newcomer", RULES_EXTENDED)) == expected

    snapshot_sources = {}
    snapshot_modules = {}
    for name in ["before", "after"]:
        path = HERE / "snapshots" / f"{name}.py"
        snapshot_sources[name] = path.read_text()
        spec = importlib.util.spec_from_file_location(f"pricing_snapshot_{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        snapshot_modules[name] = module
    before_source, after_source = snapshot_sources["before"], snapshot_sources["after"]
    assert after_source == before_source.replace(
        "return total_cents * 80 // 100", "return total_cents * 75 // 100")
    assert before_source.count("return total_cents * 80 // 100") == 1
    patch = "".join(difflib.unified_diff(
        before_source.splitlines(keepends=True), after_source.splitlines(keepends=True),
        fromfile="snapshots/before.py", tofile="snapshots/after.py"))
    (HERE / "snapshots" / "campaign-only.diff").write_text(patch)
    before_nodes = ast.parse(before_source).body
    after_nodes = ast.parse(after_source).body
    assert len(before_nodes) == len(after_nodes)
    changed_ast_nodes = []
    for left, right in zip(before_nodes, after_nodes):
        if ast.dump(left) != ast.dump(right):
            changed_ast_nodes.append(getattr(left, "name", type(left).__name__))
    assert changed_ast_nodes == ["campaign"]
    snapshot_cases = 0
    for total in [0, 1, 99, 101, 999, 10_000, 12_345]:
        for rule_name in ["ordinary", "member", "campaign"]:
            before_result = snapshot_modules["before"].checkout(
                total, snapshot_modules["before"].select_rule(rule_name))
            after_result = snapshot_modules["after"].checkout(
                total, snapshot_modules["after"].select_rule(rule_name))
            if rule_name == "campaign":
                assert before_result == total * 80 // 100
                assert after_result == total * 75 // 100
            else:
                assert before_result == after_result
            snapshot_cases += 1
    snapshot_report = {
        "changed_ast_nodes": changed_ast_nodes,
        "registry_and_checkout_ast_unchanged": True,
        "verified_cases": snapshot_cases,
        "before_sha256": hashlib.sha256(before_source.encode()).hexdigest(),
        "after_sha256": hashlib.sha256(after_source.encode()).hexdigest(),
        "before_10000_cents": {name: snapshot_modules["before"].checkout(
            10_000, snapshot_modules["before"].select_rule(name))
            for name in ["ordinary", "member", "campaign"]},
        "after_10000_cents": {name: snapshot_modules["after"].checkout(
            10_000, snapshot_modules["after"].select_rule(name))
            for name in ["ordinary", "member", "campaign"]},
        "patch": "snapshots/campaign-only.diff",
    }

    report = {
        "status": "passed", "python": platform.python_version(),
        "scope": "Finite behavior checks of this teaching example; not a proof for arbitrary strategies.",
        "currency": "integer cents", "rounding": "floor to integer cent",
        "equivalence_cases": equivalence_cases,
        "decimal_reference_cases": oracle_cases,
        "invalid_total_rejections": bad_total_cases,
        "unknown_rule_rejections": 7,
        "invalid_strategy_result_rejections": 4,
        "newcomer_boundary_cases": 5,
        "minimal_source_edit": snapshot_report,
        "unchanged_checkout_sha256": before_hash,
        "module_sha256": hashlib.sha256((HERE / "pricing.py").read_bytes()).hexdigest(),
        "original_rules": [trace(name, RULES_V1) for name in RULES_V1],
        "campaign_update": {"before": v1, "after": v2},
        "newcomer": trace("newcomer", RULES_EXTENDED),
    }
    (HERE / "verified-results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ["original_rules", "campaign_update", "newcomer"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
