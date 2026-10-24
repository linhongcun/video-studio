"""Verify this batch only after its Release-triggered Pages run succeeds.

Usage: python3 docs/leetcode-batch-20261025/verify-online.py --deployment-run ID
Uses real complete HTTPS GETs, public GitHub data via the configured gh CLI,
canonical frozen storyboard expectations and the locally tested dist VTTs.
Does not publish, modify GitHub, retain downloaded videos or claim listening.
"""
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = 'https://linhongcun.github.io/video-studio/'
REPOSITORY = 'linhongcun/video-studio'
SPECS = [('two-sum', 1, 24, ['problem', 'lookup', 'distinct', 'code']),
         ('reverse-linked-list', 206, 28, ['problem', 'save', 'reverse', 'code']),
         ('climbing-stairs', 70, 24, ['problem', 'last-step', 'rolling', 'code'])]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


class Page(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.ids, self.attributes, self.texts = set(), [], []
        self.list_items, self.item_stack = [], []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id'):
            self.ids.add(attributes['id'])
        self.attributes.append((tag, attributes))
        if tag == 'li':
            item = {'links': []}
            self.list_items.append(item)
            self.item_stack.append(item)
        if tag == 'a':
            for item in self.item_stack:
                item['links'].append(attributes.get('href', ''))

    def handle_endtag(self, tag):
        if tag == 'li' and self.item_stack:
            self.item_stack.pop()

    def handle_data(self, data):
        self.texts.append(data)

    @property
    def text(self):
        return ''.join(self.texts)

    @property
    def links(self):
        return [attrs.get('href', '') for tag, attrs in self.attributes if tag == 'a']


def gh_api(endpoint):
    # gh supplies configured authentication without exposing it in arguments/logs.
    result = subprocess.run(['gh', 'api', endpoint], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def cue_time(stamp):
    parts = stamp.split(':')
    assert len(parts) == 3
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])


