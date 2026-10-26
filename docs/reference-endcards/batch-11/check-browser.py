#!/usr/bin/env python3
"""Inspect only final-built batch-11 cards: --base-url http://127.0.0.1:4321/video-studio/.

Four desktop 1x tail plays to ended and four paused mobile native-fullscreen
cases. Every actual page needs a screenshot in each viewport and actual
view_image review; Any selected film can have multiple pages. Reuses unchanged historical
traversal/UI rules, without prior-batch fetches or an assumed old media proof.
"""
from pathlib import Path
import inspect
import json
import sys

import _qa as QA
from _batch_runtime import _load, browser_engine

ENGINE = browser_engine(QA)
# The preserved title-author case binds its helpers to this isolated _qa
# adapter. Its run_case avoids an extra full MP4 GET during browser testing.
TITLE_UI = _load("batch11_title_author_ui", Path(__file__).resolve().parent.parent / "title-author/check-browser.py")
source = inspect.getsource(TITLE_UI.run_case)
old_elapsed = 'playback["elapsedSeconds"]>final-body_end-1'
assert source.count(old_elapsed) == 1
source = source.replace(old_elapsed, 'playback["playbackRate"] == 1 and playback["elapsedSeconds"]>final-body_end-1')
# On-demand citations retain strict excerpt/location checks. Open a provided
# quotation through its real entry before reading visible text, then choose
# only displayed source anchors; hidden duplicate links are not actionable.
old_context = 'color_scheme="dark", reduced_motion="reduce")'
assert source.count(old_context) == 1
source = source.replace(old_context, 'color_scheme="dark", reduced_motion="reduce", has_touch=(name == "mobile"))')
old_source_loop = '        for source in refs["sources"]:\n            texts = [source["title"]]'
assert source.count(old_source_loop) == 1
source = source.replace(old_source_loop, '''        for source in refs["sources"]:
            if "quotation" in source:
                trigger = page.locator('button[data-source-trigger="' + source["id"] + '"]')
                if trigger.count():
                    if name == "mobile":
                        trigger.tap()
                    else:
                        trigger.click()
                    page.wait_for_function("id => document.querySelector('aside[data-source-panel=\\"' + id + '\\"]')?.matches(':popover-open')", arg=source["id"])
                    check(source["id"] + " actual citation entry opens exact original quotation", trigger.get_attribute("aria-expanded") == "true")
                    case.setdefault("openedReferenceSourcePanels", []).append({"sourceId": source["id"], "input": "touch tap" if name == "mobile" else "mouse click"})
                    article = UI.normalized(page.locator("#article").inner_text())
            texts = [source["title"]]''')
old_indexes = 'indexes = links.evaluate_all("(els,url)=>els.flatMap((a,i)=>a.href===url?[i]:[])", url)'
assert source.count(old_indexes) == 1
source = source.replace(old_indexes, 'indexes = links.evaluate_all("(els,url)=>els.flatMap((a,i)=>a.href===url && a.getClientRects().length && getComputedStyle(a).visibility!==\\"hidden\\" ?[i]:[])", url)')
namespace = dict(vars(TITLE_UI))
exec(compile(source, str(Path(__file__).resolve()) + "#first-append-no-code-card", "exec"), namespace)
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
                  scope="Four batch-11 first appendices after complete original bodies with no code cards; derived pages, title/credit-only cards, 4 desktop 1x endings and 4 native mobile fullscreen cases. No prior-batch media or old appendix proof.")
    report["automatedAssertionsPassed"] = bool(report["automatedAssertionsPassed"] and counts)
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
