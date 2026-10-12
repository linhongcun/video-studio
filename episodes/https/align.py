#!/usr/bin/env python3
"""Align storyboard.json shot durations to measured voiceover timing.json.

Reads timing.json (per-shot duration / scale / audioFrames). Updates each
shot's durationInFrames, scales subtitle from/to and animation keyframe frames
by new/old ratio (rounded), recalculates shot/scene from and meta.durationInFrames.

Usage:
  python3 align.py [timing.json] [storyboard.json]
Defaults: ./timing.json ./storyboard.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_TIMING = HERE / "timing.json"
DEFAULT_SB = HERE / "storyboard.json"


def scale_frame(f: int, old: int, new: int) -> int:
    if old <= 1:
        return 0
    return max(0, min(new - 1, round(f * new / old)))


def scale_subtitles(subs: list, old: int, new: int) -> list:
    if not subs:
        return subs
    out = []
    for st in subs:
        a = scale_frame(st["from"], old, new)
        b = scale_frame(st["to"], old, new)
        if b < a:
            b = a
        out.append({**st, "from": a, "to": b})
    # Repair overlaps / order; keep last subtitle ending at new-1
    for i in range(1, len(out)):
        if out[i]["from"] <= out[i - 1]["to"]:
            out[i]["from"] = out[i - 1]["to"] + 1
        if out[i]["from"] > out[i]["to"]:
            out[i]["to"] = out[i]["from"]
        if out[i]["to"] >= new:
            out[i]["to"] = new - 1
        if out[i]["from"] >= new:
            out[i]["from"] = new - 1
            out[i]["to"] = new - 1
    out[-1]["to"] = new - 1
    # Drop empty/inverted after clamp
    cleaned = []
    for st in out:
        if 0 <= st["from"] <= st["to"] < new:
            cleaned.append(st)
    if cleaned:
        cleaned[-1]["to"] = new - 1
    return cleaned or [{"text": subs[-1]["text"], "from": 0, "to": new - 1}]


def scale_animations(anims: list, old: int, new: int) -> list:
    out = []
    for a in anims:
        kfs = []
        for k in a.get("keyframes", []):
            kfs.append({**k, "frame": scale_frame(k["frame"], old, new)})
        # Keep keyframe order; if two collapse to same frame, nudge later ones
        last = -1
        for k in kfs:
            if k["frame"] <= last:
                k["frame"] = min(new - 1, last + 1)
            last = k["frame"]
        out.append({**a, "keyframes": kfs})
    return out


def align(timing_path: Path, sb_path: Path) -> dict:
    timing = json.loads(timing_path.read_text())
    sb = json.loads(sb_path.read_text())
    g = 0
    missing = []
    for sc in sb["scenes"]:
        sc["from"] = g
        f = g
        for sh in sc["shots"]:
            sid = sh["id"]
            if sid not in timing:
                missing.append(sid)
                continue
            old = sh["durationInFrames"]
            new = int(timing[sid]["duration"])
            if new < 1:
                raise SystemExit(f"invalid duration for {sid}: {new}")
            sh["from"] = f
            if old != new:
                sh["subtitles"] = scale_subtitles(sh.get("subtitles", []), old, new)
                sh["animations"] = scale_animations(sh.get("animations", []), old, new)
            sh["durationInFrames"] = new
            f += new
        sc["durationInFrames"] = f - g
        g = f
    if missing:
        raise SystemExit(f"shots missing from timing.json: {missing}")
    sb["meta"]["durationInFrames"] = g
    # 第二期：保留 gen.py 写入的 meta.notes，不覆盖
    sb_path.write_text(json.dumps(sb, ensure_ascii=False, indent=1) + "\n")
    return {
        "total": g,
        "scenes": [
            (sc["chapterId"], sc["from"], sc["durationInFrames"], len(sc["shots"]))
            for sc in sb["scenes"]
        ],
        "shots": [
            (sh["id"], sh["from"], sh["durationInFrames"])
            for sc in sb["scenes"]
            for sh in sc["shots"]
        ],
    }


def main():
    timing = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TIMING
    sb = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SB
    r = align(timing, sb)
    print("total", r["total"])
    for row in r["scenes"]:
        print("scene", *row)
    for row in r["shots"]:
        print("shot", *row)


if __name__ == "__main__":
    main()
