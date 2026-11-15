"""Freeze LC15 inputs and the actual shared rendering dependency closure."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

EP = Path(__file__).resolve().parent
ROOT = next(p for p in EP.parents if (p / 'AGENTS.md').is_file())
manifest = EP / 'source-sha256.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run([sys.executable, str(EP / 'scripts/require_formal_inputs.py')], check=True)
if '--verify' in sys.argv:
    inputs = json.loads(manifest.read_text())
    for relative, expected in inputs.items():
        assert sha((EP / relative).resolve()) == expected, relative
    print(f'{len(inputs)} LC15 frozen inputs unchanged.')
    raise SystemExit

required = [
    'plan.json', 'episode-config.json', 'solution.py', 'solution.json', 'three_sum_trace.py',
    'trace/main-example.json', 'storyboard-design.md', 'visual-direction.md',
    'references.json', 'script.md', 'article.mdx', 'pronunciation.md', 'research.md',
    'research/source-evidence.json', 'README.md', 'assemble.py', 'prepare_code_endcard.py',
    'render.py', 'render_body.py', 'references_bt709.py', 'freeze.py', 'requirements-runtime.txt', 'cover-style.json',
    '../publication/article/01.svg', 'voice/params.json',
    'qa/independent-review-4ba29a5a.md', 'qa/independent-rereview-20208508.md',
]
for relative in required:
    assert (EP / relative).is_file(), f'Missing required input: {relative}'
subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/freeze_sentence_episode.py'), str(EP)], check=True)
inputs = json.loads(manifest.read_text())
files = [EP / relative for relative in required]
for folder in ('scripts', 'tests', 'cover-inputs', 'covers'):
    files += [p for p in (EP / folder).rglob('*')
              if p.is_file() and '__pycache__' not in p.parts]
shared = [
    'episodes/_shared/assemble_sentence_episode.py', 'episodes/_shared/freeze_sentence_episode.py',
    'episodes/_shared/render_with_references.py', 'episodes/_shared/append_references_bibliography.py',
    'episodes/_shared/append_references_original.py', 'episodes/_shared/append_references.py',
    'episodes/_shared/requirements-reference-appendix.txt', 'episodes/_shared/leetcode-video/references.py',
    'episodes/_shared/leetcode-video/Frame.tsx', 'episodes/_shared/leetcode-video/theme.ts',
    'episodes/_shared/leetcode-video/identities-v1.json', 'episodes/_shared/leetcode-video/style-v1.json',
    'episodes/_shared/puzzles-video/references.py', 'site/scripts/check-references.mjs',
    'episodes/_shared/leetcode-covers/render.py', 'episodes/_shared/leetcode-covers/template.mjs',
    'episodes/_shared/leetcode-covers/catalog.json', 'episodes/_shared/leetcode-covers/diagrams.mjs',
]
files += [ROOT / relative for relative in shared]
for p in files:
    inputs[os.path.relpath(p, EP)] = sha(p)
manifest.write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + '\n')
print(f'{len(inputs)} LC15 production inputs frozen.')
