"""Verify one explicitly identified three-film publication after local QA/deployment.

Required: --slugs a,b,c --revision-tag vX.Y.Z --preservation-base SHA --deployment-run ID.
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
        assert not changed, 'Non-batch canonical changed: ' + changed
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
        body = subprocess.check_output(['gh', 'api', endpoint], text=True)
        parsed = json.loads(body)
        self.api_records.append({'endpoint': endpoint, 'parsedJSON': True})
        return parsed

    def get(self, relative, expected=200):
        url = BASE + relative + ('&' if '?' in relative else '?') + 'verify=' + self.tag
        request = urllib.request.Request(url, headers={'User-Agent': 'video-studio-leetcode-batch-verification', 'Cache-Control': 'no-cache'})
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
    assert linked == set(args.slugs), 'This release must explicitly associate exactly the three selected films'
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
    publication_preservation = qa.get('publicationPreservation')
    qa_baseline = publication_preservation['baselineCommit'] if publication_preservation else qa['preservationBaseline']
    assert qa['status'] == 'passed' and qa['revisionTag'] == args.revision_tag and qa_baseline == baseline and set(qa['slugs']) == set(args.slugs)
    if publication_preservation:
        evidence_path = publication_preservation['reportPath']
        evidence_bytes = (ROOT / evidence_path).read_bytes()
        assert sha(evidence_bytes) == publication_preservation['reportSHA256']
        assert blob(tagged, evidence_path) == evidence_bytes
        evidence = json.loads(evidence_bytes)
        assert evidence['status'] == 'passed' and evidence['previousBaseline'] == qa['preservationBaseline']
        assert evidence['upstreamCommit'] == baseline
        assert evidence['siteInputPathsChanged'] == evidence['frozenInputPathsChanged'] == []
        assert evidence['canonicalDelta'] == ['episodes/observer-pattern/online-verification.json']
        git('merge-base', '--is-ancestor', baseline, tagged)
    assert qa['actualScreenshotReviewPending'] is False and qa['visualReview']['status'] == 'passed'
    run.stage = 'All non-batch canonical identities'
    retained = preserved(baseline, tagged, args.slugs)
    episode_reports = []
    for slug in args.slugs:
        run.stage = slug + ': finalized identity/dates/media/captions/HTML'
        canonical, production = ROOT / 'episodes' / slug, ROOT / 'episodes-codex' / slug
        meta, sb = read(canonical / 'meta.json'), read(canonical / 'storyboard.json')
        assert paths(baseline, f'episodes/{slug}') == [f'episodes/{slug}/meta.json']
        reserved = json.loads(blob(baseline, f'episodes/{slug}/meta.json'))
        assert reserved['draft'] is True and 'publishedAt' not in reserved
        for key in ['slug', 'ep', 'problemNumber', 'firstRelease', 'createdAt', 'sourcePath']:
            assert meta[key] == reserved[key], f'{slug}: reserved {key} changed'
        assert meta['draft'] is False and meta['series'] == 'leetcode' and meta['sourcePath'] == f'episodes-codex/{slug}/remotion'
        assert meta['title'] == read(production / 'episode-config.json')['title']
        assert iso(meta['updatedAt']) >= iso(reserved['updatedAt']) >= iso(meta['createdAt'])
        assert iso(meta['publishedAt']) >= iso(meta['createdAt'])
        fps, frames, card = sb['meta']['fps'], sb['meta']['finalVideoFrames'], sb['meta']['unvoicedEndCard']
        assert fps == 30 and frames == meta['finalVideoFrames'] and frames > 150
        assert card['durationInFrames'] == 150 and card['from'] + 150 == frames
        expected, chapter_plan = captions(sb), chapters(sb)
        assert expected and len(chapter_plan) == len({chapter['id'] for chapter in chapter_plan}) == 4
        assert all(cue['end'] <= card['from'] / fps for cue in expected)
        rendered = read(production / 'render-result.json')
        assert rendered['frames'] == frames and sha((production / 'render-result.json').read_bytes()) == sha(blob(tagged, f'episodes-codex/{slug}/render-result.json'))
        transform_path = OUT / 'derived-articles/derive.cjs'
        article_derivation = json.loads(subprocess.check_output(['node', str(transform_path), '--check', slug, str(canonical / 'article.mdx')], text=True))
        for relative in article_derivation.get('artifacts', [str(transform_path.relative_to(ROOT))]):
            assert sha((ROOT / relative).read_bytes()) == sha(blob(tagged, relative)), relative
        for name in ['meta.json', 'article.mdx', 'script.md', 'storyboard.json', meta['video'], 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']:
            assert sha((canonical / name).read_bytes()) == sha(blob(tagged, f'episodes/{slug}/{name}'))
            if name not in ['meta.json', 'article.mdx']:
                assert sha((canonical / name).read_bytes()) == sha((production / name).read_bytes())
        local_movie = (canonical / meta['video']).read_bytes()
        assert sha(local_movie) == rendered['sha256'] and len(local_movie) == rendered['bytes']
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
        payloads = [json.loads(attrs['data-chapters']) for _, attrs in document.attrs if 'data-chapters' in attrs]
        assert len(payloads) == 1 and [{key: chapter[key] for key in ['id', 'start']} for chapter in payloads[0]] == chapter_plan
        videos = [attrs for element, attrs in document.attrs if element == 'video']
        assert len(videos) == 1 and 'controls' in videos[0] and videos[0]['poster'].endswith(f'episodes/{slug}/{meta["poster"]}')
        assert any(element == 'track' and attrs.get('kind') == 'captions' and attrs['src'].endswith(vtt_path) for element, attrs in document.attrs)
        episode_reports.append({'slug': slug, 'problemNumber': meta['problemNumber'], 'frames': frames, 'fps': fps, 'cues': len(actual), 'chapters': chapter_plan, 'cardFrames': 150, 'firstRelease': meta['firstRelease'], 'dates': {key: meta[key] for key in ['createdAt', 'updatedAt', 'publishedAt']}, 'media': media, 'captionsSHA256': sha(vtt), 'source': source, 'completePythonExact': True, 'articleDerivation': article_derivation})
    run.stage = 'Two retained films: only corrected VTT endpoints, no old movie downloads'
    boundary_audit = read(OUT / 'site-qa/vtt-boundary-audit.json')
    assert set(boundary_audit['changed']) == {'climbing-stairs', 'reverse-linked-list', 'permutations'}
    assert boundary_audit['generatedBuiltVTTMatched'] is True and boundary_audit['unchangedCount'] == 42
    local_boundaries = read(OUT / 'site-qa/retained-card-boundaries.json')
    assert local_boundaries['status'] == 'passed' and {row['slug'] for row in local_boundaries['rows']} == {'climbing-stairs', 'reverse-linked-list'}
    assert all(not sample['activeCues'] for row in local_boundaries['rows'] for sample in row['samples'])
    retained_caption_checks = []
    for slug in ['climbing-stairs', 'reverse-linked-list']:
        relative = f'episodes/{slug}/captions.vtt'
        online = run.get(relative)
        assert online == (ROOT / 'site/dist' / relative).read_bytes()
        audit = next(row for row in boundary_audit['rows'] if row['slug'] == slug)
        original = (OUT / f'site-qa/vtt-boundary-before/{slug}.vtt').read_bytes()
        assert sha(online) == audit['correctedSHA256'] and sha(original) == audit['previousSHA256']
        before, after = vtt_cues(original), vtt_cues(online)
        assert len(before) == len(after) and len(audit['changes']) == 1
        changed = []
        sb = read(ROOT / 'episodes' / slug / 'storyboard.json')
        boundary = sb['meta']['unvoicedEndCard']['from'] / sb['meta']['fps']
        endpoint = (math.ceil(boundary * 1000) - 1) / 1000
        for i, (old, new) in enumerate(zip(before, after)):
            assert old['text'] == new['text'] and old['start'] == new['start']
            if old['end'] != new['end']:
                assert abs(old['end'] - boundary) < 1e-9 and abs(new['end'] - endpoint) < 1e-9
                assert abs(old['end'] - new['end'] - .001) < 1e-9
                changed.append(i + 1)
        assert changed == [audit['changes'][0]['cue']]
        retained_caption_checks.append({'slug': slug, 'bytes': len(online), 'sha256': sha(online), 'onlyChangedCue': changed[0], 'previousEndpoint': boundary, 'publishedEndpoint': endpoint, 'allTextStartsAndOtherEndsUnchanged': True})
    run.stage = 'Batch home/learning/series/library/RSS and this release only'
    home, learning, library, series = [Document(run.get(relative).decode()) for relative in ['', 'learn/', 'library/', 'series/leetcode/']]
    assert args.revision_tag in home.footer and '/video-studio/learn/#algorithms' in home.links
    assert 'algorithms' in learning.ids and '/video-studio/series/leetcode/' in learning.links
    for slug in args.slugs:
        href = f'/video-studio/episodes/{slug}/'
        assert href in home.links and href in library.links and href in series.links
    rss_items = ET.fromstring(run.get('rss.xml')).findall('./channel/item')
    for episode in episode_reports:
        selected = [item for item in rss_items if item.findtext('link') == BASE + f'episodes/{episode["slug"]}/']
        assert len(selected) == 1 and f'LC.{episode["problemNumber"]}' in selected[0].findtext('title')
        assert int(parsedate_to_datetime(selected[0].findtext('pubDate')).timestamp()) == int(iso(episode['dates']['publishedAt']).timestamp())
    changelog = Document(run.get('changelog/').decode())
    items = [item for item in changelog.items if release['html_url'] in item['links']]
    assert len(items) == 1
    associated = {link for link in items[0]['links'] if re.fullmatch(r'/video-studio/episodes/[a-z0-9-]+/', link)}
    assert associated == {f'/video-studio/episodes/{slug}/' for slug in args.slugs}
    run.stage = 'One necessary retired Agent URL sweep'
    for slug in ['agent-intro', 'agent-tool-execution']:
        for suffix in ['', 'video.mp4', 'cover-16x9.jpg', 'captions.vtt']:
            run.get(f'episodes/{slug}/' + suffix, expected=404)
    deployment_record = {key: deployment[key] for key in ['id', 'html_url', 'head_sha', 'event', 'head_branch', 'path', 'status', 'conclusion', 'created_at', 'updated_at']}
    return {'status': 'passed', 'checkedAtUTC': now(), 'revisionTag': args.revision_tag, 'preservationBaseline': baseline, 'slugs': args.slugs,
            'release': {key: release[key] for key in ['tag_name', 'html_url', 'published_at', 'target_commitish']},
            'annotatedTag': {'tagObjectSha': ref['object']['sha'], 'commit': tagged}, 'deployment': deployment_record,
            'episodes': episode_reports, 'retained': retained, 'retainedCaptionBoundaryChecks': retained_caption_checks, 'localRetainedNativeCCScope': local_boundaries['scope'], 'httpRecords': run.http_records, 'apiRecords': run.api_records,
            'changelogAssociatedExactlyThreeFilms': True, 'retiredAgentURLsStill404': True,
            'limits': ['Only three changed films are downloaded; other canonical identities are preserved through complete Git/local bytes. No redundant old-media HTTP downloads.', 'Serialized HTTP/VTT/HTML checks complement the actual local player/CC/seek/screenshot evidence. No complete listening, ASR or measured learning outcome is claimed.', 'Reserved createdAt and firstRelease are retained; explicit ISO updatedAt/publishedAt are checked independently. Publication identity comes from the supplied tag/run, not future main.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slugs', required=True, help='Exactly three comma-separated selected slugs')
    parser.add_argument('--revision-tag', required=True)
    parser.add_argument('--preservation-base', required=True)
    parser.add_argument('--deployment-run', required=True, type=int)
    args = parser.parse_args()
    args.slugs = args.slugs.split(',')
    assert len(args.slugs) == len(set(args.slugs)) == 3 and all(re.fullmatch(r'[a-z][a-z0-9-]*', slug) for slug in args.slugs)
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
        (OUT / 'online-verification.md').write_text(f'# 三片批量生产核验\n\n实际检查{result["checkedAtUTC"]}，显式{args.revision_tag}通过；实际手动run{args.deployment_run}的head为`{result["deployment"]["head_sha"]}`，与附注tag身份核对。\n\n3片视频/海报完整HTTPS、production、canonical及tag SHA相同。实际SB帧数/字幕/四章/5秒无cue卡、完整Python/source及ISO创建/修改/首次公开日期正确；createdAt和firstRelease保留预留身份。算法方向、主页、系列/库/RSS和本次Release自身仅关联3片的li通过；其他canonical完整SHA保持，没有重复下载旧片媒体。旧Agent8个URL保持404。\n\n本次读取{count}次完整HTTP响应、{total}字节。机器结果见online-verification.json；实际每次成败/阶段见online-verification-attempts.json，部署身份见deployment.json。播放器实际交互/截图范围另见本地QA；不声称全片听辨、ASR或学习效果。\n')
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
