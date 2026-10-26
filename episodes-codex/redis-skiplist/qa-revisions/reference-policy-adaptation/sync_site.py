#!/usr/bin/env python3
"""Validate the current Redis skiplist production and copy a fixed site whitelist.

Default mode reads completed artifacts only. Publishing additionally requires
the reviewed final-video SHA and an explicit release matching site/package.json:

  python3 episodes-codex/redis-skiplist/sync_site.py --publish \
    --reviewed-video-sha256 <final-reviewed-sha256> --release v0.72.0

That SHA binds the operator's completed media review; this script checks media
identity and receipts, and does not perform a visual or listening review.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import wave
from zoneinfo import ZoneInfo


D = Path(__file__).resolve().parent
ROOT = next(parent for parent in D.parents
            if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
SLUG = "redis-skiplist"
DESTINATION = ROOT / "episodes" / SLUG
FILES = (
    "article.mdx", "script.md", "research.md", "storyboard.json", "video.mp4",
    "cover-16x9.jpg", "cover-4x3.jpg", "cover-3x4.jpg", "references.json",
    "reference-appendix.json", "reference-appendix-media-check.json",
)


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(256 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    assert result.tzinfo is not None, "Content/publication times need an explicit timezone"
    return result


def probe(path: Path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ], text=True))


def validate(reviewed_sha: str | None = None):
    # The episode freezer verifies its actual current manifest without rewriting it.
    subprocess.run(["python3", str(D / "freeze.py"), "--verify"], cwd=ROOT, check=True)
    draft = read(D / "meta.draft.json")
    startup = read(D / "startup.json")
    config = read(D / "episode-config.json")
    sb = read(D / "storyboard.json")
    words = read(D / "words.json")
    voice_build = read(D / "voice/build.json")
    render = read(D / "render-result.json")
    refs = read(D / "references.json")
    receipt = read(D / "reference-appendix.json")
    media = read(D / "reference-appendix-media-check.json")
    manifest = read(D / "source-sha256.json")

    assert draft["draft"] is True and "publishedAt" not in draft
    assert draft["slug"] == startup["slug"] == config["slug"] == SLUG
    assert draft["ep"] == startup["ep"] == sb["meta"]["episode"] == 40
    assert draft["series"] == startup["series"] == "engineering-algorithms"
    assert draft["episodePart"] == "工程算法 03"
    assert draft["sourcePath"] == str((D / "remotion").relative_to(ROOT))
    assert draft["createdAt"] == startup["createdAt"]
    assert timestamp(draft["updatedAt"]) >= timestamp(draft["createdAt"])
    assert draft["title"] == config["title"] == sb["meta"]["title"]
    assert draft["video"] == "video.mp4" and draft["poster"] == "cover-16x9.jpg"
    assert draft["series"] in read(ROOT / "site/src/content/series.json")
    for slug in draft["related"]:
        assert read(ROOT / "episodes" / slug / "meta.json")["draft"] is False

    body_frames = sb["meta"]["durationInFrames"]
    fps = sb["meta"]["fps"]
    assert fps == words["fps"] == 30
    assert body_frames == sb["meta"]["finalVideoFrames"] == words["durationFrames"]
    assert body_frames == voice_build["summary"]["frames"]
    assert words["scriptSha256"] == sha(D / "script.md")
    voice_sha = sha(D / "voice.wav")
    assert voice_sha == words["audioSha256"] == voice_build["summary"]["sha"]
    with wave.open(str(D / "voice.wav"), "rb") as audio:
        assert audio.getframerate() == 48000
        assert audio.getnframes() == voice_build["summary"]["samples"] == body_frames * 1600
    shots = [shot for scene in sb["scenes"] for shot in scene["shots"]]
    chapter_ids = list(dict.fromkeys(shot["chapterId"] for shot in shots))
    planned_chapters = list(dict.fromkeys(item["chapterId"] for item in read(D / "plan.json")))
    assert planned_chapters and chapter_ids == planned_chapters
    assert len(shots) == config["shotCount"]
    caption_count = sum(len(shot["subtitles"]) for shot in shots)
    assert caption_count == sum(len(shot["sentences"]) for shot in words["shots"])
    assert sum(shot["durationInFrames"] for shot in shots) == body_frames

    assert receipt["episode"] == refs["episode"] == SLUG
    assert refs["presentation"] == receipt["presentation"] == "original-title-quote"
    assert Fraction(str(receipt["fps"])) == fps
    assert receipt["bodyFrames"] == render["bodyFrames"] == body_frames
    assert receipt["inputs"]["referencesSHA256"] == sha(D / "references.json")
    assert receipt["inputs"]["bodySHA256"] == media["bodySHA256"]
    body_path = Path(receipt["body"])
    body_path = body_path if body_path.is_absolute() else D / body_path
    assert body_path.resolve().is_relative_to(D.resolve())
    assert sha(body_path) == receipt["inputs"]["bodySHA256"]
    appendix = receipt["appendix"]
    assert appendix["kind"] == "references" and appendix["from"] == body_frames
    assert refs["sources"]
    expected_pages = (len(refs["sources"]) + 1) // 2
    assert len(appendix["pages"]) == expected_pages
    assert appendix["framesPerPage"] == fps * 5
    assert appendix["durationInFrames"] == fps * 5 * expected_pages
    assert appendix["sourceIds"] == [source["id"] for source in refs["sources"]]
    assert receipt["sourceTitles"] == [{"id": source["id"], "title": source["title"]}
                                        for source in refs["sources"]]
    assert receipt["quotations"] == [{"id": source["id"], **source["quotation"]}
                                      for source in refs["sources"] if "quotation" in source]
    artifacts = D / "revisions/reference-endcards"
    for page in appendix["pages"]:
        assert sha(artifacts / page["file"]) == page["sha256"]
    final_frames = body_frames + appendix["durationInFrames"]
    publication = {
        "finalVideoFrames": final_frames,
        "referenceAppendix": {"kind": "references", "from": body_frames,
            "durationInFrames": appendix["durationInFrames"],
            "sources": "references.json", "manifest": "reference-appendix.json"},
    }
    assert render["publicationMetadata"] == publication
    assert all(render[key] == value for key, value in publication.items())
    assert render["frames"] == receipt["finalVideoFrames"] == final_frames
    assert media["passed"] is True
    assert media["bodyFrames"] == body_frames and media["finalFrames"] == final_frames
    assert media["appendedFrames"] == appendix["durationInFrames"]
    for field in ["bodyDecodedFramesAndTimestampsEqual", "outputVideoTimelineContinuous",
                  "audioPacketsAndTimingEqual"]:
        assert media[field] is True, field
    for field in ["bodyFrameMD5RowsSHA256", "audioPacketPayloadAndTimingSHA256"]:
        assert re.fullmatch(r"[a-f0-9]{64}", media[field]), field
    assert re.fullmatch(r"SHA256=[a-f0-9]{64}", media["decodedAudioPCM"])

    actual = probe(D / "video.mp4")
    video = next(stream for stream in actual["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in actual["streams"] if stream["codec_type"] == "audio")
    assert (video["width"], video["height"]) == (1920, 1080)
    assert Fraction(video["r_frame_rate"]) == fps and int(video["nb_frames"]) == final_frames
    assert audio["codec_name"] == "aac" and int(audio["sample_rate"]) == 48000
    assert abs(float(actual["format"]["duration"]) - final_frames / fps) < .1
    assert render["seconds"] == receipt["durationSeconds"] == final_frames / fps
    video_sha = sha(D / "video.mp4")
    assert video_sha == render["sha256"] == receipt["outputSHA256"] == media["outputSHA256"]
    assert (D / "video.mp4").stat().st_size == render["bytes"]
    if reviewed_sha is not None:
        assert reviewed_sha == video_sha, "Final reviewed media changed; review the actual current output"
    for label, numerator, denominator in [("16x9", 16, 9), ("4x3", 4, 3), ("3x4", 3, 4)]:
        image = next(stream for stream in probe(D / f"cover-{label}.jpg")["streams"]
                     if stream["codec_type"] == "video")
        assert image["width"] * denominator == image["height"] * numerator
    files = {name: {"sha256": sha(D / name), "bytes": (D / name).stat().st_size}
             for name in FILES}
    return draft, publication, {
        "sourceManifestSHA256": sha(D / "source-sha256.json"), "frozenInputCount": len(manifest),
        "scriptSHA256": words["scriptSha256"], "voiceSHA256": voice_sha,
        "renderResultSHA256": sha(D / "render-result.json"), "videoSHA256": video_sha,
        "reviewedVideoSHA256": reviewed_sha, "bodyFrames": body_frames,
        "frames": final_frames, "fps": fps, "captions": caption_count,
        "chapters": chapter_ids, "files": files,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="Copy the validated final site whitelist")
    parser.add_argument("--reviewed-video-sha256", help="SHA of final media actually reviewed before copying")
    parser.add_argument("--release", help="Explicit release tag; required when publishing")
    parser.add_argument("--published-at", help="Actual first-publication ISO time; defaults to invocation time")
    args = parser.parse_args()
    if args.publish:
        if not args.reviewed_video_sha256 or not re.fullmatch(r"[a-f0-9]{64}", args.reviewed_video_sha256):
            parser.error("--publish requires --reviewed-video-sha256 after completed final-media QA")
        if not args.release or not re.fullmatch(r"v\d+\.\d+\.\d+", args.release):
            parser.error("--publish requires an explicit --release vMAJOR.MINOR.PATCH")
        assert read(ROOT / "site/package.json")["version"] == args.release[1:], \
            "Set and recheck the real publication version before copying"
    draft, publication, detail = validate(args.reviewed_video_sha256)
    if not args.publish:
        print(json.dumps({"status": "read-only-validation-passed", **detail}, ensure_ascii=False, indent=2))
        return

    now = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    existing = read(DESTINATION / "meta.json") if (DESTINATION / "meta.json").exists() else None
    if existing:
        assert existing["slug"] == SLUG and existing["ep"] == 40
        for key in ["title", "episodePart", "series"]:
            assert existing[key] == draft[key], "Preserve published episode identity"
        assert existing["createdAt"] == draft["createdAt"], "Preserve original creation time"
        assert timestamp(draft["updatedAt"]) >= timestamp(existing["updatedAt"]), "Do not reset content time"
        if args.published_at and existing.get("publishedAt"):
            assert args.published_at == existing["publishedAt"], "Preserve original first-publication time"
    else:
        assert draft["updatedAt"] == draft["createdAt"], "First edition starts with creation time"
    published_at = (existing or {}).get("publishedAt") or args.published_at or now
    assert timestamp(published_at) >= timestamp(draft["createdAt"])
    if not (existing or {}).get("publishedAt"):
        assert timestamp(published_at) >= timestamp(draft["updatedAt"])
    first_release = existing["firstRelease"] if (existing or {}).get("publishedAt") else args.release
    if "firstRelease" in draft:
        assert draft["firstRelease"] == first_release, "Recheck actual first-release version before copying"
    metadata = {**draft, **publication, "draft": False, "publishedAt": published_at,
                "firstRelease": first_release, "targetDuration": round(detail["frames"] / detail["fps"])}
    allowed = {*FILES, "meta.json"}
    if DESTINATION.exists():
        assert set(path.name for path in DESTINATION.iterdir()) <= allowed, "Unexpected site files; preserve them"
    # Prepare and validate the entire copy before creating/updating the public directory.
    with tempfile.TemporaryDirectory(prefix=".site-copy-", dir=D) as temporary:
        stage = Path(temporary) / SLUG
        stage.mkdir()
        for name in FILES:
            shutil.copyfile(D / name, stage / name)
            assert sha(stage / name) == detail["files"][name]["sha256"]
        (stage / "meta.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
        subprocess.run(["node", "--input-type=module", "-e",
            "import {checkEpisode} from './site/scripts/check-references.mjs'; "
            "console.log(JSON.stringify(checkEpisode(process.argv[1])));", str(stage)], cwd=ROOT, check=True)
        DESTINATION.mkdir(parents=True, exist_ok=True)
        for name in sorted(allowed):
            shutil.copyfile(stage / name, DESTINATION / name)
            assert sha(stage / name) == sha(DESTINATION / name)
    detail["files"]["meta.json"] = {"sha256": sha(DESTINATION / "meta.json"),
                                     "bytes": (DESTINATION / "meta.json").stat().st_size}
    report = {"schemaVersion": 1, "status": "site-copy-prepared", "preparedAtBeijing": now,
        "release": args.release, "metadata": metadata, **detail,
        "source": str(D.relative_to(ROOT)), "destination": str(DESTINATION.relative_to(ROOT)),
        "publicationStatus": "Validated publishable copy prepared; live availability is checked after deployment.",
        "reviewScope": "Operator supplied the reviewed output SHA; automatic input/receipt/format identity checks do not replace visual or listening QA.",
        "exclusions": ["voice.wav", "production PNGs", "Remotion source", "dependencies"]}
    (D / "delivery-copy.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "files": len(detail["files"]),
        "videoSHA256": detail["videoSHA256"], "publishedAt": published_at,
        "firstRelease": first_release}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
