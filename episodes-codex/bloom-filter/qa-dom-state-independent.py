#!/usr/bin/env python3
"""Review completed real-render DOM samples using independent Bloom invariants.

No production module or Scene.state is imported or trusted. Event metadata is
used only to locate sampled phase boundaries, not to reproduce stages/easing.
This is a DOM/glyph/state audit, not a pixel-motion or audio-listening review.
Run only after the coordinator confirms the final preflight has completed.
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


def check(condition: bool, category: str, detail: object = None) -> None:
    COUNTS[category] += 1
    if not condition:
        FAILURES.append({"category": category, "detail": detail})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(row: dict) -> list[str]:
    return [item["text"].strip() for item in row["audit"]["texts"]]


def has(row: dict, value: str) -> bool:
    return any(value in item for item in text(row))


def card_key(row: dict) -> str | None:
    # Read the actual large identifier glyph in the left hash-input card.
    candidates = [item["text"].strip() for item in row["audit"]["texts"]
                  if 315 <= item["y"] <= 390
                  and 310 <= item["x"] + item["w"] / 2 <= 365
                  and re.fullmatch(r"\d{3}", item["text"].strip())]
    check(len(candidates) <= 1, "actual-key-glyph-unique", row["frame"])
    return candidates[0] if candidates else None


def slot_texts(row: dict, slot: int) -> tuple[str | None, str | None]:
    x = (780, 1110, 1440)[slot]
    nearby = [item for item in row["audit"]["texts"]
              if abs(item["x"] + item["w"] / 2 - x) < 4]
    values = [item["text"].strip() for item in nearby
              if 320 <= item["y"] <= 390 and re.fullmatch(r"\d{1,2}", item["text"].strip())]
    labels = [item["text"].strip() for item in nearby
              if item["text"].strip().startswith(f"第{slot+1}路")]
    check(len(values) <= 1 and len(labels) <= 1, "actual-hash-slot-glyph-unique", (row["frame"], slot))
    return (values[0] if values else None, labels[0] if labels else None)


def last_before(rows: list[dict], moment: float) -> dict | None:
    return next((row for row in reversed(rows) if row["local"] < moment), None)


def first_at_or_after(rows: list[dict], moment: float) -> dict | None:
    return next((row for row in rows if row["local"] >= moment), None)


def check_boundary(rows: list[dict], moment: float, position: int, before: int, after: int,
                   name: str) -> dict:
    left = last_before(rows, moment)
    right = first_at_or_after(rows, moment)
    check(left is not None and right is not None, "phase-boundary-bracket", (name, moment))
    if left is not None and right is not None:
        check(int(position in left["ones"]) == before,
              "actual-bit-before-boundary", (name, left["frame"], position, before))
        check(int(position in right["ones"]) == after,
              "actual-bit-after-boundary", (name, right["frame"], position, after))
    return {"name": name, "localBoundary": moment, "position": position,
            "beforeGlobalFrame": left["frame"] if left else None,
            "afterGlobalFrame": right["frame"] if right else None,
            "beforeValue": before, "afterValue": after}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--samples", type=Path, default=D / "remotion/out/preflight/samples.json")
    args = ap.parse_args()
    sample_path = args.samples.resolve()
    rendered = json.loads(sample_path.read_text())
    model = json.loads((D / "model.json").read_text())
    sb = json.loads((D / "storyboard.json").read_text())
    events = json.loads((D / "qa-animation-events.json").read_text())
    plan = json.loads((D / "qa-preflight-plan.json").read_text())
    check(events["inputs"]["storyboard.json"] == sha(D / "storyboard.json"),
          "event-timing-input-identity", "storyboard")
    check(events["inputs"]["Main.tsx"] == sha(D / "remotion/src/Main.tsx"),
          "event-timing-input-identity", "Main event-clock source")
    check(rendered["inputProps"].get("auditLayout") is True,
          "actual-render-audit-enabled", rendered["inputProps"])
    for relative, expected in rendered["sourceSHA"].items():
        path = (ROOT / relative).resolve()
        check(path.is_relative_to(ROOT) and path.is_file() and sha(path) == expected,
              "actual-render-source-identity", relative)
    for required in ["episodes-codex/bloom-filter/storyboard.json",
                     "episodes-codex/bloom-filter/model.json",
                     "episodes-codex/bloom-filter/remotion/src/Main.tsx",
                     "episodes-codex/bloom-filter/remotion/src/graphics.tsx",
                     "episodes-codex/bloom-filter/remotion/src/LayoutAudit.tsx"]:
        check(required in rendered["sourceSHA"], "required-render-input-recorded", required)

    shots = []
    offset = 0
    for scene in sb["scenes"]:
        for original in scene["shots"]:
            shot = {**original, "id": str(original["id"]).zfill(2), "from": offset}
            check(original.get("from", offset) == offset, "storyboard-offset", shot["id"])
            shots.append(shot)
            offset += int(shot["durationInFrames"])
    check(offset == events["bodyFrames"] == plan["bodyFrames"], "body-timing-total", offset)
    expected_frames = sorted(set(plan["frames"]))
    actual_frames = [sample["frame"] for sample in rendered["samples"]]
    check(sorted(actual_frames) == expected_frames and len(actual_frames) == len(set(actual_frames)),
          "completed-planned-sample-matrix", (len(actual_frames), len(expected_frames)))
    check(len(rendered["audits"]) == len(actual_frames), "sample-dom-count", len(rendered["audits"]))
    check(not rendered.get("violations"), "preflight-layout-gate", len(rendered.get("violations", [])))
    audits = {audit["frame"]: audit for audit in rendered["audits"]}
    event_shots = {shot["id"]: shot for shot in events["shots"]}
    groups: dict[str, list[dict]] = defaultdict(list)
    geometry: dict[int, tuple[float, ...]] = {}
    display_to_key = {item["display"]: item["key"] for item in model["items"]}
    positions = {item["key"]: item["positions"] for item in model["items"]}
    displays = {item["key"]: item["display"] for item in model["items"]}
    actual_rows = []
    for sample in sorted(rendered["samples"], key=lambda item: item["frame"]):
        frame = sample["frame"]
        audit = audits.get(frame)
        check(audit is not None, "actual-dom-present", frame)
        if audit is None:
            continue
        shot = next((shot for shot in shots if shot["from"] <= frame < shot["from"] + shot["durationInFrames"]), None)
        check(shot is not None, "real-frame-in-storyboard", frame)
        if shot is None:
            continue
        local = frame - shot["from"]
        check(sample["local"] == local and str(sample["shot"]).zfill(2) == shot["id"],
              "real-frame-shot-binding", frame)
        check(sample["visualType"] == shot["visualType"] and audit["kind"] == "main",
              "real-frame-kind-binding", frame)
        png = Path(sample["file"])
        check(png.is_file() and sha(png) == sample["sha256"], "actual-png-identity", frame)
        indices = [bit["index"] for bit in audit.get("bits", [])]
        check(len(indices) == len(set(indices)) and indices == sorted(indices), "bit-index-unique-order", frame)
        check(all(isinstance(index, int) and 0 <= index < model["bitCount"] for index in indices),
              "bit-index-range", frame)
        glyph_ones: set[int] = set()
        for bit in audit.get("bits", []):
            value_text = bit["bitValueText"].strip()
            check(value_text in {"0", "1"}, "actual-binary-glyph", (frame, bit["index"], value_text))
            check(bit["indexText"].strip() == str(bit["index"]),
                  "actual-index-glyph", (frame, bit["index"], bit["indexText"]))
            check(value_text == str(bit["value"]), "actual-glyph-value-attribute-agree", (frame, bit["index"]))
            if value_text == "1":
                glyph_ones.add(bit["index"])
            box = tuple(float(bit[name]) for name in ["x", "y", "w", "h"])
            if bit["index"] in geometry:
                check(all(abs(left-right) < .05 for left, right in zip(box, geometry[bit["index"]])),
                      "bit-position-continuity", (frame, bit["index"]))
            else:
                geometry[bit["index"]] = box
        if shot["visualType"] == "missing":
            check(not indices, "opening-has-no-premature-bit-array", frame)
        elif shot["visualType"] == "bits":
            check(indices == list(range(len(indices))) and 1 <= len(indices) <= 16,
                  "progressive-array-reveal", frame)
        else:
            check(indices == list(range(16)), "complete-array-visible", frame)
        catalog_lists = []
        for catalog in audit.get("catalogs", []):
            lines = [value.strip() for value in catalog["actualTexts"] if value.strip().startswith("收录 ")]
            check(len(lines) == 1, "actual-directory-row-visible", frame)
            actual_displays = re.findall(r"\d{3}", lines[0]) if lines else []
            actual_keys = [display_to_key.get(value, "UNKNOWN:" + value) for value in actual_displays]
            check(actual_keys == catalog["records"], "actual-directory-text-attribute-agree", frame)
            catalog_lists.append(actual_keys)
        row = {"frame": frame, "local": local, "shot": shot, "audit": audit,
               "ones": glyph_ones, "catalogs": catalog_lists}
        key_display = card_key(row)
        if key_display is not None:
            key = display_to_key.get(key_display)
            check(key is not None, "actual-key-exists-in-model", (frame, key_display))
            if key is not None:
                for slot, expected_position in enumerate(positions[key]):
                    value, _ = slot_texts(row, slot)
                    if value is not None:
                        check(value == str(expected_position), "actual-hash-result-glyph", (frame, slot, key_display))
        groups[shot["id"]].append(row)
        actual_rows.append({"globalFrame": frame, "localFrame": local, "shot": shot["id"],
                            "visualType": shot["visualType"], "actualOneGlyphIndices": sorted(glyph_ones),
                            "actualCatalogKeys": catalog_lists, "actualHashInputGlyph": key_display,
                            "actualSlotLabels": [slot_texts(row, slot)[1] for slot in range(3)],
                            "pngSHA256": sample["sha256"]})

    normal = set(model["snapshots"]["after205"])
    first = set(model["snapshots"]["after101"])
    original_catalog = model["catalogInitially"]
    boundaries = []
    for shot in shots:
        rows = groups[shot["id"]]
        check(bool(rows), "shot-has-actual-dom-samples", shot["id"])
        if not rows:
            continue
        check(rows[0]["local"] == 0 and rows[-1]["local"] == shot["durationInFrames"]-1,
              "shot-start-and-tail-sampled", shot["id"])
        ev = event_shots[shot["id"]]
        for i, voice in enumerate(shot["voice"]):
            start = float(shot["cueFrames"]["sentences"][i])
            end = float(voice["localEnd"])
            check(abs(start - ev["sentenceSpans"][i][0]) < 1e-7 and
                  abs(end - ev["sentenceSpans"][i][1]) < 1e-7,
                  "real-sentence-window-binding", (shot["id"], i))
        kind = shot["visualType"]
        if kind in {"bits", "hash"}:
            for row in rows:
                check(not row["ones"], "unwritten-array-remains-zero", row["frame"])
        if kind in {"insert-101", "insert-205"}:
            base = set() if kind == "insert-101" else first
            targets = set(positions["sku101" if kind == "insert-101" else "sku205"])
            wanted_end = base | targets
            check(rows[0]["ones"] == base, "insertion-start-state", shot["id"])
            check(rows[-1]["ones"] == wanted_end, "insertion-final-state", shot["id"])
            previous = base
            for row in rows:
                check(base <= row["ones"] <= wanted_end, "insertion-only-targets-change", row["frame"])
                check(previous <= row["ones"], "actual-insertion-monotonicity", row["frame"])
                previous = row["ones"]
            for event in ev["events"]:
                if event["kind"] in {"set-one-on-arrival", "set-one-or-keep-one"}:
                    position = event["position"]
                    boundaries.append(check_boundary(rows, event["arrive"], position,
                                                     int(position in base), 1, f"{shot['id']}:write:{position}"))
        if kind in {"reject-001", "why-zero", "false-positive", "shared-marks", "gate"}:
            for row in rows:
                check(row["ones"] == normal, "queries-never-modify-marks", row["frame"])
        if kind == "reject-001":
            read_events = [event for event in ev["events"] if event["kind"] == "read-until-zero"]
            check([event["position"] for event in read_events] == [12, 2], "negative-query-probe-prefix", shot["id"])
            finish = read_events[-1]["arrive"]
            for row in rows:
                check(card_key(row) == "001", "negative-query-actual-key", row["frame"])
                if row["local"] < finish:
                    check(not has(row, "位置2是0 → 排除001"), "no-premature-negative-result", row["frame"])
                else:
                    check(has(row, "位置2是0 → 排除001") and has(row, "这次不查库"),
                          "actual-zero-rejection-and-db-stop", row["frame"])
                    check(slot_texts(row, 2)[1] == "第3路 · 未探测",
                          "actual-third-slot-unprobed-label", row["frame"])
        if kind == "false-positive":
            finish = max(event["arrive"] for event in ev["events"] if event["kind"] == "read-three-ones")
            confirm = next(event["begin"] for event in ev["events"] if event["kind"] == "database-confirms-absent")
            for row in rows:
                check(card_key(row) == "067", "false-positive-actual-key", row["frame"])
                check((not has(row, "三位全1 → 可能存在067")) if row["local"] < finish else has(row, "三位全1 → 可能存在067"),
                      "all-one-result-after-actual-probes", row["frame"])
                check((not has(row, "确认：没有067")) if row["local"] < confirm else has(row, "确认：没有067"),
                      "authoritative-confirmation-not-premature", row["frame"])
        if kind == "gate":
            switch = next(event["begin"] for event in ev["events"] if event["kind"] == "independent-query-switch")
            for row in rows:
                check(card_key(row) == ("001" if row["local"] < switch else "067"),
                      "independent-query-key-switch", row["frame"])
        if kind == "capacity":
            restored = next(event["begin"] for event in ev["events"] if event["kind"] == "restore-original-bits")
            check(rows[0]["ones"] == normal and rows[-1]["ones"] == normal,
                  "capacity-original-start-tail", shot["id"])
            check(any(row["ones"] > normal for row in rows), "capacity-actually-shows-denser-state", shot["id"])
            previous = normal
            for row in rows:
                check(normal <= row["ones"] <= set(range(16)), "capacity-keeps-original-marks", row["frame"])
                if row["local"] < restored:
                    check(previous <= row["ones"], "capacity-density-monotonicity-before-restore", row["frame"])
                    previous = row["ones"]
                else:
                    check(row["ones"] == normal and has(row, "原示例已恢复"),
                          "capacity-actual-restoration", row["frame"])
                if row["ones"] != normal:
                    check(has(row, "另一份容量示意") and has(row, "不执行查询"),
                          "capacity-alternate-state-clearly-labeled", row["frame"])
        if kind == "bad-delete":
            restore = next(event["begin"] for event in ev["events"] if event["kind"] == "restore-bits-and-catalog")
            clears = [event for event in ev["events"] if event["kind"] == "invalid-clear"]
            check([event["position"] for event in clears] == positions["sku101"], "wrong-clear-targets", shot["id"])
            check(rows[0]["ones"] == normal and rows[-1]["ones"] == normal,
                  "wrong-deletion-start-tail-restored", shot["id"])
            previous = normal
            for row in rows:
                if row["local"] < restore:
                    check(normal - set(positions["sku101"]) <= row["ones"] <= normal,
                          "wrong-clear-only-explicit-counterexample-targets", row["frame"])
                    check(row["ones"] <= previous, "wrong-clear-monotonic-loss-before-reset", row["frame"])
                    check(has(row, "错误删除反例"), "invalid-operation-visibly-labeled", row["frame"])
                    previous = row["ones"]
                else:
                    check(row["ones"] == normal and row["catalogs"] == [original_catalog],
                          "bits-and-catalog-restore-together", row["frame"])
                    check(has(row, "已恢复101 / 205的原始状态"), "actual-restoration-label", row["frame"])
            for event in clears:
                boundaries.append(check_boundary(rows, event["arrive"], event["position"], 1, 0,
                                                 f"{shot['id']}:invalid-clear:{event['position']}"))
            rejection = [event for event in ev["events"] if event["kind"] == "query-205-wrongly-rejected"]
            finish = rejection[-1]["arrive"]
            for row in rows:
                if finish <= row["local"] < restore:
                    check(card_key(row) == "205" and has(row, "205仍在目录，却被位置3的0错拦")
                          and row["catalogs"] == [["sku205"]], "shared-bit-harm-actual-witness", row["frame"])
                    check(slot_texts(row, 2)[1] == "第3路 · 未探测",
                          "wrong-query-stops-at-shared-zero", row["frame"])
        if kind == "maintenance":
            new_catalog = [*original_catalog, "sku001"]
            writes = [event for event in ev["events"] if event["kind"] == "correct-insert-001"]
            changed = next(event for event in writes if event["position"] == 2)
            check(rows[0]["ones"] == normal and rows[-1]["ones"] == normal | {2},
                  "maintenance-start-final-state", shot["id"])
            previous = normal
            for row in rows:
                check(row["catalogs"] == [new_catalog], "actual-new-catalog-record-present", row["frame"])
                check(normal <= row["ones"] <= normal | {2}, "maintenance-only-missing-bit-can-change", row["frame"])
                check(previous <= row["ones"], "maintenance-correct-write-monotonicity", row["frame"])
                previous = row["ones"]
            boundaries.append(check_boundary(rows, changed["arrive"], 2, 0, 1, "13:correct-insert:2"))
            stale_done = max(event["arrive"] for event in ev["events"] if event["kind"] == "unsafe-stale-query")
            second_sentence = ev["sentenceSpans"][1][0]
            fixed_done = max(event["arrive"] for event in writes)
            for row in rows:
                if stale_done <= row["local"] < second_sentence:
                    check(2 not in row["ones"] and has(row, "危险：旧标记的0不能证明目录不存在"),
                          "stale-zero-unsafe-actual-witness", row["frame"])
                    check(slot_texts(row, 2)[1] == "第3路 · 未探测",
                          "stale-query-third-slot-unprobed-label", row["frame"])
                if row["local"] >= fixed_done:
                    check(row["ones"] == normal | {2} and has(row, "确认：001存在"),
                          "correctly-maintained-positive-confirmation", row["frame"])

        if kind in {"missing", "reject-001", "false-positive", "gate"}:
            for row in rows:
                check(row["catalogs"] == [original_catalog], "normal-catalog-does-not-acquire-false-key", row["frame"])

    report = {
        "status": "passed" if not FAILURES else "failed",
        "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
        "checkedAtBeijing": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "reviewer": "Independent model/DOM-review agent",
        "scope": "Completed real Chromium DOM/glyph samples and independent logical invariants/phase-boundary witnesses.",
        "inputs": {"samples.json": sha(sample_path), "model.json": sha(D / "model.json"),
                   "storyboard.json": sha(D / "storyboard.json"),
                   "qa-animation-events.json": sha(D / "qa-animation-events.json"),
                   "qa-preflight-plan.json": sha(D / "qa-preflight-plan.json")},
        "checkerSHA256": sha(Path(__file__)), "sampleReport": str(sample_path.relative_to(ROOT)),
        "actualSampleCount": len(actual_rows), "bodyFrames": offset, "shotCount": len(shots),
        "assertionsExecuted": sum(COUNTS.values()), "assertionsByCategory": dict(sorted(COUNTS.items())),
        "failures": FAILURES, "phaseBoundaryWitnesses": boundaries,
        "actualSamples": actual_rows,
        "independence": [
            "Scene.state was not read. Bit values use actual SVG glyphs, cross-checked with actual index glyphs and DOM attributes.",
            "Catalog records use actual visible directory-row text, cross-checked with DOM attributes and model keys.",
            "No production stages/easing function was copied or imported. Event metadata only locates before/after witnesses; invariants independently constrain legal state changes.",
            "Hash output glyphs are read from their actual card positions and compared against the model's verified SHA-derived locations.",
        ],
        "limitations": [
            "This does not inspect PNG pixels, every continuous frame, motion readability, audio or final encoded media.",
            "The third probe's unprobed claim is checked as actual visible card text and zero-stop result; this audit does not capture every SVG path or probe color.",
            "Event scheduling comes from the recorded timing plan bound to the actual storyboard/Main source; it is not an independent speech recognizer.",
        ],
    }
    (D / "qa-dom-state-independent.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    summary = (
        "# 布隆过滤器实际DOM独立状态复核\n\n"
        f"状态：{report['status']}。实际读取{len(actual_rows)}个真实Chromium采样帧，覆盖{len(shots)}镜、{offset}帧正文；"
        f"执行{report['assertionsExecuted']:,}项检查，发现{len(FAILURES)}项失败。\n\n"
        "不读取Scene自报state，不导入或逐行复制stages。独立核对实际位值/下标文字、位置连续性、哈希卡片结果和目录实际文本，"
        "检查插入单调及非目标位保持、查询不写位、任意0停止提示、容量示意恢复、错误删除误伤与位图/目录同时恢复、新增001的旧标记风险和正确补写。"
        "阶段计划只用于定位边界前后实际帧；具体样本、边界、输入完整SHA和失败明细见JSON。\n\n"
        "本报告限定为真实DOM/glyph与状态机制检查。第三路未探测通过实际卡片文字和早停结果核对，未把它扩写为所有SVG轨迹像素检查。"
        "未作画面像素、连续媒体可读性、听辨或正式成片验收。\n"
    )
    (D / "qa-dom-state-independent.md").write_text(summary)
    print(json.dumps({"status": report["status"], "samples": len(actual_rows),
                      "assertionsExecuted": report["assertionsExecuted"], "failureCount": len(FAILURES),
                      "firstFailures": FAILURES[:8]}, ensure_ascii=False))
    if FAILURES:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
