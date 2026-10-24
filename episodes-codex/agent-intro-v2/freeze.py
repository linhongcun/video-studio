"""Freeze shared production inputs plus the actual episode wrappers and QA scripts."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys

D = Path(__file__).resolve().parent
sys.argv = [str(D.parent / '_shared/freeze_sentence_episode.py'), str(D)]
runpy.run_path(sys.argv[0], run_name='__main__')
manifest = json.loads((D / 'source-sha256.json').read_text())
files = [D / 'assemble.py', D / 'freeze.py', D / 'voice/audit-takes.py']
files += [p for p in (D / 'remotion/scripts').rglob('*') if p.is_file()]
files += sorted((D / 'voice').glob('jobs*.json'))
files += [D / 'voice/input-freeze.json']
for p in files:
    manifest[os.path.relpath(p, D)] = hashlib.sha256(p.read_bytes()).hexdigest()
(D / 'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
print(f'{len(manifest)} actual production inputs frozen, including local wrappers and render/QA scripts.')
