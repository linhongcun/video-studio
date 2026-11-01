#!/usr/bin/env python3
"""Freeze/verify the append-only stage; never rewrites the body169 manifest."""

# Resolve episode storage independently of its series and revision depth.
import sys as _layout_sys
from pathlib import Path as _LayoutPath
_layout_root = next(parent for parent in _LayoutPath(__file__).resolve().parents
                    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
_layout_sys.path.insert(0, str(_layout_root / 'episodes/_shared'))
from episode_paths import production_directory, publication_directory, resolve_repo_path, episode_slug, resolve_frozen_path
from pathlib import Path
import hashlib
import json
import os
import sys

D = Path(__file__).resolve().parent
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
R = D / 'revisions/reference-endcards'
MANIFEST = R / 'append-source-sha256.json'
BODY_SHA = 'b43510f3196f92964d21a3b854941a65f4af33fffd2484c171ca518f9f747c66'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if sys.argv[1:] == ['--verify']:
    manifest = json.loads(MANIFEST.read_text())
    bad = [rel for rel, value in manifest.items() if not (resolve_frozen_path(MANIFEST, rel)).is_file() or sha(resolve_frozen_path(MANIFEST, rel)) != value]
    assert not bad, bad
    print(json.dumps({'stage':'append-only','inputs':len(manifest),'passed':True}))
else:
    assert not sys.argv[1:]
    assert sha(R/'body/video.mp4') == BODY_SHA
    refs = json.loads((D/'references.json').read_text())
    files = [Path(__file__).resolve(), D/'references.json', D/'article.mdx',
             R/'body/video.mp4', R/'body/source-sha256.json', R/'body/identity.json',
             ROOT/'episodes/_shared/append_references.py',
             ROOT/'episodes/_shared/requirements-reference-appendix.txt',
             ROOT/'episodes/_shared/theme/pageTheme.ts',
             ROOT/'site/scripts/check-references.mjs',
             Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
             Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'),
             ROOT / 'episodes/_shared/episode_paths.py',
             ROOT / 'site/scripts/episode-paths.mjs']
    files += [resolve_repo_path(ref['verification']['evidence'], root=ROOT) for ref in refs['sources']]
    manifest = {os.path.relpath(path,D):sha(path) for path in sorted(set(files))}
    assert not MANIFEST.exists(), 'Append inputs are immutable; use a distinct revision for new inputs'
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'stage':'append-only','inputs':len(manifest),'manifest':str(MANIFEST)}))
