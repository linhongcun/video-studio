"""Check A02 only after its Release and successful post-Release Pages deployment.

python3 episodes-codex/agent-tool-execution/check-online.py --deployment-run ID

Performs ordinary canonical HTTPS GETs without cache-busting query parameters.
Compares complete media/VTT bytes with canonical, production and built outputs.
Reads public release/deployment identity through the configured gh CLI; never
publishes or changes GitHub. The default report stays in ignored remotion/out.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import urllib.request
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = Path(__file__).resolve().parent
SLUG = "agent-tool-execution"
CANONICAL = ROOT / "episodes" / SLUG
DIST = ROOT / "site" / "dist"
BASE = "https://linhongcun.github.io/video-studio/"
PREFIX = "/video-studio/"
REPOSITORY = "linhongcun/video-studio"
CHAPTER_IDS = ["hook", "execute", "deny", "recap"]
CHAPTER_FRAMES = [0, 241, 2031, 2899]
LESSON_PATHS = [PREFIX + "episodes/agent-intro/", PREFIX + f"episodes/{SLUG}/"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


class Node:
    def __init__(self, tag="root", attrs=None):
        self.tag, self.attrs = tag, dict(attrs or [])
        self.children, self.data = [], []

    def descendants(self, tag=None, css_class=None):
        for child in self.children:
            if (tag is None or child.tag == tag) and (
                css_class is None or css_class in child.attrs.get("class", "").split()
            ):
                yield child
            yield from child.descendants(tag, css_class)

    @property
    def text(self):
        return "".join(self.data) + "".join(child.text for child in self.children)

    @property
    def links(self):
        return [node.attrs.get("href", "") for node in self.descendants("a")]


class Page(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].data.append(data)


def one(nodes, label):
    nodes = list(nodes)
    assert len(nodes) == 1, f"Expected one {label}, got {len(nodes)}"
    return nodes[0]


def gh_api(endpoint):
    result = subprocess.run(["gh", "api", endpoint], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def cue_seconds(stamp):
    hours, minutes, seconds = stamp.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_vtt(data):
    blocks = re.split(r"\r?\n\s*\r?\n", data.decode().strip())
    assert blocks.pop(0) == "WEBVTT"
    cues = []
    for block in blocks:
        lines = block.splitlines()
        match = re.fullmatch(r"(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)", lines[0])
        assert match, lines[0]
        cues.append({"start": cue_seconds(match[1]), "end": cue_seconds(match[2]), "text": "\n".join(lines[1:])})
    return cues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deployment-run", type=int, required=True)
    parser.add_argument("--out", type=Path, default=PRODUCTION / "remotion/out/online-verification.json")
    args = parser.parse_args()
    meta = read_json(CANONICAL / "meta.json")
    sb = read_json(CANONICAL / "storyboard.json")
    assert meta["draft"] is False, "Finalize the canonical episode before online checks"
    assert meta["slug"] == SLUG and meta["ep"] == 28 and meta["series"] == "agent"
    assert meta["platforms"] == {} and meta["related"] == ["agent-intro"]
    assert meta["productionIssue"] == 132
    assert meta["sourcePath"] == f"episodes-codex/{SLUG}/remotion"
    assert sb["meta"]["finalVideoFrames"] == meta["finalVideoFrames"] == 3305
    assert sb["meta"]["fps"] == 30
    assert [scene["chapterId"] for scene in sb["scenes"]] == CHAPTER_IDS
    assert [scene["from"] for scene in sb["scenes"]] == CHAPTER_FRAMES
    assert (CANONICAL / "storyboard.json").read_bytes() == (PRODUCTION / "storyboard.json").read_bytes()
    tag = meta["firstRelease"]
    assert tag == "v" + read_json(ROOT / "site/package.json")["version"]

    release = gh_api(f"repos/{REPOSITORY}/releases/tags/{tag}")
    assert release["tag_name"] == tag and not release["draft"] and not release["prerelease"]
    assert release["published_at"]
    explicit_slugs = set(re.findall(r"https://linhongcun\.github\.io/video-studio/episodes/([a-z0-9-]+)/?(?=[#?\s)<>\"\]]|$)", release["body"]))
    assert explicit_slugs == {SLUG}, f"Release must explicitly associate only A02, found {explicit_slugs}"
    assert re.search(r"(?:第\s*28\s*期|EP\.?\s*28\b)", release["name"]), "Release title must identify the actual new episode"
    reference = gh_api(f"repos/{REPOSITORY}/git/ref/tags/{tag}")
    assert reference["object"]["type"] == "tag", "Expected the repository's annotated release tag"
    tag_object = gh_api(f"repos/{REPOSITORY}/git/tags/{reference['object']['sha']}")
    assert tag_object["object"]["type"] == "commit"
    tag_commit = tag_object["object"]["sha"]
    deployment = gh_api(f"repos/{REPOSITORY}/actions/runs/{args.deployment_run}")
    assert deployment["status"] == "completed" and deployment["conclusion"] == "success"
    assert deployment["event"] == "workflow_dispatch" and deployment["head_branch"] == "main"
    assert deployment["path"] == ".github/workflows/deploy.yml"
    assert deployment["head_sha"] == tag_commit
    assert datetime.fromisoformat(deployment["created_at"].replace("Z", "+00:00")) >= datetime.fromisoformat(release["published_at"].replace("Z", "+00:00"))
    http_records = []

    def get(relative):
        url = BASE + relative
        request = urllib.request.Request(url, headers={"User-Agent": "video-studio-a02-public-verification"})
        with urllib.request.urlopen(request, timeout=60) as response:
            assert response.status == 200, (url, response.status)
            assert response.geturl() == url, f"Unexpected redirect: {url} -> {response.geturl()}"
            data = response.read()
        http_records.append({"url": url, "path": relative, "status": 200, "bytes": len(data), "sha256": sha(data), "normalCanonicalGET": True})
        return data

    assets = []
    for filename in [meta["video"], meta["poster"]]:
        relative = f"episodes/{SLUG}/{filename}"
        data = get(relative)
        copies = {"production": (PRODUCTION / filename).read_bytes(), "canonical": (CANONICAL / filename).read_bytes(), "dist": (DIST / relative).read_bytes()}
        assert all(data == local for local in copies.values()), relative
        assets.append({"path": relative, "bytes": len(data), "sha256": sha(data), "productionCanonicalDistOnlineCompleteMatch": True})

    vtt_path = f"episodes/{SLUG}/captions.vtt"
    vtt = get(vtt_path)
    assert vtt == (DIST / vtt_path).read_bytes(), "Published VTT differs from the validated build"
    cues = parse_vtt(vtt)
    expected_cues = [{"text": sub["text"], "start": (shot["from"] + sub["from"]) / 30, "end": (shot["from"] + sub["to"] + 1) / 30}
                     for scene in sb["scenes"] for shot in scene["shots"] for sub in shot["subtitles"]]
    assert len(cues) == len(expected_cues) == 22
    for actual, expected in zip(cues, expected_cues):
        assert actual["text"] == expected["text"]
        assert abs(actual["start"] - expected["start"]) < 0.001
        assert abs(actual["end"] - expected["end"]) < 0.001

    page = Page(get(f"episodes/{SLUG}/").decode()).root
    assert meta["title"] in page.text and "EP.28" in page.text and tag in page.text
    assert one(page.descendants("h1"), "episode h1").text == meta["title"]
    assert f"https://github.com/{REPOSITORY}/tree/main/{meta['sourcePath']}" in page.links
    assert set(CHAPTER_IDS) <= {node.attrs.get("id") for node in page.descendants()}
    player = one((node for node in page.descendants() if "data-chapters" in node.attrs), "chapter payload")
    chapters = json.loads(player.attrs["data-chapters"])
    assert [chapter["id"] for chapter in chapters] == CHAPTER_IDS
    for chapter, frame in zip(chapters, CHAPTER_FRAMES):
        assert abs(chapter["start"] - frame / 30) < 1e-9
        for link in player.descendants("a"):
            if link.attrs.get("data-id") == chapter["id"]:
                assert abs(float(link.attrs["data-start"]) - frame / 30) < 1e-9
    video = one(player.descendants("video"), "native video")
    assert "controls" in video.attrs and video.attrs["poster"] == PREFIX + f"episodes/{SLUG}/{meta['poster']}"
    assert one(video.descendants("source"), "video source").attrs["src"] == PREFIX + f"episodes/{SLUG}/{meta['video']}"
    assert one(video.descendants("track"), "caption track").attrs["src"] == PREFIX + vtt_path
    directory = one((node for node in page.descendants("details") if node.attrs.get("id") == "course-directory"), "course directory")
    assert directory.links == LESSON_PATHS
    pager = one((node for node in page.descendants("nav") if node.attrs.get("aria-label") == "上一课 / 下一课"), "lesson pager")
    assert pager.links == [LESSON_PATHS[0]], "A02 must point back to A01 without crossing into another direction"
    previous = Page(get("episodes/agent-intro/").decode()).root
    previous_pager = one((node for node in previous.descendants("nav") if node.attrs.get("aria-label") == "上一课 / 下一课"), "A01 pager")
    assert previous_pager.links == [LESSON_PATHS[1]], "A01 must point forward to A02"
    series = Page(get("series/agent/").decode()).root
    assert [node.attrs["href"] for node in series.descendants("a", "lesson")] == LESSON_PATHS
    assert "已发布 2 篇" in series.text
    home = Page(get("").decode()).root
    library = Page(get("library/").decode()).root
    assert "IT小村" in home.text and tag in home.text and meta["title"] in home.text
    assert LESSON_PATHS[1] in home.links and LESSON_PATHS[1] in library.links
    rss = ET.fromstring(get("rss.xml"))
    items = [item for item in rss.findall("./channel/item") if item.findtext("link") == BASE + f"episodes/{SLUG}/"]
    assert len(items) == 1 and meta["title"] in items[0].findtext("title")

    changelog = Page(get("changelog/").decode()).root
    release_items = [item for item in changelog.descendants("li") if release["html_url"] in item.links]
    release_item = one(release_items, "actual release entry")
    assert tag in release_item.text
    chips = one(release_item.descendants("p", "eps"), "release's episode chips")
    assert chips.links == [LESSON_PATHS[1]], "This Release must associate A02 alone, without other EP or LeetCode courses"
    assert "EP.28" in chips.text and "LC." not in chips.text

    now = datetime.now(timezone.utc)
    report = {
        "status": "passed", "checkedAtUTC": now.isoformat(), "checkedAtBeijing": now.astimezone(ZoneInfo("Asia/Shanghai")).isoformat(),
        "executor": "Codex a02_site agent", "slug": SLUG, "episode": 28, "version": tag,
        "method": "Ordinary canonical HTTPS GETs without cache-busting parameters; complete production/canonical/dist/online asset equality; exact frozen subtitle text and frame timing; published HTML chapters, navigation and release chips; actual Release, annotated tag and successful post-Release Pages workflow APIs.",
        "assets": assets, "captions": {"count": 22, "bytes": len(vtt), "sha256": sha(vtt), "matchesValidatedDist": True, "exactFrozenTextAndTiming": True},
        "frames": 3305, "fps": 30, "durationSeconds": 3305 / 30, "chapters": chapters,
        "sourcePath": meta["sourcePath"], "nativeVideoControls": True,
        "agentCourseOrder": LESSON_PATHS, "bidirectionalA01A02Pager": True,
        "homeLibrarySeriesRSS": True, "releaseChipsOnlyThisEpisode": True,
        "release": {key: release[key] for key in ["tag_name", "html_url", "published_at", "target_commitish"]},
        "annotatedTagCommit": tag_commit,
        "deployment": {key: deployment[key] for key in ["id", "html_url", "head_sha", "event", "head_branch", "path", "status", "conclusion", "created_at", "updated_at"]},
        "httpRecords": http_records,
        "limits": ["HTTP and document checks do not replace real browser playback/seeking or rendered image review, which are recorded separately.", "No full human listening, word-level ASR, live model inference, production order access, external platform publishing or measured learning outcomes is claimed."]
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "passed", "version": tag, "deploymentRun": deployment["id"], "videoSha256": assets[0]["sha256"], "checkedAtBeijing": report["checkedAtBeijing"], "report": str(args.out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
