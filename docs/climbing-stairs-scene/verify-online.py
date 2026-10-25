"""Verify the released LC.70 staircase-scene revision using an explicit identity.

Run only after final media, local website QA and the post-Release Pages run pass:
  python3 docs/climbing-stairs-scene/verify-online.py \
    --revision-tag vX.Y.Z --deployment-run ID [--preservation-base SHA]

This reads GitHub APIs and complete HTTPS responses. It never builds, renders,
fetches Git refs, publishes, recreates missing production media or reads the
current package version as the identity of an earlier release. Each real run is
recorded in online-verification-attempts.json; successful runs additionally write
online-verification.json/.md and deployment.json. --help writes no reports.
"""
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = 'https://linhongcun.github.io/video-studio/'
REPOSITORY = 'linhongcun/video-studio'
DEFAULT_BASELINE = 'bb9b4e9782ed4b7b2d12a8fac9fd478193febfb8'
SLUG = 'climbing-stairs'
OTHER_ALGORITHMS = ['container-most-water', 'longest-substring', 'binary-search',
                    'two-sum', 'reverse-linked-list']
ALGORITHM_CHAIN = OTHER_ALGORITHMS + [SLUG]
RETIRED_AGENTS = ['agent-intro', 'agent-tool-execution']
RETIRED_PRODUCTION = ['agent-intro', 'agent-intro-v2', 'agent-intro-v3', 'agent-tool-execution']


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def git(*args, text=False):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=text)


def commit_id(value):
    return git('rev-parse', '--verify', value + '^{commit}', text=True).strip()


def git_bytes(commit, relative):
    return git('show', commit + ':' + relative)


def git_paths(commit, prefix):
    return git('ls-tree', '-r', '--name-only', commit, '--', prefix, text=True).splitlines()


