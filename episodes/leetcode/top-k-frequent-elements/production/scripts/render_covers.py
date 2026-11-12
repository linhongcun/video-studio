#!/usr/bin/env python3
"""Generate LC347 cover candidates through the shared renderer; never install other episodes.

Default is a plan. Use --execute to render, then review the candidate images.
No production/publication image is overwritten by this wrapper.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
D = Path(__file__).resolve().parents[1]
SHARED = ROOT / 'episodes/_shared/leetcode-covers'
SLUG = 'top-k-frequent-elements'
SIZES = ['16x9', '3x4', '4x3']
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--out-dir', type=Path, help='A fresh, empty candidate directory; defaults to work/lc347-cover-candidates/<timestamp>.')
    args = parser.parse_args()
    catalog = read(SHARED / 'catalog.json')
    identity = next(ep for ep in catalog['episodes'] if ep['slug'] == SLUG)
    assert identity['number'] == 347 and identity['method'] == '小顶堆'
    installed = read(D / 'cover-style.json')
    for size in SIZES:
        for ext in ['png', 'jpg']:
            assert sha(D / f'cover-{size}.{ext}') == installed['covers'][size][ext + 'Sha256'], 'Existing checked cover differs'
    assert (D / 'poster.jpg').read_bytes() == (D / 'cover-3x4.jpg').read_bytes()
    plan = {'status': 'prepared-not-executed', 'renderer': str((SHARED / 'render.py').relative_to(ROOT)),
            'identity': identity, 'installedCoversVerified': True,
            'action': 'Build a temporary metadata mirror from current published LeetCode entries plus this identity, then use the shared renderer. Retain this episode only in candidate/ after rendering.',
            'installation': 'None. Current checked production/publication bytes remain unchanged. Review candidate/ and its manifest before any explicit installation.',
            'command': 'python3 episodes/leetcode/top-k-frequent-elements/production/scripts/render_covers.py --execute'}
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = (args.out_dir or ROOT / 'work/lc347-cover-candidates' / stamp).resolve()
    assert not out.exists() or not any(out.iterdir()), 'Use a new empty output directory; preserve previous candidates'
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='lc347-cover-meta-') as tmp:
        mirror = Path(tmp)
        for source in (ROOT / 'episodes').glob('*/*/publication/meta.json'):
            metadata = read(source)
            if metadata.get('series') == 'leetcode' and not metadata.get('draft') and metadata['slug'] != SLUG:
                target = mirror / source.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        target = mirror / f'episodes/leetcode/{SLUG}/publication/meta.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        metadata = {'series': 'leetcode', 'slug': SLUG, 'problemNumber': identity['number'],
                    'title': ''.join(identity['title']) + '：' + identity['question'],
                    'tags': [identity['method']], 'draft': False}
        target.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
        subprocess.run([sys.executable, str(SHARED / 'render.py'), '--repo', str(mirror), '--out-dir', str(out / 'shared-output')], cwd=ROOT, check=True)
    report = read(out / 'shared-output/render-report.json')
    rows = [r for r in report['images'] if r['slug'] == SLUG]
    assert report['passed'] is True and {r['size'] for r in rows} == set(SIZES)
    candidate = out / 'candidate'
    candidate.mkdir()
    for row in rows:
        for ext in ['png', 'jpg']:
            source = out / 'shared-output' / SLUG / f"cover-{row['size']}.{ext}"
            assert sha(source) == row[ext + 'Sha256']
            shutil.copyfile(source, candidate / source.name)
        shutil.copyfile(out / 'shared-output' / SLUG / f"cover-{row['size']}.svg", candidate / f"cover-{row['size']}.svg")
    shutil.copyfile(candidate / 'cover-3x4.jpg', candidate / 'poster.jpg')
    snapshot = candidate / 'cover-inputs'
    snapshot.mkdir()
    for name, expected in report['inputs'].items():
        assert sha(SHARED / name) == expected, 'Source changed during render: ' + name
        shutil.copyfile(SHARED / name, snapshot / name)
    manifest = {'style': catalog['version'], 'problemNumber': 347,
                'seriesSource': 'episodes/_shared/leetcode-covers', 'sourceSha256': report['inputs'],
                'snapshot': 'cover-inputs', 'sitePoster': 'cover-16x9.jpg', 'portraitPoster': 'poster.jpg',
                'covers': {r['size']: {k: r[k] for k in ['dimensions', 'jpgSha256', 'pngSha256']} for r in rows}}
    (candidate / 'cover-style.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    receipt = {'status': 'rendered-candidates-not-installed', 'generatedAt': datetime.now(timezone.utc).isoformat(),
               'identity': identity, 'candidateDirectory': str(candidate), 'sourceSha256': report['inputs'],
               'images': rows, 'oldEpisodesInstalled': False, 'productionAssetsWritten': False,
               'review': 'Shared geometry checks passed. Actual image review is still required for this new execution.'}
    (out / 'candidate-report.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'candidateDirectory': str(candidate), 'report': str(out / 'candidate-report.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
