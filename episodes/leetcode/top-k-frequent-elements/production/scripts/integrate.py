#!/usr/bin/env python3
"""Stage checked LC347 outputs. Default prints a plan; no version bump or deploy."""
from pathlib import Path
import argparse
from datetime import datetime
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
D = Path(__file__).resolve().parents[1]
P = D.parent / 'publication'
NAMES = ['video.mp4', 'article.mdx', 'script.md', 'research.md', 'pronunciation.md',
         'storyboard.json', 'words.json', 'covers.json', 'render-result.json',
         'captions.srt', 'references.json', 'reference-appendix.json',
         'reference-appendix-media-check.json', 'cover-style.json',
         'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg', 'poster.jpg']
OPTIONAL = ['article-sources.json', 'solution.py', 'solution.json']
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--make-public', action='store_true', help='Set draft=false after the caller has completed QA.')
    parser.add_argument('--published-at', help='Actual first-publication ISO timestamp; required for a new public episode.')
    parser.add_argument('--first-release', help='Actual planned Release tag for the first publication.')
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({'status': 'prepared-not-executed', 'production': str(D.relative_to(ROOT)),
                          'publication': str(P.relative_to(ROOT)), 'required': NAMES,
                          'missing': [n for n in NAMES if not (D / n).is_file()],
                          'notes': ['Checks actual freeze and bibliography output before copying.',
                                    'Copies the frozen article verbatim and checks media SHA.',
                                    'Preserves creation time and platform metadata; no site version change or deployment.']},
                         ensure_ascii=False, indent=2))
        return
    assert all((D / n).is_file() for n in NAMES), 'Required checked output is missing'
    assert (P / 'meta.json').is_file(), 'Create truthful draft metadata first'
    before = read(P / 'meta.json')
    assert before['slug'] == 'top-k-frequent-elements' and before['series'] == 'leetcode'
    subprocess.run([sys.executable, str(D / 'freeze.py'), '--verify'], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(D / 'render.py'), '--verify'], cwd=ROOT, check=True)
    result, storyboard = read(D / 'render-result.json'), read(D / 'storyboard.json')
    assert sha(D / 'video.mp4') == result.get('sha256', result.get('videoSha256')), 'Actual final media differs'
    publication = result['publicationMetadata']
    assert result['frames'] == publication['finalVideoFrames']
    meta = dict(before)
    meta.update(video='video.mp4', poster='cover-16x9.jpg',
                sourcePath=str((D / 'remotion').relative_to(ROOT)),
                finalVideoFrames=publication['finalVideoFrames'],
                referenceAppendix=publication['referenceAppendix'],
                targetDuration=round(result['frames'] / storyboard['meta']['fps']),
                burnedInCaptions=True)
    if args.make_public:
        if not meta.get('publishedAt'):
            assert args.published_at and args.first_release, 'First publication needs actual timestamp and Release tag'
            assert datetime.fromisoformat(args.published_at.replace('Z', '+00:00')).tzinfo, 'Timestamp needs timezone'
            meta.update(publishedAt=args.published_at, firstRelease=args.first_release)
        meta['draft'] = False
    copied = {}
    for name in NAMES + [n for n in OPTIONAL if (D / n).is_file()]:
        shutil.copy2(D / name, P / name)
        assert sha(P / name) == sha(D / name), name
        copied[name] = sha(P / name)
    if (D / 'article').is_dir():
        shutil.copytree(D / 'article', P / 'article', dirs_exist_ok=True)
        for file in (D / 'article').rglob('*'):
            if file.is_file():
                rel = file.relative_to(D)
                assert sha(P / rel) == sha(file), str(rel)
                copied[str(rel)] = sha(file)
    for key in ['createdAt', 'updatedAt', 'platforms', 'series', 'tags', 'related']:
        assert meta.get(key) == before.get(key), f'Unexpected metadata change: {key}'
    (P / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    receipt = {'status': 'staged-locally', 'copied': copied,
               'productionArticleSha256': sha(D / 'article.mdx'),
               'siteArticleSha256': sha(P / 'article.mdx'),
               'articleChanges': 'None; exact frozen production article.',
               'mediaSha256': sha(P / 'video.mp4'), 'frames': result['frames'],
               'sourcePath': meta['sourcePath'], 'draft': meta['draft'], 'deployed': False}
    (P / 'site-integration.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'copied': len(copied), 'draft': meta['draft']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
