"""Pin this new production without rewriting either previous release's inputs."""

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
import subprocess
import sys

EP = Path(__file__).resolve().parent
ROOT = next(p for p in EP.parents if (p / 'AGENTS.md').is_file())
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if '--verify' in sys.argv:
    manifest = read(EP / 'source-sha256.json')
    for rel, expected in manifest.items():
        assert sha(resolve_frozen_path(EP / 'source-sha256.json', rel)) == expected, rel
    for absolute, expected in read(EP / 'font-bindings.json')['files'].items():
        assert sha(Path(absolute)) == expected, absolute
    print(f'{len(manifest)} frozen inputs unchanged.')
    raise SystemExit(0)
subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/freeze_sentence_episode.py'), str(EP)], check=True)
manifest = read(EP / 'source-sha256.json')
paths = [EP / name for name in ('solution.py', 'solution.json', 'references.json', 'prepare_code_endcard.py', 'render.py', 'render_body.py', 'freeze.py', 'font-bindings.json')]
paths += [p for p in (EP / 'research').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
paths += [EP / 'voice' / n for n in ('matrix-reuse-provenance.json', 'script-narration-sha256.json')]
paths += [ROOT / 'episodes/_shared' / n for n in ('render_with_references.py', 'append_references_bibliography.py', 'append_references_original.py', 'append_references.py', 'requirements-reference-appendix.txt')]
paths += [ROOT / 'episodes/_shared/leetcode-video' / n for n in ('Frame.tsx', 'theme.ts', 'style-v1.json', 'identities-v1.json', 'references.py')]
paths += [ROOT / 'episodes/_shared/puzzles-video/references.py', ROOT / 'site/scripts/check-references.mjs',
          ROOT / 'episodes/_shared/episode_paths.py',
          ROOT / 'site/scripts/episode-paths.mjs']
# Original evidence retains its original retrieval dates, paths and bytes.
old_research = ROOT / 'episodes/leetcode/number-of-provinces/production/research'
paths += [p for p in old_research.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
paths += [p for p in (EP / 'remotion/scripts').rglob('*') if p.is_file()]
for source in read(EP / 'references.json')['sources']:
    paths += [resolve_repo_path(source['verification']['evidence'], root=ROOT), resolve_repo_path(source['titleEvidence']['evidence'], root=ROOT)]
    if source.get('quotation'):
        paths.append(resolve_repo_path(source['quotation']['evidence'], root=ROOT))
for path in paths:
    manifest[os.path.relpath(path, EP)] = sha(path)
(EP / 'source-sha256.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(f'{len(manifest)} actual production inputs frozen.')