def parse_vtt(data):
    blocks = re.split(r'\r?\n\s*\r?\n', data.decode().strip())
    assert blocks.pop(0) == 'WEBVTT'
    cues = []
    for block in blocks:
        lines = block.splitlines()
        match = re.fullmatch(r'(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)', lines[0])
        assert match, lines[0]
        cues.append({'start': cue_time(match[1]), 'end': cue_time(match[2]), 'text': '\n'.join(lines[1:])})
    return cues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deployment-run', required=True, type=int, help='Successful workflow_dispatch Pages run after this Release')
    args = parser.parse_args()
    inputs = []
    for slug, problem, count, chapter_ids in SPECS:
        directory = ROOT / 'episodes' / slug
        meta, sb = read_json(directory / 'meta.json'), read_json(directory / 'storyboard.json')
        assert meta['draft'] is False, f'{slug}: canonical media must be finalized before online verification'
        assert meta['slug'] == slug and meta['problemNumber'] == problem
        assert meta['sourcePath'] == f'episodes-codex/{slug}/remotion'
        assert sb['meta']['finalVideoFrames'] == meta['finalVideoFrames']
        assert sb['meta']['unvoicedEndCard']['durationInFrames'] == 150
        assert sb['meta']['unvoicedEndCard']['from'] + 150 == meta['finalVideoFrames']
        assert [scene['chapterId'] for scene in sb['scenes']] == chapter_ids
        inputs.append((slug, problem, count, chapter_ids, directory, meta, sb))
    versions = {record[5]['firstRelease'] for record in inputs}
    assert len(versions) == 1
    tag = versions.pop()
    assert tag == 'v' + read_json(ROOT / 'site/package.json')['version']
    release = gh_api(f'repos/{REPOSITORY}/releases/tags/{tag}')
    assert release['tag_name'] == tag and not release['draft'] and release['published_at']
    release_urls = [BASE + f'episodes/{slug}/' for slug, *_ in SPECS]
    assert all(url in release['body'] for url in release_urls), 'Release body must explicitly associate all three episode URLs'
    deployment = gh_api(f'repos/{REPOSITORY}/actions/runs/{args.deployment_run}')
    assert deployment['status'] == 'completed' and deployment['conclusion'] == 'success'
    assert deployment['event'] == 'workflow_dispatch' and deployment['head_branch'] == 'main'
    assert deployment['path'] == '.github/workflows/deploy.yml'
    assert deployment['created_at'] >= release['published_at'], 'This must be the post-Release deployment'
    http_records = []

    def get(relative):
        url = BASE + relative + ('&' if '?' in relative else '?') + 'verify=' + tag
        request = urllib.request.Request(url, headers={'User-Agent': 'video-studio-batch-release-verification'})
        with urllib.request.urlopen(request, timeout=90) as response:
            assert response.status == 200, (url, response.status)
            data = response.read()
        http_records.append({'path': relative, 'bytes': len(data), 'sha256': sha(data), 'status': 200})
        return data

    episode_reports = []
    for slug, problem, count, chapter_ids, directory, meta, sb in inputs:
        files = []
        for filename in [meta['video'], meta['poster']]:
            relative = f'episodes/{slug}/{filename}'
            data = get(relative)
            local = (directory / filename).read_bytes()
            production = (ROOT / 'episodes-codex' / slug / filename).read_bytes()
            assert len(data) == len(local) and sha(data) == sha(local) == sha(production), relative
            files.append({'path': relative, 'bytes': len(data), 'sha256': sha(data), 'completeProductionCanonicalOnlineMatch': True})
        vtt_path = f'episodes/{slug}/captions.vtt'
        vtt = get(vtt_path)
        assert vtt == (ROOT / 'site/dist' / vtt_path).read_bytes(), f'{slug}: online VTT differs from validated build'
        cues = parse_vtt(vtt)
        expected = [{'text': sub['text'], 'start': (shot['from'] + sub['from']) / sb['meta']['fps'],
                     'end': (shot['from'] + sub['to'] + 1) / sb['meta']['fps']}
                    for scene in sb['scenes'] for shot in scene['shots'] for sub in shot['subtitles']]
        assert len(cues) == len(expected) == count
        for actual, wanted in zip(cues, expected):
            assert actual['text'] == wanted['text']
            assert abs(actual['start'] - wanted['start']) < 0.001
            assert abs(actual['end'] - wanted['end']) < 0.001
        card_start = sb['meta']['unvoicedEndCard']['from'] / sb['meta']['fps']
        assert all(cue['end'] <= card_start + 0.001 for cue in cues)
        assert abs(max(cue['end'] for cue in cues) - card_start) < 0.001
        page_body = get(f'episodes/{slug}/').decode()
        page = Page(page_body)
        assert meta['title'] in page.text and f'LC.{problem}' in page.text and tag in page.text
        assert f'EP.{meta["ep"]}' not in page.text
        assert f'https://github.com/{REPOSITORY}/tree/main/{meta["sourcePath"]}' in page.links
        assert set(chapter_ids) <= page.ids
        chapter_payloads = [json.loads(attrs['data-chapters']) for _, attrs in page.attributes if 'data-chapters' in attrs]
        assert len(chapter_payloads) == 1
        chapters = chapter_payloads[0]
        assert [chapter['id'] for chapter in chapters] == chapter_ids
        for chapter, scene in zip(chapters, sb['scenes']):
            assert abs(chapter['start'] - scene['from'] / sb['meta']['fps']) < 1e-9
        video_attrs = [attrs for element, attrs in page.attributes if element == 'video']
        assert len(video_attrs) == 1 and 'controls' in video_attrs[0]
        assert video_attrs[0]['poster'].endswith(f'episodes/{slug}/{meta["poster"]}')
        captions = [attrs for element, attrs in page.attributes if element == 'track' and attrs.get('kind') == 'captions']
        assert len(captions) == 1 and captions[0]['src'].endswith(vtt_path)
        episode_reports.append({'slug': slug, 'label': f'LC.{problem}', 'title': meta['title'], 'files': files,
                                'frames': meta['finalVideoFrames'], 'captions': count, 'captionsSha256': sha(vtt),
                                'exactCaptionTextAndFrameTiming': True, 'chapters': chapters,
                                'codeCardFromSeconds': card_start, 'codeCardSeconds': 5,
                                'noCueOverlapsCodeCard': True, 'nativeControls': True, 'sourceLink': meta['sourcePath']})

    home, library, series = (Page(get(path).decode()) for path in ['', 'library/', 'series/leetcode/'])
    assert 'IT小村' in home.text and tag in home.text
    assert any(link.endswith('/learn/') for link in home.links) and any(link.endswith('/library/') for link in home.links)
    for slug, problem, *_ in SPECS:
        path = f'/video-studio/episodes/{slug}/'
        assert path in home.links and path in library.links and path in series.links
        assert f'LC.{problem}' in library.text and f'LC.{problem}' in series.text
    rss = ET.fromstring(get('rss.xml'))
    items = rss.findall('./channel/item')
    for slug, problem, *_ in SPECS:
        matches = [item for item in items if item.findtext('link') == BASE + f'episodes/{slug}/']
        assert len(matches) == 1 and f'LC.{problem}' in matches[0].findtext('title')
    changelog = Page(get('changelog/').decode())
    assert tag in changelog.text and release['html_url'] in changelog.links
    # Restrict the episode link assertion to this Release's actual list item.
    release_items = [item for item in changelog.list_items if release['html_url'] in item['links']]
    assert len(release_items) == 1, 'The matching Release must appear once in the changelog'
    for slug, *_ in SPECS:
        assert f'/video-studio/episodes/{slug}/' in release_items[0]['links']
    report = {'status': 'passed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(), 'version': tag,
              'executor': 'Codex batch_publish_prep agent',
              'method': 'Actual complete HTTPS GETs and SHA-256; exact frozen caption text/frame timing; published HTML chapter payloads, source, native player, home/library/series/RSS/changelog; actual GitHub Release and post-Release Pages run APIs.',
              'release': {key: release[key] for key in ['tag_name', 'html_url', 'published_at', 'target_commitish']},
              'deployment': {key: deployment[key] for key in ['id', 'html_url', 'head_sha', 'event', 'head_branch', 'path', 'status', 'conclusion', 'created_at', 'updated_at']},
              'episodes': episode_reports, 'httpRecords': http_records,
              'allThreeInHomeLibrarySeriesRSSAndChangelog': True,
              'limits': ['HTTP delivery/document checks do not replace actual player seeking and rendered screenshot review; those are recorded in qa-site.',
                         'Caption cue absence verifies the 5-second card has no native CC text. Production PCM silence and encoded visual checks belong to per-video reports.',
                         'No human listening, word ASR, external platform publication or measured learning outcome is claimed.']}
    (OUT / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    rows = '\n'.join(f'| {episode["label"]} {episode["slug"]} | {episode["frames"]} | {episode["captions"]} | 4 | 5 |' for episode in episode_reports)
    (OUT / 'online-verification.md').write_text(f'# 三片生产站发布核验\n\n实际检查：{report["checkedAtUTC"]}，版本{tag}，结果通过。\n\n三个完整MP4和线上海报的制作目录、canonical与实际HTTPS响应完整SHA相同。线上VTT与本地已检验构建逐字节一致，并逐句核对冻结分镜文本和时间；代码卡内无cue。\n\n| 视频 | 帧数 | 字幕句数 | 章节 | 程序卡秒数 |\n| --- | ---: | ---: | ---: | ---: |\n{rows}\n\n三片页面、源码、原生播放器控件、章节载荷及首页/节目库/算法系列/RSS/更新日志均可访问。实际Release正文关联三个完整URL，发布后手动Pages运行[{deployment["id"]}]({deployment["html_url"]})成功。完整SHA、HTTP字节数和实际API状态见[机器报告](online-verification.json)。\n\n本记录是实际传输与文档核验；播放器交互、图片观看、成片声学与动态复核另见站点和各期报告。不声称全片人工听辨、逐字ASR、平台投稿或学习效果。\n')
    print(json.dumps({'status': report['status'], 'version': tag, 'deploymentRun': deployment['id'],
                      'episodes': [{'slug': entry['slug'], 'videoSha256': entry['files'][0]['sha256']} for entry in episode_reports]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
