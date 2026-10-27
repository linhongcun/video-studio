#!/usr/bin/env python3
"""Browser QA for the independent database learning direction.

Use --base for a local built preview or the canonical Pages site. Optional
--transport-helper loads the separately recorded urllib adapter while retaining
TLS validation. This verifies classification, course links and thumbnails, not
MP4 playback or complete media bytes. Earlier MQ QA evidence is not modified.
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
BASELINE = "bd5e75156c6eb248f83275ba038ca48746b6886f"
DB = ["db-index", "db-transaction", "db-lock", "db-replication"]
EP_ROOT = "/video-studio/episodes/"
SERIES = "/video-studio/series/database/"
TRACK = "/video-studio/learn/#database"
MQ_EP = EP_ROOT + "message-queue/"
EXPECTED = {"all": 48, "directions": 8, "database": 4, "systems": 20,
            "systemSeries": 4, "mq": 1, "leetcode": 11, "puzzles": 5}


def ep(slug):
    return EP_ROOT + slug + "/"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Site root including /video-studio/")
    parser.add_argument("--out", default=str(Path(__file__).parent / "qa-local"))
    parser.add_argument("--expected-version", default=None)
    parser.add_argument("--transport-helper", type=Path, default=None)
    parser.add_argument("--deployment", default=None, help="Optional Pages run ID; actual success evidence is recorded separately")
    args = parser.parse_args()
    base = args.base.rstrip("/") + "/"
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    version = args.expected_version or json.loads((ROOT / "site/package.json").read_text())["version"]
    db_meta = {slug: json.loads((ROOT / "episodes" / slug / "meta.json").read_text()) for slug in DB}
    checks, visits, screenshots, errors = [], [], [], []
    transport = None
    report = {
        "checkedAt": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "base": base, "expectedVersion": version, "expected": EXPECTED,
        "baseline": BASELINE,
        "sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scriptSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "deploymentRunAsSupplied": args.deployment,
        "databaseOrder": DB,
        "scope": "Actual 1440px/390px browser DOM, independent directions, database-only course navigation, system boundary links, library filtering and current thumbnail decoding. Existing media URL references are checked; MP4 playback, full media SHA and source popovers are outside this script.",
        "httpsVerificationDisabled": False,
        "checks": checks, "visits": visits, "screenshots": screenshots,
        "browserErrors": errors,
    }

    def check(name, passed, details=None):
        checks.append({"name": name, "passed": bool(passed), "details": details})
        if not passed:
            raise AssertionError(f"{name}: {details}")

    def go(page, suffix, width):
        response = page.goto(base + suffix, wait_until="domcontentloaded", timeout=60000)
        status = response.status if response else None
        visits.append({"width": width, "url": page.url, "status": status})
        check(f"{width}: GET {suffix}", status == 200, status)
        page.locator(".footer-bottom").wait_for()
        footer = page.locator(".footer-bottom").inner_text()
        check(f"{width}: version {suffix}", f"v{version}" in footer, footer)
        page.evaluate("document.fonts.ready")

    def shot(page, name, locator=None):
        path = out / f"{name}.png"
        if locator is None:
            # A full-page image should show the fixed header at the page start,
            # even after scrolling through lazy thumbnails to decode them.
            page.evaluate("window.scrollTo(0, 0)")
            page.evaluate("new Promise(requestAnimationFrame)")
            page.screenshot(path=str(path), full_page=True)
        else:
            locator.screenshot(path=str(path))
        screenshots.append(path.name)

    def hrefs(locator):
        return locator.evaluate_all("els => els.map(el => el.getAttribute('href'))")

    def fits(page, label):
        size = page.evaluate("({content:document.documentElement.scrollWidth,viewport:innerWidth})")
        check(label, size["content"] <= size["viewport"], size)

    def images(page, locator, count, label):
        for image in locator.all():
            image.scroll_into_view_if_needed()
            image.evaluate("el => el.loading = 'eager'")
            image.wait_for(state="visible")
            image.evaluate("el => el.decode()")
        rows = locator.evaluate_all("els => els.map(el => ({src:el.getAttribute('src'),complete:el.complete,width:el.naturalWidth,height:el.naturalHeight}))")
        check(label, len(rows) == count and all(r["complete"] and r["width"] > 0 and r["height"] > 0 for r in rows), rows)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox"])
            if args.transport_helper:
                helper = args.transport_helper.resolve()
                spec = importlib.util.spec_from_file_location("database_verified_transport", helper)
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                origin = "{0.scheme}://{0.netloc}".format(urlsplit(base))
                transport = module.install_browser_transport(browser, origin=origin)
                report["transportHelper"] = {"path": str(helper), "sha256": hashlib.sha256(helper.read_bytes()).hexdigest()}
            else:
                report["transport"] = {"mode": "Direct Chromium networking with HTTPS validation enabled."}

            for width, height in [(1440, 1000), (390, 844)]:
                page = browser.new_page(viewport={"width": width, "height": height}, reduced_motion="reduce", ignore_https_errors=False, service_workers="block")
                page.on("pageerror", lambda error: errors.append(str(error)))

                go(page, "", width)
                db_link = page.locator(".track-links a.track-database")
                check(f"{width}: home exposes an independent database direction", db_link.count() == 1 and db_link.get_attribute("href") == TRACK)
                copy = db_link.locator("p").text_content()
                check(f"{width}: database has its own home description", any(word in copy for word in ["索引", "事务", "存储", "查询", "复制"]) and "解法与代码" not in copy, copy)
                check(f"{width}: home database count is 4", db_link.locator(".track-count").inner_text() == "4 篇")
                check(f"{width}: home has 8 directions and 48 total lessons", page.locator(".track-link").count() == EXPECTED["directions"] and "48" in page.locator(".hero-note").inner_text())
                check(f"{width}: home database starts at original index URL", page.locator(f".start-grid a[href='{ep(DB[0])}']").count() == 1)
                check(f"{width}: systems home descriptor no longer lists database", "数据库" not in page.locator(".track-systems .track-main p").text_content())
                fits(page, f"{width}: home fits viewport")
                shot(page, f"home-database-{width}", db_link)

                go(page, "learn/", width)
                systems = page.locator("section.learning-track#systems")
                database = page.locator("section.learning-track#database")
                mq = page.locator("section.learning-track#message-queue")
                check(f"{width}: database is a sibling learning direction", database.count() == 1 and systems.locator("#database").count() == 0 and database.evaluate("el => el.parentElement.classList.contains('learning-tracks')"))
                check(f"{width}: database direction has 4 lessons and 1 series", "已发布 4 篇 · 1 个系列" in database.inner_text())
                check(f"{width}: database learning order uses four existing URLs", hrefs(database.locator(".chapter-lessons a")) == [ep(slug) for slug in DB])
                check(f"{width}: database direction exposes its series and index start", database.locator(f"a.chapter-heading[href='{SERIES}']").count() == 1 and database.locator(f"a.btn[href='{ep(DB[0])}']").count() == 1)
                check(f"{width}: systems contains 20 lessons and 4 series", "已发布 20 篇 · 4 个系列" in systems.inner_text())
                check(f"{width}: systems retains only its 4 chapter series", hrefs(systems.locator(".chapter-heading")) == [f"/video-studio/series/{item}/" for item in ["request", "cache", "peak", "distributed"]])
                check(f"{width}: systems excludes the database course URLs", not set(hrefs(systems.locator(".chapter-lessons a"))).intersection(ep(slug) for slug in DB))
                all_hrefs = hrefs(page.locator(".chapter-lessons a"))
                check(f"{width}: 48 unique lessons each have one learning home", len(all_hrefs) == EXPECTED["all"] and len(set(all_hrefs)) == EXPECTED["all"], len(all_hrefs))
                check(f"{width}: MQ remains independent with 1 lesson", "已发布 1 篇 · 1 个系列" in mq.inner_text() and hrefs(mq.locator(".chapter-lessons a")) == [MQ_EP])
                check(f"{width}: algorithm and puzzle direction counts remain 11 and 5", "已发布 11 篇" in page.locator("#algorithms .published").inner_text() and "已发布 5 篇" in page.locator("#puzzles .published").inner_text())
                fits(page, f"{width}: learning page fits viewport")
                shot(page, f"learn-database-{width}", database)
                shot(page, f"learn-systems-{width}", systems)

                go(page, "series/database/", width)
                breadcrumb = page.locator(".bc").inner_text()
                check(f"{width}: database series keeps the 4 original lessons", hrefs(page.locator(".lesson-list a.lesson")) == [ep(slug) for slug in DB])
                check(f"{width}: database breadcrumb is independent and deduplicated", "系统原理" not in breadcrumb and breadcrumb.count("数据库") == 1, breadcrumb)
                check(f"{width}: database series advertises only 4 published lessons", "已发布 4 篇" in page.locator(".course-count").inner_text())
                if width >= 768:
                    images(page, page.locator(".lesson-cover img"), 4, f"{width}: all database directory covers decode")
                fits(page, f"{width}: database series fits viewport")
                shot(page, f"series-database-{width}")

                for index, slug in enumerate(DB):
                    go(page, f"episodes/{slug}/", width)
                    breadcrumb = page.locator(".bc").inner_text()
                    check(f"{width}: {slug} keeps its EP and independent breadcrumb", f"EP.{15 + index}" in breadcrumb and "数据库" in breadcrumb and "系统原理" not in breadcrumb, breadcrumb)
                    page.locator("[data-open-course]").click()
                    directory = page.locator("#course-directory")
                    check(f"{width}: {slug} opens only the four database courses", directory.get_attribute("open") is not None and "数据库" in directory.locator("summary").inner_text() and hrefs(directory.locator("ol a")) == [ep(item) for item in DB])
                    prev = page.locator("nav.pager a.p:not(.r)")
                    nxt = page.locator("nav.pager a.r")
                    actual_prev = prev.get_attribute("href") if prev.count() else None
                    actual_next = nxt.get_attribute("href") if nxt.count() else None
                    expected_prev = ep(DB[index - 1]) if index else None
                    expected_next = ep(DB[index + 1]) if index + 1 < len(DB) else None
                    check(f"{width}: {slug} has database-only previous and next", (actual_prev, actual_next) == (expected_prev, expected_next), {"prev": actual_prev, "next": actual_next})
                    check(f"{width}: {slug} media URLs match published metadata", page.locator("video source").get_attribute("src") == ep(slug) + db_meta[slug]["video"] and page.locator("video").get_attribute("poster") == ep(slug) + db_meta[slug]["poster"])
                    if slug == "db-replication":
                        check(f"{width}: replication article removes its former cross-direction next-course teaser", "下一期继续：订单太多，一个数据库装不下怎么办？" not in page.locator(".article-body").inner_text())
                    if index in [0, 3]:
                        shot(page, f"{slug}-directory-{width}", directory)

                go(page, "episodes/degradation/", width)
                check(f"{width}: system degradation advances directly to db-sharding", page.locator("nav.pager a.r").get_attribute("href") == ep("db-sharding"))
                go(page, "episodes/db-sharding/", width)
                check(f"{width}: system db-sharding goes back to degradation", page.locator("nav.pager a.p:not(.r)").get_attribute("href") == ep("degradation"))

                go(page, "library/?track=database", width)
                page.locator(".catalog-controls:not([hidden])").wait_for()
                visible = page.locator("#library-grid>ul>li:not([hidden]) a.card")
                check(f"{width}: direct database track filter contains exactly the original 4", page.locator("select[name='track']").input_value() == "database" and set(hrefs(visible)) == {ep(slug) for slug in DB} and visible.count() == 4)
                go(page, "library/?series=database", width)
                page.locator(".catalog-controls:not([hidden])").wait_for()
                check(f"{width}: database series URL selects its own direction", page.locator("select[name='track']").input_value() == "database" and page.locator("select[name='series']").input_value() == "database")
                cards = visible.evaluate_all("els => els.map(el => ({href:el.getAttribute('href'),series:el.dataset.series,track:el.dataset.track,label:el.querySelector('.series').textContent}))")
                check(f"{width}: database library cards all belong only to database", len(cards) == 4 and {card["href"] for card in cards} == {ep(slug) for slug in DB} and all(card["series"] == "database" and card["track"] == "database" and card["label"] == "数据库" for card in cards), cards)
                images(page, visible.locator(".cover img"), 4, f"{width}: all database library covers decode")
                fits(page, f"{width}: database library fits viewport")
                shot(page, f"library-database-{width}")
                page.select_option("select[name='track']", "systems")
                state = page.locator("select[name='series']").evaluate("el => ({value:el.value,dbDisabled:el.querySelector('option[value=\"database\"]').disabled})")
                check(f"{width}: systems clears incompatible database filter", state["value"] == "" and state["dbDisabled"], state)
                system_hrefs = hrefs(visible)
                check(f"{width}: systems filter has 20 and excludes database and MQ", len(system_hrefs) == 20 and not set(system_hrefs).intersection([ep(slug) for slug in DB] + [MQ_EP]))
                check(f"{width}: systems still includes db-sharding", ep("db-sharding") in system_hrefs)
                page.locator("button.reset").click()
                all_cards = hrefs(visible)
                check(f"{width}: reset restores 48 unique library cards", len(all_cards) == 48 and len(set(all_cards)) == 48)
                page.select_option("select[name='track']", "message-queue")
                check(f"{width}: MQ library remains independent with 1 original card", hrefs(visible) == [MQ_EP])
                page.select_option("select[name='track']", "algorithms")
                check(f"{width}: algorithm library remains at 11", visible.count() == 11)
                images(page, visible.locator(".cover img"), 11, f"{width}: all 11 algorithm library covers decode")
                shot(page, f"library-leetcode-{width}", visible.first)
                page.select_option("select[name='track']", "puzzles")
                check(f"{width}: puzzle library remains at 5", visible.count() == 5)
                images(page, visible.locator(".cover img"), 5, f"{width}: all 5 puzzle library covers decode")
                shot(page, f"library-puzzles-{width}", visible.first)

                go(page, "series/message-queue/", width)
                check(f"{width}: MQ series remains independent with 1 original EP", hrefs(page.locator(".lesson-list a.lesson")) == [MQ_EP] and "系统原理" not in page.locator(".bc").inner_text())
                go(page, "episodes/message-queue/", width)
                check(f"{width}: MQ has no database or system previous/next course", page.locator("nav.pager").count() == 0 and hrefs(page.locator("#course-directory ol a")) == [MQ_EP])
                go(page, "series/leetcode/", width)
                check(f"{width}: LeetCode series keeps 11 original lessons", page.locator(".lesson-list a.lesson").count() == 11)
                go(page, "series/puzzles/", width)
                check(f"{width}: puzzle series keeps 5 original lessons", page.locator(".lesson-list a.lesson").count() == 5)
                page.close()
            check("browser has no uncaught page errors", not errors, errors)
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
