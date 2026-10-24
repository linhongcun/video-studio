"""Use the shared freezer, then include this episode's executable evidence."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
manifest_path = D / 'source-sha256.json'

if '--verify' in sys.argv:
    manifest = json.loads(manifest_path.read_text())
    for rel, expected in manifest.items():
        assert hashlib.sha256((D / rel).read_bytes()).hexdigest() == expected, rel
    print(f'{len(manifest)} frozen production inputs unchanged')
else:
    sys.argv = ['freeze_sentence_episode.py', str(D)]
    runpy.run_path(str(ROOT / 'episodes-codex/_shared/freeze_sentence_episode.py'), run_name='__main__')
    manifest = json.loads(manifest_path.read_text())
    extra = [Path(__file__).resolve()]
    extra += [p for p in (D / 'demo').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    extra += [p for p in (D / 'remotion/scripts').glob('*.mjs')]
    for p in extra:
        manifest[str(p.relative_to(D))] = hashlib.sha256(p.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=2) + '\n')
    print(f'{len(manifest)} total inputs frozen, including executable pricing evidence')
