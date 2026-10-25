#!/usr/bin/env python3
"""Independent semantic audit of actual query-link/X geometry in final DOM.

Expected rejection is derived from visible result text, actual bit/key/catalog
glyphs and the teaching contract. Caller boolean expressions are not copied.
The DOM's phase annotation is cross-checked, never used to decide whether an X
is expected. No Scene.state field or production JavaScript is evaluated.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo


D = Path(__file__).resolve().parent
ROOT = D.parents[1]
COUNTS: Counter[str] = Counter()
FAILURES: list[dict] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(value: bool, name: str, detail: object = None) -> None:
    COUNTS[name] += 1
    if not value:
        FAILURES.append({"category": name, "detail": detail})


def proper_cross(path: str | None) -> bool:
    """Recognize two independently drawn segments crossing in their interiors."""
    if not path:
        return False
    tokens = re.findall(r"[A-Za-z]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?", path)
    commands = [token for token in tokens if token in {"M", "L"}]
    if commands != ["M", "L", "M", "L"] or len(tokens) != 12:
        return False
    try:
        points = [(float(tokens[i+1]), float(tokens[i+2])) for i in (0, 3, 6, 9)]
    except ValueError:
        return False
    a, b, c, d = points
    determinant = lambda u, v: u[0]*v[1] - u[1]*v[0]
    ab = (b[0]-a[0], b[1]-a[1])
    cd = (d[0]-c[0], d[1]-c[1])
    ac = (c[0]-a[0], c[1]-a[1])
    denominator = determinant(ab, cd)
    if abs(denominator) < 1e-9:
        return False
    t = determinant(ac, cd)/denominator
    u = determinant(ac, ab)/denominator
    return 0 < t < 1 and 0 < u < 1


def actual_key(audit: dict) -> str | None:
    values = [item["text"].strip() for item in audit["texts"]
              if 315 <= item["y"] <= 390
              and 310 <= item["x"] + item["w"]/2 <= 365
              and re.fullmatch(r"\d{3}", item["text"].strip())]
    check(len(values) <= 1, "actual-key-unique", audit["frame"])
    return values[0] if values else None


def actual_catalog(audit: dict) -> list[str]:
    displays = []
    for catalog in audit["catalogs"]:
        lines = [line for line in catalog["actualTexts"] if line.strip().startswith("收录 ")]
        check(len(lines) == 1, "actual-catalog-glyph-row", audit["frame"])
        if lines:
            displays.extend(re.findall(r"\d{3}", lines[0]))
    return displays


def row_at_or_after(rows: list[dict], local: float) -> dict | None:
    return next((row for row in rows if row["local"] >= local), None)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--samples", type=Path, default=D / "remotion/out/preflight/samples.json")
    args = ap.parse_args()
    sample_path = args.samples.resolve()
    raw = json.loads(sample_path.read_text())
    model = json.loads((D / "model.json").read_text())
    plan = json.loads((D / "qa-preflight-plan.json").read_text())
    events = json.loads((D / "qa-animation-events.json").read_text())
    fix = json.loads((D / "qa-query-link-fix.json").read_text())
    sb = json.loads((D / "storyboard.json").read_text())
    for name in ["Main.tsx", "LayoutAudit.tsx"]:
        relative = f"episodes-codex/bloom-filter/remotion/src/{name}"
        check(sha(ROOT / relative) == fix["sourceSHA256"][name] == raw["sourceSHA"][relative],
              "fixed-source-is-actually-rendered", name)
    for relative, expected in raw["sourceSHA"].items():
        path = (ROOT / relative).resolve()
        check(path.is_relative_to(ROOT) and path.is_file() and sha(path) == expected,
              "render-input-identity", relative)
    frames = [sample["frame"] for sample in raw["samples"]]
    check(sorted(frames) == sorted(set(plan["frames"])) and len(frames) == len(set(frames)),
          "complete-final-sample-matrix", len(frames))
    check(len(raw["audits"]) == len(frames) and not raw["violations"],
          "final-actual-dom-layout-gate", len(raw["audits"]))
    check(events["inputs"]["storyboard.json"] == sha(D / "storyboard.json") and
          events["inputs"]["Main.tsx"] == sha(D / "remotion/src/Main.tsx"),
          "phase-witness-plan-inputs-current")
    offsets = {}
    offset = 0
    for scene in sb["scenes"]:
        for shot in scene["shots"]:
            offsets[str(shot["id"]).zfill(2)] = offset
            offset += shot["durationInFrames"]
    location_by_display = {item["display"]: item["positions"] for item in model["items"]}
    samples = {sample["frame"]: sample for sample in raw["samples"]}
    groups = defaultdict(list)
    phase_counts: Counter[str] = Counter()
    intent_counts: Counter[str] = Counter()
    rows = []
    allowed_link_scenes = {"reject-001", "false-positive", "gate", "bad-delete", "maintenance"}
    explicit_results = {
        "位置2是0 → 排除001": ("normal-zero-rejection", "001", 2),
        "001：看到0，先排除": ("normal-zero-rejection", "001", 2),
        "205仍在目录，却被位置3的0错拦": ("wrong-clear-rejection", "205", 3),
        "危险：旧标记的0不能证明目录不存在": ("stale-data-rejection", "001", 2),
    }
    for audit in sorted(raw["audits"], key=lambda item: item["frame"]):
        frame = audit["frame"]
        sample = samples[frame]
        shot = str(sample["shot"]).zfill(2)
        kind = sample["visualType"]
        png = Path(sample["file"])
        check(png.is_file() and sha(png) == sample["sha256"], "actual-png-identity", frame)
        check(sample["local"] == frame-offsets[shot], "actual-frame-local-binding", frame)
        check("queryLinks" in audit, "new-query-geometry-audit-present", frame)
        links = audit.get("queryLinks", [])
        check(len(links) == (1 if kind in allowed_link_scenes else 0),
              "actual-link-presence-by-scene-contract", frame)
        if not links:
            continue
        link = links[0]
        glyphs = [value.strip() for value in link["actualTexts"]]
        key = actual_key(audit)
        catalog = actual_catalog(audit)
        ones = {bit["index"] for bit in audit["bits"] if bit["bitValueText"].strip() == "1"}
        check(all(bit["bitValueText"].strip() in {"0", "1"} and
                  bit["bitValueText"].strip() == str(bit["value"]) for bit in audit["bits"]),
              "actual-binary-glyph-attribute-agree", frame)
        cross_paths = [value for value in link["geometry"] if proper_cross(value.get("d"))]
        for cross in cross_paths:
            check(cross["w"] > 0 and cross["h"] > 0 and cross["stroke"] not in {"none", "transparent"},
                  "actual-cross-has-visible-geometry", frame)
        check(len(cross_paths) == link["rejectMarkCount"] == len(link["rejectMarks"]),
              "independent-cross-geometry-vs-mark-annotation", frame)
        check({value["d"] for value in cross_paths} == {value["d"] for value in link["rejectMarks"]},
              "actual-reject-mark-path-identity", frame)
        lines = [value for value in link["geometry"] if value["tag"].lower() == "line"]
        check(len(lines) == 1, "actual-query-route-line", frame)
        if lines:
            line = lines[0]
            check(float(line["x2"]) > float(line["x1"]) and float(line["y2"]) == float(line["y1"]),
                  "route-leads-toward-authoritative-directory", frame)
            for cross in cross_paths:
                check(float(line["x1"]) <= cross["x"] < cross["x"]+cross["w"] <= float(line["x2"]),
                      "actual-cross-lies-on-query-route", frame)

        rejection_messages = [(label, values) for label, values in explicit_results.items() if label in glyphs]
        check(len(rejection_messages) <= 1, "one-visible-rejection-result", frame)
        expected_x = int(bool(rejection_messages))
        intent = "neutral-or-unfinished"
        if rejection_messages:
            _, (intent, wanted_key, zero) = rejection_messages[0]
            check(key == wanted_key and zero not in ones, "visible-rejection-has-actual-zero-and-key", frame)
            check(any("第3路 · 未探测" == item["text"].strip() for item in audit["texts"]),
                  "rejection-stops-before-third-probe", frame)
            if intent == "normal-zero-rejection":
                check(wanted_key not in catalog and kind in {"reject-001", "gate"},
                      "normal-zero-rejection-matches-catalog", frame)
            elif intent == "wrong-clear-rejection":
                check(kind == "bad-delete" and wanted_key in catalog and
                      any("错误删除反例" in item["text"] for item in audit["texts"]),
                      "wrong-clear-is-an-explicit-invalid-example", frame)
            else:
                check(kind == "maintenance" and wanted_key in catalog and
                      any("未同步反例" in item["text"] for item in audit["texts"]),
                      "stale-data-is-an-explicit-invalid-example", frame)
        elif any("正在同步标记" in value for value in glyphs):
            intent = "write-maintenance-no-interception"
        elif any("已恢复101 / 205的原始状态" in value for value in glyphs):
            intent = "restored-neutral-state"
        elif key == "067":
            intent = "positive-or-pending-no-rejection"
            check(all(position in ones for position in location_by_display[key]),
                  "positive-key-has-all-one-positions", frame)
        elif any("确认：001存在" in value for value in glyphs):
            intent = "maintained-positive-confirmation"
            check(all(position in ones for position in location_by_display["001"]),
                  "confirmed-new-key-has-all-marks", frame)
        check(len(cross_paths) == expected_x, "x-only-for-an-explicit-observed-zero-rejection", (frame, intent))
        phase = link["phase"]
        phase_counts[phase] += 1
        intent_counts[intent] += 1
        check(phase in {"waiting", "eligible", "dispatch", "blocked", "reset", "writing"},
              "known-link-phase-annotation", (frame, phase))
        check((phase == "blocked") is bool(cross_paths), "phase-annotation-agrees-with-actual-x", frame)
        if phase in {"eligible", "dispatch"}:
            check(key in location_by_display and all(position in ones for position in location_by_display[key]),
                  "eligible-dispatch-has-all-one-probe-values", frame)
        if phase == "eligible":
            check(key == "067" and "三位全1 → 可能存在067" in glyphs,
                  "eligible-before-dispatch-is-a-positive-result", frame)
        if phase == "writing":
            check(intent == "write-maintenance-no-interception", "writing-phase-has-neutral-wording", frame)
        if phase == "reset":
            check(intent == "restored-neutral-state" and catalog == ["101", "205"],
                  "reset-phase-has-restored-catalog-wording", frame)
        row = {"globalFrame": frame, "local": sample["local"], "shot": shot,
               "visualType": kind, "actualKeyGlyph": key, "actualCatalogGlyphs": catalog,
               "actualOneGlyphIndices": sorted(ones), "visibleLinkTexts": glyphs,
               "independentlyRecognizedCrossCount": len(cross_paths),
               "expectedCrossCountFromVisibleMeaning": expected_x, "intent": intent,
               "actualPhaseAnnotation": phase, "geometry": link["geometry"],
               "pngSHA256": sample["sha256"]}
        rows.append(row)
        groups[shot].append(row)

    events_by_id = {shot["id"]: shot for shot in events["shots"]}
    witnesses = []

    def witness(shot: str, point: float, wanted_x: int, wanted_intent: str | None, label: str) -> None:
        row = row_at_or_after(groups[shot], point)
        check(row is not None, "semantic-phase-has-actual-sample", (shot, label))
        if row is None:
            return
        check(row["independentlyRecognizedCrossCount"] == wanted_x,
              "semantic-phase-actual-cross-count", (shot, label, row["globalFrame"]))
        if wanted_intent:
            check(row["intent"] == wanted_intent, "semantic-phase-actual-meaning", (shot, label, row["globalFrame"]))
        witnesses.append({"shot": shot, "label": label, "localAnchor": point,
                          "actualGlobalFrame": row["globalFrame"], "actualIntent": row["intent"],
                          "actualCrossCount": row["independentlyRecognizedCrossCount"]})

    witness("06", 0, 0, "neutral-or-unfinished", "negative query still waiting")
    witness("06", groups["06"][-1]["local"], 1, "normal-zero-rejection", "negative query finished")
    positive_finish = max(event["arrive"] for event in events_by_id["08"]["events"] if event["kind"] == "read-three-ones")
    witness("08", positive_finish, 0, "positive-or-pending-no-rejection", "all-one eligible before database lookup")
    check(any(row["actualPhaseAnnotation"] == "eligible" for row in groups["08"]),
          "positive-eligibility-waiting-window-sampled")
    gate_switch = next(event["begin"] for event in events_by_id["10"]["events"] if event["kind"] == "independent-query-switch")
    gate_before = [row for row in groups["10"] if row["local"] < gate_switch][-1]
    witness("10", gate_before["local"], 1, "normal-zero-rejection", "first request rejected before independent switch")
    witness("10", gate_switch, 0, "positive-or-pending-no-rejection", "next independent request not rejected")
    bad_events = events_by_id["12"]["events"]
    bad_done = max(event["arrive"] for event in bad_events if event["kind"] == "query-205-wrongly-rejected")
    reset = next(event["begin"] for event in bad_events if event["kind"] == "restore-bits-and-catalog")
    witness("12", 0, 0, "neutral-or-unfinished", "explaining a wrong operation is not rejection")
    witness("12", bad_done, 1, "wrong-clear-rejection", "actual wrong rejection after shared zero")
    witness("12", reset, 0, "restored-neutral-state", "restored state does not retain rejection X")
    maintenance = events_by_id["13"]
    stale_done = max(event["arrive"] for event in maintenance["events"] if event["kind"] == "unsafe-stale-query")
    fixed_done = max(event["arrive"] for event in maintenance["events"] if event["kind"] == "correct-insert-001")
    witness("13", 0, 0, "neutral-or-unfinished", "new record but query still waiting")
    witness("13", stale_done, 1, "stale-data-rejection", "explicit stale-data wrong rejection")
    witness("13", maintenance["sentenceSpans"][1][0], 0, "write-maintenance-no-interception", "synchronizing marks is not rejection")
    witness("13", fixed_done, 0, "maintained-positive-confirmation", "updated filter allows authoritative lookup")
    for required in ["waiting", "eligible", "dispatch", "blocked", "reset", "writing"]:
        check(phase_counts[required] > 0, "all-distinct-query-link-phases-witnessed", required)
    report = {
        "status": "passed" if not FAILURES else "failed",
        "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
        "checkedAtBeijing": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "reviewer": "Independent model/query-link DOM reviewer",
        "scope": "Actual visible SVG crossing geometry and link/result semantics on the completed final sample matrix.",
        "inputs": {"samples.json": sha(sample_path), "model.json": sha(D / "model.json"),
                   "storyboard.json": sha(D / "storyboard.json"),
                   "qa-animation-events.json": sha(D / "qa-animation-events.json"),
                   "qa-query-link-fix.json": sha(D / "qa-query-link-fix.json")},
        "checkerSHA256": sha(Path(__file__)), "sampleReport": str(sample_path.relative_to(ROOT)),
        "totalActualSamples": len(raw["audits"]), "actualQueryLinkSamples": len(rows),
        "phaseCounts": dict(phase_counts), "visibleIntentCounts": dict(intent_counts),
        "assertionsExecuted": sum(COUNTS.values()), "assertionsByCategory": dict(sorted(COUNTS.items())),
        "failures": FAILURES, "semanticPhaseWitnesses": witnesses, "actualLinkSamples": rows,
        "history": "The earlier bit/catalog DOM pass did not cover query-link rejection semantics. The failed visual version and prior scope remain archived in qa-revisions/query-link-state-v1.",
        "independence": [
            "No caller boolean expression, stages function or Scene.state is imported/evaluated.",
            "X marks are independently recognized as two SVG line segments crossing in their interiors; actual marker counts/phase annotations are cross-checks rather than expectations.",
            "Whether X is justified comes from the actual visible result, input key glyph, zero-valued probe, directory text and the independently checked teaching contract.",
            "Recorded phase anchors select before/after samples; they do not recreate caller timing conditions.",
        ],
        "limitations": [
            "This is a real DOM/SVG geometry audit at sampled frames, not a continuous pixel review, audio review or encoded-final-media check.",
            "The three continuous clips and overall visual clarity require their separately recorded independent visual review.",
        ],
    }
    (D / "qa-query-link-independent.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (D / "qa-query-link-independent.md").write_text(
        "# 查询链接语义的独立实际DOM复核\n\n"
        f"状态：{report['status']}。完整采样矩阵{report['totalActualSamples']}帧中，{len(rows)}帧含实际查询链接；"
        f"执行{report['assertionsExecuted']:,}项检查，失败{len(FAILURES)}项。\n\n"
        "独立识别SVG两条线段的内部交叉来统计X，不依赖调用者布尔条件、Scene自报state或phase标签决定预期。"
        "将实际可见结果、商品编号、位值和目录文字对应到正常0拒绝、错误清位拒绝、未同步拒绝三个明确阶段；全1、等待、写入和恢复均不得出现拒绝X。"
        "12个阶段见证覆盖正向放行前的eligible停留、两请求切换、删除恢复和新增标记同步。\n\n"
        "旧DOM通过仅保留其位值/目录范围，不追认为旧链接语义通过；旧失败和旧报告另存qa-revisions/query-link-state-v1。"
        "本报告限定采样DOM/SVG几何，不代替连续像素动画、声音或正式成片复核。\n"
    )
    print(json.dumps({"status": report["status"], "samples": report["totalActualSamples"],
                      "queryLinkSamples": len(rows), "assertionsExecuted": report["assertionsExecuted"],
                      "failureCount": len(FAILURES), "firstFailures": FAILURES[:8]}, ensure_ascii=False))
    if FAILURES:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