class Document(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.ids, self.attributes, self.texts = set(), [], []
        self.list_items, self.item_stack = [], []
        self.code_blocks, self.code_depth = [], 0
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.attributes.append((tag, attrs))
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'li':
            item = {'links': []}
            self.list_items.append(item)
            self.item_stack.append(item)
        if tag == 'a':
            for item in self.item_stack:
                item['links'].append(attrs.get('href', ''))
        if tag == 'pre':
            self.code_depth += 1
            self.code_blocks.append('')

    def handle_endtag(self, tag):
        if tag == 'li' and self.item_stack:
            self.item_stack.pop()
        if tag == 'pre':
            self.code_depth -= 1

    def handle_data(self, data):
        self.texts.append(data)
        if self.code_depth:
            self.code_blocks[-1] += data

    @property
    def text(self):
        return ''.join(self.texts)

    @property
    def links(self):
        return [attrs.get('href', '') for tag, attrs in self.attributes if tag == 'a']


def expected_cues(storyboard):
    fps = storyboard['meta']['fps']
    return [{'text': sub['text'], 'start': (shot['from'] + sub['from']) / fps,
             'end': (shot['from'] + sub['to'] + 1) / fps}
            for scene in storyboard['scenes'] for shot in scene['shots']
            for sub in shot['subtitles']]


def stamp_seconds(stamp):
    hh, mm, ss = stamp.split(':')
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


def parse_vtt(body):
    blocks = re.split(r'\r?\n\s*\r?\n', body.decode().strip())
    assert blocks.pop(0) == 'WEBVTT'
    cues = []
    for block in blocks:
        lines = block.splitlines()
        match = re.fullmatch(r'(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)', lines[0])
        assert match, lines[0]
        cues.append({'start': stamp_seconds(match[1]), 'end': stamp_seconds(match[2]),
                     'text': '\n'.join(lines[1:])})
    return cues


def preserve_canonical(baseline, tagged_commit):
    """Check tracked current/tag bytes; ignored local caches are not site content."""
    paths = ['episodes', ':(exclude)episodes/climbing-stairs']
    for revision_args, label in [([baseline], 'current checkout'),
                                 ([baseline, tagged_commit], 'released tag')]:
        changed = git('diff', '--no-ext-diff', '--name-only', *revision_args,
                      '--', *paths, text=True).strip()
        assert not changed, f'Non-task canonical content changed in {label}: {changed}'
    extra = git('ls-files', '--others', '--exclude-standard', '--', *paths, text=True).strip()
    assert not extra, 'Unexpected non-task canonical content: ' + extra
    names = [name for name in git_paths(baseline, 'episodes')
             if not name.startswith('episodes/climbing-stairs/')]
    actual_slugs = sorted(path.parent.name for path in (ROOT / 'episodes').glob('*/meta.json')
                          if path.parent.name != SLUG)
    expected_slugs = sorted(name.split('/')[1] for name in names
                            if re.fullmatch(r'episodes/[^/]+/meta\.json', name))
    assert actual_slugs == expected_slugs
    for slug in RETIRED_AGENTS:
        assert slug not in actual_slugs and not (ROOT / 'episodes' / slug / 'meta.json').exists()
    for slug in RETIRED_PRODUCTION:
        prefix = f'episodes-codex/{slug}'
        assert not git('ls-files', '--', prefix, text=True).strip(), f'Retired production restored in current tree: {prefix}'
        assert not git_paths(tagged_commit, prefix), f'Retired production restored in release tag: {prefix}'
    hashes = {name: sha((ROOT / name).read_bytes()) for name in names}
    other_algorithms = {}
    for slug in OTHER_ALGORITHMS:
        selected = [name for name in names if name.startswith(f'episodes/{slug}/')]
        assert selected, slug
        for name in selected:
            assert hashes[name] == sha(git_bytes(baseline, name)) == sha(git_bytes(tagged_commit, name)), name
        other_algorithms[slug] = {name: hashes[name] for name in selected}
    return {'preservationBaseline': baseline, 'releasedTagCommit': tagged_commit,
            'canonicalEpisodeSlugs': expected_slugs, 'canonicalTrackedFiles': len(names),
            'currentAndReleasedTrackedBytesUnchanged': True,
            'allRetainedCanonicalSHA256': hashes,
            'fiveOtherLeetCodeCompleteCanonicalSHA256': other_algorithms,
            'retiredAgentCanonicalMetadataAbsent': RETIRED_AGENTS,
            'retiredAgentProductionTrackedPathsAbsent': RETIRED_PRODUCTION}


class Verification:
    def __init__(self):
        self.stage = 'starting'
        self.http_records = []
        self.api_records = []

    def api(self, endpoint):
        result = subprocess.run(['gh', 'api', endpoint], check=True, capture_output=True, text=True)
        value = json.loads(result.stdout)
        self.api_records.append({'endpoint': endpoint, 'parsedJSON': True})
        return value

    def get(self, relative, expected_status=200):
        url = BASE + relative
        request = urllib.request.Request(url, headers={
            'User-Agent': 'video-studio-climbing-stairs-scene-verification',
            'Cache-Control': 'no-cache'})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                status, data = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, data = error.code, error.read()
        self.http_records.append({'path': relative, 'url': url, 'status': status,
                                  'bytes': len(data), 'sha256': sha(data)})
        assert status == expected_status, f'{url}: expected HTTP {expected_status}, got {status}'
        return data


def verify(args, run):
    run.stage = 'Release, annotated tag and successful post-Release deployment identity'
    tag = args.revision_tag
    assert re.fullmatch(r'v\d+\.\d+\.\d+', tag), 'Use an explicit complete revision tag'
    release = run.api(f'repos/{REPOSITORY}/releases/tags/{tag}')
    assert release['tag_name'] == tag and not release['draft'] and release['published_at']
    explicit_slugs = set(re.findall(r'https://linhongcun\.github\.io/video-studio/episodes/([a-z0-9-]+)/', release['body'] or ''))
    assert explicit_slugs == {SLUG}, 'This patch Release must explicitly associate LC.70 only'
    tag_ref = run.api(f'repos/{REPOSITORY}/git/ref/tags/{tag}')
    assert tag_ref['object']['type'] == 'tag', 'An annotated tag is required'
    tag_object = run.api(f'repos/{REPOSITORY}/git/tags/{tag_ref["object"]["sha"]}')
    assert tag_object['object']['type'] == 'commit'
    tagged_commit = commit_id(tag_object['object']['sha'])
    tagged_package = json.loads(git_bytes(tagged_commit, 'site/package.json'))
    assert 'v' + tagged_package['version'] == tag, 'The release tag must identify the version actually built in that tagged commit'
    deployment = run.api(f'repos/{REPOSITORY}/actions/runs/{args.deployment_run}')
    assert deployment['status'] == 'completed' and deployment['conclusion'] == 'success'
    assert deployment['event'] == 'workflow_dispatch' and deployment['head_branch'] == 'main'
    assert deployment['path'] == '.github/workflows/deploy.yml'
    assert deployment['created_at'] >= release['published_at'], 'Deployment must start after this Release'
    if deployment['head_sha'] != tagged_commit:
        compare = run.api(f'repos/{REPOSITORY}/compare/{tagged_commit}...{deployment["head_sha"]}')
        assert compare['status'] in ['ahead', 'identical'], 'The deployment does not contain this revision tag'

    run.stage = 'Tagged/local finalized LC.70 inputs and the exact locally tested website identity'
    baseline = commit_id(args.preservation_base)
    canonical = ROOT / 'episodes' / SLUG
    production = ROOT / 'episodes-codex' / SLUG
    meta = read_json(canonical / 'meta.json')
    sb = read_json(canonical / 'storyboard.json')
    original_meta = json.loads(git_bytes(baseline, f'episodes/{SLUG}/meta.json'))
    assert meta['slug'] == SLUG and meta['ep'] == 27 and meta['problemNumber'] == 70
    assert meta['draft'] is False and meta['series'] == 'leetcode'
    assert meta['sourcePath'] == 'episodes-codex/climbing-stairs/remotion'
    assert meta['firstRelease'] == original_meta['firstRelease'] == 'v0.57.0'
    assert meta['publishedAt'] == original_meta['publishedAt'] == '2026-10-25'
    assert meta['updatedAt'] == args.revision_date and meta['firstRelease'] != tag
    assert sb['meta']['fps'] == 30 and sb['meta']['finalVideoFrames'] == meta['finalVideoFrames'] == 4779
    card = sb['meta']['unvoicedEndCard']
    assert card['durationInFrames'] == 150 and card['from'] + 150 == 4779
    chapters = [scene['chapterId'] for scene in sb['scenes']]
    assert len(chapters) == len(set(chapters)) == 4
    assert sha((canonical / 'storyboard.json').read_bytes()) == sha((production / 'storyboard.json').read_bytes())
    expected = expected_cues(sb)
    original_sb = json.loads(git_bytes(baseline, f'episodes/{SLUG}/storyboard.json'))
    assert len(expected) == 24 and expected == expected_cues(original_sb), 'The original 24 sentence texts and frame timing must remain exact'
    assert all(cue['end'] <= card['from'] / 30 for cue in expected)
    assert max(cue['end'] for cue in expected) == card['from'] / 30
    solution = (production / 'solution.py').read_text().strip()
    assert solution == git_bytes(baseline, f'episodes-codex/{SLUG}/solution.py').decode().strip()
    rendered = read_json(production / 'render-result.json')
    assert rendered['frames'] == 4779
    assert sha((production / 'render-result.json').read_bytes()) == sha(git_bytes(tagged_commit, f'episodes-codex/{SLUG}/render-result.json'))
    for name in ['meta.json', 'article.mdx', 'script.md', 'storyboard.json', meta['video'],
                 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']:
        current = (canonical / name).read_bytes()
        assert sha(current) == sha(git_bytes(tagged_commit, f'episodes/{SLUG}/{name}')), f'Current/tagged LC.70 differs: {name}'
        if name != 'meta.json':
            source = production / name
            assert source.is_file(), f'Finalized LC.70 production input missing: {source}'
            assert sha(current) == sha(source.read_bytes()), f'Canonical/final production LC.70 differs: {name}'
    movie = (canonical / meta['video']).read_bytes()
    assert sha(movie) == rendered['sha256'] and len(movie) == rendered['bytes']
    assert sha(movie) != sha(git_bytes(baseline, f'episodes/{SLUG}/{meta["video"]}')), 'The old video has not been replaced'
    assert sha((canonical / meta['poster']).read_bytes()) != sha(git_bytes(baseline, f'episodes/{SLUG}/{meta["poster"]}')), 'The old poster has not been replaced'
    qa = read_json(OUT / 'qa-site.json')
    assert qa['status'] == 'passed' and qa['revisionTag'] == tag
    assert qa['preservationBaseline'] == baseline
    qa_media = next(item for item in qa['media'] if item['slug'] == SLUG)
    assert qa_media['videoSha256'] == sha(movie)
    retained = preserve_canonical(baseline, tagged_commit)

    run.stage = 'Complete LC.70 HTTPS media, exact 24 captions, four chapters and complete Python'
    media = []
    for name in [meta['video'], meta['poster']]:
        relative = f'episodes/{SLUG}/{name}'
        body = run.get(relative)
        assert sha(body) == sha((canonical / name).read_bytes()) == sha((production / name).read_bytes())
        assert sha(body) == sha(git_bytes(tagged_commit, relative))
        media.append({'path': relative, 'bytes': len(body), 'sha256': sha(body),
                      'completeOnlineCanonicalProductionAndTagMatch': True})
    vtt_path = f'episodes/{SLUG}/captions.vtt'
    vtt = run.get(vtt_path)
    assert vtt == (ROOT / 'site/dist' / vtt_path).read_bytes(), 'Online captions differ from the tested dist'
    cues = parse_vtt(vtt)
    assert len(cues) == len(expected) == 24
    for actual, wanted in zip(cues, expected):
        assert actual['text'] == wanted['text']
        assert abs(actual['start'] - wanted['start']) < .001 and abs(actual['end'] - wanted['end']) < .001
    card_start = card['from'] / 30
    assert all(cue['end'] <= card_start + .001 for cue in cues)
    page = Document(run.get(f'episodes/{SLUG}/').decode())
    assert meta['title'] in page.text and 'LC.70' in page.text and tag in page.text
    assert solution in [block.strip() for block in page.code_blocks], 'Published complete Python differs from solution.py'
    source_link = f'https://github.com/{REPOSITORY}/tree/main/{meta["sourcePath"]}'
    assert source_link in page.links and set(chapters) <= page.ids
    payloads = [json.loads(attrs['data-chapters']) for _, attrs in page.attributes if 'data-chapters' in attrs]
    assert len(payloads) == 1 and [item['id'] for item in payloads[0]] == chapters
    chapter_links = {attrs['data-id']: attrs for element, attrs in page.attributes
                     if element == 'a' and 'data-id' in attrs and 'data-start' in attrs}
    for item, scene in zip(payloads[0], sb['scenes']):
        assert abs(item['start'] - scene['from'] / 30) < .001
        assert abs(float(chapter_links[item['id']]['data-start']) - item['start']) < .001
        assert chapter_links[item['id']]['href'] == '#' + item['id']
    videos = [attrs for element, attrs in page.attributes if element == 'video']
    assert len(videos) == 1 and 'controls' in videos[0]
    assert videos[0]['poster'].endswith(f'episodes/{SLUG}/{meta["poster"]}')
    tracks = [attrs for element, attrs in page.attributes if element == 'track' and attrs.get('kind') == 'captions']
    assert len(tracks) == 1 and tracks[0]['src'].endswith(vtt_path)
    seconds = 4779 / 30
    assert f'视频 {int(seconds // 60)}:{int(seconds % 60):02}' in page.text
    episode = {'slug': SLUG, 'label': 'LC.70', 'title': meta['title'], 'frames': 4779,
               'firstRelease': meta['firstRelease'], 'publishedAt': meta['publishedAt'],
               'files': media, 'captions': 24, 'captionsSha256': sha(vtt), 'chapters': payloads[0],
               'exactOriginalNarrationAndFrameTimingPreserved': True,
               'codeCardFromSeconds': card_start, 'codeCardSeconds': 5, 'noCueOverlapsCodeCard': True,
               'sourceLink': source_link, 'nativeControls': True, 'completePythonExact': True}

    run.stage = 'Five retained LeetCode videos/posters through complete canonical HTTPS responses'
    retained_http = []
    for slug in OTHER_ALGORITHMS:
        other = read_json(ROOT / 'episodes' / slug / 'meta.json')
        for name in [other['video'], other['poster']]:
            relative = f'episodes/{slug}/{name}'
            body = run.get(relative)
            assert sha(body) == retained['allRetainedCanonicalSHA256'][relative]
            retained_http.append({'path': relative, 'bytes': len(body), 'sha256': sha(body)})

    run.stage = 'Home learning direction, library, algorithm series, RSS and this patch changelog entry'
    home, learning, library, series = (Document(run.get(path).decode())
                                       for path in ['', 'learn/', 'library/', 'series/leetcode/'])
    assert tag in home.text and '/video-studio/learn/#algorithms' in home.links
    assert '/video-studio/episodes/container-most-water/' in home.links
    assert 'algorithms' in learning.ids and '/video-studio/series/leetcode/' in learning.links
    for slug in ALGORITHM_CHAIN:
        href = f'/video-studio/episodes/{slug}/'
        assert href in series.links and href in library.links
    rss_body = run.get('rss.xml')
    rss_items = ET.fromstring(rss_body).findall('./channel/item')
    matches = [item for item in rss_items if item.findtext('link') == BASE + f'episodes/{SLUG}/']
    assert len(matches) == 1 and 'LC.70' in matches[0].findtext('title')
    changelog = Document(run.get('changelog/').decode())
    assert tag in changelog.text
    items = [item for item in changelog.list_items if release['html_url'] in item['links']]
    assert len(items) == 1
    linked_episodes = {link for link in items[0]['links'] if re.fullmatch(r'/video-studio/episodes/[a-z0-9-]+/', link)}
    assert linked_episodes == {f'/video-studio/episodes/{SLUG}/'}, 'The patch changelog entry must associate LC.70 only'

    run.stage = 'Retired Agent pages/media remain absent; no active navigation or RSS link restores them'
    for slug in RETIRED_AGENTS:
        retired = f'/video-studio/episodes/{slug}/'
        assert all(retired not in doc.links for doc in [home, learning, library, series])
        assert all(item.findtext('link') != BASE + f'episodes/{slug}/' for item in rss_items)
        for suffix in ['', 'video.mp4', 'cover-16x9.jpg', 'captions.vtt']:
            run.get(f'episodes/{slug}/' + suffix, expected_status=404)

    deployment_record = {key: deployment[key] for key in ['id', 'html_url', 'head_sha', 'event', 'head_branch', 'path', 'status', 'conclusion', 'created_at', 'updated_at']}
    return {'status': 'passed', 'checkedAtUTC': utc_now(), 'executor': 'Codex stairs online verification agent',
            'revisionTag': tag, 'preservationBaseline': baseline,
            'release': {key: release[key] for key in ['tag_name', 'html_url', 'published_at', 'target_commitish']},
            'annotatedTag': {'tagObjectSha': tag_ref['object']['sha'], 'commit': tagged_commit},
            'deployment': deployment_record, 'episode': episode, 'retainedCanonical': retained,
            'fiveRetainedLeetCodeHTTPMedia': retained_http, 'httpRecords': run.http_records,
            'apiRecords': run.api_records, 'patchChangelogAssociatedOnlyLC70': True,
            'learningEntryLibrarySeriesRSSPassed': True, 'retiredAgentURLsStill404': True,
            'limits': ['Complete HTTP/document and identity checks do not replace rendered-scene review, narration listening or measured learning outcomes.',
                       'Actual player playback, captions and chapter seeking are recorded in local qa-site; this verifier checks serialized HTML/VTT and complete delivered bytes.',
                       'Non-task production MP4 paths are neither required nor recreated. Retained identity comes from actual canonical/Git bytes.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision-tag', required=True, help='Exact released revision tag; never inferred from current main package.json')
    parser.add_argument('--deployment-run', required=True, type=int, help='Successful post-Release workflow_dispatch deploy.yml run')
    parser.add_argument('--preservation-base', default=DEFAULT_BASELINE, help='Final upstream commit whose non-task canonical content must remain exact')
    parser.add_argument('--revision-date', default='2026-10-25', help='Expected actual LC.70 meta.updatedAt date')
    args = parser.parse_args()
    run, started = Verification(), time.monotonic()
    attempts_path = OUT / 'online-verification-attempts.json'
    history = read_json(attempts_path) if attempts_path.exists() else {'attempts': []}
    attempt = {'attempt': len(history['attempts']) + 1, 'status': 'running', 'startedAtUTC': utc_now(),
               'revisionTag': args.revision_tag, 'deploymentRun': args.deployment_run,
               'preservationBaseArgument': args.preservation_base}
    history['attempts'].append(attempt)
    history['status'] = 'running'
    write_json(attempts_path, history)
    try:
        report = verify(args, run)
        write_json(OUT / 'online-verification.json', report)
        write_json(OUT / 'deployment.json', report['deployment'])
        count, total = len(run.http_records), sum(item['bytes'] for item in run.http_records)
        (OUT / 'online-verification.md').write_text(
            f'# LC.70 楼梯场景返工：线上核验\n\n'
            f'实际检查：{report["checkedAtUTC"]}。显式修订 {args.revision_tag}，结果通过；'
            f'实际[手动部署]({report["deployment"]["html_url"]})的 head 为 `{report["deployment"]["head_sha"]}`，'
            '与本次附注标签身份核对，没有用后来 main 的 package 版本替代。\n\n'
            'LC.70 完整视频/海报与正式制作、canonical和标签完整SHA一致；4779帧，'
            '原24句文字及帧时保留，四章、源码、完整Python、原生控件和5秒无cue静卡均通过。'
            '首页算法方向经学习入口可达系列和资料库，RSS正确；该补丁自身更新日志仅关联LC.70。\n\n'
            f'其余canonical与基线 `{report["preservationBaseline"]}` 保持；五条其他LeetCode逐文件完整SHA及其线上视频/海报一致。'
            f'撤下的两期Agent页面/视频/海报/字幕仍为404。本次完成 {count} 次完整HTTPS响应读取、{total} 字节。\n\n'
            '机器记录见[online-verification.json](online-verification.json)，部署记录见[deployment.json](deployment.json)，'
            '每次真实运行的成功/失败及到达阶段见[attempts](online-verification-attempts.json)。'
            '本记录不声称全片听辨、ASR、用户认可或学习效果；实际本地播放器交互和截图范围另见qa-site。\n')
        attempt.update(status='passed', finishedAtUTC=utc_now(), seconds=round(time.monotonic() - started, 3),
                       stage='all checks completed', httpRecords=run.http_records, apiRecords=run.api_records,
                       passReport='online-verification.json')
        history['status'] = 'passed_on_attempt_' + str(attempt['attempt'])
        print(json.dumps({'status': 'passed', 'revisionTag': args.revision_tag,
                          'deploymentRun': args.deployment_run, 'completeHTTPResponses': count,
                          'responseBytes': total, 'videoSha256': report['episode']['files'][0]['sha256']}, ensure_ascii=False, indent=2))
    except Exception as error:
        attempt.update(status='failed', finishedAtUTC=utc_now(), seconds=round(time.monotonic() - started, 3),
                       stage=run.stage, exception=type(error).__name__, message=str(error),
                       httpRecords=run.http_records, apiRecords=run.api_records, passReportWritten=False)
        history['status'] = 'failed_on_attempt_' + str(attempt['attempt'])
        raise
    finally:
        write_json(attempts_path, history)


if __name__ == '__main__':
    main()
