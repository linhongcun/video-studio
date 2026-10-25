"""Thin D03 revision freezer: canonical source freeze plus explicit real Java body."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
REVISION = D / 'revisions/business-boundary-v2'
BODY = REVISION / 'voiced-body'
manifest_path = D / 'source-sha256.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if '--verify' in sys.argv:
    manifest = json.loads(manifest_path.read_text())
    failures = [name for name, expected in manifest.items()
                if not (D / name).is_file() or sha(D / name) != expected]
    assert not failures, failures
    print(f'{len(manifest)} D03 revision production/reference inputs unchanged')
else:
    subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/append_java_endcard.py'),
                    'verify', str(D), '--body-dir', str(BODY)], check=True)
    sys.argv = ['freeze_sentence_episode.py', str(D)]
    runpy.run_path(str(ROOT / 'episodes-codex/_shared/freeze_sentence_episode.py'), run_name='__main__')
    manifest = json.loads(manifest_path.read_text())
    extras = [Path(__file__).resolve(), ROOT / 'episodes-codex/_shared/append_java_endcard.py',
              REVISION / 'baseline/baseline-manifest.json', D / 'check-encoded-voice.py',
              REVISION / 'previous-track/manifest.json']
    for folder in [D / 'sources', D / 'demo-java', BODY, D / 'remotion/scripts']:
        extras += [path for path in folder.rglob('*') if path.is_file()
                   and not any(part in {'node_modules', 'out', '__pycache__'} for part in path.parts)
                   and path.suffix not in {'.class', '.pyc'}]
    # The old candidate remains an immutable reference, not a source for new speech.
    extras += [path for path in (REVISION / 'baseline').rglob('*')
               if path.is_file() and 'voice' not in path.relative_to(REVISION / 'baseline').parts]
    for name in ['voice/jobs-business-boundary-v2.json', 'voice/signal-audit.py']:
        if (D / name).is_file(): extras.append(D / name)
    for path in extras:
        assert path.is_file(), path
        manifest[os.path.relpath(path, D)] = sha(path)
    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
    print(f'{len(manifest)} D03 revision inputs frozen; actual Java body and read sources included')
