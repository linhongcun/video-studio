"""Freeze the observer-first revision and its actual Java-card body derivation."""

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
import runpy
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
BODY = 'revisions/observer-first/voiced-body'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if '--verify' in sys.argv:
    manifest = json.loads((D/'source-sha256.json').read_text())
    failures = [name for name, expected in manifest.items()
                if not (resolve_frozen_path(D/'source-sha256.json', name)).is_file() or sha(resolve_frozen_path(D/'source-sha256.json', name)) != expected]
    assert not failures, failures
    print(f'{len(manifest)} observer-first inputs unchanged')
else:
    helper = ROOT/'episodes/_shared/append_java_endcard.py'
    subprocess.run([sys.executable, str(helper), 'verify', str(D),
                    '--body-dir', BODY], check=True)
    (D/'remotion/src/placeholders').mkdir(parents=True, exist_ok=True)
    sys.argv = ['freeze_sentence_episode.py', str(D)]
    runpy.run_path(str(ROOT/'episodes/_shared/freeze_sentence_episode.py'),
                   run_name='__main__')
    manifest = json.loads((D/'source-sha256.json').read_text())
    extras = [Path(__file__).resolve(), helper, D/'voice/jobs-observer-first.json', D/'voice/observer-first-reuse.json', D/'voice/observer-first-inputs.json']
    extras += list((D/'revisions/mq-practice').glob('research-*.json'))
    for base in [D/BODY, D/'demo-java', D/'revisions/observer-first/baseline', D/'remotion/scripts', ROOT/'episodes/_shared/middleware-identity']:
        if base.is_dir():
            extras.extend(p for p in base.rglob('*') if p.is_file()
                          and not any(x in {'node_modules', '__pycache__', 'out'} for x in p.parts)
                          and p.suffix not in {'.class', '.pyc', '.mp4'})
    # Current reference inputs are separate from the preserved 4442-frame core.
    extras += [D/'references.json', D/'article.mdx', D/'remotion/package.json',
               ROOT/'episodes/_shared/append_references_original.py',
               ROOT/'episodes/_shared/append_references.py',
               ROOT/'episodes/_shared/render_with_references.py',
               ROOT/'episodes/_shared/requirements-reference-appendix.txt',
               ROOT/'site/scripts/check-references.mjs',
               ROOT/'episodes/_shared/theme/pageTheme.ts',
               ROOT / 'episodes/_shared/episode_paths.py',
               ROOT / 'site/scripts/episode-paths.mjs']
    for source in json.loads((D/'references.json').read_text())['sources']:
        evidence_paths = [source['verification']['evidence'], source['titleEvidence']['evidence']]
        if 'quotation' in source:
            evidence_paths.append(source['quotation']['evidence'])
        extras.extend(resolve_repo_path(evidence, root=ROOT) for evidence in evidence_paths)
    extras += [ROOT/'episodes/_shared/append_references_bibliography.py']
    for path in extras:
        manifest[os.path.relpath(path, D)] = sha(path)
    (D/'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())),
                                      ensure_ascii=False, indent=2)+'\n')
    print(f'{len(manifest)} inputs frozen including actual observer-first voiced body')
