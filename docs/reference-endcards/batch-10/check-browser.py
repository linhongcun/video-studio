#!/usr/bin/env python3
"""Inspect only final-built batch-10 cards: --base-url http://127.0.0.1:4321/video-studio/.

Five desktop 1x Python-card-to-reference plays to ended and five paused mobile native-fullscreen
cases. Every actual page needs a screenshot in each viewport and actual
view_image review; Any selected film can have multiple pages. Reuses unchanged historical
traversal/UI rules, without prior-batch fetches or an assumed old media proof.
"""
from pathlib import Path
import json
import inspect
import sys

import _qa as QA
from _batch_runtime import _load, browser_engine

ENGINE = browser_engine(QA)
# The preserved title-author case binds its helpers to this isolated _qa
# adapter. Its run_case avoids an extra full MP4 GET during browser testing.
TITLE_UI = _load("batch10_title_author_ui", Path(__file__).resolve().parent.parent / "title-author/check-browser.py")
# Preserve the historical helper, but start this batch's actual continuous
# playback before the original Python card. This crosses the original audio
# endpoint, all 150 Python frames, then every new reference page at real 1x.
source = inspect.getsource(TITLE_UI.run_case)
old_start = '{"from": body_end-.2, "bodyEnd": body_end'
new_start = '{"from": expected["existingCodeCard"]["from"]/fps-.2, "bodyEnd": body_end'
assert source.count(old_start) == 1
source = source.replace(old_start, new_start)
old_elapsed = 'playback["elapsedSeconds"]>final-body_end-1'
assert source.count(old_elapsed) == 1
source = source.replace(old_elapsed,
    'playback["playbackRate"] == 1 and playback["elapsedSeconds"] > final - expected["existingCodeCard"]["from"]/fps - 1'
    ' and any(expected["existingCodeCard"]["from"]/fps + .5 < sample["time"] < body_end - .5 for sample in playback["samples"])')
assert source.count('if slug == "observer-pattern":') == 1
source = source.replace('if slug == "observer-pattern":', 'if True:')
source = source.replace("original Observer Java card", "original full Python card")
source = source.replace("preserved Java card", "preserved Python card")
source = source.replace("preserved-java-code-card", "preserved-python-code-card")
namespace = dict(vars(TITLE_UI))
exec(compile(source, str(Path(__file__).resolve()) + "#preserved-code-card-case", "exec"), namespace)
ENGINE.run_case = namespace["run_case"]
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
    page_counts = {slug: (len(QA.read(QA.ROOT / "episodes" / slug / "references.json")["sources"]) + 3) // 4
                   for slug in QA.targets()}
    expected_names = {f"{slug}-{viewport}-{prefix}reference-page-{number}.png"
                      for slug, count in page_counts.items()
                      for viewport, prefix in (("desktop", ""), ("mobile", "fullscreen-"))
                      for number in range(1, count + 1)}
    counts = (len(cases) == 2 * len(QA.targets()) and desktop == mobile == len(QA.targets())
              and len(required) == len(expected_names)
              and {Path(path).name for path in required} == expected_names)
    report.update(expectedUICaseCount=2 * len(QA.targets()), desktopTailPlaybackCount=desktop, mobileFullscreenCaseCount=mobile,
                  requiredCardScreenshots=required, expectedRequiredCardScreenshotCount=len(expected_names),
                  expectedReferencePageCount=sum(page_counts.values()), referencePageCounts=page_counts,
                  scope="Five batch-10 first appendices; derived pages, title/credit-only cards, 5 desktop 1x Python-card-to-reference endings and 5 native mobile fullscreen cases. No prior-batch media or old appendix proof.")
    preserved_cards = [c.get("preservedCodeCard") for c in cases if c["name"] == "desktop"]
    code_check = (len(preserved_cards) == len(QA.targets()) and all(preserved_cards))
    report["originalPythonCardsActuallyPaused"] = len([x for x in preserved_cards if x])
    report["automatedAssertionsPassed"] = bool(report["automatedAssertionsPassed"] and counts and code_check)
    report["limitations"] = [item.replace("three changed appendices", "five changed appendices") for item in report.get("limitations", [])]
    if not report["automatedAssertionsPassed"]:
        report["status"] = "failed"
    report["visualReview"] = f"Pending actual view_image inspection of all {len(expected_names)} required card screenshots."
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
