"""Small batch adapter; the historical verification scripts stay unchanged."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, OUT.parent / "original-titles" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ONLINE = load("batch3_online_engine", "verify-online.py")
UI = load("batch3_browser_helpers", "check-browser.py")


def targets():
    selected = read(OUT / "startup.json")["selection"]
    ONLINE.require(len(selected) == 3 and set(selected) == {
        "load-balancing", "server-cache", "cache-consistency"}, "Unexpected batch-3 selection")
    return selected


def verify_page(body, expected):
    """Keep native h3 citation labels as well as the earlier [R1] style.

    Version strings remain bound in references/receipt and shown on cards;
    prose does not have to repeat that entire formatting string verbatim.
    Original title, quoted words and original locator must still be present.
    """
    v, meta = ONLINE, expected["meta"]
    page = v.Page(body)
    slug = meta["slug"]
    v.require(page.title == meta["title"] and page.chapters == expected["chapters"], f"{slug}: title/chapters differ")
    for chapter in expected["articleChapters"]:
        v.require(chapter["id"] in page.ids and chapter["id"] in page.seeks, f"{slug}: original chapter anchor/seek missing")
    heading = expected["referenceHeading"]
    v.require(any(h["title"] == heading["title"] and (heading["id"] is None or h["id"] == heading["id"])
                  for h in page.headings), f"{slug}: reference section heading missing")
    for source in expected["references"]["sources"]:
        bracketed = re.search(r"\[\s*" + re.escape(source["id"]) + r"\s*\]", page.text)
        native_heading = any(v.visible_text(h["title"]) == v.visible_text(source["id"] + " · " + source["title"])
                             for h in page.headings)
        v.require(bracketed or native_heading, f"{slug}: citation identity missing: {source['id']}")
        original = [source["organization"], source["title"]]
        if "quotation" in source:
            original.extend((source["quotation"]["text"], source["quotation"]["locator"]))
        for text in original:
            v.require(v.visible_text(text) in v.visible_text(page.text), f"{slug}: original reference text/locator missing: {text}")
        for url in (source["url"], source["verification"]["sourceUrl"]):
            v.require(url in page.links, f"{slug}: reference link missing: {url}")
    ld = next((item for item in page.json_ld if item.get("@type") == "VideoObject"), None)
    v.require(ld, f"{slug}: VideoObject missing")
    url = v.BASE + f"episodes/{slug}/"
    duration = meta["finalVideoFrames"] / expected["fps"]
    values = {"name": meta["title"], "uploadDate": v.date_iso(meta["publishedAt"]),
              "dateCreated": v.date_iso(meta["createdAt"]), "dateModified": v.date_iso(meta["updatedAt"]),
              "contentUrl": url + meta["video"], "embedUrl": url,
              "duration": f"PT{int(duration // 60)}M{int(duration % 60)}S"}
    v.require(all(ld.get(k) == value for k, value in values.items()), f"{slug}: VideoObject identity/date/media differs")
    v.require(url + meta["poster"] in ld.get("thumbnailUrl", []), f"{slug}: poster identity differs")
    v.require(any(t.get("aria-label") == "当前版本" and t.get("datetime") == meta["updatedAt"] for t in page.times)
              and any(t.get("datetime") == meta["createdAt"] for t in page.times), f"{slug}: rendered dates missing")
    source_url = f"https://github.com/{v.REPO}/tree/main/{meta['sourcePath']}"
    v.require(source_url in page.links, f"{slug}: production source link missing")
    return {"title": page.title, "chapters": page.chapters, "uploadDate": ld["uploadDate"],
            "dateModified": ld["dateModified"], "referenceIds": [s["id"] for s in expected["references"]["sources"]],
            "originalReferenceTitles": [s["title"] for s in expected["references"]["sources"]],
            "exactQuotationsAndLocatorsVerified": True, "referenceLinksVerified": True, "sourceUrl": source_url}


def expectation(slug, release_commit=None):
    """Validate this first appendix against its original published body SHA.

    Unlike the previous migration, these videos have no older appendix media
    receipt. The new full media comparison is bound to the baseline body hash;
    we do not invent an earlier decoded-frame or audio fingerprint record.
    """
    v = ONLINE
    v.require(slug in targets(), "Episode is outside this batch")
    ep, prod = ROOT / "episodes" / slug, ROOT / "episodes-codex" / slug
    revision = prod / "revisions/reference-endcards"
    meta, refs = read(ep / "meta.json"), read(ep / "references.json")
    baseline = read(revision / "baseline.json")
    old = baseline["metadata"]
    v.require(meta["slug"] == refs["episode"] == slug and meta.get("draft") is False,
              f"{slug}: invalid public identity")
    stable = ("slug", "ep", "title", "createdAt", "publishedAt", "firstRelease", "platforms", "sourcePath")
    v.require(all(meta.get(k) == old.get(k) for k in stable), f"{slug}: original identity/date/platforms changed")
    for override in ("chapters.txt", "remotion/src/timing.json"):
        v.require(not (ep / override).exists(), f"{slug}: unexpected timing override {override}")
    sb = read(ep / "storyboard.json")
    old_sb = json.loads(v.git_file(baseline["baseCommit"], f"episodes/{slug}/storyboard.json"))
    v.require(sb == old_sb, f"{slug}: original complete storyboard changed")
    article = (ep / "article.mdx").read_text()
    fm = v.frontmatter_chapters(article)
    old_fm = v.frontmatter_chapters(v.git_file(baseline["baseCommit"], f"episodes/{slug}/article.mdx").decode())
    v.require(fm == old_fm, f"{slug}: original article chapter titles/ids changed")
    chapters, body_frames, fps = v.expected_chapters(sb, old_fm)
    appendix = meta["referenceAppendix"]
    receipt, media = read(ep / appendix["manifest"]), read(ep / "reference-appendix-media-check.json")
    v.require(refs.get("presentation") == receipt.get("presentation") == v.PRESENTATION,
              f"{slug}: original-title presentation missing")
    v.require(receipt.get("sourceTitles") == [{"id": s["id"], "title": s["title"]} for s in refs["sources"]],
              f"{slug}: receipt original titles differ")
    v.require(receipt.get("quotations") == [{"id": s["id"], **s["quotation"]} for s in refs["sources"] if "quotation" in s],
              f"{slug}: receipt exact quotations differ")
    pages = receipt["appendix"]["pages"]
    added = len(pages) * fps * 5
    v.require(len(pages) == (len(refs["sources"]) + 1) // 2
              and receipt["appendix"]["framesPerPage"] == fps * 5
              and receipt["appendix"]["durationInFrames"] == appendix["durationInFrames"] == added,
              f"{slug}: five-second/two-source page layout differs")
    v.require(receipt["bodyFrames"] == baseline["bodyFrames"] == body_frames == appendix["from"]
              == receipt["appendix"]["from"] and receipt["finalVideoFrames"] == meta["finalVideoFrames"] == body_frames + added,
              f"{slug}: original-body/appendix/final frame boundary differs")
    body_sha = baseline["originalBodySHA256"]
    v.require(receipt["inputs"]["bodySHA256"] == media["bodySHA256"] == body_sha,
              f"{slug}: media proof is not bound to the original published body")
    for flag in ("passed", "bodyDecodedFramesAndTimestampsEqual", "audioPacketsAndTimingEqual", "outputVideoTimelineContinuous"):
        v.require(media.get(flag) is True, f"{slug}: complete media comparison failed: {flag}")
    for key in ("bodyFrameMD5RowsSHA256", "audioPacketPayloadAndTimingSHA256", "decodedAudioPCM"):
        v.require(isinstance(media.get(key), str) and bool(media[key]), f"{slug}: missing media fingerprint {key}")
    actual_sha = v.sha_file(ep / meta["video"])
    v.require(actual_sha == receipt["outputSHA256"] == media["outputSHA256"], f"{slug}: final media SHA differs")
    v.require(receipt["inputs"]["referencesSHA256"] == v.sha_file(ep / "references.json"), f"{slug}: references SHA differs")
    for filename in (meta["video"], meta["poster"]):
        v.require(v.sha_file(v.DIST / "episodes" / slug / filename) == v.sha_file(ep / filename),
                  f"{slug}: built {filename} differs")
    if release_commit:
        for filename in ("meta.json", "references.json", "article.mdx", "storyboard.json", appendix["manifest"],
                         "reference-appendix-media-check.json", meta["video"], meta["poster"]):
            rel = str((ep / filename).relative_to(ROOT))
            blob = v.command(["git", "hash-object", "--", rel]).decode().strip()
            v.require(blob == v.command(["git", "rev-parse", f"{release_commit}:{rel}"]).decode().strip(),
                      f"{rel}: differs from explicit release commit")
        rel = str((revision / "baseline.json").relative_to(ROOT))
        v.require((ROOT / rel).read_bytes() == v.git_file(release_commit, rel), f"{slug}: release baseline differs")
    expected = {"meta": meta, "references": refs, "chapters": chapters, "articleChapters": fm,
                "fps": fps, "bodyFrames": body_frames, "referenceHeading": v.article_reference_heading(article)}
    v.verify_page((v.DIST / "episodes" / slug / "index.html").read_bytes(), expected)
    cues = v.verify_vtt(v.caption_path(slug).read_bytes(), sb, expected)
    return expected, {"episode": slug, "status": "passed", "filesMatchCommit": release_commit is not None,
                      "referenceSourceCount": len(refs["sources"]), "referencePageCount": len(pages), "secondsPerPage": 5,
                      "baseCommit": baseline["baseCommit"], "firstRelease": meta["firstRelease"],
                      "baselineBodySHA256": body_sha, "originalBodySHAAndFullMediaComparisonVerified": True,
                      "originalTitleAndPublicationPreserved": True, "oldChaptersPreserved": True,
                      "finalVideoSHA256": actual_sha, **cues}


ONLINE.ROOT = ROOT
ONLINE.DIST = ROOT / "site/dist"
ONLINE.REPORT = OUT / "online-verification.json"
ONLINE.published_targets = targets
ONLINE.local_expectation = expectation
ONLINE.verify_page = verify_page
