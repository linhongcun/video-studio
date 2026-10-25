"""Freeze the MQ-practice revision and its actual Java-card body derivation."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
BODY = 'revisions/mq-practice/voiced-body'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if '--verify' in sys.argv:
    manifest = json.loads((D/'source-sha256.json').read_text())
    failures = [name for name, expected in manifest.items()
                if not (D/name).is_file() or sha(D/name) != expected]
    assert not failures, failures
    print(f'{len(manifest)} MQ-practice inputs unchanged')
else:
    helper = ROOT/'episodes-codex/_shared/append_java_endcard.py'
    subprocess.run([sys.executable, str(helper), 'verify', str(D),
                    '--body-dir', BODY], check=True)
    (D/'remotion/src/placeholders').mkdir(parents=True, exist_ok=True)
    sys.argv = ['freeze_sentence_episode.py', str(D)]
    runpy.run_path(str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),
                   run_name='__main__')
    manifest = json.loads((D/'source-sha256.json').read_text())
    extras = [Path(__file__).resolve(), helper, D/'voice/jobs-mq-practice.json', D/'voice/jobs-mq-correction.json']
    extras += list((D/'revisions/mq-practice').glob('research-*.json'))
    for base in [D/BODY, D/'demo-java', D/'revisions/mq-practice/baseline', D/'remotion/scripts', ROOT/'episodes-codex/_shared/middleware-identity']:
        if base.is_dir():
            extras.extend(p for p in base.rglob('*') if p.is_file()
                          and not any(x in {'node_modules', '__pycache__', 'out'} for x in p.parts)
                          and p.suffix not in {'.class', '.pyc', '.mp4'})
    for path in extras:
        manifest[os.path.relpath(path, D)] = sha(path)
    (D/'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())),
                                      ensure_ascii=False, indent=2)+'\n')
    print(f'{len(manifest)} inputs frozen including actual MQ-practice voiced body')
