"""Exercise the actual original-title appendices in desktop/mobile Chromium.

Run after a site build and local preview, with production inputs stopped:
  python3 docs/reference-endcards/original-titles/check-browser.py \
    --base-url http://127.0.0.1:4321/video-studio/

External citations are activated with native clicks while preventing navigation;
source-content verification is recorded separately in sources-core/extra.json.
Only desktop repeats actual 1x appendix playback. Mobile inspects every painted
page in native landscape fullscreen; saved images require a separate visual
review before qa-browser.json can be marked passed.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright
import yaml


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SLUGS = ("browser-cache", "cdn", "consistent-hashing", "cookie-session", "dns",
         "http-request", "https", "observer-pattern")
PRESENTATION = "original-title-quote"
VIEWPORTS = (("desktop", {"width": 1440, "height": 1000}),
             ("mobile", {"width": 390, "height": 844}))


def read(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def chapters(storyboard, frontmatter):
    """Match the site's chapter grouping, using original published titles."""
    groups, offset, previous = [], 0, None
    for scene in storyboard["scenes"]:
        merge = previous is not None and (
            (scene.get("chapterId") and scene.get("chapterId") == previous.get("chapterId"))
            or (scene.get("title") and scene.get("title") == previous.get("title")))
        if merge:
            groups[-1]["scenes"].append(scene)
        else:
            groups.append({"from": offset, "scenes": [scene]})
        offset += sum(shot["durationInFrames"] for shot in scene["shots"])
        previous = scene
    fm = frontmatter.get("chapters", [])
    mapping = {entry["id"]: entry for entry in fm}
    by_id = any(scene.get("chapterId") for scene in storyboard["scenes"])
    result = []
    for index, group in enumerate(groups):
        first = group["scenes"][0]
        match = next((mapping[s["chapterId"]] for s in group["scenes"]
                      if s.get("chapterId") in mapping), {}) if by_id else (fm[index] if index < len(fm) else {})
        result.append({"id": match.get("id", first.get("chapterId") or first["id"]),
                       "title": match.get("title", first["title"]),
                       "start": group["from"] / storyboard["meta"]["fps"]})
    return result


def reference_pages(manifest, fps):
    appendix = manifest["appendix"]
    count, per_page = len(appendix["pages"]), appendix["framesPerPage"]
    assert count > 0 and count * per_page == appendix["durationInFrames"]
    assert per_page == fps * 5, "Every reference page must last five seconds"
    return [{"number": index + 1, "fromFrame": appendix["from"] + index * per_page,
             "endFrame": appendix["from"] + (index + 1) * per_page,
             "from": (appendix["from"] + index * per_page) / fps,
             "end": (appendix["from"] + (index + 1) * per_page) / fps}
            for index in range(count)]


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


def critical_pages(slugs):
    """Keep the four densest original-title/excerpt pages as desktop evidence."""
    pages = []
    for slug in slugs:
        sources = read(ROOT / "episodes-codex" / slug / "references.json")["sources"]
        for index in range(0, len(sources), 2):
            pair = sources[index:index + 2]
            pages.append({"slug": slug, "page": index // 2 + 1,
                          "longestTitle": max(len(s["title"]) for s in pair),
                          "longestQuotation": max(len(s.get("quotation", {}).get("text", "")) for s in pair)})
    ranked = sorted(pages, key=lambda p: (p["longestTitle"] + p["longestQuotation"],
                                         p["longestTitle"], p["slug"]), reverse=True)
    return ranked[:4]


SEEK = """async (t) => {
  const v = document.querySelector('#player video');
  v.pause();
  const frame = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('No painted video frame after seek')), 5000);
    v.requestVideoFrameCallback((now, info) => { clearTimeout(timer); resolve(info.mediaTime); });
  });
  const seeked = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('Seek did not complete')), 5000);
    v.addEventListener('seeked', () => { clearTimeout(timer); resolve(); }, {once:true});
  });
  v.currentTime = t;
  await seeked;
  const paintedTime = await frame;
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  return {requestedTime:t, currentTime:v.currentTime, paintedTime,
    paused:v.paused, readyState:v.readyState, seeking:v.seeking,
    activeCues:[...v.textTracks].flatMap(tr => [...(tr.activeCues || [])].map(c => c.text))};
}"""

