#!/usr/bin/env python3
"""Canonical full GET/content identity checks for this published revision.

Reads actual published metadata for video/poster filenames. It never requests
repository-only 4:3/3:4 covers, uses no Range/cache-busting/custom cache headers,
and performs no automatic retry. It checks HTTP/content identity only; browser
playback, chapter seeking and visual/listening review are separate checks.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import shutil
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo


D = Path(__file__).resolve().parent
ROOT = next(parent for parent in D.parents
            if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
SLUG = "redis-skiplist"
BASE = "https://linhongcun.github.io/video-studio/"
REFERENCE_GENERATOR = ROOT / "episodes-codex/_shared/append_references_bibliography.py"
ORIGINAL_RENDERER = REFERENCE_GENERATOR.with_name("append_references_original.py")
OLD_ENGINE = REFERENCE_GENERATOR.with_name("append_references.py")
REFERENCE_LAYOUT = {"kind": "title-author-single-column", "maxItemsPerPage": 4,
                    "renderedFields": ["title", "credit"], "quotesRendered": False}


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(256 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True, help="Actual newly published Release tag")
    parser.add_argument("--report", type=Path, default=D / "online-verification.json")
    args = parser.parse_args()
    assert re.fullmatch(r"v\d+\.\d+\.\d+", args.release)
    report_path = args.report.resolve()
    assert report_path.is_relative_to(D.resolve()), "Keep the QA report in this production directory"
    published = ROOT / "episodes" / SLUG
    meta = read(published / "meta.json")
    render = read(D / "render-result.json")
    sb = read(D / "storyboard.json")
    assert meta["slug"] == SLUG and meta["ep"] == 40 and meta["draft"] is False
    assert meta["series"] == "engineering-algorithms" and meta["publishedAt"] and meta["firstRelease"]
    draft = read(D / "meta.draft.json")
    for key in ["slug", "ep", "episodePart", "title", "series", "createdAt", "updatedAt", "publishedAt", "firstRelease"]:
        assert meta[key] == draft[key], "Published metadata differs from production identity"
    assert meta["sourcePath"] == draft["sourcePath"] == str((D / "remotion").relative_to(ROOT))
    startup = read(D / "startup.json")
    for key in ["createdAt", "publishedAt", "firstRelease"]:
        assert meta[key] == startup[key], "Retain the historical first-release identity"
    assert re.fullmatch(r"v\d+\.\d+\.\d+", meta["firstRelease"])
    assert tuple(map(int, args.release[1:].split("."))) > tuple(map(int, meta["firstRelease"][1:].split("."))), \
        "Verify the new revision Release separately from the original first Release"
    times = [datetime.fromisoformat(meta[key]) for key in ["createdAt", "publishedAt", "updatedAt"]]
    assert all(value.tzinfo is not None for value in times) and times[0] <= times[1] <= times[2]
    assert read(ROOT / "site/package.json")["version"] == args.release[1:], "Verify the actual current publication release"
    for key in ["video", "poster"]:
        assert isinstance(meta[key], str) and Path(meta[key]).name == meta[key]
        assert (published / meta[key]).is_file()
        assert sha(published / meta[key]) == sha(D / meta[key])
    assert meta["video"].endswith(".mp4") and meta["poster"].endswith(".jpg")
    assert sha(published / meta["video"]) == render["sha256"]
    assert meta["finalVideoFrames"] == render["frames"]
    assert meta["referenceAppendix"] == render["publicationMetadata"]["referenceAppendix"]
    for name in ["references.json", "reference-appendix.json", "reference-appendix-media-check.json"]:
        assert sha(published / name) == sha(D / name), "Published reference identity differs from production"
    refs = read(published / "references.json")
    receipt = read(published / "reference-appendix.json")
    assert receipt["schemaVersion"] == refs["schemaVersion"] == 1
    assert receipt["episode"] == refs["episode"] == SLUG
    assert refs["presentation"] == receipt["presentation"] == "title-author"
    assert receipt["layout"] == REFERENCE_LAYOUT
    bibliography = []
    for source in refs["sources"]:
        credit = source["author"] if "author" in source else source["organization"]
        assert isinstance(credit, str) and credit.strip(), "Reference credit must be explicit and nonempty"
        bibliography.append({"id": source["id"], "title": source["title"], "credit": credit})
    assert bibliography and receipt["bibliography"] == bibliography
    assert receipt["sourceTitles"] == [{"id": source["id"], "title": source["title"]}
                                        for source in refs["sources"]]
    assert receipt["quotations"] == [{"id": source["id"], **source["quotation"]}
                                      for source in refs["sources"] if "quotation" in source]
    assert receipt["inputs"]["referencesSHA256"] == sha(published / "references.json")
    assert receipt["inputs"]["generatorSHA256"] == sha(REFERENCE_GENERATOR)
    assert receipt["dependencies"] == {
        "oldEngine": str(OLD_ENGINE.relative_to(ROOT)), "oldEngineSHA256": sha(OLD_ENGINE),
        "originalRenderer": str(ORIGINAL_RENDERER.relative_to(ROOT)),
        "originalRendererSHA256": sha(ORIGINAL_RENDERER),
    }
    fps = Fraction(str(receipt["fps"]))
    assert fps == sb["meta"]["fps"] == 30
    body_frames = sb["meta"]["durationInFrames"]
    assert receipt["bodyFrames"] == render["bodyFrames"] == sb["meta"]["finalVideoFrames"] == body_frames
    appendix = receipt["appendix"]
    expected_pages = (len(refs["sources"]) + 3) // 4
    assert appendix["kind"] == "references" and appendix["from"] == body_frames
    assert appendix["sourceIds"] == [source["id"] for source in refs["sources"]]
    assert len(appendix["pages"]) == expected_pages
    assert receipt["inputs"]["secondsPerPage"] == 5
    assert appendix["framesPerPage"] == fps * 5
    assert appendix["durationInFrames"] == fps * 5 * expected_pages
    final_frames = body_frames + appendix["durationInFrames"]
    assert receipt["finalVideoFrames"] == meta["finalVideoFrames"] == render["frames"] == final_frames
    assert render["finalVideoFrames"] == render["publicationMetadata"]["finalVideoFrames"] == final_frames
    assert receipt["durationSeconds"] == render["seconds"] == float(final_frames / fps)
    assert meta["referenceAppendix"] == {
        "kind": "references", "from": body_frames, "durationInFrames": appendix["durationInFrames"],
        "sources": "references.json", "manifest": "reference-appendix.json",
    }
    chapter_ids = list(dict.fromkeys(shot["chapterId"] for scene in sb["scenes"] for shot in scene["shots"]))
    planned_chapters = list(dict.fromkeys(item["chapterId"] for item in read(D / "plan.json")))
    assert planned_chapters and chapter_ids == planned_chapters
    caption_count = sum(len(shot["subtitles"]) for scene in sb["scenes"] for shot in scene["shots"])
    expected_vtt = ROOT / "site/dist/episodes" / SLUG / "captions.vtt"
    assert expected_vtt.is_file(), "Build the current real episode before online verification"

    rows = []
    report = {"schemaVersion": 1, "status": "in-progress",
        "checkedAtUTC": datetime.now(timezone.utc).isoformat(),
        "checkedAtBeijing": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "page": BASE + "episodes/" + SLUG + "/", "release": args.release,
        "firstRelease": meta["firstRelease"], "contentUpdatedAt": meta["updatedAt"],
        "productionSource": meta["sourcePath"],
        "referencePresentation": receipt["presentation"], "bibliography": bibliography,
        "referenceLayout": receipt["layout"],
        "referenceReceiptSHA256": sha(published / "reference-appendix.json"),
        "referenceGeneratorSHA256": receipt["inputs"]["generatorSHA256"],
        "referenceDependencies": receipt["dependencies"],
        "transport": "Ordinary canonical urllib GET via inherited proxy and CA trust",
        "rangeRequests": False, "cacheBusting": False, "customCacheHeaders": False,
        "automaticRetryCount": 0, "requests": rows,
        "scope": "HTTP/content identity only; no browser-playback, physical-device or listening claim.",
        "localOnlyCovers": []}
    for name in ["cover-4x3.jpg", "cover-3x4.jpg"]:
        production_sha = sha(D / name)
        repository_sha = sha(published / name)
        assert production_sha == repository_sha
        report["localOnlyCovers"].append({"file": name, "sha256": repository_sha,
            "scope": "Production/repository asset; not requested from Pages"})
    if report_path.exists():
        archive = D / "revisions/online-verification"
        archive.mkdir(parents=True, exist_ok=True)
        destination = archive / ("previous-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
        shutil.copyfile(report_path, destination)
        report["previousReportArchived"] = {"file": str(destination.relative_to(D)), "sha256": sha(destination)}

    def save():
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    def fetch(relative: str, local: Path | None = None):
        url = relative if relative.startswith("https://") else BASE + relative
        row = {"url": url, "method": "GET", "status": "in-progress"}
        if local is not None:
            row.update(localFile=str(local.relative_to(ROOT)), expectedSHA256=sha(local))
        rows.append(row)
        save()
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                row.update(status=response.status, finalURL=response.url)
                assert response.status == 200, (url, response.status)
                digest = hashlib.sha256()
                count = 0
                bodies = []
                while True:
                    block = response.read(256 * 1024)
                    if not block:
                        break
                    digest.update(block)
                    count += len(block)
                    if local is None:
                        bodies.append(block)
                row.update(bytes=count, sha256=digest.hexdigest())
            if local is not None:
                assert row["sha256"] == row["expectedSHA256"], row
                row["contentIdentity"] = "matched"
            save()
            print("verified", url, flush=True)
            return b"".join(bodies).decode("utf-8") if local is None else row
        except Exception as exc:
            row["error"] = repr(exc)
            if isinstance(exc, urllib.error.HTTPError):
                row["status"] = exc.code
            save()
            raise

    try:
        page = fetch("episodes/" + SLUG + "/")
        text_page = unescape(page)
        for text in [meta["title"], "工程算法", meta["video"], "captions.vtt", meta["sourcePath"]]:
            assert text in text_page, ("page missing", text)
        for chapter in chapter_ids:
            assert ('id="' + chapter + '"') in page, ("chapter anchor missing", chapter)
        for key in ["video", "poster"]:
            fetch("episodes/" + SLUG + "/" + meta[key], published / meta[key])
        fetch("episodes/" + SLUG + "/captions.vtt", expected_vtt)
        local_vtt = expected_vtt.read_text()
        assert local_vtt.count(" --> ") == caption_count
        lesson = "/video-studio/episodes/" + SLUG + "/"
        for relative in ["series/engineering-algorithms/", "learn/", "library/", ""]:
            html = fetch(relative)
            assert lesson in html and "工程算法" in unescape(html), (relative, "lesson/series link missing")
        changelog = fetch("changelog/")
        release_url = "https://github.com/linhongcun/video-studio/releases/tag/" + args.release
        assert release_url in changelog, ("actual Release entry missing", args.release)
        release = json.loads(fetch("https://api.github.com/repos/linhongcun/video-studio/releases/tags/" + args.release))
        assert release["tag_name"] == args.release and release["html_url"] == release_url
        assert release["draft"] is False and release["prerelease"] is False and release["published_at"]
        assert report["page"] in release["body"], "Actual Release must identify this lesson"
        report.update(status="passed", requestCount=len(rows), chapterCount=len(chapter_ids),
            captionCount=caption_count, frames=render["frames"], mediaSHA256=render["sha256"],
            publishedMedia=meta["video"], publishedPoster=meta["poster"],
            completedAtUTC=datetime.now(timezone.utc).isoformat())
        save()
    except Exception as exc:
        report.update(status="failed", requestCount=len(rows), error=repr(exc),
                      completedAtUTC=datetime.now(timezone.utc).isoformat())
        save()
        raise


if __name__ == "__main__":
    main()
