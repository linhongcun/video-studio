#!/usr/bin/env python3
"""Freeze the actual current episode inputs through the shared freezer."""

# Resolve episode storage independently of its series and revision depth.
import sys as _layout_sys
from pathlib import Path as _LayoutPath
_layout_root = next(parent for parent in _LayoutPath(__file__).resolve().parents
                    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
_layout_sys.path.insert(0, str(_layout_root / 'episodes/_shared'))
from episode_paths import production_directory, publication_directory, resolve_repo_path, episode_slug, resolve_frozen_path
from pathlib import Path
import hashlib, json, os, runpy, sys
D = Path(__file__).resolve().parent
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
if sys.argv[1:] == ['--verify']:
    manifest = json.loads((D/'source-sha256.json').read_text())
    failures = [rel for rel, digest in manifest.items() if not (resolve_frozen_path(D/'source-sha256.json', rel)).is_file() or sha(resolve_frozen_path(D/'source-sha256.json', rel)) != digest]
    assert not failures, failures
    print(json.dumps({'status':'passed','inputs':len(manifest)}))
else:
    assert not sys.argv[1:], 'Usage: freeze.py [--verify]'
    sys.argv = [str(ROOT/'episodes/_shared/freeze_sentence_episode.py'), str(D)]
    runpy.run_path(sys.argv[0],run_name='__main__')
    manifest = json.loads((D/'source-sha256.json').read_text())
    extras = [Path(__file__).resolve(), D/'assemble.py', D/'voice/input-provenance.json', D/'model.json', D/'voice/audit_takes.py']
    extras += [p for p in (D/'remotion/scripts').rglob('*') if p.is_file()]
    extras += list((D/'voice').glob('jobs*.json'))
    extras += [p for p in D.glob('*.py') if p.name != 'freeze.py']
    for path in extras:
        if path.is_file(): manifest[os.path.relpath(path,D)] = sha(path)
    (D/'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())),ensure_ascii=False,indent=2)+'\n')
    print(f'{len(manifest)} current production inputs frozen')
