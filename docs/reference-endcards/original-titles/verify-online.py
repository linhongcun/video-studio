#!/usr/bin/env python3
"""Verify published original-title reference appendices after Pages deployment.

Example (replace all identities with the actual release):
  python3 docs/reference-endcards/original-titles/verify-online.py \
    --version vX.Y.Z --deployment-run RUN_ID --commit FULL_COMMIT_SHA

Before committing or releasing, check built local files without HTTP/GitHub calls:
  python3 docs/reference-endcards/original-titles/verify-online.py --local-only

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
import math
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
PRESENTATION = 'original-title-quote'
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


def published_targets():
    """Discover declarations; an incomplete published declaration must fail."""
    targets = []
    for meta_path in sorted((ROOT / 'episodes').glob('*/meta.json')):
        meta = read_json(meta_path)
        if meta.get('draft') is True:
            continue
        refs_path = meta_path.with_name('references.json')
        if 'referenceAppendix' not in meta and not refs_path.exists():
            continue
        require(isinstance(meta.get('referenceAppendix'), dict) and bool(meta['referenceAppendix']),
                f'{meta_path.parent.name}: published references lack an appendix declaration')
        require(refs_path.is_file(), f'{meta_path.parent.name}: appendix declares missing references.json')
        targets.append(meta_path.parent.name)
    require(bool(targets), 'no published reference appendices found')
    return targets


def git_file(commit, path):
    return command(['git', 'show', f'{commit}:{path}'])


def date_iso(value):
    return value + 'T00:00:00+08:00' if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) else value


def visible_text(value):
    """Allow only MDX's observed smart quotes and visible whitespace changes.

    Original references and receipt strings still match exactly; this compares
    rendered article text without removing or rewriting any words.
    """
    return re.sub(r'\s+', ' ', value.translate(str.maketrans({'‘': "'", '’': "'",
                                                           '“': '"', '”': '"'}))).strip()


class Page(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.seeks, self.times = set(), set(), set(), []
        self.chapters, self.json_ld, self.words, self.h1, self.headings = [], [], [], [], []
        self._script, self._script_text, self._hidden, self._h1 = False, [], 0, False
        self._heading, self._heading_text = None, []
        self._heading_control = False
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
        if tag in ('h2', 'h3'):
            self._heading, self._heading_text = {'tag': tag, 'id': attrs.get('id')}, []
        if self._heading is not None and tag == 'a' and 'data-pagefind-ignore' in attrs:
            self._heading_control = True
        if tag in ('script', 'style'):
            self._hidden += 1
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self._script, self._script_text = True, []

    def handle_endtag(self, tag):
        if tag == 'a':
            self._heading_control = False
        if self._heading is not None and tag == self._heading['tag']:
            self.headings.append({**self._heading, 'title': re.sub(
                r'\s+', ' ', ''.join(self._heading_text)).strip()})
            self._heading = None
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
            if self._heading is not None and not self._heading_control:
                self._heading_text.append(text)


def yaml_scalar(value):
    """The chapter inputs use plain, JSON-double-quoted or YAML-single-quoted strings."""
    value = value.strip()
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def frontmatter_chapters(article):
    """Read the frozen articles' inline maps and block chapter mappings.

    This intentionally reads only the id/title list used by these batch inputs;
    it never guesses a chapter from an unrelated heading or rewritten article.
    """
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
        inline = re.fullmatch(r'\s*-\s*\{\s*(.*?)\s*\}\s*', line)
        if inline:
            fields = re.findall(r'(?:^|,)\s*(id|title)\s*:\s*(.*?)(?=,\s*(?:id|title)\s*:|$)',
                                inline.group(1))
            chapter = {key: yaml_scalar(value) for key, value in fields}
            require(set(chapter) == {'id', 'title'}, 'inline chapter map incomplete')
            chapters.append(chapter)
            continue
        field = re.match(r'\s*(?:-\s*)?(id|title):\s*(.*?)\s*$', line)
        if field:
            key, value = field.groups()
            value = yaml_scalar(value)
            if key == 'id':
                chapters.append({'id': value})
            else:
                require(bool(chapters), 'chapter title has no id')
                chapters[-1]['title'] = value
    require(bool(chapters) and all(c.get('id') and c.get('title') for c in chapters),
            'chapter list incomplete')
    require(len({c['id'] for c in chapters}) == len(chapters), 'duplicate chapter ids')
    return chapters


def expected_chapters(storyboard, fm):
    """Keep all scene groups, including intro/recap absent from the article list."""
    fps = storyboard['meta'].get('fps', 30)
    mapping, groups, offset = {c['id']: c for c in fm}, [], 0
    by_id = any(scene.get('chapterId') for scene in storyboard['scenes'])
    previous = None
    for scene in storyboard['scenes']:
        chapter_id = scene.get('chapterId') or scene['id']
        merged = previous is not None and (
            (scene.get('chapterId') and scene.get('chapterId') == previous.get('chapterId'))
            or (scene.get('title') and scene.get('title') == previous.get('title')))
        if merged:
            groups[-1]['scenes'].append(scene)
        else:
            groups.append({'scenes': [scene], 'from': offset})
        offset += sum(shot['durationInFrames'] for shot in scene['shots'])
        previous = scene
    result = []
    for index, group in enumerate(groups):
        first = group['scenes'][0]
        if by_id:
            front = next((mapping[s['chapterId']] for s in group['scenes']
                          if s.get('chapterId') in mapping), {})
        else:
            front = fm[index] if index < len(fm) else {}
        result.append({'id': front.get('id', first.get('chapterId') or first['id']),
                       'title': front.get('title', first.get('title')),
                       'start': group['from'] / fps})
    return result, offset, fps


def article_reference_heading(article):
    for match in re.finditer(r'^#{2,3}\s+(.+?)(?:\s+\{#([^}]+)\})?\s*$', article, re.M):
        title, anchor = match.groups()
        if title in ('公开来源与核验范围', '适用边界与来源', '资料与阅读范围') or '参考资料' in title:
            return {'title': title, 'id': anchor}
    raise VerificationError('article reference heading missing')


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
    reference_heading = expected['referenceHeading']
    require(any(h['title'] == reference_heading['title'] and (
                reference_heading['id'] is None or h['id'] == reference_heading['id'])
                for h in page.headings), f'{meta["slug"]}: actual article reference heading/anchor missing')
    for source in expected['references']['sources']:
        require(re.search(r'\[\s*' + re.escape(source['id']) + r'\s*\]', page.text),
                f'{meta["slug"]}: citation label missing: {source["id"]}')
        original_text = [source['organization'], source['title'], source['version']]
        if 'quotation' in source:
            original_text.extend((source['quotation']['text'], source['quotation']['locator']))
        for text in original_text:
            require(visible_text(text) in visible_text(page.text),
                    f'{meta["slug"]}: original reference text or locator missing: {text}')
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
            'referenceLinksVerified': True, 'referenceHeading': reference_heading,
            'originalReferenceTitles': [s['title'] for s in expected['references']['sources']],
            'exactQuotationsAndLocatorsVerified': True,
            'renderedTextComparison': 'Whitespace folding and MDX smart quotation marks only; no words removed or paraphrased.',
            'sourceUrl': source_url}


def caption_path(slug):
    path = DIST / 'episodes' / slug / 'captions.vtt'
    return path / 'index.html' if path.is_dir() else path


def verify_vtt(vtt, storyboard, expected):
    slug = expected['meta']['slug']
    require(vtt.startswith(b'WEBVTT'), f'{slug}: native VTT header missing')
    cues = []
    for block in re.split(r'\n\s*\n', vtt.decode().replace('\r\n', '\n').strip())[1:]:
        timing, separator, text = block.partition('\n')
        match = re.fullmatch(r'(\d{2,}:\d{2}:\d{2}\.\d{3}) --> (\d{2,}:\d{2}:\d{2}\.\d{3})', timing)
        require(match and separator, f'{slug}: malformed native VTT cue')
        cues.append({'start': vtt_seconds(match[1]), 'end': vtt_seconds(match[2]), 'text': text})
    fps, offset, expected_cues = expected['fps'], 0, []
    card = storyboard['meta'].get('unvoicedEndCard') or storyboard['meta'].get('javaEndCard') or expected['meta']['referenceAppendix']
    for scene in storyboard['scenes']:
        for shot in scene['shots']:
            previous_end = -1
            for sub in shot.get('subtitles', []):
                require(isinstance(sub.get('from'), int) and isinstance(sub.get('to'), int)
                        and previous_end < sub['from'] <= sub['to'] < shot['durationInFrames'],
                        f'{slug}: expected frozen subtitle timing is incomplete')
                end_frame = offset + sub['to'] + 1
                end = end_frame / fps
                if end_frame == card['from']:
                    end = (math.ceil(end * 1000) - 1) / 1000
                expected_cues.append({'start': (offset + sub['from']) / fps,
                                      'end': end, 'text': sub['text']})
                previous_end = sub['to']
            offset += shot['durationInFrames']
    require(bool(cues) and len(cues) == len(expected_cues), f'{slug}: native VTT cue count differs')
    require(all(c['text'] == e['text'] and abs(c['start']-e['start']) <= .000501
                and abs(c['end']-e['end']) <= .000501 for c, e in zip(cues, expected_cues)),
            f'{slug}: full native VTT text or frozen timing differs')
    cue_count, cue_ends = len(cues), [c['end'] for c in cues]
    require(max(cue_ends) < expected['bodyFrames'] / expected['fps'],
            f'{slug}: native subtitles reach or overlap the first reference frame')
    return {'subtitleCueCount': cue_count, 'fullSubtitleTextAndTimingVerified': True,
            'lastSubtitleEndSeconds': max(cue_ends),
            'subtitleEndsStrictlyBeforeAppendix': True}


def local_expectation(folder, release_commit=None):
    """Read and check current build inputs; no HTTP or GitHub calls occur here."""
    ep = ROOT / 'episodes' / folder
    meta, refs = read_json(ep / 'meta.json'), read_json(ep / 'references.json')
    slug = meta['slug']
    require(slug == folder and refs['episode'] == slug and meta.get('draft') is False,
            f'{folder}: final published identity invalid')
    source_path = (ROOT / meta['sourcePath']).resolve()
    revision = source_path.parent / 'revisions/original-titles'
    baseline = read_json(revision / 'baseline.json')
    original = baseline['metadata']
    for key in ('slug', 'ep', 'title', 'createdAt', 'publishedAt', 'firstRelease', 'platforms',
                'sourcePath', 'javaEndCard', 'unvoicedEndCard'):
        require(meta.get(key) == original.get(key), f'{slug}: original {key} changed')
    if release_commit is not None:
        for filename in ('meta.json', 'references.json', 'article.mdx', 'storyboard.json',
                         'reference-appendix.json', 'reference-appendix-media-check.json',
                         meta['video'], meta['poster']):
            rel = str((ep / filename).relative_to(ROOT))
            current_blob = command(['git', 'hash-object', '--', rel]).decode().strip()
            commit_blob = command(['git', 'rev-parse', f'{release_commit}:{rel}']).decode().strip()
            require(current_blob == commit_blob, f'{rel}: local file differs from explicit release commit')
        for filename in ('baseline.json', 'before-reference-appendix-media-check.json'):
            baseline_rel = str((revision / filename).relative_to(ROOT))
            require((ROOT / baseline_rel).read_bytes() == git_file(release_commit, baseline_rel),
                    f'{slug}: original-title {filename} differs from explicit release commit')
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
    receipt = read_json(ep / 'reference-appendix.json')
    media_check = read_json(ep / 'reference-appendix-media-check.json')
    require(refs.get('presentation') == receipt.get('presentation') == PRESENTATION,
            f'{slug}: original-title presentation is missing')
    require(receipt.get('sourceTitles') == [{'id': s['id'], 'title': s['title']} for s in refs['sources']],
            f'{slug}: receipt original titles differ from published references')
    quotes = [{'id': s['id'], **s['quotation']} for s in refs['sources'] if 'quotation' in s]
    require(receipt.get('quotations') == quotes, f'{slug}: receipt original quotations differ')
    pages = receipt['appendix']['pages']
    require(len(pages) == (len(refs['sources']) + 1) // 2
            and receipt['appendix']['framesPerPage'] == fps * 5
            and receipt['appendix']['durationInFrames'] == len(pages) * fps * 5,
            f'{slug}: expected two-source, five-second reference pages differ')
    require(receipt['bodyFrames'] == baseline['bodyFrames'] == body_frames,
            f'{slug}: original complete body/code-card boundary changed')
    old_media = read_json(revision / 'before-reference-appendix-media-check.json')
    preserved_keys = ('bodyFrameMD5RowsSHA256', 'audioPacketCount',
                      'audioPacketPayloadAndTimingSHA256', 'decodedAudioPCM',
                      'audioStreamEndsAtOriginalEndpointSeconds')
    require(all(media_check.get(k) is not None and media_check[k] == old_media.get(k)
                for k in preserved_keys), f'{slug}: original body/code-card or audio fingerprint changed')
    actual_video_sha = sha_file(ep / meta['video'])
    require(receipt['outputSHA256'] == actual_video_sha == media_check['outputSHA256'],
            f'{slug}: final video differs from appendix/media receipts')
    require(receipt['inputs']['referencesSHA256'] == sha_file(ep / 'references.json'),
            f'{slug}: receipt references differ from published source list')
    require(receipt['appendix']['from'] == body_frames and receipt['finalVideoFrames'] == meta['finalVideoFrames'],
            f'{slug}: receipt appendix boundary or final frame count differs')
    require(media_check['passed'] is True and media_check['bodyDecodedFramesAndTimestampsEqual'] is True
            and media_check['audioPacketsAndTimingEqual'] is True
            and media_check.get('outputVideoTimelineContinuous') is True,
            f'{slug}: body preservation media checks did not pass')
    for filename in (meta['video'], meta['poster']):
        require(sha_file(DIST / 'episodes' / slug / filename) == sha_file(ep / filename),
                f'{slug}: built {filename} differs from current published file')
    expected = {'meta': meta, 'references': refs, 'chapters': chapters,
                'articleChapters': fm, 'fps': fps, 'bodyFrames': body_frames,
                'referenceHeading': article_reference_heading(article)}
    verify_page((DIST / 'episodes' / slug / 'index.html').read_bytes(), expected)
    cues = verify_vtt(caption_path(slug).read_bytes(), sb, expected)
    local_check = {'episode': slug, 'status': 'passed',
                   'filesMatchCommit': release_commit is not None,
                   'originalTitleAndPublicationPreserved': True, 'oldChaptersPreserved': True,
                   'originalPlatformLinksPreserved': True,
                   'originalBodyAndCodeCardFingerprintsPreserved': True,
                   'presentation': PRESENTATION, 'referenceSourceCount': len(refs['sources']),
                   'referencePageCount': len(pages), 'secondsPerPage': 5,
                   'baseCommit': baseline['baseCommit'], 'firstRelease': meta['firstRelease'],
                   'referenceHeading': expected['referenceHeading'],
                   'articleChapterCount': len(fm), 'playerChapterCount': len(chapters),
                   'finalVideoSHA256': actual_video_sha, **cues}
    return expected, local_check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', help='Exact released tag, e.g. vX.Y.Z')
    parser.add_argument('--deployment-run', help='Exact successful deploy.yml run ID')
    parser.add_argument('--commit', help='Full 40-character commit SHA for this release')
    parser.add_argument('--local-only', action='store_true',
                        help='Validate built local inputs only; no HTTP/GitHub/release checks')
    args = parser.parse_args()
    if not args.local_only and not all((args.version, args.deployment_run, args.commit)):
        parser.error('online verification requires explicit --version, --deployment-run, and --commit')
    if args.version is not None and not re.fullmatch(r'v\d+\.\d+\.\d+', args.version):
        parser.error('--version must be an explicit vX.Y.Z tag')
    if args.commit is not None and not re.fullmatch(r'[0-9a-fA-F]{40}', args.commit):
        parser.error('--commit must contain the full 40-character SHA')
    if args.deployment_run is not None and not re.fullmatch(r'\d+', args.deployment_run):
        parser.error('--deployment-run must be numeric')
    if args.commit:
        args.commit = args.commit.lower()
    report_path = REPORT.with_name('local-verification.json') if args.local_only else REPORT
    now = datetime.now(timezone.utc)
    report = {'status': 'running', 'checkedAtUTC': now.isoformat(),
              'checkedAtBeijing': now.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
              'executedBy': 'Codex original-title reference appendix website verification',
              'release': args.version, 'commit': args.commit, 'deploymentRun': args.deployment_run,
              'mode': 'local-only' if args.local_only else 'post-release-online',
              'networkChecksExecuted': False,
              'canonicalQueriesAdded': False, 'remoteMediaSaved': False,
              'scope': 'Discover all published reference appendices; verify original titles/quotes/locators, full media hashes and VTT, preserved body/code-card fingerprints and chapters/dates, explicit tag/Release/Pages identity. Browser interaction is reviewed separately.',
              'httpGets': [], 'githubChecks': [], 'localChecks': [], 'episodes': []}
    if report_path.exists():
        try:
            previous = read_json(report_path)
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
        if args.commit is not None:
            version_at_commit = json.loads(git_file(args.commit, 'site/package.json'))['version']
            require(args.version is None or args.version == 'v' + version_at_commit,
                    'explicit version differs from package at explicit commit')
        if args.local_only:
            working_version = read_json(ROOT / 'site/package.json')['version']
            require(args.version is None or args.version == 'v' + working_version,
                    'explicit local version differs from working package')
            report['workingVersion'] = 'v' + working_version
        targets = published_targets()
        report.update(targetEpisodes=targets, expectedEpisodeCount=len(targets),
                      expectedCanonicalGetCount=len(targets) * 4 + 1)
        expected_episodes = []
        for folder in targets:
            expected, local_check = local_expectation(folder, args.commit)
            expected_episodes.append(expected)
            report['localChecks'].append(local_check)
        report['referenceSourceCount'] = sum(c['referenceSourceCount'] for c in report['localChecks'])
        report['referencePageCount'] = sum(c['referencePageCount'] for c in report['localChecks'])
        report['scope'] = (f'{len(targets)} published episodes, {report["referenceSourceCount"]} sources, '
                           f'{report["referencePageCount"]} reference pages; original titles/quotes/locators, '
                           'full media hashes and VTT, preserved body/code-card fingerprints and chapters/dates, '
                           'explicit tag/Release/Pages identity. Browser interaction is reviewed separately.')

        if args.local_only:
            report.update(status='passed', networkChecksExecuted=False,
                          scope=f'{len(targets)} built local episode pages, {report["referenceSourceCount"]} sources and '
                                f'{report["referencePageCount"]} reference pages; receipts, original chapters/dates, '
                                'body/code-card fingerprints and full VTT. No tag/Release/deployment/online checks executed.')
            return 0

        report['networkChecksExecuted'] = True
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
            vtt_path = caption_path(slug)
            vtt = get(slug + '-captions', page_url + 'captions.vtt', vtt_path)
            require(vtt == vtt_path.read_bytes(), f'{slug}: VTT differs byte for byte')
            sb = read_json(ep / 'storyboard.json')
            cues = verify_vtt(vtt, sb, expected)
            page_result = verify_page(get(slug + '-page', page_url,
                                          DIST / 'episodes' / slug / 'index.html'), expected)
            report['episodes'].append({'episode': slug, 'status': 'passed', **page_result,
                                       **cues, 'vttByteForByteMatch': True,
                                       'firstRelease': meta['firstRelease'],
                                       'bodyFrames': expected['bodyFrames'], 'finalVideoFrames': meta['finalVideoFrames']})
        changelog = Page(get('changelog', BASE + 'changelog/'))
        require(release_url in changelog.links and args.version in changelog.text,
                'actual Release entry is missing from online changelog')
        require(len(report['httpGets']) == len(targets) * 4 + 1, 'unexpected canonical GET count')
        report.update(status='passed', fullVideoStreamHashed=True, changelogReleasePresent=True,
                      canonicalFullGetCount=len(report['httpGets']))
    except Exception as exc:
        report.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    finally:
        report['finishedAtUTC'] = datetime.now(timezone.utc).isoformat()
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'status': report['status'], 'mode': report['mode'],
                          'release': args.version, 'commit': args.commit,
                          'deploymentRun': args.deployment_run, 'completedHttpGets': sum(
                              row['status'] == 'passed' for row in report['httpGets']),
                          'completedLocalChecks': len(report['localChecks']),
                          'report': str(report_path), **({'error': report['error']} if 'error' in report else {})},
                         ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
