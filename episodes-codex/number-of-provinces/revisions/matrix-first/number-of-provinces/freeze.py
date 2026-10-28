"""Pin this new production without rewriting either previous release's inputs."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

EP = Path(__file__).resolve().parent
ROOT = next(p for p in EP.parents if (p / 'AGENTS.md').is_file())
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if '--verify' in sys.argv:
    manifest = read(EP / 'source-sha256.json')
    for rel, expected in manifest.items():
        assert sha(EP / rel) == expected, rel
    for absolute, expected in read(EP / 'font-bindings.json')['files'].items():
        assert sha(Path(absolute)) == expected, absolute
    print(f'{len(manifest)} frozen inputs unchanged.')
    raise SystemExit(0)
subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/freeze_sentence_episode.py'), str(EP)], check=True)
manifest = read(EP / 'source-sha256.json')
paths = [EP / name for name in ('solution.py', 'solution.json', 'references.json', 'prepare_code_endcard.py', 'render.py', 'render_body.py', 'freeze.py', 'font-bindings.json')]
paths += [p for p in (EP / 'research').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
paths += [EP / 'voice' / n for n in ('matrix-reuse-provenance.json', 'script-narration-sha256.json')]
paths += [ROOT / 'episodes-codex/_shared' / n for n in ('render_with_references.py', 'append_references_bibliography.py', 'append_references_original.py', 'append_references.py', 'requirements-reference-appendix.txt')]
paths += [ROOT / 'episodes-codex/_shared/leetcode-video' / n for n in ('Frame.tsx', 'theme.ts', 'style-v1.json', 'identities-v1.json', 'references.py')]
paths += [ROOT / 'episodes-codex/_shared/puzzles-video/references.py', ROOT / 'site/scripts/check-references.mjs']
# Original evidence retains its original retrieval dates, paths and bytes.
old_research = ROOT / 'episodes-codex/number-of-provinces/research'
paths += [p for p in old_research.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
paths += [p for p in (EP / 'remotion/scripts').rglob('*') if p.is_file()]
for source in read(EP / 'references.json')['sources']:
    paths += [ROOT / source['verification']['evidence'], ROOT / source['titleEvidence']['evidence']]
    if source.get('quotation'):
        paths.append(ROOT / source['quotation']['evidence'])
for path in paths:
    manifest[os.path.relpath(path, EP)] = sha(path)
(EP / 'source-sha256.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(f'{len(manifest)} actual production inputs frozen.')
