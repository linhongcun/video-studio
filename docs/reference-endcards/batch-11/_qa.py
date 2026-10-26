"""Batch-11 first-append QA using unchanged historical parsers and engines.

These four original videos had no prior reference appendix. Bind the new full
media comparison to their captured original body SHA; do not borrow an old
appendix fingerprint proof from the title/author migration.
"""
from __future__ import annotations

import json
import hashlib
import math
from fractions import Fraction
from pathlib import Path
import re
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(OUT.parent))
from _batch_runtime import configure_batch

ALLOWED = ("horse-racing", "bridge-torch", "water-jug", "monty-hall")
BASELINE_COMMIT = "a1a9821845c83a61a57fbb3f0e10461ef4c55238"
PUBLICATION_BASELINE_COMMIT = "a1a9821845c83a61a57fbb3f0e10461ef4c55238"
BASE = configure_batch(OUT, ALLOWED)
ONLINE, UI, read = BASE.ONLINE, BASE.UI, BASE.read
PRESENTATION = "title-author"
LAYOUT = {"kind": "title-author-single-column", "maxItemsPerPage": 4,
          "renderedFields": ["title", "credit"], "quotesRendered": False}


def declarations():
    data = read(OUT / "startup.json")
    rows = data["episodes"]
    ONLINE.require(data["baseCommit"] == BASELINE_COMMIT
                   and data["selection"] == list(ALLOWED)
                   and len(rows) == len(ALLOWED)
                   and {row["slug"] for row in rows} == set(ALLOWED),
                   "Unexpected batch-11 selection/baseline")
    ONLINE.require(all(isinstance(row["bodyFrames"], int) and row["bodyFrames"] > 0
                       and re.fullmatch(r"[0-9a-f]{64}", row["bodySHA256"]) for row in rows),
                   "Invalid batch-11 startup body frame/SHA declaration")
    return rows


def targets():
    return [row["slug"] for row in declarations()]


def representatives():
    # The reusable title-author browser case imports this helper. Batch 11
    # checks every selected episode rather than choosing migration samples.
    return targets()


def bibliography(refs):
    entries = []
    for source in refs["sources"]:
        key = "author" if "author" in source else "organization"
        credit = source.get(key)
        ONLINE.require(isinstance(credit, str) and bool(credit.strip()),
                       f"{source.get('id')}: empty original {key}")
        entries.append({"id": source["id"], "title": source["title"], "credit": credit})
    return entries


def reference_heading(article):
    # These four originals keep their sources in footnotes. The new, separate
    # appendix bibliography is the real heading we must locate and validate.
    matches = re.findall(r"^##[ \t]+(片尾参考资料)(?:[ \t]+\{#([^}]+)\})?[ \t]*$", article, re.M)
    ONLINE.require(len(matches) == 1, "Expected one batch-11 appendix bibliography heading")
    title, anchor = matches[0]
    return {"title": title, "id": anchor or None}


def verify_page(body, expected):
    # Batch 3 already checks original titles/organizations, canonical and
    # actually read source links, provided quotes, chapters and all dates.
    result = BASE.verify_page(body, expected)
    visible = ONLINE.visible_text(ONLINE.Page(body).text)
    for anchor in expected.get("originalMarkdownAnchors", []):
        ONLINE.require(anchor in ONLINE.Page(body).ids, f"{expected['meta']['slug']}: original article anchor missing: {anchor}")
    author_checks = []
    for source in expected["references"]["sources"]:
        if "author" not in source:
            continue
        author = source["author"]
        ONLINE.require(isinstance(author, str) and bool(author.strip())
                       and ONLINE.visible_text(author) in visible,
                       f"{expected['meta']['slug']}: exact personal author missing from visible page text: {author}")
        author_checks.append({"sourceId": source["id"], "author": author,
                              "exactVisiblePersonalAuthorVerified": True})
    provided = sum("quotation" in source for source in expected["references"]["sources"])
    result["exactProvidedQuotationsAndLocatorsVerified"] = result.pop("exactQuotationsAndLocatorsVerified")
    result.update(cardPresentation=PRESENTATION, bibliography=bibliography(expected["references"]),
                  quotationsRequired=False, providedQuotationCount=provided,
                  visiblePersonalAuthorChecks=author_checks)
    return result


