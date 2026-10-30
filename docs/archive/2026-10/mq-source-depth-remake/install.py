#!/usr/bin/env python3
"""Install four reviewed remakes while preserving published identities and covers."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import shutil
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
HERE = Path(__file__).resolve().parent
SLUGS = ['message-queue', 'kafka-consumer-groups', 'kafka-log-replay', 'kafka-send-confirmation']
SUMMARIES = {
    'message-queue': '沿同一订单事件展开编码、日志追加、按位置拉取与业务执行，理解已受理为什么还没完成。',
    'kafka-consumer-groups': '从分区归属表的计算、安装与读取请求，解释同组怎样分工，不同组为什么各读一份。',
    'kafka-log-replay': '跟踪保存的恢复值怎样装回内存并成为读取请求的起点，解释重启重读与日志保留边界。',
    'kafka-send-confirmation': '展开批次缓冲、后台在途状态、结果完成与Broker判重，分清调用返回、发送证据和业务完成。',
}


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def derived_article(slug, source):
    plan = read(HERE / 'article-anchor-plan.json')['episodes'][slug]
    assert sha(source) == plan['frozenSourceSHA256']
    text = source.read_text()
    grouped = {}
    for old_id, heading in plan['aliasesBeforeHeading'].items():
        grouped.setdefault(heading, []).append(old_id)
    for heading, old_ids in grouped.items():
        assert text.count(heading) == 1
        aliases = ''.join(f'<span id="{old_id}"></span>\n' for old_id in old_ids)
        text = text.replace(heading, aliases + '\n' + heading, 1)
    relative_figures = text.count('<Figure src="article/')
    text = text.replace('<Figure src="article/', f'<Figure src="/video-studio/episodes/{slug}/article/')
    return text, {**plan, 'relativeFigureSourcesExpanded': relative_figures}


def install(slug, stamp, preflight_only=False):
    d = ROOT / 'episodes-codex' / slug / 'revisions/source-depth-v2'
    dest = ROOT / 'episodes' / slug
    before = read(HERE / 'publication-before.json')[slug]
    current = read(dest / 'meta.json')
    for key in ['slug', 'ep', 'title', 'createdAt', 'publishedAt', 'firstRelease', 'platforms', 'poster']:
        assert current.get(key) == before.get(key), ('Published identity changed', slug, key)
    config = read(d / 'episode-config.json')
    assert config['slug'] == slug and config['ep'] == current['ep'] and config['title'] == current['title']
    result = read(d / 'render-result.json')
    receipt = read(d / 'reference-appendix.json')
    media = read(d / 'reference-appendix-media-check.json')
    actual = sha(d / 'video.mp4')
    assert result['sha256'] == receipt['outputSHA256'] == actual
    assert media['passed'] is True and media['outputSHA256'] == actual
    assert result['publicationMetadata']['finalVideoFrames'] == receipt['finalVideoFrames']
    for rel, expected in read(d / 'source-sha256.json').items():
        assert sha(d / rel) == expected, ('Frozen input changed', slug, rel)
    figures = read(d / 'article-figure-plan.json')['figures']
    exported = read(d / 'article-figures-export.json')
    assert exported['videoSHA256'] == actual and exported['visualReviewed'] is True
    assert [(x['file'], x['frame']) for x in exported['figures']] == [(x['file'], x['frame']) for x in figures]
    figure_hashes = {x['file']: x['sha256'] for x in exported['figures']}
    assert figures
    for fig in figures:
        assert type(fig['frame']) is int and 0 <= fig['frame'] < result['bodyFrames']
        assert abs(fig['seconds'] - fig['frame'] / 30) < 1e-8
        assert (d / fig['file']).is_file()
        assert sha(d / fig['file']) == figure_hashes[fig['file']]
    required = ['video.mp4', 'article.mdx', 'script.md', 'storyboard.json', 'words.json',
                'captions.srt', 'research.md', 'pronunciation.md', 'references.json',
                'reference-appendix.json', 'reference-appendix-media-check.json', 'render-result.json']
    optional = ['article-sources.json', 'knoll-props.md']
    sources = [d / n for n in required]
    sources += [d / n for n in optional if (d / n).is_file()]
    sources += [p for p in (d / 'article').rglob('*') if p.is_file()]
    protected_covers = {p.name: sha(p) for p in dest.glob('cover-*') if p.is_file()}
    if (dest / before['poster']).is_file():
        protected_covers[before['poster']] = sha(dest / before['poster'])
    baseline_blobs = read(HERE / 'baseline.json')['protectedGitBlobs']
    for name in protected_covers:
        relative = str((dest / name).relative_to(ROOT))
        assert subprocess.check_output(['git', 'hash-object', str(dest / name)], text=True, cwd=ROOT).strip() == baseline_blobs[relative], ('Cover differs from startup baseline', slug, name)
    assert all(source.is_file() for source in sources), ('Missing publication source', slug)
    article, anchor_plan = derived_article(slug, d / 'article.mdx')
    if preflight_only:
        return {'slug': slug, 'preflight': 'passed'}
    installed = {}
    for source in sources:
        assert source.is_file(), source
        rel = source.relative_to(d)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if str(rel) == 'article.mdx':
            target.write_text(article)
        else:
            shutil.copyfile(source, target)
            assert sha(target) == sha(source)
        installed[str(rel)] = sha(target)
    current.update(updatedAt=stamp, sourcePath=str((d / 'remotion').relative_to(ROOT)),
                   targetDuration=result['seconds'], burnedInCaptions=True,
                   **result['publicationMetadata'])
    current.update(summary=SUMMARIES[slug], description=SUMMARIES[slug])
    # Source owners may supply concise, content-specific descriptions without changing identity.
    for key in ['summary', 'description']:
        if isinstance(config.get(key), str) and config[key].strip():
            current[key] = config[key]
    (dest / 'meta.json').write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n')
    installed['meta.json'] = sha(dest / 'meta.json')
    for name, expected in protected_covers.items():
        assert sha(dest / name) == expected, ('Cover changed', slug, name)
    return {'slug': slug, 'production': str(d.relative_to(ROOT)), 'files': installed,
            'preservedCovers': protected_covers, 'videoSHA256': actual,
            'articleDerivation': {'frozenSourceSHA256': anchor_plan['frozenSourceSHA256'],
                                  'publishedSHA256': installed['article.mdx'],
                                  'change': 'Legacy anchor spans and equivalent same-episode Figure source prefix normalization only; prose, quotes, Figure times/captions and actual image files unchanged',
                                  'relativeFigureSourcesExpanded': anchor_plan['relativeFigureSourcesExpanded'],
                                  'aliases': anchor_plan['aliasesBeforeHeading']},
            'frames': receipt['finalVideoFrames'], 'seconds': result['seconds']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', required=True)
    args = parser.parse_args()
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    # Check all four before the first site-input write. Owners have stopped at frozen inputs.
    for slug in SLUGS:
        install(slug, stamp, preflight_only=True)
    records = [install(slug, stamp) for slug in SLUGS]
    (HERE / 'publication-files.json').write_text(json.dumps(
        {'installedAt': stamp, 'scope': 'Local site inputs; remote publishing is separate.', 'episodes': records},
        ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'installedEpisodes': len(records), 'updatedAt': stamp}))


if __name__ == '__main__':
    main()