PLAY_TO_END = """async ({from, bodyEnd, pages, duration}) => {
  const v = document.querySelector('#player video');
  v.muted = true; v.playbackRate = 1;
  const samples = [];
  const update = () => samples.push({time:v.currentTime, paused:v.paused, ended:v.ended});
  v.addEventListener('timeupdate', update);
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('Playback-start seek timed out')), 5000);
    v.addEventListener('seeked', () => { clearTimeout(timer); resolve(); }, {once:true});
    v.currentTime = from;
  });
  const began = performance.now();
  const ended = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('Playback did not reach ended')),
      Math.ceil((duration-from+8)*1000));
    v.addEventListener('ended', () => { clearTimeout(timer); resolve(); }, {once:true});
    v.addEventListener('error', () => { clearTimeout(timer); reject(new Error('Media playback error')); }, {once:true});
  });
  await v.play();
  await ended;
  v.removeEventListener('timeupdate', update);
  return {from, bodyEnd, currentTime:v.currentTime, duration:v.duration, ended:v.ended,
    elapsedSeconds:(performance.now()-began)/1000, playbackRate:v.playbackRate,
    muted:v.muted, seenInsideAppendix:samples.some(s => s.time > bodyEnd + 0.5),
    seenEachPage:pages.map(p=>({number:p.number,
      observed:samples.some(s=>s.time>p.from+0.25&&s.time<p.end-0.25)})), samples,
    mediaError:v.error ? {code:v.error.code,message:v.error.message} : null};
}"""