def _commit_file(commit, path):
    rel = str(path.relative_to(ROOT))
    blob = ONLINE.command(["git", "hash-object", "--", rel]).decode().strip()
    ONLINE.require(blob == ONLINE.command(["git", "rev-parse", f"{commit}:{rel}"]).decode().strip(),
                   f"{rel}: differs from explicit release commit")


def verify_vtt(vtt, storyboard, expected):
    """Keep full frozen cue checks, with an exact rational card-end boundary.

    The preserved historical helper multiplies an already rounded seconds
    float by 1000. At frame 3924 / 30 this is one ULP above 130800 and can
    incorrectly keep the final cue at the first card frame. Integer frame
    arithmetic defines the greatest millisecond strictly before that frame.
    """
    v, slug = ONLINE, expected["meta"]["slug"]
    v.require(vtt.startswith(b"WEBVTT"), f"{slug}: native VTT header missing")
    cues = []
    for block in re.split(r"\n\s*\n", vtt.decode().replace("\r\n", "\n").strip())[1:]:
        timing, separator, text = block.partition("\n")
        match = re.fullmatch(r"(\d{2,}:\d{2}:\d{2}\.\d{3}) --> (\d{2,}:\d{2}:\d{2}\.\d{3})", timing)
        v.require(match and separator, f"{slug}: malformed native VTT cue")
        cues.append({"start": v.vtt_seconds(match[1]), "end": v.vtt_seconds(match[2]), "text": text})
    fps, offset, wanted = expected["fps"], 0, []
    card = storyboard["meta"].get("unvoicedEndCard") or storyboard["meta"].get("javaEndCard") or expected["meta"]["referenceAppendix"]
    for scene in storyboard["scenes"]:
        for shot in scene["shots"]:
            previous_end = -1
            for sub in shot.get("subtitles", []):
                v.require(isinstance(sub.get("from"), int) and isinstance(sub.get("to"), int)
                          and previous_end < sub["from"] <= sub["to"] < shot["durationInFrames"],
                          f"{slug}: frozen subtitle timing is incomplete")
                end_frame = offset + sub["to"] + 1
                end = end_frame / fps
                if end_frame == card["from"]:
                    end = (math.ceil(Fraction(end_frame * 1000) / Fraction(str(fps))) - 1) / 1000
                wanted.append({"start": (offset + sub["from"]) / fps, "end": end, "text": sub["text"]})
                previous_end = sub["to"]
            offset += shot["durationInFrames"]
    v.require(bool(cues) and len(cues) == len(wanted), f"{slug}: native VTT cue count differs")
    v.require(all(c["text"] == e["text"] and abs(c["start"] - e["start"]) <= .000501
                  and abs(c["end"] - e["end"]) <= .000501 for c, e in zip(cues, wanted)),
              f"{slug}: full native VTT text or frozen timing differs")
    last_end = max(c["end"] for c in cues)
    v.require(last_end < card["from"] / fps, f"{slug}: native captions overlap the first reference frame")
    v.require(last_end < expected["bodyFrames"] / fps,
              f"{slug}: native subtitles reach or overlap the first reference frame")
    snapshot = next(row for row in read(OUT / "before-caption-snapshots.json") if row["slug"] == slug)
    previous_path = ROOT / snapshot["path"]
    previous_bytes = previous_path.read_bytes()
    v.require(v.sha_file(previous_path) == snapshot["sha256"], f"{slug}: saved original VTT differs")
    timing_pattern = r"(?m)^(\d{2,}:\d{2}:\d{2}\.\d{3}) --> (\d{2,}:\d{2}:\d{2}\.\d{3})$"
    previous_text, current_text = previous_bytes.decode(), vtt.decode()
    previous_timings, current_timings = list(re.finditer(timing_pattern, previous_text)), list(re.finditer(timing_pattern, current_text))
    v.require(len(previous_timings) == len(current_timings) == len(cues), f"{slug}: original/current VTT cue count differs")
    previous_end, current_end = previous_timings[-1][2], current_timings[-1][2]
    adjustment_ms = round((v.vtt_seconds(previous_end) - v.vtt_seconds(current_end)) * 1000)
    v.require(adjustment_ms in (0, 1), f"{slug}: unexpected final VTT cue adjustment")
    before = previous_timings[-1]
    expected_current = previous_text[:before.start()] + current_timings[-1][0] + previous_text[before.end():]
    v.require(expected_current == current_text and previous_timings[-1][1] == current_timings[-1][1],
              f"{slug}: derived VTT changed more than the final cue end")
    return {"subtitleCueCount": len(cues), "fullSubtitleTextAndTimingVerified": True,
            "lastSubtitleEndSeconds": last_end, "subtitleEndsStrictlyBeforeAppendix": True,
            "cardEndMillisecondsComputedFromExactFrameRatio": True, "unvoicedCodeCardPresent": False,
            "derivedVTTBoundaryHandling": {"originalSnapshot": snapshot["path"],
                "originalSHA256": snapshot["sha256"], "currentSHA256": hashlib.sha256(vtt).hexdigest(),
                "bytesUnchanged": previous_bytes == vtt, "originalLastCueEnd": previous_end,
                "currentLastCueEnd": current_end, "lastCueEndShortenedMilliseconds": adjustment_ms,
                "onlyFinalCueEndMayDiffer": True,
                "reason": "Derived native VTT ends at the greatest millisecond strictly before the first reference frame; original storyboard, words and media are preserved."}}


