"""Read-only facts and document checks for the EP.01 technical-depth revision."""
from pathlib import Path
import importlib.util
import json
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SLUG = 'http-request'
PRODUCTION = ROOT / 'episodes-codex' / SLUG
CANONICAL = ROOT / 'episodes' / SLUG
DIST = ROOT / 'site/dist'
REPOSITORY = 'linhongcun/video-studio'
BASE = 'https://linhongcun.github.io/video-studio/'
# Reuse the existing pure HTML/VTT parser; importing it performs no checks/writes.
_spec = importlib.util.spec_from_file_location('existing_site_document_checks', ROOT / 'docs/number-of-islands-boundaries/verify-online.py')
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
Document, parse_vtt, expected_cues = _module.Document, _module.parse_vtt, _module.expected_cues
sha, utc_now, git_bytes, commit_id = _module.sha, _module.utc_now, _module.git_bytes, _module.commit_id
PUBLIC_FILES = ('article.mdx', 'script.md', 'pronunciation.md', 'research.md',
                'words.json', 'storyboard.json', 'captions.srt', 'covers.json',
                'video.mp4', 'render-result.json', 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg')


def read_json(path):
    return json.loads(path.read_text())


def facts():
    meta = read_json(CANONICAL / 'meta.json')
    config = read_json(PRODUCTION / 'production.json')
    sb = read_json(PRODUCTION / 'storyboard.json')
    rendered = read_json(PRODUCTION / 'render-result.json')
    fps, frames = sb['meta']['fps'], sb['meta']['durationInFrames']
    assert fps == 30 and frames == rendered['frames'] == meta['finalVideoFrames']
    assert config['ep'] == meta['ep'] == 1 and config['title'] == meta['title']
    assert meta['slug'] == SLUG and meta['series'] == 'request' and meta['draft'] is False
    assert meta['sourcePath'] == 'episodes-codex/http-request/remotion'
    assert meta['summary'] == meta['description'] == config['summary']
    assert not sb['meta'].get('pendingAudio') and not sb['meta'].get('provisionalTiming')
    chapters = []
    for scene in sb['scenes']:
        cid = scene.get('chapterId', scene['id'])
        title = next(item[1] for item in config['chapters'] if item[0] == cid)
        chapters.append({'id': cid, 'title': title, 'start': scene['from'] / fps, 'frame': scene['from']})
    cues = expected_cues(sb)
    assert [cue['text'] for cue in cues] == [row['text'] for row in read_json(PRODUCTION / 'voice/sents.json')]
    return {'meta': meta, 'config': config, 'storyboard': sb, 'rendered': rendered,
            'fps': fps, 'frames': frames, 'chapters': chapters, 'cues': cues}


def request_slugs():
    metas = [read_json(path) for path in (ROOT / 'episodes').glob('*/meta.json')]
    return [m['slug'] for m in sorted(metas, key=lambda m: (m.get('ep', 0), m.get('lessonOrder', 0), m['slug']))
            if m.get('series') == 'request' and not m.get('draft') and not m.get('archived')]


def check_identity(data, baseline, tagged_commit=None):
    old = json.loads(git_bytes(baseline, f'episodes/{SLUG}/meta.json'))
    meta, rendered = data['meta'], data['rendered']
    for key in ('slug', 'ep', 'title', 'series', 'createdAt', 'firstRelease', 'publishedAt', 'platforms', 'sourcePath'):
        assert meta.get(key) == old.get(key), key
    updated = datetime.fromisoformat(meta['updatedAt'])
    assert updated.utcoffset() == timedelta(hours=8) and meta['updatedAt'].endswith('+08:00')
    assert updated.date().isoformat() == '2026-10-25'
    assert updated > datetime.fromisoformat(date_iso(old['updatedAt']))
    files = {}
    for name in PUBLIC_FILES:
        body = (CANONICAL / name).read_bytes()
        assert body == (PRODUCTION / name).read_bytes(), ('production/canonical', name)
        if tagged_commit:
            assert body == git_bytes(tagged_commit, f'episodes/{SLUG}/{name}'), ('tagged copy', name)
        files[name] = {'bytes': len(body), 'sha256': sha(body)}
    assert files['video.mp4']['sha256'] == rendered['sha256']
    assert files['video.mp4']['bytes'] == rendered['bytes']
    assert files['video.mp4']['sha256'] != sha(git_bytes(baseline, f'episodes/{SLUG}/video.mp4'))
    current_non_task_changes = subprocess.check_output(['git', 'diff', '--name-only', baseline, '--',
                'episodes', ':(exclude)episodes/http-request'], cwd=ROOT, text=True).splitlines()
    assert not current_non_task_changes, ('current non-task canonical changes', current_non_task_changes)
    if tagged_commit:
        assert (CANONICAL / 'meta.json').read_bytes() == git_bytes(tagged_commit, f'episodes/{SLUG}/meta.json')
        changes = subprocess.check_output(['git', 'diff', '--name-only', baseline, tagged_commit, '--',
                    'episodes', ':(exclude)episodes/http-request'], cwd=ROOT, text=True).splitlines()
        assert not changes, ('non-task canonical changes', changes)
    return files


def date_iso(value):
    return value if len(value) > 10 else value + 'T00:00:00+08:00'


def date_display(value):
    dt = datetime.fromisoformat(date_iso(value)).astimezone(timezone(timedelta(hours=8)))
    return f'{dt.year}年{dt.month}月{dt.day}日' + (dt.strftime(' %H:%M:%S') if len(value) > 10 else '')


def date_version(value):
    dt = datetime.fromisoformat(date_iso(value)).astimezone(timezone(timedelta(hours=8)))
    return dt.strftime('%Y-%m-%d %H:%M:%S' if len(value) > 10 else '%Y-%m-%d') + ' 版'


def check_rss(body, data):
    matches = [item for item in ET.fromstring(body).findall('./channel/item')
               if item.findtext('link') == BASE + f'episodes/{SLUG}/']
    assert len(matches) == 1
    pub = parsedate_to_datetime(matches[0].findtext('pubDate'))
    assert pub == datetime.fromisoformat(date_iso(data['meta']['publishedAt']))
    return {'firstPublicationPreserved': True, 'pubDate': matches[0].findtext('pubDate')}


def check_episode(page, vtt, data, revision_tag):
    meta, chapters, cues = data['meta'], data['chapters'], data['cues']
    assert meta['title'] in page.text and 'EP.01' in page.text and revision_tag in page.text
    source_link = f'https://github.com/{REPOSITORY}/tree/main/{meta["sourcePath"]}'
    assert source_link in page.links
    assert {c['id'] for c in chapters} <= page.ids
    payload = [json.loads(attrs['data-chapters']) for _, attrs in page.attributes if 'data-chapters' in attrs]
    assert payload == [[{k: c[k] for k in ('id', 'title', 'start')} for c in chapters]]
    links = [a for tag, a in page.attributes if tag == 'a' and 'data-id' in a and 'data-start' in a]
    assert len(links) == len(chapters) * 2
    for index, chapter in enumerate(chapters):
        matched = [a for a in links if a['data-id'] == chapter['id']]
        assert len(matched) == 2 and {a['class'] for a in matched} == {'ch', 'chip'}
        assert all(abs(float(a['data-start']) - chapter['start']) < 1e-9 and int(a['data-index']) == index
                   and a['href'] == '#' + chapter['id'] for a in matched)
    videos = [a for tag, a in page.attributes if tag == 'video']
    sources = [a for tag, a in page.attributes if tag == 'source']
    tracks = [a for tag, a in page.attributes if tag == 'track' and a.get('kind') == 'captions']
    assert len(videos) == len(sources) == len(tracks) == 1
    assert 'controls' in videos[0] and videos[0]['poster'].endswith(f'episodes/{SLUG}/{meta["poster"]}')
    assert sources[0]['src'].endswith(f'episodes/{SLUG}/{meta["video"]}')
    assert tracks[0]['src'].endswith(f'episodes/{SLUG}/captions.vtt')
    actual = parse_vtt(vtt)
    assert len(actual) == len(cues)
    for a, e in zip(actual, cues):
        assert a['text'] == e['text'] and abs(a['start'] - e['start']) <= .00051 and abs(a['end'] - e['end']) <= .00051
    seconds = data['frames'] / data['fps']
    assert f'视频 {int(seconds // 60)}:{int(seconds % 60):02}' in page.text
    assert 'SYN' in page.text and 'ACK' in page.text and 'TCP' in page.text and 'TLS' in page.text
    assert '/video-studio/episodes/https/' in page.links
    assert date_version(meta['updatedAt']) in page.text
    assert '创建于' in page.text and '修改于' in page.text
    assert date_display(meta['createdAt']) in page.text and date_display(meta['updatedAt']) in page.text
    times = [a for tag, a in page.attributes if tag == 'time']
    assert any(a.get('aria-label') == '当前版本' and a.get('datetime') == meta['updatedAt'] for a in times)
    assert any(a.get('datetime') == meta['createdAt'] for a in times)
    structured = [json.loads(t) for t in page.texts if t.strip().startswith('{"@context"')]
    assert len(structured) == 1 and structured[0]['@type'] == 'VideoObject'
    assert structured[0]['dateCreated'] == date_iso(meta['createdAt'])
    assert structured[0]['dateModified'] == meta['updatedAt']
    assert structured[0]['uploadDate'] == date_iso(meta['publishedAt'])
    return {'captions': len(cues), 'chapters': chapters, 'nativeControls': True,
            'exactFrozenCaptionTiming': True, 'sourceLink': source_link, 'videoFrames': data['frames'],
            'dateVersion': date_version(meta['updatedAt']), 'createdAt': meta['createdAt'],
            'updatedAt': meta['updatedAt'], 'publishedAt': meta['publishedAt'], 'structuredDatesMatch': True}
