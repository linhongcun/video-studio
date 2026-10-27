#!/usr/bin/env python3
"""Real-browser QA for MQ's independent learning direction.

Run against a built preview or Pages using --base. In environments where
Chromium lacks the managed proxy CA, --transport-helper may point to the
separately recorded TLS-verified urllib adapter. HTTPS verification stays on.
This checks classification/navigation/images; it does not re-review the MP4.
"""
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
MQ = "message-queue"
EP = "/video-studio/episodes/message-queue/"
SERIES = "/video-studio/series/message-queue/"
TRACK = "/video-studio/learn/#message-queue"
EXPECTED = {"all": 48, "systems": 24, "peak": 4, "mq": 1, "leetcode": 11, "directions": 7}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Site root including /video-studio/")
    parser.add_argument("--out", default=str(Path(__file__).parent / "qa-local"))
    parser.add_argument("--expected-version", default=None)
    parser.add_argument("--transport-helper", type=Path, default=None)
    parser.add_argument("--deployment", default=None, help="Optional successful Pages run ID, recorded as supplied")
    args = parser.parse_args()
    base = args.base.rstrip("/") + "/"
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    expected_version = args.expected_version or json.loads((ROOT / "site/package.json").read_text())["version"]
    checks, visits, screenshots, browser_errors = [], [], [], []
    report = {
        "checkedAt": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "base": base,
        "expectedVersion": expected_version,
        "expected": EXPECTED,
        "deploymentRunAsSupplied": args.deployment,
        "sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scriptSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "Actual 1440px/390px browser DOM, classification, navigation, filters and existing thumbnail loading. No MP4 playback or source-popover re-review.",
        "httpsVerificationDisabled": False,
        "checks": checks,
        "visits": visits,
        "screenshots": screenshots,
        "browserErrors": browser_errors,
    }
    transport = None

    def check(name, passed, details=None):
        checks.append({"name": name, "passed": bool(passed), "details": details})
        if not passed:
            raise AssertionError(f"{name}: {details}")

    def screenshot(page, name, locator=None):
        path = out / (name + ".png")
        if locator is None:
            page.screenshot(path=str(path), full_page=True)
        else:
            locator.screenshot(path=str(path))
        screenshots.append(path.name)

    def go(page, suffix, width):
        response = page.goto(base + suffix, wait_until="domcontentloaded", timeout=60000)
        status = response.status if response else None
        visits.append({"width": width, "url": page.url, "status": status})
        check(f"{width}: GET {suffix}", status == 200, status)
        page.locator(".footer-bottom").wait_for()
        version = page.locator(".footer-bottom").inner_text()
        check(f"{width}: version {suffix}", f"v{expected_version}" in version, version)
        page.evaluate("document.fonts.ready")

    def no_overflow(page, name):
        size = page.evaluate("({content:document.documentElement.scrollWidth,viewport:innerWidth})")
        check(name, size["content"] <= size["viewport"], size)

    def load_images(page, locator, name):
        for image in locator.all():
            image.scroll_into_view_if_needed()
            image.evaluate("el => el.loading = 'eager'")
            image.wait_for(state="visible")
            image.evaluate("el => el.decode()")
        rows = locator.evaluate_all("els => els.map(el => ({src:el.getAttribute('src'),complete:el.complete,width:el.naturalWidth,height:el.naturalHeight}))")
        check(name, len(rows) == EXPECTED["leetcode"] and all(r["complete"] and r["width"] > 0 and r["height"] > 0 for r in rows), rows)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox"])
            if args.transport_helper:
                helper = args.transport_helper.resolve()
                spec = importlib.util.spec_from_file_location("mq_verified_transport", helper)
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                origin = "{0.scheme}://{0.netloc}".format(urlsplit(base))
                transport = module.install_browser_transport(browser, origin=origin)
                report["transportHelper"] = {"path": str(helper), "sha256": hashlib.sha256(helper.read_bytes()).hexdigest()}
            else:
                report["transport"] = {"mode": "Direct Chromium networking; HTTPS verification remains enabled."}

            for width, height in [(1440, 1000), (390, 844)]:
                page = browser.new_page(viewport={"width": width, "height": height}, reduced_motion="reduce", ignore_https_errors=False, service_workers="block")
                page.on("pageerror", lambda error: browser_errors.append(str(error)))

                go(page, "", width)
                mq_link = page.locator(".track-links a.track-message-queue")
                check(f"{width}: home has independent MQ entry", mq_link.count() == 1 and mq_link.get_attribute("href") == TRACK)
                check(f"{width}: home MQ has its own copy", "保存 · 投递 · 消费 · 确认" in mq_link.locator("p").text_content(), mq_link.inner_text())
                check(f"{width}: home MQ advertises only 1 lesson", mq_link.locator(".track-count").inner_text() == "1 篇")
                check(f"{width}: home has 7 learning directions", page.locator(".track-link").count() == EXPECTED["directions"])
                check(f"{width}: home total stays 48", "48" in page.locator(".hero-note").inner_text(), page.locator(".hero-note").inner_text())
                start = page.locator(f".start-grid a[href='{EP}']")
                check(f"{width}: home MQ intro uses existing EP URL", start.count() == 1 and "消息队列" in start.inner_text())
                no_overflow(page, f"{width}: home fits viewport")
                screenshot(page, f"home-mq-{width}", mq_link)

                go(page, "learn/", width)
                systems = page.locator("section.learning-track#systems")
                mq_track = page.locator("section.learning-track#message-queue")
                check(f"{width}: MQ is an independent sibling direction", mq_track.count() == 1 and systems.locator("#message-queue").count() == 0 and mq_track.evaluate("el => el.parentElement.classList.contains('learning-tracks')"))
                check(f"{width}: MQ direction has one series and lesson", "已发布 1 篇 · 1 个系列" in mq_track.inner_text())
                check(f"{width}: MQ direction starts at existing intro", mq_track.locator(f"a.btn[href='{EP}']").count() == 1)
                check(f"{width}: MQ direction links its own directory", mq_track.locator(f"a.chapter-heading[href='{SERIES}']").count() == 1)
                check(f"{width}: systems has 24 unique lessons and 5 series", "已发布 24 篇 · 5 个系列" in systems.inner_text())
                check(f"{width}: systems excludes MQ episode and series", systems.locator(f"a[href='{EP}'],a[href='{SERIES}']").count() == 0)
                all_lesson_hrefs = page.locator(".chapter-lessons a").evaluate_all("els => els.map(el=>el.getAttribute('href'))")
                check(f"{width}: all 48 lessons have one learning home", len(all_lesson_hrefs) == EXPECTED["all"] and len(set(all_lesson_hrefs)) == EXPECTED["all"], len(all_lesson_hrefs))
                no_overflow(page, f"{width}: learning page fits viewport")
                screenshot(page, f"learn-mq-{width}", mq_track)
                screenshot(page, f"learn-systems-{width}", systems)

                go(page, "series/message-queue/", width)
                lessons = page.locator(".lesson-list a.lesson")
                breadcrumb = page.locator(".bc").inner_text()
                check(f"{width}: MQ directory only reuses one EP", lessons.count() == 1 and lessons.get_attribute("href") == EP)
                check(f"{width}: MQ directory has no systems breadcrumb", "系统原理" not in breadcrumb and breadcrumb.count("消息队列") == 1, breadcrumb)
                check(f"{width}: MQ directory promises independent viewing", "可以独立观看" in page.locator(".series-overview").inner_text())
                no_overflow(page, f"{width}: MQ directory fits viewport")
                screenshot(page, f"series-mq-{width}")

                go(page, "series/peak/", width)
                peak_lessons = page.locator(".lesson-list a.lesson")
                check(f"{width}: peak has 4 lessons and excludes MQ", peak_lessons.count() == EXPECTED["peak"] and page.locator(f".lesson-list a[href='{EP}']").count() == 0)
                check(f"{width}: peak description excludes MQ", "消息队列" not in page.locator(".page-intro").inner_text())

                go(page, "episodes/message-queue/", width)
                directory = page.locator("#course-directory")
                check(f"{width}: EP10 breadcrumb uses MQ only", "消息队列" in page.locator(".bc").inner_text() and "系统原理" not in page.locator(".bc").inner_text() and "扛住高峰" not in page.locator(".bc").inner_text() and "EP.10" in page.locator(".bc").inner_text(), page.locator(".bc").inner_text())
                page.locator("[data-open-course]").click()
                check(f"{width}: EP10 opens only its MQ course directory", directory.get_attribute("open") is not None and "消息队列" in directory.locator("summary").inner_text() and directory.locator("ol li").count() == 1 and directory.locator("ol a").get_attribute("href") == EP)
                check(f"{width}: EP10 has no system previous or next lesson", page.locator("nav.pager").count() == 0)
                check(f"{width}: EP10 footer points to MQ directory", page.locator(f".sp a[href='{SERIES}']").count() == 2)
                no_overflow(page, f"{width}: EP10 fits viewport")
                screenshot(page, f"ep10-directory-{width}", directory)

                go(page, "episodes/cache-consistency/", width)
                check(f"{width}: system chain skips MQ toward rate-limit", page.locator("nav.pager a.r").get_attribute("href") == "/video-studio/episodes/rate-limit/")
                go(page, "episodes/rate-limit/", width)
                check(f"{width}: rate-limit goes back to cache-consistency", page.locator("nav.pager a.p:not(.r)").get_attribute("href") == "/video-studio/episodes/cache-consistency/")

                go(page, "library/?track=message-queue", width)
                page.locator(".catalog-controls:not([hidden])").wait_for()
                visible = page.locator("#library-grid>ul>li:not([hidden]) a.card")
                check(f"{width}: direct MQ track filter shows only original intro", page.locator("select[name='track']").input_value() == MQ and page.locator("select[name='series']").input_value() == "" and visible.count() == 1 and visible.get_attribute("href") == EP)
                go(page, "library/?series=message-queue", width)
                page.locator(".catalog-controls:not([hidden])").wait_for()
                check(f"{width}: MQ series URL selects independent MQ track", page.locator("select[name='track']").input_value() == MQ and page.locator("select[name='series']").input_value() == MQ)
                check(f"{width}: MQ library has one original card", visible.count() == 1 and visible.get_attribute("href") == EP and visible.get_attribute("data-series") == MQ and visible.get_attribute("data-track") == MQ)
                check(f"{width}: MQ library label is its own series", visible.locator(".series").inner_text() == "消息队列")
                screenshot(page, f"library-mq-{width}")
                page.select_option("select[name='track']", "systems")
                filter_state = page.locator("select[name='series']").evaluate("el => ({value:el.value,mqDisabled:el.querySelector('option[value=\"message-queue\"]').disabled})")
                check(f"{width}: systems clears incompatible MQ filter", filter_state["value"] == "" and filter_state["mqDisabled"], filter_state)
                check(f"{width}: systems filter has 24 and excludes MQ", visible.count() == EXPECTED["systems"] and all(row != EP for row in visible.evaluate_all("els => els.map(el=>el.getAttribute('href'))")))
                check(f"{width}: systems retains its 4 peak lessons", sum(value == "peak" for value in visible.evaluate_all("els => els.map(el=>el.dataset.series)")) == EXPECTED["peak"])
                page.select_option("select[name='series']", "peak")
                check(f"{width}: peak filter has 4 and excludes MQ", visible.count() == EXPECTED["peak"] and all(row != EP for row in visible.evaluate_all("els => els.map(el=>el.getAttribute('href'))")))
                page.locator("button.reset").click()
                hrefs = visible.evaluate_all("els => els.map(el=>el.getAttribute('href'))")
                check(f"{width}: reset restores 48 unique cards", len(hrefs) == EXPECTED["all"] and len(set(hrefs)) == EXPECTED["all"])
                page.select_option("select[name='track']", "algorithms")
                check(f"{width}: algorithm library keeps 11 cards", visible.count() == EXPECTED["leetcode"])
                load_images(page, visible.locator(".cover img"), f"{width}: all 11 algorithm library thumbnails decode")
                no_overflow(page, f"{width}: filtered library fits viewport")
                screenshot(page, f"library-leetcode-{width}")

                go(page, "series/leetcode/", width)
                check(f"{width}: LeetCode directory keeps 11 lessons", page.locator(".lesson-list a.lesson").count() == EXPECTED["leetcode"])
                # Narrow screens intentionally hide directory covers; actual
                # mobile thumbnail loading is exercised in the library above.
                if width >= 768:
                    load_images(page, page.locator(".lesson-cover img"), f"{width}: all 11 LeetCode directory thumbnails decode")
                    screenshot(page, f"series-leetcode-{width}")
                no_overflow(page, f"{width}: LeetCode directory fits viewport")
                page.close()
            check("browser has no uncaught page errors", not browser_errors, browser_errors)
            browser.close()
    except Exception as error:
        report["error"] = str(error)
    finally:
        if transport:
            report["transport"] = transport.report()
        report["passed"] = sum(row["passed"] for row in checks)
        report["failed"] = sum(not row["passed"] for row in checks)
        report["complete"] = "error" not in report
        (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"report": str(out / "report.json"), "passed": report["passed"], "failed": report["failed"], "complete": report["complete"], "error": report.get("error")}, ensure_ascii=False))
    return 0 if report["complete"] and not report["failed"] else 1


if __name__ == "__main__":
    sys.exit(main())