def expectation(slug, release_commit=None):
    v = ONLINE
    v.require(slug in targets(), "Episode is outside batch 11")
    row = next(item for item in declarations() if item["slug"] == slug)
    ep = ROOT / "episodes" / slug
    meta, refs = read(ep / "meta.json"), read(ep / "references.json")
    production = (ROOT / meta["sourcePath"]).resolve().parent
    v.require(production == (ROOT / "episodes-codex" / slug).resolve(),
              f"{slug}: unexpected production sourcePath")
    revision = production / "revisions/reference-endcards"
    baseline = read(revision / "baseline.json")
    old = baseline["metadata"]
    v.require(baseline["baseCommit"] == BASELINE_COMMIT
              and baseline["episode"] == slug
              and baseline["bodyFrames"] == row["bodyFrames"]
              and baseline["originalBodySHA256"] == row["bodySHA256"],
              f"{slug}: original body does not match startup/baseline")
    v.require("referenceAppendix" not in old, f"{slug}: expected first appendix, not a migration")
    v.require(meta["slug"] == refs["episode"] == slug and meta.get("draft") is False,
              f"{slug}: invalid publication identity")
    mutable = {"updatedAt", "finalVideoFrames", "targetDuration", "referenceAppendix"}
    v.require(all(meta.get(key) == value for key, value in old.items() if key not in mutable),
              f"{slug}: original publication/date/platform metadata changed")
    original_overrides = []
    for override in ("chapters.txt", "remotion/src/timing.json"):
        path = ep / override
        rel = str(path.relative_to(ROOT))
        existed = bool(v.command(["git", "ls-tree", "--name-only", BASELINE_COMMIT, "--", rel]).strip())
        v.require(path.is_file() == existed, f"{slug}: original timing override presence changed: {override}")
        if existed:
            v.require(path.read_bytes() == v.git_file(BASELINE_COMMIT, rel),
                      f"{slug}: original timing override changed: {override}")
            original_overrides.append(override)
    # Preserve any original chapter override, but reject a new override. The
    # selected four baseline films have no separate shot-duration override.
    v.require("remotion/src/timing.json" not in original_overrides,
              f"{slug}: an unhandled preexisting shot-duration override needs explicit support")
    sb = read(ep / "storyboard.json")
    v.require(sb == json.loads(v.git_file(BASELINE_COMMIT, f"episodes/{slug}/storyboard.json")),
              f"{slug}: complete original storyboard changed")
    # The selected lessons must retain their complete approved original body,
    # not pick up an earlier teaching version from another revision directory.
    original_production_inputs = []
    for filename in ("script.md", "storyboard.json", "words.json"):
        path = production / filename
        rel = str(path.relative_to(ROOT))
        v.require(path.read_bytes() == v.git_file(BASELINE_COMMIT, rel),
                  f"{slug}: original production profile changed: {filename}")
        original_production_inputs.append(rel)
    preserved_source_prefixes = []
    for filename in ("article.mdx", "research.md"):
        path = production / filename
        rel = str(path.relative_to(ROOT))
        original_bytes = v.git_file(BASELINE_COMMIT, rel)
        v.require(path.read_bytes().startswith(original_bytes),
                  f"{slug}: original source {filename} is not a complete preserved prefix")
        preserved_source_prefixes.append(rel)
    original_code_card = sb["meta"].get("unvoicedEndCard") or sb["meta"].get("javaEndCard")
    v.require(original_code_card is None and baseline["existingCodeCard"] is None
              and row["existingCodeCard"] is None,
              f"{slug}: unexpected original code card; batch 11 appends after the full spoken body")
    article = (ep / "article.mdx").read_bytes()
    old_article = v.git_file(PUBLICATION_BASELINE_COMMIT, f"episodes/{slug}/article.mdx")
    v.require(article.startswith(old_article), f"{slug}: original article body is not preserved")
    public_research = ep / "research.md"
    research_rel = str(public_research.relative_to(ROOT))
    public_research_existed = bool(v.command(["git", "ls-tree", "--name-only", PUBLICATION_BASELINE_COMMIT,
                                             "--", research_rel]).strip())
    if public_research_existed:
        v.require(public_research.read_bytes().startswith(v.git_file(PUBLICATION_BASELINE_COMMIT, research_rel)),
                  f"{slug}: original published research is not a complete preserved prefix")
    else:
        v.require(public_research.read_bytes() == (production / "research.md").read_bytes(),
                  f"{slug}: newly published research must exactly match current production research")
    fm, old_fm = v.frontmatter_chapters(article.decode()), v.frontmatter_chapters(old_article.decode())
    original_anchors = re.findall(r"\{#([\w-]+)\}", old_article.decode())
    v.require(re.findall(r"\{#([\w-]+)\}", article.decode()) == original_anchors,
              f"{slug}: original article anchors changed")
    v.require(fm == old_fm, f"{slug}: original article chapters/anchors changed")
    chapters, body_frames, fps = v.expected_chapters(sb, old_fm)
    v.require(body_frames == baseline["bodyFrames"], f"{slug}: original storyboard/body boundary differs")
    if "chapters.txt" in original_overrides:
        from_frontmatter = {item["title"]: item for item in old_fm}
        from_scenes = {item["title"]: item for item in chapters}
        original_chapters = []
        for line in (ep / "chapters.txt").read_text().splitlines():
            if not line.strip():
                continue
            match = re.fullmatch(r"(\d{2,}):([0-5]\d)\s+(.+)", line.strip())
            v.require(match is not None, f"{slug}: invalid original chapter override line")
            minute, second, title = match.groups()
            identity = from_frontmatter.get(title) or from_scenes.get(title)
            v.require(identity is not None, f"{slug}: original chapter title has no known identity: {title}")
            original_chapters.append({"id": identity["id"], "title": title,
                                      "start": int(minute) * 60 + int(second)})
        chapters = original_chapters
    appendix = meta["referenceAppendix"]
    receipt = read(ep / appendix["manifest"])
    media = read(ep / "reference-appendix-media-check.json")
    v.require(refs.get("presentation") == receipt.get("presentation") == PRESENTATION,
              f"{slug}: title-author presentation missing")
    entries = bibliography(refs)
    v.require(receipt.get("bibliography") == entries, f"{slug}: exact original title/credit list differs")
    v.require(all(receipt.get("layout", {}).get(key) == value for key, value in LAYOUT.items()),
              f"{slug}: card must show only title/credit, at most four items per page")
    v.require(receipt.get("sourceTitles") == [{"id": s["id"], "title": s["title"]} for s in refs["sources"]],
              f"{slug}: original title receipt differs")
    v.require(receipt.get("quotations") == [{"id": s["id"], **s["quotation"]}
                                           for s in refs["sources"] if "quotation" in s],
              f"{slug}: optional original quotations differ")
    pages = receipt["appendix"]["pages"]
    page_count = (len(entries) + 3) // 4
    v.require(1 <= len(entries) and page_count == len(pages)
              and receipt["appendix"]["framesPerPage"] == fps * 5,
              f"{slug}: expected derived four-item-maximum five-second pages")
    added = page_count * fps * 5
    v.require(receipt["appendix"]["durationInFrames"] == appendix["durationInFrames"] == added
              and receipt["bodyFrames"] == appendix["from"] == receipt["appendix"]["from"] == body_frames
              and receipt["finalVideoFrames"] == meta["finalVideoFrames"] == body_frames + added,
              f"{slug}: body/appendix/final boundary differs")
    body_sha = baseline["originalBodySHA256"]
    v.require(v.sha_file(ROOT / baseline["bodyPath"]) == body_sha
              == receipt["inputs"]["bodySHA256"] == media["bodySHA256"],
              f"{slug}: NEW media proof is not bound to the original published body")
    for flag in ("passed", "bodyDecodedFramesAndTimestampsEqual", "audioPacketsAndTimingEqual",
                 "outputVideoTimelineContinuous"):
        v.require(media.get(flag) is True, f"{slug}: full new media comparison failed: {flag}")
    for key in ("bodyFrameMD5RowsSHA256", "audioPacketPayloadAndTimingSHA256", "decodedAudioPCM"):
        v.require(isinstance(media.get(key), str) and bool(media[key]), f"{slug}: missing new media fingerprint {key}")
    v.require(media.get("bodyFrames") == body_frames and media.get("appendedFrames") == added
              and media.get("finalFrames") == body_frames + added,
              f"{slug}: full comparison frame totals differ")
    actual_sha = v.sha_file(ep / meta["video"])
    v.require(actual_sha == receipt["outputSHA256"] == media["outputSHA256"], f"{slug}: final output SHA differs")
    v.require(receipt["inputs"]["referencesSHA256"] == v.sha_file(ep / "references.json")
              == v.sha_file(production / "references.json"), f"{slug}: reference input identity differs")
    for filename in (appendix["manifest"], "reference-appendix-media-check.json"):
        v.require((ep / filename).read_bytes() == (production / filename).read_bytes(),
                  f"{slug}: published/production receipt bytes differ")
    v.require(v.sha_file(ROOT / baseline["productionOutput"]) == actual_sha,
              f"{slug}: actual production output differs")
    for filename in (meta["video"], meta["poster"]):
        v.require(v.sha_file(v.DIST / "episodes" / slug / filename) == v.sha_file(ep / filename),
                  f"{slug}: built {filename} differs")
    if release_commit:
        for filename in ("meta.json", "references.json", "article.mdx", "storyboard.json", appendix["manifest"],
                         "reference-appendix-media-check.json", meta["video"], meta["poster"]):
            _commit_file(release_commit, ep / filename)
        for filename in original_overrides:
            _commit_file(release_commit, ep / filename)
        for rel in original_production_inputs + preserved_source_prefixes:
            _commit_file(release_commit, ROOT / rel)
        _commit_file(release_commit, public_research)
        _commit_file(release_commit, revision / "baseline.json")
        _commit_file(release_commit, OUT / "startup.json")
    expected = {"meta": meta, "references": refs, "chapters": chapters, "articleChapters": fm,
                "fps": fps, "bodyFrames": body_frames, "existingCodeCard": original_code_card, "originalMarkdownAnchors": original_anchors, "referenceHeading": reference_heading(article.decode())}
    page_review = verify_page((v.DIST / "episodes" / slug / "index.html").read_bytes(), expected)
    captions = v.verify_vtt(v.caption_path(slug).read_bytes(), sb, expected)
    return expected, {"episode": slug, "status": "passed", "filesMatchCommit": release_commit is not None,
                      "referenceSourceCount": len(entries), "referencePageCount": len(pages), "secondsPerPage": 5,
                      "presentation": PRESENTATION, "bibliography": entries, "layout": LAYOUT,
                      "baseCommit": BASELINE_COMMIT, "firstRelease": meta["firstRelease"],
                      "baselineBodySHA256": body_sha, "originalBodySHAAndFullMediaComparisonVerified": True,
                      "priorAppendixMediaProofUsed": False, "quotationsRequired": False,
                      "originalTitleAndPublicationPreserved": True, "oldChaptersPreserved": True,
                      "preservedOriginalTimingOverrides": original_overrides,
                      "originalProductionProfileInputsPreserved": original_production_inputs,
                      "originalSourceArticleResearchPrefixesPreserved": preserved_source_prefixes,
                      "originalPublishedArticleResearchPrefixesPreserved": [str((ep / "article.mdx").relative_to(ROOT))]
                          + ([research_rel] if public_research_existed else []),
                      "publishedResearch": {"path": research_rel, "presentAtBaseline": public_research_existed,
                          "originalPrefixPreserved": public_research_existed,
                          "newPublicationMatchesCurrentProductionExactly": not public_research_existed},
                      "originalCodeCardPresent": False,
                      "visiblePersonalAuthorChecks": page_review["visiblePersonalAuthorChecks"],
                      "finalVideoSHA256": actual_sha, **captions}


ONLINE.PRESENTATION = PRESENTATION
ONLINE.ROOT = ROOT
ONLINE.DIST = ROOT / "site/dist"
ONLINE.REPORT = OUT / "online-verification.json"
ONLINE.published_targets = targets
ONLINE.local_expectation = expectation
ONLINE.verify_page = verify_page
ONLINE.verify_vtt = verify_vtt
