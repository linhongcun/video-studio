"""Isolated title/author migration QA; historical engines remain byte-for-byte.

Only this run's 17 startup declarations are checked. Publication sourcePath and
per-production title-author baselines select the actual body (including the
current nested single-position Bloom project); no old directory is guessed.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(OUT.parent))
from _batch_runtime import configure_batch

ALLOWED = ("bloom-filter", "browser-cache", "cache-consistency", "cdn", "circuit-breaker",
           "consistent-hashing", "cookie-session", "daily-temperatures", "dns", "egg-drop",
           "http-request", "https", "load-balancing", "message-queue", "observer-pattern",
           "rate-limit", "server-cache")
BASELINE_COMMIT = "07d4c4916821fd17dae113055480d7a7c495466c"
_BASE = configure_batch(OUT, ALLOWED)
ONLINE, UI, read = _BASE.ONLINE, _BASE.UI, _BASE.read
PRESENTATION = "title-author"
FINGERPRINTS = ("bodyFrameMD5RowsSHA256", "audioPacketCount", "audioPacketPayloadAndTimingSHA256",
                "decodedAudioPCM", "audioStreamEndsAtOriginalEndpointSeconds")


def declarations():
    data = read(OUT / "startup.json")
    rows = data["episodes"]
    ONLINE.require(data["baseCommit"] == BASELINE_COMMIT and len(rows) == 17
                   and {row["slug"] for row in rows} == set(ALLOWED), "Unexpected title-author migration scope")
    ONLINE.require(len({row["slug"] for row in rows}) == 17, "Duplicate migration declaration")
    return rows


def targets():
    return [row["slug"] for row in declarations()]


def resolve_credit(source):
    key = "author" if "author" in source else "organization"
    value = source.get(key)
    ONLINE.require(isinstance(value, str) and bool(value.strip()), f"{source.get('id')}: empty {key}")
    return value


def bibliography(refs):
    return [{"id": s["id"], "title": s["title"], "credit": resolve_credit(s)} for s in refs["sources"]]


def representatives():
    selected = ["cookie-session", "http-request", "https", "bloom-filter", "observer-pattern"]
    remaining = [slug for slug in targets() if slug not in selected]
    def longest(slug):
        return max(len(resolve_credit(s)) for s in read(ROOT / "episodes" / slug / "references.json")["sources"])
    # Current longest credit is shared by Observer and Server Cache. Keep six
    # distinct representative episodes and explicitly cover that long byline.
    selected.append(max(remaining, key=lambda slug: (longest(slug), slug)))
    ONLINE.require(len(selected) == 6 and len(set(selected)) == 6, "Expected six UI representatives")
    ONLINE.require(max(longest(slug) for slug in selected) == max(longest(slug) for slug in targets()),
                   "UI representatives do not cover the longest author/organization")
    return selected


_ORIGINAL_REFERENCE_HEADING = ONLINE.article_reference_heading


def article_reference_heading(article):
    try:
        return _ORIGINAL_REFERENCE_HEADING(article)
    except ONLINE.VerificationError:
        ONLINE.require(re.search(r"^###\s+资料依据\s*$", article, re.M),
                       "article reference heading missing")
        return {"title": "资料依据", "id": None}


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
    research_locations = []
    for source in expected["references"]["sources"]:
        bracketed = re.search(r"\[\s*" + re.escape(source["id"]) + r"\s*\]", page.text)
        native_heading = any(v.visible_text(h["title"]) == v.visible_text(source["id"] + " · " + source["title"])
                             for h in page.headings)
        alias = {"R1": "redis", "R2": "cassandra"}.get(source["id"]) if slug == "bloom-filter" else None
        original_footnote = alias is not None and "user-content-fn-" + alias in page.ids
        v.require(bracketed or native_heading or original_footnote,
                  f"{slug}: citation identity missing: {source['id']}")
        original = [source["organization"], source["title"]]
        if "quotation" in source:
            quote = source["quotation"]
            original.append(quote["text"])
            if v.visible_text(quote["locator"]) in v.visible_text(page.text):
                original.append(quote["locator"])
            else:
                # Current published single-position Bloom has original named
                # footnotes; its detailed line locators live in research data.
                v.require(slug == "bloom-filter" and original_footnote,
                          f"{slug}: original reference locator missing: {quote['locator']}")
                match = re.search(r"\blines?\s+(\d+)(?:[–-](\d+))?", quote["locator"])
                v.require(match, f"{slug}: missing preserved source-line locator")
                first, last = int(match[1]), int(match[2] or match[1])
                raw = (ROOT / quote["evidence"]).read_text().splitlines()
                v.require(1 <= first <= last <= len(raw)
                          and v.visible_text(quote["text"]) in v.visible_text("\n".join(raw[first-1:last])),
                          f"{slug}: quote differs from original source locator lines")
                research_locations.append({"sourceId": source["id"], "locator": quote["locator"],
                                           "evidence": quote["evidence"], "lineRange": [first, last],
                                           "quotationMatchesExactSourceLines": True})
        for text in original:
            v.require(v.visible_text(text) in v.visible_text(page.text), f"{slug}: original reference text/locator missing: {text}")
        urls = {source["url"], source["verification"]["sourceUrl"]}
        if source.get("canonicalUrl"):
            urls.add(source["canonicalUrl"])
        for url in urls:
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
            "exactQuotationsAndLocatorsVerified": True, "referenceLinksVerified": True,
            "researchLocatorChecks": research_locations, "cardPresentation": PRESENTATION,
            "bibliography": bibliography(expected["references"]), "sourceUrl": source_url}


def _commit_file(commit, path):
    rel = str(path.relative_to(ROOT))
    ONLINE.require(path.read_bytes() == ONLINE.git_file(commit, rel), f"{rel}: differs from explicit release commit")


def expectation(slug, release_commit=None):
    v = ONLINE
    v.require(slug in targets(), "Episode is outside the 17-video migration")
    row = next(item for item in declarations() if item["slug"] == slug)
    ep = ROOT / "episodes" / slug
    meta, refs = read(ep / "meta.json"), read(ep / "references.json")
    production = (ROOT / meta["sourcePath"]).resolve().parent
    v.require(production == (ROOT / row["productionDir"]).resolve(), f"{slug}: production entry differs")
    revision = production / "revisions/title-author"
    baseline = read(revision / "baseline.json")
    v.require(baseline["slug"] == slug and baseline["baseCommit"] == BASELINE_COMMIT,
              f"{slug}: wrong title-author baseline")
    original = baseline["metadata"]
    v.require(meta["slug"] == refs["episode"] == slug and meta.get("draft") is False, f"{slug}: public identity differs")
    mutable = {"updatedAt", "finalVideoFrames", "targetDuration", "referenceAppendix"}
    v.require(all(meta.get(k) == value for k, value in original.items() if k not in mutable),
              f"{slug}: original title/date/platform/body metadata changed")
    for override in ("chapters.txt", "remotion/src/timing.json"):
        v.require(not (ep / override).exists(), f"{slug}: unsupported timing override")
    sb = read(ep / "storyboard.json")
    old_sb = read(revision / "before-published-storyboard.json")
    v.require(sb == old_sb, f"{slug}: original complete storyboard changed")
    old_refs = read(revision / "before-published-references.json")
    original_sources = {source["id"]: source for source in old_refs["sources"]}
    v.require(set(original_sources) == {source["id"] for source in refs["sources"]},
              f"{slug}: original citation identities changed")
    for source in refs["sources"]:
        old_source = original_sources[source["id"]]
        v.require(all(source.get(key) == old_source.get(key) for key in ("title", "quotation", "titleEvidence", "url")),
                  f"{slug}: original research title/quotation/locator changed")
    article = (ep / "article.mdx").read_bytes()
    v.require(article == (revision / "before-published-article.mdx").read_bytes(),
              f"{slug}: original article/research quotations changed")
    fm = v.frontmatter_chapters(article.decode())
    chapters, scene_frames, fps = v.expected_chapters(sb, fm)
    # The declared actual encoded body is authoritative. Do not infer an older
    # multi-position Bloom body from an unrelated source project or revision.
    body_frames = baseline["bodyFrames"]
    v.require(isinstance(body_frames, int) and body_frames > 0 and fps > 0,
              f"{slug}: invalid actual body boundary")
    appendix = meta["referenceAppendix"]
    receipt, media = read(ep / appendix["manifest"]), read(ep / "reference-appendix-media-check.json")
    old_media = read(revision / "before-published-reference-appendix-media-check.json")
    v.require(old_media["outputSHA256"] == baseline["previousPublishedSHA256"], f"{slug}: old media proof identity differs")
    v.require(refs.get("presentation") == receipt.get("presentation") == PRESENTATION,
              f"{slug}: title-author presentation missing")
    entries = bibliography(refs)
    v.require(receipt.get("bibliography") == entries, f"{slug}: rendered title/credit bibliography differs")
    policy = {"kind": "title-author-single-column", "maxItemsPerPage": 4,
              "renderedFields": ["title", "credit"], "quotesRendered": False}
    v.require(all(receipt.get("layout", {}).get(k) == value for k, value in policy.items()),
              f"{slug}: card layout must render only title and credit")
    pages = receipt["appendix"]["pages"]
    page_count = math.ceil(len(entries) / 4)
    v.require(1 <= len(entries) <= 4 and page_count == len(pages) == 1
              and receipt["appendix"]["framesPerPage"] == fps * 5,
              f"{slug}: expected one four-item maximum, five-second page")
    added = page_count * fps * 5
    v.require(receipt["appendix"]["durationInFrames"] == appendix["durationInFrames"] == added
              and receipt["bodyFrames"] == appendix["from"] == receipt["appendix"]["from"] == body_frames
              and receipt["finalVideoFrames"] == meta["finalVideoFrames"] == body_frames + added,
              f"{slug}: actual-body/appendix/final timeline differs")
    body_sha = baseline.get("recoveredBodySHA256", baseline["originalBodySHA256"])
    v.require(v.sha_file(ROOT / baseline["bodyPath"]) == body_sha
              == receipt["inputs"]["bodySHA256"] == media["bodySHA256"],
              f"{slug}: current body input SHA differs from the declared actual baseline")
    v.require(all(media.get(k) is not None and media[k] == old_media.get(k) for k in FINGERPRINTS),
              f"{slug}: decoded original body/code-card/audio fingerprint changed")
    if "recoveredBodySHA256" in baseline:
        recovery = read(ROOT / baseline["bodyRecoveryProof"])
        v.require(recovery.get("originalFramePTSAACAndPCMExactlyMatchHistoricalProof") is True
                  and recovery.get("recoveredBodySHA256") == body_sha
                  and recovery.get("publishedSHA256") == baseline["previousPublishedSHA256"]
                  and recovery.get("historicalBodyContainerSHA256") == baseline["originalBodySHA256"]
                  and recovery.get("bodyFrames") == body_frames
                  and all(recovery.get(k) == old_media.get(k) for k in (
                      "bodyFrameMD5RowsSHA256", "audioPacketPayloadAndTimingSHA256", "decodedAudioPCM")),
                  f"{slug}: remuxed body recovery is not bound to the exact prior fingerprints")
    for flag in ("passed", "bodyDecodedFramesAndTimestampsEqual", "audioPacketsAndTimingEqual", "outputVideoTimelineContinuous"):
        v.require(media.get(flag) is True, f"{slug}: media comparison failed: {flag}")
    video_sha = v.sha_file(ep / meta["video"])
    v.require(video_sha == receipt["outputSHA256"] == media["outputSHA256"], f"{slug}: final media/receipt SHA differs")
    refs_sha = v.sha_file(ep / "references.json")
    v.require(receipt["inputs"]["referencesSHA256"] == refs_sha == v.sha_file(production / "references.json"),
              f"{slug}: bibliography input does not match current published/production references")
    for filename in (meta["video"], meta["poster"]):
        v.require(v.sha_file(v.DIST / "episodes" / slug / filename) == v.sha_file(ep / filename),
                  f"{slug}: built {filename} differs")
    if release_commit:
        for filename in ("meta.json", "references.json", "article.mdx", "storyboard.json", appendix["manifest"],
                         "reference-appendix-media-check.json", meta["video"], meta["poster"]):
            rel = str((ep / filename).relative_to(ROOT))
            blob = v.command(["git", "hash-object", "--", rel]).decode().strip()
            v.require(blob == v.command(["git", "rev-parse", f"{release_commit}:{rel}"]).decode().strip(),
                      f"{rel}: local publication differs from explicit release commit")
        for filename in ("baseline.json", "before-published-reference-appendix-media-check.json",
                         "before-published-article.mdx", "before-published-meta.json", "before-published-storyboard.json",
                         "before-published-references.json"):
            _commit_file(release_commit, revision / filename)
        if "bodyRecoveryProof" in baseline:
            _commit_file(release_commit, ROOT / baseline["bodyRecoveryProof"])
        _commit_file(release_commit, OUT / "startup.json")
    expected = {"meta": meta, "references": refs, "chapters": chapters, "articleChapters": fm,
                "fps": fps, "bodyFrames": body_frames, "referenceHeading": v.article_reference_heading(article.decode())}
    page_result = verify_page((v.DIST / "episodes" / slug / "index.html").read_bytes(), expected)
    captions = v.verify_vtt(v.caption_path(slug).read_bytes(), sb, expected)
    return expected, {"episode": slug, "status": "passed", "filesMatchCommit": release_commit is not None,
                      "referenceSourceCount": len(entries), "referencePageCount": len(pages), "secondsPerPage": 5,
                      "presentation": PRESENTATION, "bibliography": entries, "layout": policy,
                      "baseCommit": baseline["baseCommit"], "firstRelease": meta["firstRelease"],
                      "productionDir": str(production.relative_to(ROOT)), "actualBodyFrames": body_frames,
                      "storyboardFrames": scene_frames, "actualBodySHA256": body_sha,
                      "historicalBodyContainerSHA256": baseline["originalBodySHA256"],
                      "originalBodyAndCodeCardFingerprintsPreserved": True,
                      "originalTitleAndPublicationPreserved": True, "oldChaptersPreserved": True,
                      "quotesRetainedInArticleAndExactLocatorsInArticleOrOriginalResearch": True,
                      "researchLocatorChecks": page_result["researchLocatorChecks"],
                      "cardQuoteAbsenceDeclaredByLayout": True,
                      "finalVideoSHA256": video_sha, **captions}


ONLINE.PRESENTATION = PRESENTATION
ONLINE.ROOT = ROOT
ONLINE.DIST = ROOT / "site/dist"
ONLINE.REPORT = OUT / "online-verification.json"
ONLINE.published_targets = targets
ONLINE.local_expectation = expectation
ONLINE.verify_page = verify_page
ONLINE.article_reference_heading = article_reference_heading
