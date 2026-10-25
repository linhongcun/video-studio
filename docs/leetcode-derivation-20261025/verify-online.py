"""Verify this five-video revision only after its Release-triggered Pages run succeeds.

Usage: python3 docs/leetcode-derivation-20261025/verify-online.py --deployment-run ID
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
BASELINE_COMMIT = 'e38fa9236fbc340f834581302320494d2a1c1ce7'
UPSTREAM_COMMIT = '057b9d0d293ff58f410129860b71b742340e5dd1'
REVISION_DATE = '2026-10-25'
SPECS = [('two-sum', 1, 28), ('longest-substring', 3, 40),
         ('binary-search', 704, 30), ('reverse-linked-list', 206, 30),
         ('container-most-water', 11, 44)]
ALGORITHM_SLUGS = ['container-most-water', 'longest-substring', 'binary-search', 'two-sum', 'reverse-linked-list', 'climbing-stairs']
TASK_SHARED_PATHS = ['episodes-codex/_shared/remix_approach.py', 'episodes-codex/_shared/test_remix_approach.py', 'episodes-codex/_template/README.md']



def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def git_bytes(relative, commit=BASELINE_COMMIT):
    return subprocess.check_output(['git', 'show', commit + ':' + relative], cwd=ROOT)


def original_meta(slug):
    return json.loads(git_bytes(f'episodes/{slug}/meta.json'))


def preserve_climbing_stairs():
    prefix = 'episodes/climbing-stairs/'
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE_COMMIT, '--', prefix], cwd=ROOT, text=True).splitlines()
    actual = sorted(str(p.relative_to(ROOT)) for p in (ROOT / prefix).rglob('*') if p.is_file())
    assert actual == sorted(paths), 'Retained LC.70 canonical file set changed'
    files = {}
    for relative in paths:
        expected = sha(git_bytes(relative))
        assert sha((ROOT / relative).read_bytes()) == expected, relative
        files[relative] = expected
    return {'baselineCommit': BASELINE_COMMIT, 'allCanonicalFilesSHA256': files}


def preserve_upstream():
    excluded = [prefix + slug for slug, *_ in SPECS for prefix in ['episodes/', 'episodes-codex/']] + TASK_SHARED_PATHS
    paths = ['episodes', 'episodes-codex'] + [':(exclude)' + path for path in excluded]
    changed = subprocess.check_output(['git', 'diff', '--no-ext-diff', '--name-only', UPSTREAM_COMMIT, '--', *paths], cwd=ROOT, text=True)
    assert not changed.strip(), 'Non-task upstream episode content changed: ' + changed
    extra = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', *paths], cwd=ROOT, text=True)
    assert not extra.strip(), 'Unexpected non-task episode content: ' + extra
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', UPSTREAM_COMMIT, '--', 'episodes', 'episodes-codex'], cwd=ROOT, text=True).splitlines()
    names = [name for name in names if name not in TASK_SHARED_PATHS and not any(name.startswith(prefix + slug + '/') for slug, *_ in SPECS for prefix in ['episodes/', 'episodes-codex/'])]
    meta_paths = [name for name in names if re.fullmatch(r'episodes/[^/]+/meta\.json', name)]
    actual_slugs = sorted(path.parent.name for path in (ROOT / 'episodes').glob('*/meta.json') if path.parent.name not in [spec[0] for spec in SPECS])
    assert actual_slugs == sorted(relative.split('/')[1] for relative in meta_paths)
    episodes = []
    for relative in meta_paths:
        slug = relative.split('/')[1]
        meta = json.loads(git_bytes(relative, UPSTREAM_COMMIT))
        expected_files = sorted(name for name in names if name.startswith(f'episodes/{slug}/'))
        # Ignored local node_modules/caches in historical canonical trees are
        # outside the published tracked content checked by git diff above.
        assert sha((ROOT / relative).read_bytes()) == sha(git_bytes(relative, UPSTREAM_COMMIT)), slug
        episodes.append({'slug': slug, 'title': meta['title'], 'series': meta.get('series'), 'frames': meta.get('finalVideoFrames'), 'fileCount': len(expected_files), 'metaSha256': sha((ROOT / relative).read_bytes())})
    return {'baselineCommit': UPSTREAM_COMMIT, 'trackedCanonicalAndProductionFiles': len(names),
            'exactTrackedBytesUnchanged': True, 'taskSharedFilesExcluded': TASK_SHARED_PATHS, 'canonicalEpisodes': episodes}


def expected_recent_hrefs():
    metas = [read_json(path) for path in sorted((ROOT / 'episodes').glob('*/meta.json'))]
    metas = [meta for meta in metas if not meta.get('draft') and not meta.get('archived')]
    metas.sort(key=lambda meta: (str(meta['publishedAt']), meta.get('ep', 0), meta.get('lessonOrder', 0)), reverse=True)
    return [f'/video-studio/episodes/{meta["slug"]}/' for meta in metas[:6]]


def expected_series_pager(slug):
    current = read_json(ROOT / 'episodes' / slug / 'meta.json')
    metas = [read_json(path) for path in sorted((ROOT / 'episodes').glob('*/meta.json'))]
    lessons = [meta for meta in metas if not meta.get('draft') and not meta.get('archived') and meta.get('series') == current['series']]
    lessons.sort(key=lambda meta: (meta.get('ep', 0), meta.get('lessonOrder', 0)))
    index = next(index for index, lesson in enumerate(lessons) if lesson['slug'] == slug)
    return [f'/video-studio/episodes/{lessons[position]["slug"]}/' for position in [index - 1, index + 1] if 0 <= position < len(lessons)]


def actual_pager_hrefs(html):
    matches = re.findall(r'<nav\b[^>]*class="[^"]*\bpager\b[^"]*"[^>]*>(.*?)</nav>', html, re.S)
    assert len(matches) <= 1
    return Page(matches[0]).links if matches else []


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
    for slug, problem, count in SPECS:
        directory = ROOT / 'episodes' / slug
        meta, sb = read_json(directory / 'meta.json'), read_json(directory / 'storyboard.json')
        assert meta['draft'] is False, f'{slug}: canonical media must be finalized before online verification'
        assert meta['slug'] == slug and meta['problemNumber'] == problem
        assert meta['sourcePath'] == f'episodes-codex/{slug}/remotion'
        original = original_meta(slug)
        assert meta['firstRelease'] == original['firstRelease'] and meta['publishedAt'] == original['publishedAt']
        assert meta['updatedAt'] == REVISION_DATE
        assert sha((directory / 'storyboard.json').read_bytes()) == sha((ROOT / 'episodes-codex' / slug / 'storyboard.json').read_bytes())
        rendered = read_json(ROOT / 'episodes-codex' / slug / 'render-result.json')
        assert rendered['sha256'] == sha((directory / meta['video']).read_bytes())
        assert rendered['frames'] == meta['finalVideoFrames']
        assert sb['meta']['finalVideoFrames'] == meta['finalVideoFrames']
        assert sb['meta']['unvoicedEndCard']['durationInFrames'] == 150
        assert sb['meta']['unvoicedEndCard']['from'] + 150 == meta['finalVideoFrames']
        chapter_ids = [scene['chapterId'] for scene in sb['scenes']]
        assert len(chapter_ids) == len(set(chapter_ids)) == 4
        inputs.append((slug, problem, count, chapter_ids, directory, meta, sb))
    assert sum(record[2] for record in inputs) == 172
    retained = preserve_climbing_stairs()
    upstream = preserve_upstream()
    tag = 'v' + read_json(ROOT / 'site/package.json')['version']
    assert all(record[5]['firstRelease'] != tag for record in inputs), 'Use the actual patch tag, not a historical debut'
    release = gh_api(f'repos/{REPOSITORY}/releases/tags/{tag}')
    assert release['tag_name'] == tag and not release['draft'] and release['published_at']
    release_urls = [BASE + f'episodes/{slug}/' for slug, *_ in SPECS]
    assert all(url in release['body'] for url in release_urls), 'Release body must explicitly associate all five revised episode URLs'
    deployment = gh_api(f'repos/{REPOSITORY}/actions/runs/{args.deployment_run}')
    assert deployment['status'] == 'completed' and deployment['conclusion'] == 'success'
    assert deployment['event'] == 'workflow_dispatch' and deployment['head_branch'] == 'main'
    assert deployment['path'] == '.github/workflows/deploy.yml'
    assert deployment['created_at'] >= release['published_at'], 'This must be the post-Release deployment'
    tag_ref = gh_api(f'repos/{REPOSITORY}/git/ref/tags/{tag}')
    assert tag_ref['object']['type'] == 'tag', 'Release must use an annotated tag'
    tag_object = gh_api(f'repos/{REPOSITORY}/git/tags/{tag_ref["object"]["sha"]}')
    assert tag_object['object']['type'] == 'commit'
    tagged_commit = tag_object['object']['sha']
    if tagged_commit != deployment['head_sha']:
        comparison = gh_api(f'repos/{REPOSITORY}/compare/{tagged_commit}...{deployment["head_sha"]}')
        assert comparison['status'] in ['ahead', 'identical'], 'The deployment does not include the tagged revision'
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

    climb_dir = ROOT / 'episodes/climbing-stairs'
    climb_meta = read_json(climb_dir / 'meta.json')
    climb_sb = read_json(climb_dir / 'storyboard.json')
    assert climb_meta['finalVideoFrames'] == 4779
    retained_files = []
    for name in [climb_meta['video'], climb_meta['poster']]:
        path = f'episodes/climbing-stairs/{name}'
        body = get(path)
        assert sha(body) == sha((climb_dir / name).read_bytes()) == sha((ROOT / 'episodes-codex/climbing-stairs' / name).read_bytes())
        retained_files.append({'path': path, 'sha256': sha(body), 'bytes': len(body)})
    climb_vtt = get('episodes/climbing-stairs/captions.vtt')
    assert climb_vtt == (ROOT / 'site/dist/episodes/climbing-stairs/captions.vtt').read_bytes()
    previous_climb = next(e for e in read_json(ROOT / 'docs/leetcode-batch-20261025/online-verification.json')['episodes'] if e['slug'] == 'climbing-stairs')
    assert sha(climb_vtt) == previous_climb['captionsSha256']
    assert len(parse_vtt(climb_vtt)) == 24
    climb_page = Page(get('episodes/climbing-stairs/').decode())
    assert climb_meta['title'] in climb_page.text and 'LC.70' in climb_page.text
    assert any(element == 'video' and 'controls' in attrs for element, attrs in climb_page.attributes)
    retained.update(files=retained_files, captionsSha256=sha(climb_vtt), captionCount=24, pageAccessible=True)
    puzzle_dir = ROOT / 'episodes/horse-racing'
    puzzle_meta = read_json(puzzle_dir / 'meta.json')
    assert puzzle_meta == json.loads(git_bytes('episodes/horse-racing/meta.json', UPSTREAM_COMMIT)), 'Keep latest-main P01 metadata'
    puzzle_video = get('episodes/horse-racing/' + puzzle_meta['video'])
    assert sha(puzzle_video) == sha((puzzle_dir / puzzle_meta['video']).read_bytes()) == sha((ROOT / 'episodes-codex/horse-racing' / puzzle_meta['video']).read_bytes())
    assert sha(puzzle_video) == sha(git_bytes('episodes/horse-racing/' + puzzle_meta['video'], UPSTREAM_COMMIT))
    puzzle_html = get('episodes/horse-racing/').decode()
    puzzle_page = Page(puzzle_html)
    assert puzzle_meta['title'] in puzzle_page.text and 'P01' in puzzle_page.text
    assert any(element == 'video' and 'controls' in attrs for element, attrs in puzzle_page.attributes)
    assert actual_pager_hrefs(puzzle_html) == expected_series_pager('horse-racing')
    preserved_p01 = {'baselineCommit': UPSTREAM_COMMIT, 'frames': puzzle_meta['finalVideoFrames'], 'videoSha256': sha(puzzle_video), 'bytes': len(puzzle_video), 'pageAccessible': True, 'pagerHrefs': actual_pager_hrefs(puzzle_html)}
    bridge_dir = ROOT / 'episodes/bridge-torch'
    bridge_meta = read_json(bridge_dir / 'meta.json')
    assert bridge_meta == json.loads(git_bytes('episodes/bridge-torch/meta.json', UPSTREAM_COMMIT))
    bridge_files = []
    for filename in [bridge_meta['video'], bridge_meta['poster']]:
        relative = 'episodes/bridge-torch/' + filename
        body = get(relative)
        assert sha(body) == sha((bridge_dir / filename).read_bytes()) == sha((ROOT / 'episodes-codex/bridge-torch' / filename).read_bytes()) == sha(git_bytes(relative, UPSTREAM_COMMIT))
        bridge_files.append({'path': relative, 'sha256': sha(body), 'bytes': len(body)})
    bridge_html = get('episodes/bridge-torch/').decode()
    bridge_page = Page(bridge_html)
    assert bridge_meta['title'] in bridge_page.text and 'P02' in bridge_page.text
    assert any(element == 'video' and 'controls' in attrs for element, attrs in bridge_page.attributes)
    assert actual_pager_hrefs(bridge_html) == expected_series_pager('bridge-torch')
    upstream['preservedP02'] = {'frames': bridge_meta['finalVideoFrames'], 'files': bridge_files, 'pageAccessible': True, 'pagerHrefs': actual_pager_hrefs(bridge_html)}
    home, library, series = (Page(get(path).decode()) for path in ['', 'library/', 'series/leetcode/'])
    assert 'IT小村' in home.text and tag in home.text
    assert any(link.endswith('/learn/') for link in home.links) and any(link.endswith('/library/') for link in home.links)
    for slug, problem, *_ in SPECS:
        path = f'/video-studio/episodes/{slug}/'
        assert path in library.links and path in series.links
        assert f'LC.{problem}' in library.text and f'LC.{problem}' in series.text
    assert '/video-studio/learn/#algorithms' in home.links
    assert '/video-studio/episodes/container-most-water/' in home.links
    for href in expected_recent_hrefs():
        assert href in home.links, 'Latest upstream lesson disappeared from home: ' + href
    learning = Page(get('learn/').decode())
    assert 'algorithms' in learning.ids and '/video-studio/series/leetcode/' in learning.links
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
    revised_links = {f'/video-studio/episodes/{slug}/' for slug, *_ in SPECS}
    actual_algorithm_links = {link for link in release_items[0]['links'] if any(link == f'/video-studio/episodes/{slug}/' for slug in ALGORITHM_SLUGS)}
    assert actual_algorithm_links == revised_links, 'The patch changelog entry must associate the five revised videos only'
    report = {'status': 'passed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(), 'version': tag,
              'executor': 'Codex derive_site agent',
              'method': 'Actual complete HTTPS GETs and SHA-256; exact frozen caption text/frame timing; published HTML chapter payloads, source, native player, learning entry/library/series/RSS/changelog; actual GitHub Release and post-Release Pages run APIs.',
              'release': {key: release[key] for key in ['tag_name', 'html_url', 'published_at', 'target_commitish']},
              'deployment': {key: deployment[key] for key in ['id', 'html_url', 'head_sha', 'event', 'head_branch', 'path', 'status', 'conclusion', 'created_at', 'updated_at']},
              'episodes': episode_reports, 'httpRecords': http_records, 'retainedClimbingStairs': retained, 'preservedP01': preserved_p01, 'retainedUpstream': upstream,
              'originalFirstReleases': {record[0]: record[5]['firstRelease'] for record in inputs},
              'annotatedTag': {'tagObjectSha': tag_ref['object']['sha'], 'commit': tagged_commit},
              'allFiveInLibrarySeriesRSSAndPatchChangelog': True, 'homeAlgorithmDirectionAndStartAvailable': True,
              'limits': ['HTTP delivery/document checks do not replace actual player seeking and rendered screenshot review; those are recorded in qa-site. Homepage keeps original publication dates and six recent cards; all five are reachable through the algorithm direction/library.',
                         'Caption cue absence verifies the 5-second card has no native CC text. Production PCM silence and encoded visual checks belong to per-video reports.',
                         'No human listening, word ASR, external platform publication or measured learning outcome is claimed.']}
    (OUT / 'online-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    rows = '\n'.join(f'| {episode["label"]} {episode["slug"]} | {episode["frames"]} | {episode["captions"]} | 4 | 5 |' for episode in episode_reports)
    deployment_record = {key: deployment[key] for key in ['id', 'html_url', 'head_sha', 'event', 'head_branch', 'path', 'status', 'conclusion', 'created_at', 'updated_at']}
    (OUT / 'deployment.json').write_text(json.dumps(deployment_record, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'online-verification.md').write_text(f'# 五片思路推导修订：生产站核验\n\n实际检查：{report["checkedAtUTC"]}，补丁版本{tag}，结果通过。\n\n五片完整MP4和海报的制作、canonical与实际HTTPS响应完整SHA相同。线上VTT与已检验dist逐字节相同，172句逐句文字/时间均对应冻结分镜，5秒代码卡内无cue。\n\n| 视频 | 帧数 | 字幕句数 | 章节 | 程序卡秒数 |\n| --- | ---: | ---: | ---: | ---: |\n{rows}\n\n首发版本/日期保留，本次按实际新补丁Release核验。每页四章、源码、原生控件及资料库/算法系列/RSS可访问；首页算法方向及入门入口可达，保留最近6条的原排序规则。本次Release正文显式关联五片完整URL，线上该Release自己的li恰好关联这五条算法修订。\n\nLC.70全部9个canonical文件与Git基线逐字节保持，线上视频/海报/VTT一致，P01按最新上游基线{UPSTREAM_COMMIT}保留{preserved_p01["frames"]}帧短版完整媒体；其余{len(upstream["canonicalEpisodes"])}个非本任务canonical目录及上游制作输入保持。Release后实际手动Pages运行[{deployment["id"]}]({deployment["html_url"]})成功。完整SHA、HTTP记录与部署API状态见[机器报告](online-verification.json)、[部署记录](deployment.json)。\n\n本记录是完整传输与文档核验；实际播放器交互/截图、成片声学/动态另见各自报告，不声称全片听辨、逐字ASR、外部平台投稿或学习效果。\n')
    print(json.dumps({'status': report['status'], 'version': tag, 'deploymentRun': deployment['id'],
                      'episodes': [{'slug': entry['slug'], 'videoSha256': entry['files'][0]['sha256']} for entry in episode_reports]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
