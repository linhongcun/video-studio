"""D03 thin freeze entry: shared Java-tail gate plus read source evidence."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
verify = '--verify' in sys.argv
helper = ROOT / 'episodes-codex/_shared/freeze_pattern_flow_episode.py'
sys.argv = [str(helper), str(D)] + (['--verify'] if verify else [])
runpy.run_path(str(helper), run_name='__main__')
if not verify:
    manifest_path = D / 'source-sha256.json'
    manifest = json.loads(manifest_path.read_text())
    for folder in [D / 'sources', D / 'revisions/visual-preflight-v1', D / 'revisions/order-status-copyfix']:
        for path in folder.rglob('*'):
            if path.is_file():
                manifest[os.path.relpath(path, D)] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
    print(f'{len(manifest)} D03 inputs frozen, including actual official-source evidence')
