#!/usr/bin/env python3
"""Check final batch-3 build: --base-url http://127.0.0.1:4321/video-studio/.

Three desktop tail plays at actual 1x, painted reference boundaries and native
mobile fullscreen pages. Saved screenshots require separate view_image review
before either report can be marked passed. No earlier batch is fetched.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

from _qa import OUT, ROOT, UI, ONLINE, expectation, read, targets


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run_case(browser, base_url, expected, local, name, viewport, directory):
    slug, fps = expected["meta"]["slug"], expected["fps"]
    ep = ROOT / "episodes" / slug
    meta, refs = expected["meta"], expected["references"]
    receipt = read(ep / meta["referenceAppendix"]["manifest"])
    pages = UI.reference_pages(receipt, fps)
    body_end, final = expected["bodyFrames"] / fps, meta["finalVideoFrames"] / fps
    case = {"slug": slug, "name": name, "viewport": viewport, "referencePages": pages,
            "localChecks": local, "checks": [], "screenshots": [], "errors": []}

    def check(label, passed, observed=None):
        case["checks"].append({"name": label, "passed": bool(passed), "observed": observed})

    def screenshot(page, label):
        path = directory / f"{slug}-{name}-{label}.png"
        page.screenshot(path=str(path))
        relative = str(path.relative_to(ROOT))
        case["screenshots"].append(relative)
        return relative

    context = browser.new_context(viewport=viewport, device_scale_factor=1, color_scheme="dark", reduced_motion="reduce")
    page = context.new_page()
    page.set_default_timeout(10000)
    page.on("pageerror", lambda error: case["errors"].append(str(error)))
    page.on("console", lambda msg: case["errors"].append(msg.text) if msg.type == "error" else None)
    try:
        response = page.goto(base_url.rstrip("/") + f"/episodes/{slug}/", wait_until="networkidle")
        check("exact final built HTML served", response.status == 200 and sha(response.body()) ==
              ONLINE.sha_file(ONLINE.DIST / "episodes" / slug / "index.html"))
        page.wait_for_function("() => {const v=document.querySelector('#player video');return v&&v.readyState>=1&&Number.isFinite(v.duration)}")
        video = page.locator("#player video")
        state = video.evaluate("v=>({duration:v.duration,controls:v.controls,inline:v.playsInline,src:v.currentSrc,error:v.error?.message??null})")
        case["metadata"] = state
        check("native controls and complete video duration", state["controls"] and state["inline"] and not state["error"] and abs(state["duration"]-final) < .02, state)
        if name == "desktop":
            served = context.request.get(state["src"])
            body = served.body()
            case["servedVideo"] = {"status": served.status, "bytes": len(body), "sha256": sha(body), "fullResponseRead": True}
            check("complete MP4 GET matches final approved SHA", served.status == 200 and sha(body) == receipt["outputSHA256"] == local["finalVideoSHA256"], case["servedVideo"])
            served.dispose()
        actual_chapters = page.locator("#player").evaluate("e=>JSON.parse(e.dataset.chapters)")
        check("original chapter identities and starts retained", actual_chapters == expected["chapters"], actual_chapters)
        dates = page.locator("header.eh time").evaluate_all("els=>els.map(e=>({date:e.dateTime,label:e.getAttribute('aria-label')}))")
        check("creation and current version rendered", any(d["date"] == meta["createdAt"] for d in dates)
              and any(d["date"] == meta["updatedAt"] and d["label"] == "当前版本" for d in dates), dates)
        ld = page.locator('script[type="application/ld+json"]').evaluate_all("els=>els.map(e=>JSON.parse(e.textContent))")
        video_ld = next(item for item in ld if item.get("@type") == "VideoObject")
        check("first publication and first creation retained", video_ld.get("uploadDate") == ONLINE.date_iso(meta["publishedAt"])
              and video_ld.get("dateCreated") == ONLINE.date_iso(meta["createdAt"]), video_ld)
        video.evaluate("v=>{if(!v.textTracks.length)throw Error('No captions');v.textTracks[0].mode='showing'}")
        page.wait_for_function("()=>{const t=document.querySelector('#player video').textTracks[0];return t&&t.cues&&t.cues.length}")
        actual_cues = video.evaluate("v=>[...v.textTracks[0].cues].map(c=>c.text)")
        sb = read(ep / "storyboard.json")
        frozen_text = [sub["text"] for sc in sb["scenes"] for shot in sc["shots"] for sub in shot.get("subtitles", [])]
        check("actual native caption text complete", actual_cues == frozen_text, {"count": len(actual_cues)})
        case["appendixPauses"] = []
        page.locator("#player").scroll_into_view_if_needed()
        for card in pages:
            for label, time in (("exact-first-frame", card["from"]), ("first-plus-0.1ms", card["from"]+.0001),
                                ("middle", (card["from"]+card["end"])/2), ("last-frame", card["end"]-1/fps)):
                painted = page.evaluate(UI.SEEK, time)
                case["appendixPauses"].append({"page": card["number"], "name": label, **painted})
                check(f"page {card['number']} {label} painted without native subtitle", painted["paused"] and not painted["activeCues"]
                      and abs(painted["paintedTime"]-time) <= 1/fps+.001, painted)
        if name == "desktop":
            playback = page.evaluate(UI.PLAY_TO_END, {"from": body_end-.2, "bodyEnd": body_end, "pages": pages, "duration": final})
            case["continuousPlayback"] = playback
            check("actual 1x tail play reaches ended after original AAC endpoint", playback["ended"] and playback["seenInsideAppendix"]
                  and all(p["observed"] for p in playback["seenEachPage"]) and abs(playback["currentTime"]-final)<.02
                  and playback["elapsedSeconds"]>final-body_end-1, playback)
            for card in pages:
                page.evaluate(UI.SEEK, (card["from"]+card["end"])/2)
                screenshot(page, f"reference-page-{card['number']}")
        else:
            page.evaluate("""()=>{const b=document.createElement('button');b.id='qa-fullscreen';b.textContent='Fullscreen QA';
              b.onclick=()=>document.querySelector('#player video').requestFullscreen();document.body.append(b)}""")
            page.locator("#qa-fullscreen").click()
            page.wait_for_function("()=>document.fullscreenElement===document.querySelector('#player video')")
            page.set_viewport_size({"width": 844, "height": 390})
            case["fullscreenPages"] = []
            for card in pages:
                painted = page.evaluate(UI.SEEK, (card["from"]+card["end"])/2+1/fps)
                fullscreen = video.evaluate("v=>({fullscreen:document.fullscreenElement===v,paused:v.paused,time:v.currentTime})")
                check(f"native mobile fullscreen page {card['number']}", fullscreen["fullscreen"] and fullscreen["paused"] and not painted["activeCues"], fullscreen)
                case["fullscreenPages"].append({"page": card["number"], **fullscreen,
                    "screenshot": screenshot(page, f"fullscreen-reference-page-{card['number']}")})
            page.evaluate("()=>document.exitFullscreen()")
            page.wait_for_function("()=>!document.fullscreenElement")
            page.set_viewport_size(viewport)
            page.locator("#qa-fullscreen").evaluate("e=>e.remove()")
        article = UI.normalized(page.locator("#article").inner_text())
        case["referenceLinks"] = []
        last_link = None
        for source in refs["sources"]:
            texts = [source["title"]]
            if "quotation" in source:
                texts += [source["quotation"]["text"], source["quotation"]["locator"]]
            check(source["id"] + " exact original title/excerpt/locator present in article", all(UI.normalized(t) in article for t in texts), texts)
            for kind, url in (("canonical", source["url"]), ("fixed", source["verification"]["sourceUrl"])):
                links = page.locator("#article a")
                indexes = links.evaluate_all("(els,url)=>els.flatMap((a,i)=>a.href===url?[i]:[])", url)
                check(source["id"]+" "+kind+" link exists", bool(indexes), url)
                if not indexes:
                    continue
                link = links.nth(indexes[-1]); last_link = link
                rects = link.evaluate("a=>[...a.getClientRects()].map(r=>({left:r.left,right:r.right}))")
                check(source["id"]+" "+kind+" link wraps", all(r["left"]>=-1 and r["right"]<=viewport["width"]+1 for r in rects), rects)
                record = {"sourceId": source["id"], "kind": kind, "url": url}
                if name == "desktop":
                    link.evaluate("a=>a.addEventListener('click',e=>{e.preventDefault();window.__qaHref=a.href},{once:true})")
                    link.click()
                    record["nativeClick"] = page.evaluate("window.__qaHref")
                    check(source["id"]+" "+kind+" native anchor activates", record["nativeClick"]==url)
                case["referenceLinks"].append(record)
        overflow = page.evaluate("({width:document.documentElement.clientWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})")
        check("no horizontal overflow", max(overflow["page"],overflow["body"])<=overflow["width"]+1, overflow)
        if name == "mobile" and last_link:
            last_link.scroll_into_view_if_needed()
            screenshot(page, "reference-article")
        check("no browser/media errors", not case["errors"], case["errors"])
    except Exception as error:
        check("case completed", False, repr(error))
        screenshot(page, "failure")
    finally:
        context.close()
    case["passed"] = all(c["passed"] for c in case["checks"])
    return case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    stamp = now.strftime("%Y%m%d-%H%M%S")
    directory = OUT / "browser-qa" / stamp
    directory.mkdir(parents=True, exist_ok=False)
    report = {"checkedAt": now.isoformat(), "baseUrl": args.base_url, "targets": targets(),
              "version": read(ROOT / "site/package.json")["version"],
              "commit": subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
              "cases": [], "visualReview": "Pending actual view_image inspection.", "passed": False,
              "limitations": ["Chromium viewport emulation, not physical mobile/iOS Safari.",
                "Only the three changed appendices play at 1x on desktop; no duplicate mobile plays or prior-batch media GETs.",
                "Playback is muted; no human audio/ASR claim. Complete body preservation uses the baseline-SHA-bound full media receipts.",
                "390px embedded video remains small; full reading is inspected in actual native fullscreen at 844×390 and article text.",
                "Citation clicks prevent navigation; source verification is a separate record."]}
    try:
        expected = [expectation(slug) for slug in targets()]
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="/usr/bin/chromium",headless=True,
                args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
            report["browserVersion"] = browser.version
            for name, viewport in UI.VIEWPORTS:
                for inputs, local in expected:
                    case = run_case(browser,args.base_url,inputs,local,name,viewport,directory)
                    report["cases"].append(case)
                    print(json.dumps({"slug":case["slug"],"viewport":name,"passed":case["passed"],
                        "failures":[c for c in case["checks"] if not c["passed"]]},ensure_ascii=False),flush=True)
            browser.close()
        report["automatedAssertionsPassed"] = all(c["passed"] for c in report["cases"])
        report["status"] = "automated-passed-visual-pending" if report["automatedAssertionsPassed"] else "failed"
    except Exception as error:
        report.update(status="failed",automatedAssertionsPassed=False,error=repr(error))
    for path in (OUT/"qa-browser.json",OUT/f"qa-browser-attempt-{stamp}.json"):
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    return 0 if report["automatedAssertionsPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
