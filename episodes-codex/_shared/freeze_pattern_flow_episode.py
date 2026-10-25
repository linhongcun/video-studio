"""Freeze this pattern-flow revision without changing any older shared freezer.

The checked voiced body and the explicit Java tail are separate, reproducible
inputs. Baseline files are immutable references for scoped reuse and review.
"""
from pathlib import Path
import hashlib
import json
import os
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
assert len(sys.argv) in (2, 3), 'Usage: freeze_pattern_flow_episode.py EPDIR [--verify]'
D = Path(sys.argv[1]).resolve()
manifest_path = D / 'source-sha256.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if '--verify' in sys.argv:
    manifest = json.loads(manifest_path.read_text())
    failures = [name for name, expected in manifest.items()
                if not (D / name).is_file() or sha(D / name) != expected]
    assert not failures, failures
    print(f'{len(manifest)} pattern-flow production/reference inputs unchanged')
else:
    subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/append_java_endcard.py'),
                    'verify', str(D)], check=True)
    (D / 'remotion/src/placeholders').mkdir(parents=True, exist_ok=True)
    sys.argv = ['freeze_sentence_episode.py', str(D)]
    runpy.run_path(str(ROOT / 'episodes-codex/_shared/freeze_sentence_episode.py'), run_name='__main__')
    manifest = json.loads(manifest_path.read_text())
    extra = [Path(__file__).resolve()]
    extra += [ROOT / 'episodes-codex/_shared' / name for name in
              ['append_java_endcard.py', 'audit_sentence_reuse.py']]
    extra += [path for path in (D / 'voice').glob('flow-*') if path.is_file()]
    if (D / 'voice/jobs-flow-ui-java.json').is_file():
        extra.append(D / 'voice/jobs-flow-ui-java.json')
    if (D / 'freeze.py').is_file():
        extra.append(D / 'freeze.py')
    for name in ['render-plan.json', 'tail-reuse-proof.json', 'local-timing-comparison.json']:
        if (D / 'revisions/flow-ui-java' / name).is_file():
            extra.append(D / 'revisions/flow-ui-java' / name)
    # The card JSON is already included by the canonical src/ walk. Add the
    # compiled example's source/evidence and the exact body from which we padded.
    for base in [D / 'demo-java', D / 'revisions/flow-ui-java/voiced-body',
                 D / 'revisions/flow-ui-java/baseline']:
        if base.is_dir():
            extra += [path for path in base.rglob('*')
                      if path.is_file() and not any(part in {'node_modules', 'out', '__pycache__'}
                                                    for part in path.parts)
                      and path.suffix not in {'.class', '.pyc'}]
    extra += [path for path in (D / 'remotion/scripts').glob('*')
              if path.is_file() and path.suffix in {'.mjs', '.cjs', '.py'}]
    for path in extra:
        assert path.is_file(), path
        manifest[os.path.relpath(path, D)] = sha(path)
    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False,
                                        indent=2) + '\n')
    print(f'{len(manifest)} inputs frozen, including Java-tail derivation and baseline references')
