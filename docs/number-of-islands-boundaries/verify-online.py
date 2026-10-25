"""Verify the released LC.200 number-of-islands boundary revision using an explicit identity.

Run only after final media, local website QA and the post-Release Pages run pass:
  python3 docs/number-of-islands-boundaries/verify-online.py \
    --revision-tag vX.Y.Z --deployment-run ID --preservation-base SHA

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
SLUG = 'number-of-islands'
OTHER_ALGORITHMS = ['container-most-water', 'longest-substring', 'binary-search',
                    'two-sum', 'reverse-linked-list', 'climbing-stairs']
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


def expected_chapters(storyboard):
    chapters = []
    for scene in storyboard['scenes']:
        if not chapters or chapters[-1]['id'] != scene['chapterId']:
            chapters.append({'id': scene['chapterId'], 'start': scene['from'] / storyboard['meta']['fps']})
    return chapters


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
    paths = ['episodes', ':(exclude)episodes/number-of-islands']
    for revision_args, label in [([baseline], 'current checkout'),
                                 ([baseline, tagged_commit], 'released tag')]:
        changed = git('diff', '--no-ext-diff', '--name-only', *revision_args,
                      '--', *paths, text=True).strip()
        assert not changed, f'Non-task canonical content changed in {label}: {changed}'
    extra = git('ls-files', '--others', '--exclude-standard', '--', *paths, text=True).strip()
    assert not extra, 'Unexpected non-task canonical content: ' + extra
    names = [name for name in git_paths(baseline, 'episodes')
             if not name.startswith('episodes/number-of-islands/')]
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
    for slug in ['monty-hall', 'agent-skills', 'adapter-pattern']:
        assert f'episodes/{slug}/meta.json' in hashes, f'Published {slug} must remain'
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
            'sixPublishedLeetCodeCompleteCanonicalSHA256': other_algorithms,
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
            'User-Agent': 'video-studio-number-of-islands-scene-verification',
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
    assert explicit_slugs == {SLUG}, 'This revision Release must explicitly associate LC.200 only'
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

    run.stage = 'Tagged/local finalized LC.200 inputs and the exact locally tested website identity'
    baseline = commit_id(args.preservation_base)
    canonical = ROOT / 'episodes' / SLUG
    production = ROOT / 'episodes-codex' / SLUG
    meta = read_json(canonical / 'meta.json')
    original = json.loads(git_bytes(baseline, f'episodes/{SLUG}/meta.json'))
    assert original['draft'] is False, 'This revision requires the already-published baseline'
    for key in ['slug', 'ep', 'problemNumber', 'firstRelease', 'publishedAt', 'sourcePath']:
        assert meta[key] == original[key], f'Published identity changed: {key}'
    assert meta['ep'] == 34 and meta['problemNumber'] == 200 and meta['firstRelease'] == 'v0.66.0'
    assert meta['firstRelease'] != tag and meta['updatedAt'] == args.revision_date
    sb = read_json(canonical / 'storyboard.json')
    config = read_json(production / 'episode-config.json')
    assert meta['slug'] == SLUG and meta['title'] == config['title'] and meta['draft'] is False and meta['series'] == 'leetcode'
    assert meta['sourcePath'] == 'episodes-codex/number-of-islands/remotion'
    fps, frames = sb['meta']['fps'], sb['meta']['finalVideoFrames']
    assert fps == 30 and isinstance(frames, int) and frames > 150 and meta['finalVideoFrames'] == frames
    card = sb['meta']['unvoicedEndCard']
    assert card['durationInFrames'] == 150 and card['from'] + 150 == frames
    chapter_plan = expected_chapters(sb)
    chapters = [chapter['id'] for chapter in chapter_plan]
    assert len(chapters) == len(set(chapters)) == 4
    assert sha((canonical / 'storyboard.json').read_bytes()) == sha((production / 'storyboard.json').read_bytes())
    expected = expected_cues(sb)
    assert expected and all(cue['start'] >= 0 and cue['end'] > cue['start'] and cue['end'] <= card['from'] / fps for cue in expected)
    narration_lines = re.findall(r'^旁白：(.+)$', (production / 'script.md').read_text(), re.M)
    script_sentences = [sentence for line in narration_lines for sentence in re.findall(r'[^。！？]+[。！？]?', line.strip())]
    assert script_sentences and len(script_sentences) == len(expected)
    assert re.sub(r'\s', '', ''.join(script_sentences)) == re.sub(r'\s', '', ''.join(cue['text'] for cue in expected))
    solution = (production / 'solution.py').read_text().strip()
    assert '\n'.join(read_json(production / 'solution.json')['lines']).strip() == solution
    rendered = read_json(production / 'render-result.json')
    assert rendered['frames'] == frames and rendered['width'] == 1920 and rendered['height'] == 1080
    assert sha((production / 'render-result.json').read_bytes()) == sha(git_bytes(tagged_commit, f'episodes-codex/{SLUG}/render-result.json'))
    for name in ['meta.json', 'article.mdx', 'script.md', 'storyboard.json', meta['video'],
                 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']:
        current = (canonical / name).read_bytes()
        assert sha(current) == sha(git_bytes(tagged_commit, f'episodes/{SLUG}/{name}')), f'Current/tagged LC.200 differs: {name}'
        if name != 'meta.json':
            source = production / name
            assert source.is_file(), f'Finalized LC.200 production input missing: {source}'
            assert sha(current) == sha(source.read_bytes()), f'Canonical/final production LC.200 differs: {name}'
    movie = (canonical / meta['video']).read_bytes()
    assert sha(movie) == rendered['sha256'] and len(movie) == rendered['bytes']
    assert sha(movie) != sha(git_bytes(baseline, f'episodes/{SLUG}/{meta["video"]}')), 'The revised final movie has not been delivered'
    for name in ['cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']:
        assert sha((canonical / name).read_bytes()) == sha(git_bytes(baseline, f'episodes/{SLUG}/{name}'))
    for name in ['solution.py', 'solution.json', 'research/demo-trace.json']:
        assert sha((production / name).read_bytes()) == sha(git_bytes(baseline, f'episodes-codex/{SLUG}/{name}'))
    qa = read_json(OUT / 'qa-site.json')
    assert qa['status'] == 'passed' and qa['revisionTag'] == tag
    assert qa['preservationBaseline'] == baseline
    qa_media = next(item for item in qa['media'] if item['slug'] == SLUG)
    assert qa_media['videoSha256'] == sha(movie) and qa_media['posterSha256'] == sha((canonical / meta['poster']).read_bytes())
    assert qa_media['frames'] == frames and qa_media['narrationCues'] == len(expected)
    retained = preserve_canonical(baseline, tagged_commit)

    run.stage = 'Complete LC.200 HTTPS media, exact frozen captions, four chapters and complete Python'
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
    assert len(cues) == len(expected)
    for actual, wanted in zip(cues, expected):
        assert actual['text'] == wanted['text']
        assert abs(actual['start'] - wanted['start']) < .001 and abs(actual['end'] - wanted['end']) < .001
    card_start = card['from'] / fps
    assert all(cue['end'] <= card_start + .001 for cue in cues)
    page = Document(run.get(f'episodes/{SLUG}/').decode())
    assert meta['title'] in page.text and 'LC.200' in page.text and tag in page.text
    assert solution in [block.strip() for block in page.code_blocks], 'Published complete Python differs from solution.py'
    source_link = f'https://github.com/{REPOSITORY}/tree/main/{meta["sourcePath"]}'
    assert source_link in page.links and set(chapters) <= page.ids
    payloads = [json.loads(attrs['data-chapters']) for _, attrs in page.attributes if 'data-chapters' in attrs]
    assert len(payloads) == 1 and [item['id'] for item in payloads[0]] == chapters
    chapter_links = [attrs for element, attrs in page.attributes
                     if element == 'a' and 'data-id' in attrs and 'data-start' in attrs]
    assert len(chapter_links) == 2 * len(chapter_plan), 'Both desktop and mobile chapter controls must exist'
    for index, (item, expected_chapter) in enumerate(zip(payloads[0], chapter_plan)):
        assert abs(item['start'] - expected_chapter['start']) < .001
        links = [attrs for attrs in chapter_links if attrs['data-id'] == item['id']]
        assert len(links) == 2
        assert {attrs['class'] for attrs in links} == {'ch', 'chip'}
        for attrs in links:
            assert abs(float(attrs['data-start']) - item['start']) < .001
            assert int(attrs['data-index']) == index
            expected_href = '#' + item['id'] if item.get('inArticle') else '#player'
            assert attrs['href'] == expected_href
    videos = [attrs for element, attrs in page.attributes if element == 'video']
    assert len(videos) == 1 and 'controls' in videos[0]
    assert videos[0]['poster'].endswith(f'episodes/{SLUG}/{meta["poster"]}')
    tracks = [attrs for element, attrs in page.attributes if element == 'track' and attrs.get('kind') == 'captions']
    assert len(tracks) == 1 and tracks[0]['src'].endswith(vtt_path)
    seconds = frames / fps
    assert f'视频 {int(seconds // 60)}:{int(seconds % 60):02}' in page.text
    episode = {'slug': SLUG, 'label': 'LC.200', 'title': meta['title'], 'frames': frames,
               'firstRelease': meta['firstRelease'], 'publishedAt': meta['publishedAt'],
               'files': media, 'captions': len(expected), 'captionsSha256': sha(vtt), 'chapters': payloads[0],
               'exactFrozenNarrationAndFrameTiming': True, 'publishedInternalEp': meta['ep'], 'productionInternalEp': config['episode'],
               'codeCardFromSeconds': card_start, 'codeCardSeconds': 5, 'noCueOverlapsCodeCard': True,
               'sourceLink': source_link, 'nativeControls': True, 'completePythonExact': True}

    run.stage = 'Home learning direction, library, algorithm series, RSS and this release changelog entry'
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
    assert len(matches) == 1 and 'LC.200' in matches[0].findtext('title')
    changelog = Document(run.get('changelog/').decode())
    assert tag in changelog.text
    items = [item for item in changelog.list_items if release['html_url'] in item['links']]
    assert len(items) == 1
    linked_episodes = {link for link in items[0]['links'] if re.fullmatch(r'/video-studio/episodes/[a-z0-9-]+/', link)}
    assert linked_episodes == {f'/video-studio/episodes/{SLUG}/'}, 'This revision changelog entry must associate LC.200 only'

    deployment_record = {key: deployment[key] for key in ['id', 'html_url', 'head_sha', 'event', 'head_branch', 'path', 'status', 'conclusion', 'created_at', 'updated_at']}
    return {'status': 'passed', 'checkedAtUTC': utc_now(), 'executor': 'Codex number-of-islands online verification',
            'revisionTag': tag, 'preservationBaseline': baseline,
            'release': {key: release[key] for key in ['tag_name', 'html_url', 'published_at', 'target_commitish']},
            'annotatedTag': {'tagObjectSha': tag_ref['object']['sha'], 'commit': tagged_commit},
            'deployment': deployment_record, 'episode': episode, 'retainedCanonical': retained,
            'httpRecords': run.http_records,
            'apiRecords': run.api_records, 'releaseChangelogAssociatedOnlyLC200': True,
            'learningEntryLibrarySeriesRSSPassed': True, 'scope': 'Only revised LC200 HTTP/player documents and its entry paths; all other canonical checked through complete local/tag Git identity, not unrelated live page audits.',
            'limits': ['Complete HTTP/document and identity checks do not replace rendered-scene review, narration listening or measured learning outcomes.',
                       'Actual player playback, captions and chapter seeking are recorded in local qa-site; this verifier checks serialized HTML/VTT and complete delivered bytes.',
                       'Non-task production MP4 paths are neither required nor recreated. Retained identity comes from actual canonical/Git bytes.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision-tag', required=True, help='Exact released revision tag; never inferred from current main package.json')
    parser.add_argument('--deployment-run', required=True, type=int, help='Successful post-Release workflow_dispatch deploy.yml run')
    parser.add_argument('--preservation-base', required=True, help='Final upstream commit whose non-task canonical content must remain exact')
    parser.add_argument('--revision-date', default='2026-10-25', help='Expected actual LC.200 revision updatedAt date')
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
            f'# LC.200 边界说明修订：线上核验\n\n实际检查：{report["checkedAtUTC"]}。'
            f'显式修订{args.revision_tag}通过；实际[手动部署]({report["deployment"]["html_url"]})'
            f'head为`{report["deployment"]["head_sha"]}`，与附注tag绑定，不读取未来main版本。\n\n'
            f'正式修订片{report["episode"]["frames"]}帧/{report["episode"]["captions"]}句；完整线上MP4/海报与制作、canonical及tag SHA一致，'
            'VTT逐句/帧时、四章、完整Python、原生控件/source和5秒无cue卡正确，修订Release自己的li只关联LC200。'
            'ep34/LC200/首发v0.66.0与原发布日期保留，当前tag/updatedAt表示此次修订。\n\n'
            f'其他canonical、七片系列顺序及P05已发表状态按保留基线`{report["preservationBaseline"]}`保持；'
            '本次不重复覆盖无关课程线上页面。三封面和程序/trace保留，算法方向、系列/库/RSS入口正确。'
            f'本次读取{count}次完整HTTPS响应、{total}字节。实际成败见[attempts](online-verification-attempts.json)，'
            '报告见[online-verification.json](online-verification.json)及[deployment.json](deployment.json)。'
            '不声称全片听辨、ASR、用户认可或学习效果。\n')

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
