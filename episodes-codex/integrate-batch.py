#!/usr/bin/env python3
"""Copy checked EP01–14 assets into the site, adding article navigation only.

The production article remains a frozen input. The site derivative adds explicit
chapter anchors (and section headings for two unsectioned articles); it never
changes narration, images, video timing, or production inputs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['http-request', 'https', 'dns', 'cookie-session', 'cdn',
         'load-balancing', 'browser-cache', 'server-cache', 'cache-consistency',
         'message-queue', 'rate-limit', 'idempotency', 'circuit-breaker', 'degradation']
CHAPTERS = {
    'http-request': {0: 'hook', 1: 'connect', 4: 'exchange', 7: 'render', 10: 'recap'},
    'https': {0: 'hook', 3: 'identity', 5: 'encryption', 8: 'integrity'},
    'dns': {0: 'hook', 2: 'cache', 3: 'query', 8: 'ttl', 10: 'recap'},
    'cookie-session': {0: 'session', 1: 'lookup', 2: 'expire', 3: 'recap'},
    'cdn': {0: 'network', 1: 'miss', 2: 'hit', 3: 'fresh'},
    'load-balancing': {0: 'hook', 1: 'balance', 2: 'health', 3: 'limits'},
    'browser-cache': {0: 'first', 1: 'fresh', 2: 'stale', 3: 'recap'},
    'server-cache': {0: 'cache', 1: 'lifecycle'},
    'cache-consistency': {0: 'stale', 1: 'invalidate', 2: 'order'},
    'message-queue': {0: 'enqueue', 1: 'retry', 2: 'recap'},
    'rate-limit': {0: 'allow', 1: 'refill', 2: 'recap'},
    'idempotency': {0: 'retry', 1: 'identity', 2: 'boundary'},
    'circuit-breaker': {0: 'stop', 1: 'recover', 2: 'recap'},
    'degradation': {0: 'load', 1: 'degrade', 2: 'boundary'},
}
SECTION_TITLES = {
    'load-balancing': ['一台实例为何积压', '请求交给哪一个实例', '检查故障，再决定分配', '共享瓶颈与失败请求'],
    'browser-cache': ['第一次取得，再按规则保存', '有效期内直接复用', '期限到达，需要重新确认', '复用还要满足其他条件'],
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def article_for_site(slug):
    d = ROOT / 'episodes-codex' / slug
    article = (d / 'article.mdx').read_text()
    match = re.fullmatch(r'---\n(.*?)\n---\n(.*)', article, re.S)
    assert match, f'{slug}: article frontmatter'
    header, body = match.groups()
    if slug in SECTION_TITLES:
        blocks = body.lstrip('\n').split('\n\n')
        for i, title in enumerate(SECTION_TITLES[slug]):
            assert not blocks[i].startswith('[^'), f'{slug}: unexpected source paragraph'
            blocks[i] = f'## {title}\n\n{blocks[i]}'
        body = '\n' + '\n\n'.join(blocks)
    headings = re.findall(r'^## (.+)$', body, re.M)
    mapping = CHAPTERS[slug]
    assert all(i < len(headings) for i in mapping), f'{slug}: heading map'
    scenes = json.loads((d / 'storyboard.json').read_text())['scenes']
    available = {s.get('chapterId', s['id']) for s in scenes}
    assert set(mapping.values()) <= available, f'{slug}: nonexistent video chapter'
    index = 0

    def heading(m):
        nonlocal index
        i = index
        index += 1
        return m[0] + (f' {{#{mapping[i]}}}' if i in mapping else '')

    body = re.sub(r'^## .+$', heading, body, flags=re.M)
    lines, out, i = header.splitlines(), [], 0
    while i < len(lines):
        if lines[i].startswith('chapters:'):
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith((' ', '\t'))):
                i += 1
        else:
            out.append(lines[i])
            i += 1
    out.append('chapters:')
    for i, chapter in mapping.items():
        out += [f'  - id: {chapter}', f'    title: {json.dumps(headings[i], ensure_ascii=False)}']
    return '---\n' + '\n'.join(out) + '\n---\n' + body


def scalar(article, key):
    value = re.search(rf'^{key}: (.+)$', article, re.M)[1].strip()
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def integrate(slug):
    src, dst = ROOT / 'episodes-codex' / slug, ROOT / 'episodes' / slug
    report = json.loads((src / 'render-result.json').read_text())
    expected = report.get('sha256', report.get('videoSha256'))
    assert digest(src / 'video.mp4') == expected, f'{slug}: render report/video mismatch'
    sb = json.loads((src / 'storyboard.json').read_text())
    before = json.loads((dst / 'meta.json').read_text())
    meta = dict(before)
    article = article_for_site(slug)
    meta.update(title=sb['meta']['title'], summary=scalar(article, 'summary'),
                description=scalar(article, 'summary'), updatedAt='2026-10-24',
                targetDuration=round(report['frames'] / 30), finalVideoFrames=report['frames'],
                video='video.mp4', poster='cover-16x9.jpg', coverFrame=0, draft=False,
                sourcePath=f'episodes-codex/{slug}/remotion')
    proposal = src / 'site-meta-proposal.json'
    if proposal.exists():
        p = json.loads(proposal.read_text())
        for key in ['title', 'summary', 'description']:
            if key in p:
                meta[key] = p[key]
    meta.pop('legacy', None)
    names = ['video.mp4', 'voice.wav', 'script.md', 'research.md', 'pronunciation.md',
             'storyboard.json', 'words.json', 'covers.json', 'render-result.json',
             'captions.srt', 'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg',
             'cover-16x9.png', 'cover-4x3.png', 'cover-3x4.png', 'poster.jpg']
    copied = {}
    for name in names:
        if (src / name).exists():
            shutil.copy2(src / name, dst / name)
            copied[name] = digest(dst / name)
    (dst / 'article.mdx').write_text(article)
    (dst / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    for name in ['timing.json', 'remotion/src/timing.json', 'chapters.txt']:
        (dst / name).unlink(missing_ok=True)
    for key in ['publishedAt', 'firstRelease', 'platforms', 'series', 'tags', 'related']:
        assert meta.get(key) == before.get(key), f'{slug}: historical field changed: {key}'
    integration = dict(productionArticleSha256=digest(src / 'article.mdx'),
                       siteArticleSha256=digest(dst / 'article.mdx'),
                       articleChanges='Navigation-only derivative: explicit chapter anchors; EP06/07 section headings. Production article and media inputs remain frozen.',
                       chapterMap=CHAPTERS[slug], copied=copied,
                       sourcePath=meta['sourcePath'], published=False)
    (dst / 'site-integration.json').write_text(json.dumps(integration, ensure_ascii=False, indent=2) + '\n')
    (dst / 'README.md').write_text(f'# EP.{meta["ep"]:02d}《{meta["title"]}》\n\n'
        f'2026-10-24 Codex 重制，实测 {report["frames"]} 帧。现行制作与检查入口：'
        f'[episodes-codex/{slug}](../../episodes-codex/{slug}/README.md)。\n\n'
        '本站使用检查通过的冻结成片和字幕，保留原发布日期、首发版本与历史平台链接。'
        '文章仅在站点接入层补章节锚点，变换记录见 site-integration.json。旧 remotion/ 目录为历史工程，'
        '现行源码以 meta.json 的 sourcePath 为准。\n')
    print(f'EP{meta["ep"]:02d} {slug}: integrated {len(copied)} frozen assets; preserved historical metadata')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--slugs', nargs='+', choices=SLUGS, default=SLUGS)
    args = p.parse_args()
    for slug in args.slugs:
        integrate(slug)


if __name__ == '__main__':
    main()
