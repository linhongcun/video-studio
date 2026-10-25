"""Exercise the actual built reference appendices in desktop and mobile Chromium.

Run after a site build and local preview, with production inputs stopped:
  python3 docs/reference-endcards/batch-1/check-browser.py \
    --base-url http://127.0.0.1:4321/video-studio/

External citations are activated with native clicks while preventing navigation;
source-content verification is recorded separately in source-verification.json.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright
import yaml


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SLUGS = ("dns", "https", "browser-cache")
VIEWPORTS = (("desktop", {"width": 1440, "height": 1000}),
             ("mobile", {"width": 390, "height": 844}))


def read(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def chapters(storyboard, frontmatter):
    result, offset = [], 0
    titles = {c["id"]: c["title"] for c in frontmatter.get("chapters", [])}
    for scene in storyboard["scenes"]:
        if not result or (scene.get("chapterId") != result[-1]["id"]
                          and scene.get("title") != result[-1]["title"]):
            result.append({"id": scene.get("chapterId", scene["id"]),
                           "title": titles.get(scene.get("chapterId"), scene["title"]),
                           "start": offset / storyboard["meta"]["fps"]})
        offset += sum(shot["durationInFrames"] for shot in scene["shots"])
    return result


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

PLAY_TO_END = """async ({from, bodyEnd}) => {
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
    const timer = setTimeout(() => reject(new Error('Playback did not reach ended')), 15000);
    v.addEventListener('ended', () => { clearTimeout(timer); resolve(); }, {once:true});
    v.addEventListener('error', () => { clearTimeout(timer); reject(new Error('Media playback error')); }, {once:true});
  });
  await v.play();
  await ended;
  v.removeEventListener('timeupdate', update);
  return {from, bodyEnd, currentTime:v.currentTime, duration:v.duration, ended:v.ended,
    elapsedSeconds:(performance.now()-began)/1000, playbackRate:v.playbackRate,
    muted:v.muted, seenInsideAppendix:samples.some(s => s.time > bodyEnd + 0.5), samples,
    mediaError:v.error ? {code:v.error.code,message:v.error.message} : null};
}"""


def run_case(browser, base_url, slug, viewport_name, viewport, run_dir):
    ep = ROOT / "episodes" / slug
    prod = ROOT / "episodes-codex" / slug
    meta = read(ep / "meta.json")
    baseline = read(prod / "revisions/reference-endcards/baseline.json")
    manifest = read(prod / "revisions/reference-endcards/reference-appendix.json")
    refs = read(prod / "references.json")
    storyboard = read(ep / "storyboard.json")
    fps = storyboard["meta"]["fps"]
    body_end = manifest["bodyFrames"] / fps
    final_time = meta["finalVideoFrames"] / fps
    case = {"slug": slug, "viewport": viewport, "name": viewport_name,
            "expectedDuration": final_time, "bodyEnd": body_end, "checks": [],
            "screenshots": [], "pageErrors": [], "consoleErrors": []}

    def check(name, ok, observed=None, expected=None):
        case["checks"].append({"name": name, "passed": bool(ok),
                               "observed": observed, "expected": expected})

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
        prior_meta = baseline["publishedMetadata"]
        stable_fields = ("slug", "ep", "title", "createdAt", "publishedAt", "firstRelease", "sourcePath", "platforms")
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
        for name, target in (("exact-first-frame", body_end), ("first-frame-plus-0.1ms", body_end+.0001),
                             ("middle", (body_end+final_time)/2), ("last-frame", (meta["finalVideoFrames"]-1)/fps)):
            paused = page.evaluate(SEEK, target)
            paused["name"] = name
            case["appendixPauses"].append(paused)
            check("no native cue at " + name, paused["paused"] and not paused["activeCues"], paused)
        playback = page.evaluate(PLAY_TO_END, {"from": body_end-.2, "bodyEnd": body_end})
        case["continuousPlayback"] = playback
        check("actual playback crosses short AAC end and reaches video end", playback["ended"]
              and playback["seenInsideAppendix"] and abs(playback["currentTime"]-final_time) < .02
              and playback["elapsedSeconds"] > 4, playback)
        page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
        screenshot = run_dir / f"{slug}-{viewport_name}-reference-card.png"
        page.screenshot(path=str(screenshot))
        case["screenshots"].append(str(screenshot.relative_to(ROOT)))
        case["referenceCardScreenshotState"] = "After actual 1x playback reached ended; final reference frame remains displayed."
        case["referenceLinks"] = []
        for source in refs["sources"]:
            for kind, url in (("canonical", source["url"]), ("fixed-source", source["verification"]["sourceUrl"])):
                candidates = page.locator("#article a")
                matches = candidates.evaluate_all("(els,url)=>els.map((a,i)=>({index:i,href:a.href})).filter(a=>a.href===url)", url)
                check(source["id"] + " " + kind + " present", bool(matches), matches, url)
                if not matches:
                    continue
                link = candidates.nth(matches[-1]["index"])
                link.evaluate("a=>a.addEventListener('click',e=>{e.preventDefault();window.__citationClick={href:a.href,text:a.textContent};},{once:true})")
                link.click()
                active = page.evaluate("window.__citationClick")
                record = {"sourceId": source["id"], "kind": kind, "url": url, "nativeClick": active}
                case["referenceLinks"].append(record)
                check(source["id"] + " " + kind + " native anchor activates", active["href"] == url, record)
        overflow = page.evaluate("({viewport:document.documentElement.clientWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})")
        check("no horizontal page overflow", overflow["page"] <= overflow["viewport"]+1 and overflow["body"] <= overflow["viewport"]+1, overflow)
        screenshot = run_dir / f"{slug}-{viewport_name}-reference-links.png"
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
                  "Citation links were activated with native clicks and navigation prevented; this does not claim canonical external destinations were fetched.",
                  "Playback was muted; these checks do not claim human audio listening or ASR."]}
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
    report["qaCorrectionHistory"] = [
        {"attempt": "qa-browser-attempt-20261025-214728.json",
         "issue": "QA expected chapter titles from storyboard only; original published article frontmatter already supplied different titles.",
         "correction": "Expected titles now come from the immutable baseline published article; chapter starts still come from the same baseline storyboard. No product change was needed for this false failure."}]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True,
                     args=["--no-sandbox", "--autoplay-policy=no-user-gesture-required"])
        report["browserVersion"] = browser.version
        for name, viewport in VIEWPORTS:
            for slug in args.slugs:
                case = run_case(browser, args.base_url, slug, name, viewport, run_dir)
                report["cases"].append(case)
                print(json.dumps({"slug": slug, "viewport": name, "passed": case["passed"],
                      "failures": [c for c in case["checks"] if not c["passed"]]}, ensure_ascii=False), flush=True)
        browser.close()
    report["passed"] = all(case["passed"] for case in report["cases"])
    dump(out / f"qa-browser-attempt-{stamp}.json", report)
    dump(out / "qa-browser.json", report)
    print(json.dumps({"passed": report["passed"], "cases": len(report["cases"]), "report": str(out / "qa-browser.json")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
