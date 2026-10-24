#!/usr/bin/env python3
"""Replace only frames 0..236, then copy the approved V2 tail and whole AAC."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile

D = Path(__file__).resolve().parent
C = runpy.run_path(str(D / "check-splice.py"))


def main():
    args = C["parser"](__doc__).parse_args()
    report = {"checkedAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "status": "blocked",
              "mode": "preflight" if args.preflight_only else "compose-and-check", "commands": []}
    report_path_safe = False
    try:
        C["safe_report_path"](args.report, D, args.base, args.opening, args.output)
        report_path_safe = True
        report["freeze"] = C["frozen_inputs"](D, args.base)
        state = C["preflight"](args.base, args.opening)
        report["preflight"] = state["evidence"]
        if args.preflight_only:
            C["need"](report["freeze"] == C["frozen_inputs"](D, args.base), "Frozen manifest changed during preflight")
            report["status"] = "passed"
        else:
            C["need"](not args.output.exists(), f"Refusing to overwrite existing output: {args.output}")
            C["need"](args.output.resolve() not in (args.base.resolve(), args.opening.resolve()), "Output conflicts with an input")
            work = Path(tempfile.mkdtemp(prefix="splice-", dir=D / "remotion/out"))
            report["workDirectory"] = str(work)
            tail, listing, candidate = work / "tail-v2.mp4", work / "splice.ffconcat", work / "candidate.mp4"
            extract = ["ffmpeg", "-hide_banner", "-v", "warning", "-n", "-ss", "7.9", "-i", str(args.base.resolve()),
                       "-map", "0:v:0", "-an", "-c:v", "copy", "-avoid_negative_ts", "disabled",
                       "-use_editlist", "1", "-video_track_timescale", "90000", str(tail)]
            report["commands"].append(extract)
            C["command"](extract)
            report["tailExtraction"] = C["check_tail"](state, tail)
            # The opening path is relative to this scratch directory, avoiding
            # quoting user-supplied paths in ffconcat syntax. The scratch name
            # and tail filename are generated here and contain no quotes.
            local_head = work / "opening.mp4"
            shutil.copyfile(args.opening, local_head)
            C["need"](C["sha"](local_head) == state["evidence"]["openingSha256"], "Opening changed while copying")
            listing.write_text("ffconcat version 1.0\nfile 'opening.mp4'\nduration 7.900000\nfile 'tail-v2.mp4'\n")
            compose = ["ffmpeg", "-hide_banner", "-v", "warning", "-n", "-copyts", "-f", "concat", "-safe", "0",
                       "-auto_convert", "0", "-i", str(listing), "-i", str(args.base.resolve()),
                       "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", "-avoid_negative_ts", "disabled",
                       "-use_editlist", "1", "-video_track_timescale", "90000", "-movflags", "+faststart", str(candidate)]
            report["commands"].append(compose)
            C["command"](compose)
            report["checks"] = C["check_output"](args.base, args.opening, candidate, state)
            C["need"](report["freeze"] == C["frozen_inputs"](D, args.base), "Frozen manifest changed while composing")
            C["need"](C["sha"](args.opening) == state["evidence"]["openingSha256"], "Opening changed while composing")
            # Only a fully checked candidate becomes the canonical V3 MP4.
            C["need"](not args.output.exists(), f"Output appeared during validation: {args.output}")
            candidate.rename(args.output)
            report["output"] = str(args.output.resolve())
            report["status"] = "passed"
    except (C["SpliceError"], OSError, ValueError, KeyError) as error:
        report["error"] = str(error)
    if report_path_safe:
        C["write_report"](args.report, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
