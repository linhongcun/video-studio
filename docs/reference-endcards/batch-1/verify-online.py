#!/usr/bin/env python3
"""Verify this batch after its Release-following Pages deployment.

Example (replace all identities with the actual release):
  python3 docs/reference-endcards/batch-1/verify-online.py \
    --version vX.Y.Z --deployment-run RUN_ID --commit FULL_COMMIT_SHA

Uses normal HTTPS GET, inherited proxy/CA settings, and read-only gh/git commands.
Remote media is streamed into SHA-256 and never saved. Every attempted run writes
online-verification.json, including a failed run and previous attempt records.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).with_name('online-verification.json')
DIST = ROOT / 'site/dist'
BASE = 'https://linhongcun.github.io/video-studio/'
REPO = 'linhongcun/video-studio'
TARGETS = ('dns', 'https', 'browser-cache')
CHUNK = 256 * 1024


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def sha_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            digest.update(chunk)
    return digest.hexdigest()


def command(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=60)
    require(result.returncode == 0,
            f'{args[0]} read failed: {result.stderr.decode(errors="replace")[:800]}')
    return result.stdout


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def git_file(commit, path):
    return command(['git', 'show', f'{commit}:{path}'])


def date_iso(value):
    return value + 'T00:00:00+08:00' if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) else value


class Page(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.seeks, self.times = set(), set(), set(), []
        self.chapters, self.json_ld, self.words, self.h1 = [], [], [], []
        self._script, self._script_text, self._hidden, self._h1 = False, [], 0, False
        self.feed(body.decode('utf-8'))
        self.text = re.sub(r'\s+', ' ', ' '.join(self.words)).strip()
        self.title = re.sub(r'\s+', ' ', ''.join(self.h1)).strip()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'href' in attrs:
            self.links.add(attrs['href'])
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if 'data-seek' in attrs:
            self.seeks.add(attrs['data-seek'])
        if 'data-chapters' in attrs:
            self.chapters = json.loads(attrs['data-chapters'])
        if tag == 'time':
            self.times.append(attrs)
        if tag == 'h1':
            self._h1 = True
        if tag in ('script', 'style'):
            self._hidden += 1
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self._script, self._script_text = True, []

    def handle_endtag(self, tag):
        if tag == 'h1':
            self._h1 = False
        if tag == 'script' and self._script:
            data = json.loads(''.join(self._script_text))
            self.json_ld.extend(data if isinstance(data, list) else [data])
            self._script = False
        if tag in ('script', 'style'):
            self._hidden = max(0, self._hidden - 1)

    def handle_data(self, text):
        if self._script:
            self._script_text.append(text)
        if not self._hidden:
            self.words.append(text)
            if self._h1:
                self.h1.append(text)


def frontmatter_chapters(article):
    """Read the id/title chapter list used by these three fixed batch inputs."""
    match = re.match(r'^---\s*\n(.*?)\n---', article, re.S)
    require(match, 'article frontmatter missing')
    lines, chapters, active = match[1].splitlines(), [], False
    for line in lines:
        if line.startswith('chapters:'):
            active = True
            continue
        if active and line and not line[0].isspace():
            break
        if not active:
            continue
        field = re.match(r'\s*(?:-\s*)?(id|title):\s*(.*?)\s*$', line)
        if field:
            key, value = field.groups()
            if value.startswith('"'):
                value = json.loads(value)
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1].replace("''", "'")
            if key == 'id':
                chapters.append({'id': value})
            else:
                require(bool(chapters), 'chapter title has no id')
                chapters[-1]['title'] = value
    require(bool(chapters) and all('title' in c for c in chapters), 'chapter list incomplete')
    return chapters


def expected_chapters(storyboard, fm):
    """These batch inputs use scene.chapterId and no timing/chapters override."""
    fps = storyboard['meta'].get('fps', 30)
    mapping, result, offset = {c['id']: c for c in fm}, [], 0
    previous = None
    for scene in storyboard['scenes']:
        chapter_id = scene.get('chapterId') or scene['id']
        merged = previous is not None and (
            (scene.get('chapterId') and scene.get('chapterId') == previous.get('chapterId'))
            or (scene.get('title') and scene.get('title') == previous.get('title')))
        if not merged:
            result.append({'id': chapter_id,
                           'title': mapping.get(chapter_id, {}).get('title', scene.get('title')),
                           'start': offset / fps})
        offset += sum(shot['durationInFrames'] for shot in scene['shots'])
        previous = scene
    return result, offset, fps


def vtt_seconds(value):
    h, m, s = value.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def verify_page(body, expected):
    page, meta = Page(body), expected['meta']
    require(page.title == meta['title'], f'{meta["slug"]}: h1 title changed')
    require(page.chapters == expected['chapters'], f'{meta["slug"]}: chapter titles/starts differ')
    for chapter in expected['articleChapters']:
        require(chapter['id'] in page.ids and chapter['id'] in page.seeks,
                f'{meta["slug"]}: chapter anchor/seek missing: {chapter["id"]}')
    require(any(label in page.text for label in ('参考资料', '适用边界与来源')),
            f'{meta["slug"]}: reference heading missing')
    for source in expected['references']['sources']:
        require(re.search(r'\[\s*' + re.escape(source['id']) + r'\s*\]', page.text),
                f'{meta["slug"]}: citation label missing: {source["id"]}')
        for text in (source['organization'], source['title'], source['version']):
            require(text in page.text, f'{meta["slug"]}: reference text missing: {text}')
        for url in (source['url'], source['verification']['sourceUrl']):
            require(url in page.links, f'{meta["slug"]}: reference link missing: {url}')
    ld = next((item for item in page.json_ld if item.get('@type') == 'VideoObject'), None)
    require(ld, f'{meta["slug"]}: VideoObject missing')
    page_url = BASE + 'episodes/' + meta['slug'] + '/'
    for key, value in {'name': meta['title'], 'uploadDate': date_iso(meta['publishedAt']),
                       'dateCreated': date_iso(meta['createdAt']), 'dateModified': date_iso(meta['updatedAt']),
                       'contentUrl': page_url + meta['video'], 'embedUrl': page_url}.items():
        require(ld.get(key) == value, f'{meta["slug"]}: VideoObject {key} differs')
    require(page_url + meta['poster'] in ld.get('thumbnailUrl', []), 'JSON-LD poster differs')
    duration = meta['finalVideoFrames'] / expected['fps']
    require(ld.get('duration') == f'PT{int(duration // 60)}M{int(duration % 60)}S', 'JSON-LD duration differs')
    require(any(t.get('aria-label') == '当前版本' and t.get('datetime') == meta['updatedAt']
                for t in page.times), f'{meta["slug"]}: current version time missing')
    require(any(t.get('datetime') == meta['createdAt'] for t in page.times), 'original creation time missing')
    source_url = f'https://github.com/{REPO}/tree/main/{meta["sourcePath"]}'
    require(source_url in page.links, f'{meta["slug"]}: production source link missing')
    return {'title': page.title, 'chapters': page.chapters, 'uploadDate': ld['uploadDate'],
            'dateModified': ld['dateModified'], 'referenceIds': [s['id'] for s in expected['references']['sources']],
            'referenceLinksVerified': True, 'sourceUrl': source_url}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True, help='Exact released tag, e.g. v0.69.1')
    parser.add_argument('--deployment-run', required=True, help='Exact successful deploy.yml run ID')
    parser.add_argument('--commit', required=True, help='Full 40-character commit SHA for this release')
    args = parser.parse_args()
    if not re.fullmatch(r'v\d+\.\d+\.\d+', args.version):
        parser.error('--version must be an explicit vX.Y.Z tag')
    if not re.fullmatch(r'[0-9a-fA-F]{40}', args.commit):
        parser.error('--commit must contain the full 40-character SHA')
    if not re.fullmatch(r'\d+', args.deployment_run):
        parser.error('--deployment-run must be numeric')
    args.commit = args.commit.lower()
    now = datetime.now(timezone.utc)
    report = {'status': 'running', 'checkedAtUTC': now.isoformat(),
              'checkedAtBeijing': now.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
              'executedBy': 'Codex reference endcards batch-1 website verification',
              'release': args.version, 'commit': args.commit, 'deploymentRun': args.deployment_run,
              'canonicalQueriesAdded': False, 'remoteMediaSaved': False,
              'scope': 'Three batch episodes; full media hashes, exact native VTT, citations, original chapters/dates, tag/Release/Pages identity. Browser interaction is reviewed separately.',
              'httpGets': [], 'githubChecks': [], 'localChecks': [], 'episodes': []}
    if REPORT.exists():
        try:
            previous = read_json(REPORT)
            history = previous.pop('previousAttempts', [])
            report['previousAttempts'] = history + [previous]
        except (OSError, ValueError):
            report['previousReportUnreadable'] = True

    def github(endpoint, name):
        item = {'name': name, 'endpoint': endpoint, 'status': 'running'}
        report['githubChecks'].append(item)
        try:
            data = json.loads(command(['gh', 'api', endpoint]))
            item['status'] = 'read'
            return data, item
        except Exception as exc:
            item.update(status='failed', error=str(exc))
            raise

    def get(name, url, expected_path=None, keep_body=True):
        require(not urllib.parse.urlsplit(url).query, 'canonical GET must not add query parameters')
        item = {'name': name, 'url': url, 'method': 'GET', 'status': 'running'}
        report['httpGets'].append(item)
        digest, count, chunks = hashlib.sha256(), 0, []
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'video-studio-reference-check/1.0'})
            with urllib.request.urlopen(request, timeout=45, context=ssl.create_default_context()) as response:
                item.update(httpStatus=response.status, finalUrl=response.geturl(),
                            contentType=response.headers.get('Content-Type'), etag=response.headers.get('ETag'),
                            cacheControl=response.headers.get('Cache-Control'), age=response.headers.get('Age'))
                require(response.status == 200 and response.geturl() == url, f'{name}: HTTP status or redirect differs')
                for chunk in iter(lambda: response.read(CHUNK), b''):
                    count += len(chunk)
                    digest.update(chunk)
                    if keep_body:
                        chunks.append(chunk)
            item.update(bytes=count, sha256=digest.hexdigest(), fullResponseRead=True)
            if expected_path is not None:
                item.update(expectedBytes=expected_path.stat().st_size, expectedSha256=sha_file(expected_path),
                            localPath=str(expected_path.relative_to(ROOT)))
                require(item['bytes'] == item['expectedBytes'] and item['sha256'] == item['expectedSha256'],
                        f'{name}: full response differs from local published bytes')
                item['fullBytesHashMatch'] = True
            item['status'] = 'passed'
            return b''.join(chunks) if keep_body else None
        except Exception as exc:
            item.update(status='failed', bytes=count, partialSha256=digest.hexdigest(), error=str(exc))
            raise

    try:
        version_at_commit = json.loads(git_file(args.commit, 'site/package.json'))['version']
        require(args.version == 'v' + version_at_commit, 'explicit version differs from package at explicit commit')
        expected_episodes = []
        for folder in TARGETS:
            ep = ROOT / 'episodes' / folder
            meta, refs = read_json(ep / 'meta.json'), read_json(ep / 'references.json')
            slug = meta['slug']
            require(slug == folder and refs['episode'] == slug and meta.get('draft') is False,
                    f'{folder}: final published identity invalid')
            source_path = (ROOT / meta['sourcePath']).resolve()
            baseline = read_json(source_path.parent / 'revisions/reference-endcards/baseline.json')
            original = baseline['publishedMetadata']
            for key in ('title', 'createdAt', 'publishedAt', 'firstRelease'):
                require(meta[key] == original[key], f'{slug}: original {key} changed')
            for filename in ('meta.json', 'references.json', 'article.mdx', 'storyboard.json', meta['video'], meta['poster']):
                rel = str((ep / filename).relative_to(ROOT))
                current_blob = command(['git', 'hash-object', '--', rel]).decode().strip()
                commit_blob = command(['git', 'rev-parse', f'{args.commit}:{rel}']).decode().strip()
                require(current_blob == commit_blob, f'{rel}: local file differs from explicit release commit')
            for override in ('chapters.txt', 'remotion/src/timing.json'):
                require(not (ep / override).exists(), f'{slug}: unsupported chapter timing override: {override}')
            sb = read_json(ep / 'storyboard.json')
            article = (ep / 'article.mdx').read_text(encoding='utf-8')
            fm = frontmatter_chapters(article)
            old_fm = frontmatter_chapters(git_file(baseline['baseCommit'], f'episodes/{slug}/article.mdx').decode())
            old_sb = json.loads(git_file(baseline['baseCommit'], f'episodes/{slug}/storyboard.json'))
            require(fm == old_fm, f'{slug}: original article chapter titles/ids changed')
            chapters, body_frames, fps = expected_chapters(sb, fm)
            old_chapters, old_frames, old_fps = expected_chapters(old_sb, old_fm)
            require(chapters == old_chapters and body_frames == old_frames and fps == old_fps,
                    f'{slug}: original chapter titles or starts changed')
            appendix = meta['referenceAppendix']
            require(appendix['from'] == body_frames and appendix['durationInFrames'] > 0,
                    f'{slug}: reference appendix boundary differs from body')
            require(meta['finalVideoFrames'] == body_frames + appendix['durationInFrames'],
                    f'{slug}: final duration differs from reference appendix')
            expected = {'meta': meta, 'references': refs, 'chapters': chapters,
                        'articleChapters': fm, 'fps': fps, 'bodyFrames': body_frames}
            page_path = DIST / 'episodes' / slug / 'index.html'
            verify_page(page_path.read_bytes(), expected)
            expected_episodes.append(expected)
            report['localChecks'].append({'episode': slug, 'status': 'passed', 'filesMatchCommit': True,
                                          'originalTitleAndPublicationPreserved': True, 'oldChaptersPreserved': True,
                                          'baseCommit': baseline['baseCommit'], 'firstRelease': meta['firstRelease']})

        tag, item = github(f'repos/{REPO}/git/ref/tags/{args.version}', 'release-tag')
        obj, seen = tag['object'], set()
        while obj['type'] == 'tag':
            require(obj['sha'] not in seen, 'cyclic annotated tag')
            seen.add(obj['sha'])
            annotated, detail = github(f'repos/{REPO}/git/tags/{obj["sha"]}', 'annotated-tag')
            obj = annotated['object']
            detail.update(status='passed', object=obj)
        require(obj['type'] == 'commit' and obj['sha'] == args.commit, 'tag does not point at explicit commit')
        item.update(status='passed', resolvedCommit=obj['sha'])
        release, item = github(f'repos/{REPO}/releases/tags/{args.version}', 'published-release')
        release_url = f'https://github.com/{REPO}/releases/tag/{args.version}'
        require(release['tag_name'] == args.version and release['draft'] is False and bool(release.get('published_at')),
                'Release is missing, a draft, or unpublished')
        require(release['html_url'] == release_url, 'Release URL differs')
        item.update(status='passed', releaseId=release['id'], publishedAt=release['published_at'], url=release_url)
        run, item = github(f'repos/{REPO}/actions/runs/{args.deployment_run}', 'pages-deployment-run')
        require(str(run['id']) == args.deployment_run and run['status'] == 'completed'
                and run['conclusion'] == 'success' and run['head_sha'] == args.commit,
                'Pages run is not successful for the explicit commit')
        require(run.get('path', '').split('@')[0] == '.github/workflows/deploy.yml', 'run is not deploy.yml')
        require(run.get('head_branch') == 'main', 'canonical Pages deployment must use main')
        require(datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                >= datetime.fromisoformat(release['published_at'].replace('Z', '+00:00')),
                'specified Pages run predates Release publication')
        item.update(status='passed', headSha=run['head_sha'], conclusion=run['conclusion'], event=run['event'],
                    createdAt=run['created_at'], url=run['html_url'])
        jobs, item = github(f'repos/{REPO}/actions/runs/{args.deployment_run}/jobs?per_page=100', 'pages-deployment-jobs')
        require(any(job['name'] == 'deploy' and job['conclusion'] == 'success' for job in jobs['jobs']),
                'successful deploy job missing from run')
        item.update(status='passed', jobs=[{'name': j['name'], 'conclusion': j['conclusion']} for j in jobs['jobs']])

        for expected in expected_episodes:
            meta, slug = expected['meta'], expected['meta']['slug']
            ep, page_url = ROOT / 'episodes' / slug, BASE + 'episodes/' + slug + '/'
            get(slug + '-video', page_url + meta['video'], ep / meta['video'], keep_body=False)
            get(slug + '-poster', page_url + meta['poster'], ep / meta['poster'], keep_body=False)
            vtt_path = DIST / 'episodes' / slug / 'captions.vtt'
            if vtt_path.is_dir():
                vtt_path /= 'index.html'
            vtt = get(slug + '-captions', page_url + 'captions.vtt', vtt_path)
            require(vtt == vtt_path.read_bytes(), f'{slug}: VTT differs byte for byte')
            cue_ends = [vtt_seconds(end) for end in re.findall(
                r'\d{2,}:\d{2}:\d{2}\.\d{3}\s+-->\s+(\d{2,}:\d{2}:\d{2}\.\d{3})', vtt.decode())]
            sb = read_json(ep / 'storyboard.json')
            cue_count = sum(len(shot.get('subtitles', [])) for scene in sb['scenes'] for shot in scene['shots'])
            require(len(cue_ends) == cue_count and bool(cue_ends), f'{slug}: native VTT cue count differs')
            require(max(cue_ends) <= expected['bodyFrames'] / expected['fps'],
                    f'{slug}: native subtitles overlap the reference appendix')
            page_result = verify_page(get(slug + '-page', page_url), expected)
            report['episodes'].append({'episode': slug, 'status': 'passed', **page_result,
                                       'subtitleCueCount': cue_count, 'vttByteForByteMatch': True,
                                       'lastSubtitleEndSeconds': max(cue_ends), 'firstRelease': meta['firstRelease'],
                                       'bodyFrames': expected['bodyFrames'], 'finalVideoFrames': meta['finalVideoFrames']})
        changelog = Page(get('changelog', BASE + 'changelog/'))
        require(release_url in changelog.links and args.version in changelog.text,
                'actual Release entry is missing from online changelog')
        report.update(status='passed', fullVideoStreamHashed=True, changelogReleasePresent=True)
    except Exception as exc:
        report.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    finally:
        report['finishedAtUTC'] = datetime.now(timezone.utc).isoformat()
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'release': args.version, 'commit': args.commit,
                      'deploymentRun': args.deployment_run, 'completedHttpGets': sum(
                          row['status'] == 'passed' for row in report['httpGets']),
                      'report': str(REPORT), **({'error': report['error']} if 'error' in report else {})},
                     ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
