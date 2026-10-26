"""Verify the explicitly identified Daily Temperatures problem-derived method after local QA/deployment.

Required: --revision-tag vX.Y.Z --preservation-base SHA --deployment-run ID.
Never builds, renders, publishes or infers an old publication from future main's
package version. --help writes nothing. Every real attempt retains its outcome.
"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import tarfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = 'https://linhongcun.github.io/video-studio/'
REPO = 'linhongcun/video-studio'
SLUG = 'daily-temperatures'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def git(*args, text=False):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=text)


def blob(commit, relative):
    return git('show', commit + ':' + relative)


def paths(commit, prefix):
    return git('ls-tree', '-r', '--name-only', commit, '--', prefix, text=True).splitlines()


def iso(value):
    assert isinstance(value, str) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,3})?(?:Z|[+-]\d\d:\d\d)', value), 'New dates require full ISO timestamps with timezone'
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    assert result.tzinfo is not None
    return result


class Document(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.ids, self.attrs, self.texts, self.links = set(), [], [], []
        self.items, self.item_stack, self.code_blocks = [], [], []
        self.in_pre, self.in_footer, self.in_json = False, False, False
        self.footer, self.jsonld = '', ''
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.attrs.append((tag, attrs))
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
            for item in self.item_stack:
                item['links'].append(attrs.get('href', ''))
        if tag == 'li':
            item = {'links': []}
            self.items.append(item)
            self.item_stack.append(item)
        if tag == 'pre':
            self.in_pre = True
            self.code_blocks.append('')
        if tag == 'footer':
            self.in_footer = True
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_json = True

    def handle_endtag(self, tag):
        if tag == 'li' and self.item_stack:
            self.item_stack.pop()
        if tag == 'pre':
            self.in_pre = False
        if tag == 'footer':
            self.in_footer = False
        if tag == 'script':
            self.in_json = False

    def handle_data(self, value):
        self.texts.append(value)
        if self.in_pre:
            self.code_blocks[-1] += value
        if self.in_footer:
            self.footer += value
        if self.in_json:
            self.jsonld += value

    @property
    def text(self):
        return ''.join(self.texts)


def captions(sb):
    fps = sb['meta']['fps']
    return [{'text': sub['text'], 'start': (shot['from'] + sub['from']) / fps,
             'end': (shot['from'] + sub['to'] + 1) / fps}
            for scene in sb['scenes'] for shot in scene['shots'] for sub in shot['subtitles']]


def chapters(sb):
    result = []
    for scene in sb['scenes']:
        if not result or result[-1]['id'] != scene['chapterId']:
            result.append({'id': scene['chapterId'], 'start': scene['from'] / sb['meta']['fps']})
    return result


def title_author_contract(references, receipt):
    assert references['presentation'] == receipt['presentation'] == 'title-author'
    assert receipt['layout']['kind'] == 'title-author-single-column'
    assert receipt['layout']['maxItemsPerPage'] == 4 and receipt['layout']['renderedFields'] == ['title', 'credit']
    assert receipt['layout']['quotesRendered'] is False and receipt['inputs']['secondsPerPage'] == 5
    bibliography = [{'id': source['id'], 'title': source['title'], 'credit': source.get('author', source['organization'])}
                    for source in references['sources']]
    assert all(isinstance(value, str) and value.strip() for item in bibliography for value in item.values())
    assert receipt['bibliography'] == bibliography
    return bibliography


def prefix_cue(shot, prefix, sentence):
    assert shot['subtitles'][sentence]['text'].startswith(prefix)
    frame = shot['cueFrames']['labels'][prefix]
    assert isinstance(frame, int)
    return {'prefix': prefix, 'sentence': sentence, 'appearLocalFrame': frame,
            'onsetScope': 'Sentence-prefix acoustic cue; no word-level onset is claimed.'}


def vtt_cues(body):
    blocks = re.split(r'\r?\n\s*\r?\n', body.decode().strip())
    assert blocks.pop(0) == 'WEBVTT'
    result = []
    for block in blocks:
        lines = block.splitlines()
        match = re.fullmatch(r'(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)', lines[0])
        assert match
        def seconds(stamp):
            hh, mm, ss = stamp.split(':')
            return int(hh) * 3600 + int(mm) * 60 + float(ss)
        result.append({'start': seconds(match[1]), 'end': seconds(match[2]), 'text': '\n'.join(lines[1:])})
    return result


def preserved(baseline, tag_commit, slugs):
    selected = ['episodes'] + [':(exclude)episodes/' + slug for slug in slugs]
    for revisions in [[baseline], [baseline, tag_commit]]:
        changed = git('diff', '--no-ext-diff', '--name-only', *revisions, '--', *selected, text=True).strip()
        assert not changed, 'Non-task canonical changed: ' + changed
    assert not git('ls-files', '--others', '--exclude-standard', '--', *selected, text=True).strip()
    hashes = {}
    process = subprocess.Popen(['git', 'archive', '--format=tar', baseline, 'episodes'], cwd=ROOT, stdout=subprocess.PIPE)
    with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
        for member in archive:
            if member.isdir() or any(member.name.startswith(f'episodes/{slug}/') for slug in slugs):
                continue
            if member.issym():
                expected, actual = member.linkname.encode(), os.readlink(ROOT / member.name).encode()
            else:
                expected, actual = archive.extractfile(member).read(), (ROOT / member.name).read_bytes()
            assert sha(expected) == sha(actual), member.name
            hashes[member.name] = sha(expected)
    assert process.wait() == 0
    meta_files = [name for name in hashes if re.fullmatch(r'episodes/[^/]+/meta\.json', name)]
    actual_slugs = sorted(path.parent.name for path in (ROOT / 'episodes').glob('*/meta.json') if path.parent.name not in slugs)
    assert actual_slugs == sorted(name.split('/')[1] for name in meta_files)
    return {'baselineCommit': baseline, 'allCanonicalSHA256': hashes,
            'metadata': [read(ROOT / relative) for relative in meta_files],
            'currentAndTagCanonicalUnchanged': True}


class Verify:
    def __init__(self, tag):
        self.tag, self.stage, self.http_records, self.api_records = tag, 'starting', [], []

    def api(self, endpoint):
        for attempt in range(1, 4):
            result = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True)
            if result.returncode == 0:
                parsed = json.loads(result.stdout)
                self.api_records.append({'endpoint': endpoint, 'attempt': attempt, 'parsedJSON': True})
                return parsed
            unauthorized = re.search(r'HTTP\s+401\b', result.stderr or '') is not None
            retry = unauthorized and attempt < 3
            self.api_records.append({'endpoint': endpoint, 'attempt': attempt, 'exitCode': result.returncode,
                                     'httpStatus': 401 if unauthorized else None,
                                     'retryDelaySeconds': attempt if retry else None, 'parsedJSON': False})
            if not retry:
                raise RuntimeError(f'GitHub API read failed for {endpoint} on attempt {attempt}; exit {result.returncode}, HTTP401={unauthorized}')
            time.sleep(attempt)

    def get(self, relative, expected=200):
        assert '?' not in relative
        url = BASE + relative
        request = urllib.request.Request(url, headers={'User-Agent': 'video-studio-daily-derivation-verification', 'Cache-Control': 'no-cache'})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                status, body = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, body = error.code, error.read()
        self.http_records.append({'path': relative, 'status': status, 'bytes': len(body), 'sha256': sha(body)})
        assert status == expected, f'{relative}: expected HTTP{expected}, got{status}'
        return body


def verify(args, run):
    run.stage = 'Explicit release/tag/post-release deployment identity'
    release = run.api(f'repos/{REPO}/releases/tags/{args.revision_tag}')
    assert release['tag_name'] == args.revision_tag and release['published_at'] and not release['draft']
    linked = set(re.findall(r'https://linhongcun\.github\.io/video-studio/episodes/([a-z0-9-]+)/', release['body'] or ''))
    assert linked == {SLUG}, 'This revision Release must explicitly associate Daily Temperatures only'
    ref = run.api(f'repos/{REPO}/git/ref/tags/{args.revision_tag}')
    assert ref['object']['type'] == 'tag'
    tag = run.api(f'repos/{REPO}/git/tags/{ref["object"]["sha"]}')
    assert tag['object']['type'] == 'commit'
    tagged = git('rev-parse', tag['object']['sha'] + '^{commit}', text=True).strip()
    assert 'v' + json.loads(blob(tagged, 'site/package.json'))['version'] == args.revision_tag
    deployment = run.api(f'repos/{REPO}/actions/runs/{args.deployment_run}')
    assert deployment['status'] == 'completed' and deployment['conclusion'] == 'success'
    assert deployment['event'] == 'workflow_dispatch' and deployment['head_branch'] == 'main' and deployment['path'] == '.github/workflows/deploy.yml'
    assert deployment['created_at'] >= release['published_at']
    if deployment['head_sha'] != tagged:
        comparison = run.api(f'repos/{REPO}/compare/{tagged}...{deployment["head_sha"]}')
        assert comparison['status'] in ['ahead', 'identical']
    baseline = git('rev-parse', args.preservation_base + '^{commit}', text=True).strip()
    qa = read(OUT / 'qa-site.json')
    assert qa['status'] == 'passed' and qa['revisionTag'] == args.revision_tag and qa['preservationBaseline'] == baseline and qa['slugs'] == [SLUG]
    assert qa['actualScreenshotReviewPending'] is False and qa['visualReview']['status'] == 'passed'
    run.stage = 'All non-task canonical identities'
    retained = preserved(baseline, tagged, args.slugs)
    episode_reports = []
    for slug in args.slugs:
        run.stage = slug + ': finalized identity/dates/media/captions/HTML'
        canonical, production = ROOT / 'episodes' / slug, ROOT / 'episodes-codex' / slug
        meta, sb = read(canonical / 'meta.json'), read(canonical / 'storyboard.json')
        original = json.loads(blob(baseline, f'episodes/{slug}/meta.json'))
        assert original['draft'] is False
        for key in ['slug', 'title', 'ep', 'problemNumber', 'firstRelease', 'createdAt', 'publishedAt', 'sourcePath']:
            assert meta[key] == original[key], f'{slug}: published {key} changed'
        assert meta['slug'] == SLUG and meta['ep'] == 35 and meta['problemNumber'] == 739 and meta['firstRelease'] == 'v0.69.0' and meta['firstRelease'] != args.revision_tag
        assert meta['createdAt'] == '2026-10-25T11:43:59.215+00:00' and meta['publishedAt'] == '2026-10-25T13:12:39+00:00'
        assert meta['draft'] is False and meta['series'] == 'leetcode' and meta['sourcePath'] == f'episodes-codex/{slug}/remotion'
        assert meta['title'] == read(production / 'episode-config.json')['title']
        assert iso(meta['updatedAt']) > iso(original['updatedAt'])
        rendered = read(production / 'render-result.json')
        publication = rendered['publicationMetadata']
        fps, frames, body_frames, card = sb['meta']['fps'], meta.get('finalVideoFrames', publication['finalVideoFrames']), sb['meta']['finalVideoFrames'], sb['meta']['unvoicedEndCard']
        appendix = meta['referenceAppendix']
        assert fps == 30 and frames == meta['finalVideoFrames'] and frames > body_frames
        assert card['durationInFrames'] == 150 and card['from'] + 150 == body_frames
        assert publication == {'finalVideoFrames': frames, 'referenceAppendix': appendix}
        assert appendix['kind'] == 'references' and appendix['from'] == body_frames and appendix['durationInFrames'] == 150 and appendix['from'] + 150 == frames
        references, receipt = read(canonical / appendix['sources']), read(canonical / appendix['manifest'])
        reference_media = read(canonical / 'reference-appendix-media-check.json')
        assert receipt['bodyFrames'] == body_frames and receipt['finalVideoFrames'] == frames
        assert len(receipt['appendix']['pages']) == 1 and receipt['appendix']['framesPerPage'] == 150
        assert receipt['inputs']['referencesSHA256'] == sha((canonical / appendix['sources']).read_bytes())
        assert receipt['inputs']['bodySHA256'] == sha((production / 'remotion/out/body.mp4').read_bytes())
        bibliography = title_author_contract(references, receipt)
        assert reference_media['passed'] is True and reference_media['bodySHA256'] == receipt['inputs']['bodySHA256']
        assert reference_media['outputSHA256'] == receipt['outputSHA256']
        assert all(reference_media[key] is True for key in ['bodyDecodedFramesAndTimestampsEqual', 'outputVideoTimelineContinuous', 'audioPacketsAndTimingEqual'])
        reference_evidence = []
        evidence_paths = {relative for source in references['sources']
                          for relative in [source['verification']['evidence'], source['titleEvidence']['evidence'],
                                           source.get('quotation', {}).get('evidence')] if relative}
        for relative in sorted(evidence_paths):
            current = (ROOT / relative).read_bytes()
            assert current == blob(tagged, relative)
            reference_evidence.append({'path': relative, 'sha256': sha(current)})
        checker = ROOT / 'site/scripts/check-references.mjs'
        assert checker.read_bytes() == blob(tagged, 'site/scripts/check-references.mjs')
        check_code = "import {pathToFileURL} from 'node:url'; const {checkEpisode}=await import(pathToFileURL(process.argv[2])); console.log(JSON.stringify(checkEpisode(process.argv[1])));"
        checked_references = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', check_code, str(canonical), str(checker)], text=True))
        assert checked_references['slug'] == SLUG and checked_references['sourceCount'] == len(references['sources'])
        expected, chapter_plan = captions(sb), chapters(sb)
        assert expected and len(chapter_plan) == len({chapter['id'] for chapter in chapter_plan}) == 4
        shots = [shot for scene in sb['scenes'] for shot in scene['shots']]
        assert len(shots) == 15 and len(expected) == 30
        assert [shot['visualType'] for shot in shots[:6]] == ['problem', 'output', 'repeat', 'stack-basics', 'order', 'name']
        assert shots[0]['from'] == 0
        named = next(shot for shot in shots if shot['visualType'] == 'name')
        basics = next(shot for shot in shots if shot['visualType'] == 'stack-basics')
        order = next(shot for shot in shots if shot['visualType'] == 'order')
        before_naming = ''.join(shot['narration'] for shot in shots if shot['from'] < named['from'])
        assert not re.search('单调栈|栈顶|栈底', before_naming)
        assert '更暖会解决' in basics['narration'] and '因此' in basics['narration'] and '更早留下的温度不会更低' in order['narration']
        assert named['from'] >= order['from'] + order['durationInFrames']
        method_cue = prefix_cue(named, '这些等待温度', 1)
        basics_cues = [prefix_cue(basics, '更暖会解决', 1), prefix_cue(named, '只从末尾加入和取出', 0)]
        assert all(cue['end'] <= card['from'] / fps for cue in expected)
        assert rendered['frames'] == frames and sha((production / 'render-result.json').read_bytes()) == sha(blob(tagged, f'episodes-codex/{slug}/render-result.json'))
        for name in ['meta.json', 'article.mdx', 'script.md', 'storyboard.json', meta['video'], 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg', appendix['sources'], appendix['manifest'], 'reference-appendix-media-check.json']:
            assert sha((canonical / name).read_bytes()) == sha(blob(tagged, f'episodes/{slug}/{name}'))
            if name != 'meta.json':
                assert sha((canonical / name).read_bytes()) == sha((production / name).read_bytes())
        config = read(production / 'episode-config.json')
        for name in ['solution.py', 'solution.json', config['algorithmTrace']]:
            assert sha((production / name).read_bytes()) == sha(blob(baseline, f'episodes-codex/{slug}/{name}'))
        for name in ['cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']:
            assert sha((canonical / name).read_bytes()) == sha(blob(baseline, f'episodes/{slug}/{name}'))
        local_movie = (canonical / meta['video']).read_bytes()
        assert sha(local_movie) != sha(blob(baseline, f'episodes/{slug}/{meta["video"]}')), 'Revised movie not delivered'
        assert sha(local_movie) == rendered['sha256'] and len(local_movie) == rendered['bytes']
        assert receipt['outputSHA256'] == sha(local_movie)
        qa_media = next(row for row in qa['media'] if row['slug'] == slug)
        assert qa_media['videoSha256'] == sha(local_movie) and qa_media['frames'] == frames and qa_media['cues'] == len(expected)
        media = []
        for name in [meta['video'], meta['poster']]:
            relative = f'episodes/{slug}/{name}'
            body = run.get(relative)
            assert sha(body) == sha((canonical / name).read_bytes()) == sha((production / name).read_bytes()) == sha(blob(tagged, relative))
            media.append({'path': relative, 'bytes': len(body), 'sha256': sha(body)})
        vtt_path = f'episodes/{slug}/captions.vtt'
        vtt = run.get(vtt_path)
        assert vtt == (ROOT / 'site/dist' / vtt_path).read_bytes()
        actual = vtt_cues(vtt)
        assert len(actual) == len(expected)
        for have, wanted in zip(actual, expected):
            assert have['text'] == wanted['text']
            assert abs(have['start'] - wanted['start']) < .001
            if wanted['end'] == card['from'] / fps:
                assert abs(have['end'] - (math.ceil(card['from'] / fps * 1000) - 1) / 1000) < 1e-9
            else:
                assert abs(have['end'] - wanted['end']) < .001
        assert all(cue['end'] <= card['from'] / fps for cue in actual)
        document = Document(run.get(f'episodes/{slug}/').decode())
        assert meta['title'] in document.text and f'LC.{meta["problemNumber"]}' in document.text and args.revision_tag in document.footer
        structured = json.loads(document.jsonld)
        for field, key in [('dateCreated', 'createdAt'), ('dateModified', 'updatedAt'), ('uploadDate', 'publishedAt')]:
            assert structured[field] == meta[key]
        version = iso(meta['updatedAt']).astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S 版')
        assert version in document.text and '创建于' in document.text and '修改于' in document.text
        solution = (production / 'solution.py').read_text().strip()
        assert '\n'.join(read(production / 'solution.json')['lines']).strip() == solution
        assert solution in [block.strip() for block in document.code_blocks]
        source = f'https://github.com/{REPO}/tree/main/{meta["sourcePath"]}'
        assert source in document.links and {chapter['id'] for chapter in chapter_plan} <= document.ids
        for reference in references['sources']:
            for label in ['organization', 'title']:
                assert reference[label] in document.text
            for fragment in reference['version'].split('·'):
                assert fragment.strip().replace('访问于', '访问') in document.text.replace('访问于', '访问')
            for url in [reference['url'], reference['verification'].get('sourceUrl')]:
                if url:
                    assert url in document.links
        payloads = [json.loads(attrs['data-chapters']) for _, attrs in document.attrs if 'data-chapters' in attrs]
        assert len(payloads) == 1 and [{key: chapter[key] for key in ['id', 'start']} for chapter in payloads[0]] == chapter_plan
        videos = [attrs for element, attrs in document.attrs if element == 'video']
        assert len(videos) == 1 and 'controls' in videos[0] and videos[0]['poster'].endswith(f'episodes/{slug}/{meta["poster"]}')
        assert any(element == 'track' and attrs.get('kind') == 'captions' and attrs['src'].endswith(vtt_path) for element, attrs in document.attrs)
        episode_reports.append({'slug': slug, 'problemNumber': meta['problemNumber'], 'frames': frames, 'bodyFrames': body_frames, 'fps': fps, 'cues': len(actual), 'chapters': chapter_plan, 'cardFrames': 150, 'methodCue': method_cue, 'basicsCues': basics_cues, 'referenceAppendix': appendix, 'referencePresentation': references['presentation'], 'bibliography': bibliography, 'referenceSourceIds': [ref['id'] for ref in references['sources']], 'referenceEvidence': reference_evidence, 'referenceReceiptSHA256': sha((canonical / appendix['manifest']).read_bytes()), 'referenceMediaCheckSHA256': sha((canonical / 'reference-appendix-media-check.json').read_bytes()), 'firstRelease': meta['firstRelease'], 'dates': {key: meta[key] for key in ['createdAt', 'updatedAt', 'publishedAt']}, 'media': media, 'captionsSHA256': sha(vtt), 'source': source, 'completePythonExact': True, 'methodNamedAfterProblemReasoning': True, 'firstMethodShot': 'name'})
    run.stage = 'Existing lesson home/learning/series/library/RSS and this revision Release only'
    home, learning, library, series = [Document(run.get(relative).decode()) for relative in ['', 'learn/', 'library/', 'series/leetcode/']]
    assert args.revision_tag in home.footer and '/video-studio/learn/#algorithms' in home.links
    assert 'algorithms' in learning.ids and '/video-studio/series/leetcode/' in learning.links
    for slug in args.slugs:
        href = f'/video-studio/episodes/{slug}/'
        assert href in library.links and href in series.links
    algorithm_chain = [row['slug'] for row in sorted(retained['metadata'] + [meta], key=lambda row: (row['ep'], row.get('lessonOrder', 0))) if row.get('series') == 'leetcode' and not row.get('draft') and not row.get('archived')]
    expected_hrefs = [f'/video-studio/episodes/{slug}/' for slug in algorithm_chain]
    assert [attrs['href'] for element, attrs in series.attrs if element == 'a' and 'lesson' in attrs.get('class', '').split()] == expected_hrefs
    assert all(href in library.links for href in expected_hrefs)
    rss_items = ET.fromstring(run.get('rss.xml')).findall('./channel/item')
    for episode in episode_reports:
        selected = [item for item in rss_items if item.findtext('link') == BASE + f'episodes/{episode["slug"]}/']
        assert len(selected) == 1 and f'LC.{episode["problemNumber"]}' in selected[0].findtext('title')
        assert int(parsedate_to_datetime(selected[0].findtext('pubDate')).timestamp()) == int(iso(episode['dates']['publishedAt']).timestamp())
    changelog = Document(run.get('changelog/').decode())
    items = [item for item in changelog.items if release['html_url'] in item['links']]
    assert len(items) == 1
    associated = {link for link in items[0]['links'] if re.fullmatch(r'/video-studio/episodes/[a-z0-9-]+/', link)}
    assert associated == {f'/video-studio/episodes/{SLUG}/'}
    deployment_record = {key: deployment[key] for key in ['id', 'html_url', 'head_sha', 'event', 'head_branch', 'path', 'status', 'conclusion', 'created_at', 'updated_at']}
    return {'status': 'passed', 'checkedAtUTC': now(), 'revisionTag': args.revision_tag, 'preservationBaseline': baseline, 'slugs': args.slugs,
            'release': {key: release[key] for key in ['tag_name', 'html_url', 'published_at', 'target_commitish']},
            'annotatedTag': {'tagObjectSha': ref['object']['sha'], 'commit': tagged}, 'deployment': deployment_record,
            'episodes': episode_reports, 'retained': retained, 'httpRecords': run.http_records, 'apiRecords': run.api_records,
            'changelogAssociatedOnlyDailyTemperatures': True,
            'limits': ['Only this revised film/video and its poster/VTT/page/entry routes are fetched. Other canonical bytes remain fixed through complete local/tag/baseline Git identities; no old online media are downloaded.', 'Actual player/CC/seek and viewed screenshots are recorded in local qa-site. This verifier checks serialized delivery, final media identity and reference receipts/article links. Reference-card first/middle/last pause and fullscreen are measured locally; original-source meaning review, full listening, ASR and learning outcomes are separate.', 'Original createdAt/publishedAt/firstRelease and title remain fixed; current updatedAt and supplied tag/run identify the revision. The already-closed issue is not mutated.']}



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision-tag', required=True)
    parser.add_argument('--preservation-base', required=True)
    parser.add_argument('--deployment-run', required=True, type=int)
    args = parser.parse_args()
    args.slugs = [SLUG]
    assert re.fullmatch(r'v\d+\.\d+\.\d+', args.revision_tag)
    run, started = Verify(args.revision_tag), time.monotonic()
    attempt_path = OUT / 'online-verification-attempts.json'
    history = read(attempt_path) if attempt_path.exists() else {'attempts': []}
    attempt = {'attempt': len(history['attempts']) + 1, 'status': 'running', 'startedAtUTC': now(), 'revisionTag': args.revision_tag, 'preservationBaseArgument': args.preservation_base, 'deploymentRun': args.deployment_run, 'slugs': args.slugs}
    history['attempts'].append(attempt)
    write(attempt_path, history)
    try:
        result = verify(args, run)
        write(OUT / 'online-verification.json', result)
        write(OUT / 'deployment.json', result['deployment'])
        count, total = len(run.http_records), sum(item['bytes'] for item in run.http_records)
        (OUT / 'online-verification.md').write_text(f'# 每日温度先推导再命名：生产核验\n\n实际检查{result["checkedAtUTC"]}，显式{args.revision_tag}及Release后手动run{args.deployment_run}的真实head通过，身份取tag提交而非以后main。完整MP4/海报与制作、canonical和tag SHA一致，题意与具体推导先于命名、15镜30句真实SB字幕/四章/严格代码卡边界、单页150帧资料附录、title-author原题/署名列表、来源/原题/摘录证据、制作与tag回执/图文完整资料链接、全文Python/source/原生控件与日期字段正确。标题、ep35/LC739、创建/首次公开日期及首发v0.69.0保持，仅updatedAt表示实质修改。\n\n其他canonical完整SHA及算法链保持，主页算法方向/学习入口/系列/库/RSS和本次修订Release自身li只关联Daily通过。只取本次修改片媒体，不下载旧视频。实际HTTP响应{count}次、{total}字节；逐次成败见attempts，部署见deployment.json。本地实际播放器/截图范围另见qa-site；不声称全片听辨、ASR或学习效果，原已关闭issue历史保持。\n')
        attempt.update(status='passed', finishedAtUTC=now(), seconds=round(time.monotonic() - started, 3), stage='all checks completed', httpRecords=run.http_records, apiRecords=run.api_records)
        print(json.dumps({'status': 'passed', 'revisionTag': args.revision_tag, 'HTTPResponses': count, 'bytes': total, 'media': [{'slug': item['slug'], 'videoSHA256': item['media'][0]['sha256']} for item in result['episodes']]}, ensure_ascii=False, indent=2))
    except Exception as error:
        attempt.update(status='failed', finishedAtUTC=now(), stage=run.stage, exception=type(error).__name__, message=str(error), httpRecords=run.http_records, apiRecords=run.api_records, passReportWrittenByThisAttempt=False)
        raise
    finally:
        history['status'] = f'{attempt["status"]}_on_attempt_{attempt["attempt"]}'
        write(attempt_path, history)


if __name__ == '__main__':
    main()