def run_case(browser, base_url, slug, viewport_name, viewport, run_dir, critical):
    ep = ROOT / "episodes" / slug
    prod = ROOT / "episodes-codex" / slug
    meta = read(ep / "meta.json")
    baseline = read(prod / "revisions/original-titles/baseline.json")
    manifest = read(ep / meta["referenceAppendix"]["manifest"])
    media = read(ep / "reference-appendix-media-check.json")
    refs = read(ep / meta["referenceAppendix"]["sources"])
    storyboard = read(ep / "storyboard.json")
    fps = storyboard["meta"]["fps"]
    body_end = manifest["bodyFrames"] / fps
    final_time = meta["finalVideoFrames"] / fps
    pages = reference_pages(manifest, fps)
    case = {"slug": slug, "viewport": viewport, "name": viewport_name,
            "expectedDuration": final_time, "bodyEnd": body_end, "checks": [],
            "referencePages": pages, "screenshots": [], "pageErrors": [], "consoleErrors": []}

    def check(name, ok, observed=None, expected=None):
        case["checks"].append({"name": name, "passed": bool(ok),
                               "observed": observed, "expected": expected})

    source_titles = [{"id": s["id"], "title": s["title"]} for s in refs["sources"]]
    quotations = [{"id": s["id"], **s["quotation"]} for s in refs["sources"] if "quotation" in s]
    check("original-title presentation and exact source receipt", refs.get("presentation") == PRESENTATION
          and manifest.get("presentation") == PRESENTATION and manifest.get("sourceTitles") == source_titles
          and manifest.get("quotations") == quotations,
          {"presentation": manifest.get("presentation"), "sourceTitles": manifest.get("sourceTitles"),
           "quotations": manifest.get("quotations")})
    check("complete original body retained before new appendix", manifest["bodyFrames"] == baseline["bodyFrames"]
          and manifest["inputs"]["bodySHA256"] == baseline["originalBodySHA256"]
          and media.get("passed") is True
          and media.get("bodyDecodedFramesAndTimestampsEqual") is True
          and media.get("audioPacketsAndTimingEqual") is True
          and media.get("outputVideoTimelineContinuous") is True
          and media.get("bodySHA256") == baseline["originalBodySHA256"]
          and media.get("outputSHA256") == manifest["outputSHA256"],
          {"bodyFrames": manifest["bodyFrames"], "bodySHA256": manifest["inputs"]["bodySHA256"],
           "mediaProof": media}, {"bodyFrames": baseline["bodyFrames"], "bodySHA256": baseline["originalBodySHA256"]})
    check("appendix pages and metadata cover final frame", len(pages) == (len(refs["sources"])+1)//2
          and pages[-1]["endFrame"] == meta["finalVideoFrames"]
          and meta["referenceAppendix"]["from"] == manifest["bodyFrames"]
          and meta["referenceAppendix"]["durationInFrames"] == manifest["appendix"]["durationInFrames"],
          {"pages": pages, "metadata": meta["referenceAppendix"]})

    context = browser.new_context(viewport=viewport, device_scale_factor=1,
                                  reduced_motion="reduce", color_scheme="dark")
    page = context.new_page()
    page.set_default_timeout(10000)
    page.on("pageerror", lambda error: case["pageErrors"].append(str(error)))
    page.on("console", lambda msg: case["consoleErrors"].append(msg.text) if msg.type == "error" else None)
    try:
        response = page.goto(base_url.rstrip("/") + f"/episodes/{slug}/", wait_until="networkidle")
        served_sha = digest(response.body())
        local_sha = digest((ROOT / f"site/dist/episodes/{slug}/index.html").read_bytes())
        case.update(url=page.url, servedHTMLSha256=served_sha, builtHTMLSha256=local_sha)
        check("served exact built HTML", response.status == 200 and served_sha == local_sha,
              {"status": response.status, "sha256": served_sha}, local_sha)
        page.wait_for_function("() => {const v=document.querySelector('#player video'); return v && v.readyState>=1 && Number.isFinite(v.duration)}")
        state = page.locator("#player video").evaluate("v => ({duration:v.duration,controls:v.controls,playsInline:v.playsInline,src:v.currentSrc,error:v.error?.message??null})")
        case["metadata"] = state
        check("duration includes reference appendix", abs(state["duration"]-final_time) < 0.02, state["duration"], final_time)
        check("native video controls retained", state["controls"] and state["playsInline"], state)
        check("no media error", state["error"] is None, state["error"])
        actual_video = context.request.get(state["src"])
        served_video = actual_video.body()
        video_sha = digest(served_video)
        published_sha = digest((ep / meta["video"]).read_bytes())
        case["servedVideo"] = {"url": state["src"], "status": actual_video.status,
                               "bytes": len(served_video), "sha256": video_sha,
                               "expectedSHA256": published_sha, "fullResponseRead": True}
        check("complete served MP4 equals approved output", actual_video.status == 200
              and video_sha == published_sha == manifest["outputSHA256"], case["servedVideo"])
        actual_video.dispose()
        prior_meta = baseline["metadata"]
        stable_fields = ("slug", "ep", "title", "createdAt", "publishedAt", "firstRelease", "sourcePath", "platforms", "javaEndCard")
        check("stable identity and first publication", all(meta.get(k) == prior_meta.get(k) for k in stable_fields),
              {k: meta.get(k) for k in stable_fields}, {k: prior_meta.get(k) for k in stable_fields})
        date_state = page.locator("header.eh time").evaluate_all("els => els.map(e=>({datetime:e.dateTime,label:e.getAttribute('aria-label'),text:e.textContent}))")
        check("created and current dates rendered", any(d["datetime"] == meta["createdAt"] for d in date_state)
              and any(d["datetime"] == meta["updatedAt"] for d in date_state), date_state)
        ld = page.locator('script[type="application/ld+json"]').evaluate_all("els=>els.map(e=>JSON.parse(e.textContent))")
        case["structuredData"] = ld
        video_ld = next(item for item in ld if item.get("@type") == "VideoObject")
        original_upload = prior_meta["publishedAt"]
        original_created = prior_meta["createdAt"]
        if len(original_upload) == 10:
            original_upload += "T00:00:00+08:00"
        if len(original_created) == 10:
            original_created += "T00:00:00+08:00"
        check("structured first-publication and creation dates retained",
              video_ld.get("uploadDate") == original_upload and video_ld.get("dateCreated") == original_created,
              {"uploadDate": video_ld.get("uploadDate"), "dateCreated": video_ld.get("dateCreated")},
              {"uploadDate": original_upload, "dateCreated": original_created})
        prior_sb = json.loads(subprocess.check_output(["git", "show", baseline["baseCommit"] + f":episodes/{slug}/storyboard.json"], cwd=ROOT))
        prior_article = subprocess.check_output(["git", "show", baseline["baseCommit"] + f":episodes/{slug}/article.mdx"], cwd=ROOT, text=True)
        prior_frontmatter = yaml.safe_load(prior_article.split("---", 2)[1])
        assert not (ep / "chapters.txt").exists() and not (ep / "remotion/src/timing.json").exists(), "This batch has no timing override"
        check("original published storyboard unchanged", storyboard == prior_sb)
        expected_chapters = chapters(prior_sb, prior_frontmatter)
        actual_chapters = page.locator("#player").evaluate("e=>JSON.parse(e.dataset.chapters)")
        check("original chapter identities and starts retained", actual_chapters == expected_chapters, actual_chapters, expected_chapters)
        page.locator("#player video").evaluate("v=>{if(!v.textTracks.length)throw new Error('No captions track');v.textTracks[0].mode='showing'}")
        page.wait_for_function("() => {const t=document.querySelector('#player video').textTracks[0];return t&&t.cues&&t.cues.length>0}")
        cues = page.locator("#player video").evaluate("v=>[...v.textTracks[0].cues].map(c=>({text:c.text,start:c.startTime,end:c.endTime}))")
        expected_cues = [{"text": c["text"], "start": (sh["from"]+c["from"])/fps,
                          "end": (sh["from"]+c["to"]+1)/fps}
                         for sc in storyboard["scenes"] for sh in sc["shots"] for c in sh["subtitles"]]
        check("native caption text and body timing retained", len(cues) == len(expected_cues) and all(
            c["text"] == e["text"] and abs(c["start"]-e["start"]) <= .00101 and abs(c["end"]-e["end"]) <= .00101
            for c, e in zip(cues, expected_cues)), {"count": len(cues), "last": cues[-1]},
            {"count": len(expected_cues), "last": expected_cues[-1]})
        case["appendixPauses"] = []
        page.locator("#player").scroll_into_view_if_needed()
        for reference_page in pages:
            start, end = reference_page["from"], reference_page["end"]
            for name, target in (("exact-first-frame", start), ("first-frame-plus-0.1ms", start+.0001),
                                 ("middle", (start+end)/2), ("last-frame", end-1/fps)):
                paused = page.evaluate(SEEK, target)
                paused.update(name=name, page=reference_page["number"])
                case["appendixPauses"].append(paused)
                check(f"no native cue at page {reference_page['number']} " + name,
                      paused["paused"] and not paused["activeCues"], paused)
        if viewport_name == "desktop":
            playback = page.evaluate(PLAY_TO_END, {"from": body_end-.2, "bodyEnd": body_end,
                                                 "pages": pages, "duration": final_time})
            case["continuousPlayback"] = playback
            check("actual 1x playback crosses original AAC end and reaches video end", playback["ended"]
                  and playback["seenInsideAppendix"] and abs(playback["currentTime"]-final_time) < .02
                  and playback["elapsedSeconds"] > final_time-body_end-1
                  and all(p["observed"] for p in playback["seenEachPage"]), playback)
            for reference_page in pages:
                if (slug, reference_page["number"]) not in critical:
                    continue
                page.evaluate(SEEK, (reference_page["from"]+reference_page["end"])/2)
                screenshot = run_dir / f"{slug}-desktop-reference-page-{reference_page['number']}.png"
                page.screenshot(path=str(screenshot))
                case["screenshots"].append(str(screenshot.relative_to(ROOT)))
            if meta.get("javaEndCard"):
                card = meta["javaEndCard"]
                check("original Java card precedes reference pages", card["from"] + card["durationInFrames"] == manifest["bodyFrames"], card)
                painted = page.evaluate(SEEK, (card["from"] + card["durationInFrames"]/2)/fps)
                screenshot = run_dir / f"{slug}-desktop-preserved-java-card.png"
                page.screenshot(path=str(screenshot))
                case["preservedCodeCard"] = {"metadata": card, "painted": painted,
                                              "screenshot": str(screenshot.relative_to(ROOT))}
                case["screenshots"].append(str(screenshot.relative_to(ROOT)))
        case["referenceCardScreenshotState"] = "Painted paused video frame; native controls retained. Desktop 1x playback and mobile fullscreen are reported separately."
        if viewport_name == "mobile":
            case["fullscreenPages"] = []
            page.evaluate("""() => {
              const b=document.createElement('button'); b.id='qa-native-fullscreen';
              b.textContent='Open native fullscreen for QA';
              b.onclick=()=>document.querySelector('#player video').requestFullscreen();
              document.body.append(b);
            }""")
            page.locator("#qa-native-fullscreen").click()
            page.wait_for_function("() => document.fullscreenElement===document.querySelector('#player video')")
            page.set_viewport_size({"width": 844, "height": 390})
            for reference_page in pages:
                painted = page.evaluate(SEEK, (reference_page["from"]+reference_page["end"])/2 + 1/fps)
                fullscreen = page.locator("#player video").evaluate("""v=>({
                    fullscreen:document.fullscreenElement===v,currentTime:v.currentTime,
                    paused:v.paused,readyState:v.readyState,
                    rect:{width:v.getBoundingClientRect().width,height:v.getBoundingClientRect().height}})""")
                fullscreen.update(page=reference_page["number"], viewport={"width": 844, "height": 390})
                check(f"native landscape fullscreen page {reference_page['number']}",
                      fullscreen["fullscreen"] and fullscreen["paused"] and not painted["activeCues"], fullscreen)
                screenshot = run_dir / f"{slug}-mobile-fullscreen-reference-page-{reference_page['number']}.png"
                page.screenshot(path=str(screenshot))
                fullscreen["screenshot"] = str(screenshot.relative_to(ROOT))
                case["screenshots"].append(fullscreen["screenshot"])
                case["fullscreenPages"].append(fullscreen)
            page.evaluate("() => document.exitFullscreen()")
            page.wait_for_function("() => !document.fullscreenElement")
            page.set_viewport_size(viewport)
            page.locator("#qa-native-fullscreen").evaluate("button=>button.remove()")
        case["referenceLinks"] = []
        article_text = normalized(page.locator("#article").inner_text())
        case["articleOriginalText"] = []
        for source in refs["sources"]:
            quotation = source.get("quotation", {})
            expected_text = {"originalTitle": source["title"]}
            if quotation:
                expected_text.update(quotation=quotation["text"], locator=quotation["locator"])
            text_record = {"id": source["id"], **expected_text,
                           "allPresent": all(normalized(text) in article_text for text in expected_text.values())}
            case["articleOriginalText"].append(text_record)
            check(source["id"] + " original title, quotation and locator visible in article", text_record["allPresent"], text_record)
            links = [("canonical", source["url"])]
            if source["verification"].get("sourceUrl"):
                links.append(("fixed-source", source["verification"]["sourceUrl"]))
            for kind, url in links:
                candidates = page.locator("#article a")
                matches = candidates.evaluate_all("(els,url)=>els.map((a,i)=>({index:i,href:a.href})).filter(a=>a.href===url)", url)
                check(source["id"] + " " + kind + " present", bool(matches), matches, url)
                if not matches:
                    continue
                link = candidates.nth(matches[-1]["index"])
                rects = link.evaluate("a=>[...a.getClientRects()].map(r=>({left:r.left,right:r.right,width:r.width,height:r.height}))")
                check(source["id"] + " " + kind + " wraps within article width", bool(rects)
                      and all(r["left"] >= -1 and r["right"] <= viewport["width"]+1 for r in rects), rects)
                record = {"sourceId": source["id"], "kind": kind, "url": url, "rects": rects}
                if viewport_name == "desktop":
                    link.evaluate("a=>a.addEventListener('click',e=>{e.preventDefault();window.__citationClick={href:a.href,text:a.textContent};},{once:true})")
                    link.click()
                    active = page.evaluate("window.__citationClick")
                    record["nativeClick"] = active
                    check(source["id"] + " " + kind + " native anchor activates", active["href"] == url, record)
                case["referenceLinks"].append(record)
        overflow = page.evaluate("({viewport:document.documentElement.clientWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})")
        check("no horizontal page overflow", overflow["page"] <= overflow["viewport"]+1 and overflow["body"] <= overflow["viewport"]+1, overflow)
        if viewport_name == "mobile" and any(s == slug for s, _ in critical):
            page.locator("#article a").filter(has_text="固定原文").last.scroll_into_view_if_needed() if page.locator("#article a").filter(has_text="固定原文").count() else None
            screenshot = run_dir / f"{slug}-mobile-reference-article.png"
            page.screenshot(path=str(screenshot))
            case["screenshots"].append(str(screenshot.relative_to(ROOT)))
        check("no browser page errors", not case["pageErrors"], case["pageErrors"])
    except Exception as error:
        case["exception"] = repr(error)
        check("case completed", False, repr(error))
        try:
            screenshot = run_dir / f"{slug}-{viewport_name}-failure.png"
            page.screenshot(path=str(screenshot))
            case["screenshots"].append(str(screenshot.relative_to(ROOT)))
        except Exception:
            pass
    finally:
        context.close()
    case["passed"] = all(item["passed"] for item in case["checks"])
    return case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--slugs", nargs="+", choices=SLUGS, default=SLUGS)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    stamp = now.strftime("%Y%m%d-%H%M%S")
    out = args.output_dir.resolve()
    run_dir = out / "browser-qa" / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    report = {"checkedAt": now.isoformat(), "baseUrl": args.base_url,
              "version": read(ROOT / "site/package.json")["version"],
              "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "cases": [], "visualReview": "Pending separate view_image inspection of the saved screenshots.",
              "limitations": ["Local built-site Chromium checks; deployment identity is checked separately.",
                  "Mobile cases use Chromium viewport emulation, not a physical device or iOS Safari.",
                  "Citation links were activated with native clicks and navigation prevented; this does not claim canonical external destinations were fetched.",
                  "The eight actual 1x plays run once on desktop, crossing the new appendix and reaching ended; mobile uses painted seeks and fullscreen, not duplicate continuous plays.",
                  "Playback was muted; these checks do not claim human audio listening or ASR.",
                  "390px embedded video remains a small viewing area and native controls can cover its lower area; the complete reference card is inspected separately in actual native fullscreen at 844x390.",
                  "Original body/code-card retention uses the recorded complete decoded-frame and AAC/PCM comparisons; this UI run does not relabel them as newly repeated media comparisons."]}
    report["priorAttempts"] = []
    for previous_path in sorted(out.glob("qa-browser-attempt-*.json")):
        previous = read(previous_path)
        review = previous.get("visualReview")
        report["priorAttempts"].append({
            "file": str(previous_path.relative_to(ROOT)), "checkedAt": previous.get("checkedAt"),
            "passed": previous.get("passed"),
            "automatedAssertionsPassed": previous.get("automatedAssertionsPassed"),
            "failedCheckNames": sorted({check["name"] for case in previous.get("cases", [])
                                        for check in case.get("checks", []) if not check["passed"]}),
            "visualFindings": review.get("findings", []) if isinstance(review, dict) else []})
    report["reusedLessons"] = [
        "Expected chapter titles come from the immutable baseline published article; group order and starts come from its storyboard, not the production article.",
        "Every actual reference page is inspected with native controls; small embedded mobile playback and native fullscreen are distinct observations.",
        "Only the reference appendix changes; existing narration, dynamics and speech-listening checks are not repeated or relabeled."]
    ranked = critical_pages(args.slugs)
    report["criticalReferencePages"] = ranked
    critical = {(p["slug"], p["page"]) for p in ranked}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True,
                     args=["--no-sandbox", "--autoplay-policy=no-user-gesture-required"])
        report["browserVersion"] = browser.version
        for name, viewport in VIEWPORTS:
            for slug in args.slugs:
                try:
                    case = run_case(browser, args.base_url, slug, name, viewport, run_dir, critical)
                except Exception as error:
                    case = {"slug": slug, "name": name, "viewport": viewport, "passed": False,
                            "checks": [{"name": "load final publication inputs", "passed": False,
                                        "observed": repr(error)}]}
                report["cases"].append(case)
                print(json.dumps({"slug": slug, "viewport": name, "passed": case["passed"],
                      "failures": [c for c in case["checks"] if not c["passed"]]}, ensure_ascii=False), flush=True)
        browser.close()
    report["automatedAssertionsPassed"] = all(case["passed"] for case in report["cases"])
    report["passed"] = False
    report["status"] = "automated-passed-visual-pending" if report["automatedAssertionsPassed"] else "failed"
    dump(out / f"qa-browser-attempt-{stamp}.json", report)
    dump(out / "qa-browser.json", report)
    print(json.dumps({"automatedAssertionsPassed": report["automatedAssertionsPassed"],
                      "visualReview": "pending", "cases": len(report["cases"]),
                      "report": str(out / "qa-browser.json")}))
    return 0 if report["automatedAssertionsPassed"] else 1


if __name__ == "__main__":
    sys.exit(main())
