#!/usr/bin/env python3
"""Inspect only final-built batch-5 cards: --base-url http://127.0.0.1:4321/video-studio/.

Three desktop 1x tail plays to ended and three paused mobile native-fullscreen
cases. The six required card screenshots need actual view_image review before
visual QA passes. Reuses unchanged three-episode traversal and title/author UI
rules; never discovers/fetches previous batches or assumes an old media proof.
"""
from pathlib import Path
import json
import sys

import _qa as QA
from _batch_runtime import _load, browser_engine

ENGINE = browser_engine(QA)
# The preserved title-author case binds its helpers to this isolated _qa
# adapter. Its run_case avoids an extra full MP4 GET during browser testing.
TITLE_UI = _load("batch5_title_author_ui", Path(__file__).resolve().parent.parent / "title-author/check-browser.py")
ENGINE.run_case = TITLE_UI.run_case
ENGINE.__doc__ = __doc__


def main():
    result = ENGINE.main()
    report_path = QA.OUT / "qa-browser.json"
    report = QA.read(report_path)
    cases = report["cases"]
    desktop = sum(c["name"] == "desktop" and bool(c.get("continuousPlayback", {}).get("ended")) for c in cases)
    mobile = sum(c["name"] == "mobile" and bool(c.get("fullscreenPages")) for c in cases)
    required = [path for case in cases for path in case["screenshots"]
                if "reference-page-" in Path(path).name]
    counts = len(cases) == 6 and desktop == mobile == 3 and len(required) == 6
    report.update(expectedUICaseCount=6, desktopTailPlaybackCount=desktop, mobileFullscreenCaseCount=mobile,
                  requiredCardScreenshots=required, expectedRequiredCardScreenshotCount=6,
                  scope="Three batch-5 first appendices; title/credit-only cards, 3 desktop 1x endings and 3 native mobile fullscreen cases. No prior-batch media or old appendix proof.")
    report["automatedAssertionsPassed"] = bool(report["automatedAssertionsPassed"] and counts)
    if not report["automatedAssertionsPassed"]:
        report["status"] = "failed"
    report["visualReview"] = "Pending actual view_image inspection of all six required card screenshots."
    report["passed"] = False
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    report_path.write_text(text)
    # Retain the same truthful counters in this attempt's own report.
    for path in QA.OUT.glob("qa-browser-attempt-*.json"):
        if QA.read(path).get("checkedAt") == report["checkedAt"]:
            path.write_text(text)
    return result or (0 if report["automatedAssertionsPassed"] else 1)


if __name__ == "__main__":
    raise SystemExit(main())
