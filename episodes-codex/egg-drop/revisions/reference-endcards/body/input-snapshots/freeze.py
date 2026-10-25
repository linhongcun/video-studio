#!/usr/bin/env python3
"""Use the shared freezer and pin P05's own mathematical/production inputs."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys

D = Path(__file__).resolve().parent
ROOT = D.parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if sys.argv[1:] == ['--verify']:
    manifest = json.loads((D / 'source-sha256.json').read_text())
    mismatches = [rel for rel, sha in manifest.items()
                  if not (D / rel).is_file() or digest(D / rel) != sha]
    assert not mismatches, mismatches
    print(json.dumps({'inputs': len(manifest), 'status': 'passed'}, ensure_ascii=False))
else:
    assert not sys.argv[1:], 'Usage: freeze.py [--verify]'
    sys.argv = [str(ROOT / 'episodes-codex/_shared/freeze_sentence_episode.py'), str(D)]
    runpy.run_path(sys.argv[0], run_name='__main__')
    manifest = json.loads((D / 'source-sha256.json').read_text())
    extras = [Path(__file__).resolve(), D / 'assemble.py', D / 'research-math.md',
              D / 'verify_math.py', D / 'voice/input-provenance.json',
              D / 'voice/final-cover-sync.json', D / 'cover-source-reuse.json']
    # The revised track is an exact composition, not a full-track rebuild.
    # Pin every persistent input consumed by its shared-build mini/wrapper.
    extras += [D / 'build_binary_voice.py',
               D / 'voice/binary-input-provenance.json',
               D / 'voice/binary-narration-sha256.json',
               D / 'voice/binary-opening-composition.json']
    baseline = D / 'revisions/binary-opening/baseline'
    extras += [baseline / name for name in [
        'voice.wav', 'storyboard.json', 'voice/build.json', 'voice/input-provenance.json',
        'voice/script-narration-sha256.json']]
    dependencies = json.loads((D / 'voice/binary-dependencies.json').read_text())
    for rel, expected in dependencies['requiredProductionInputs'].items():
        assert digest(D / rel) == expected, ('Binary revision input changed', rel)
        extras.append(D / rel)
    extras += [D / 'voice/binary-audio-inputs.json',
               D / 'voice/binary-dependencies.json', D / 'voice/binary-qa.md',
               D / 'voice/binary-mini/audit.py']
    mini = D / 'voice/binary-mini'
    extras += [mini / name for name in [
        'voice.wav', 'voice/params.json', 'voice/sents.json',
        'voice/picks.json', 'voice/build.json', 'voice/input-provenance.json']]
    mini_picks = json.loads((mini / 'voice/picks.json').read_text())
    for row in json.loads((mini / 'voice/sents.json').read_text()):
        stem = f"{row['id']}-{mini_picks[row['id']]}"
        extras += [mini / 'voice/takes' / (stem + suffix)
                   for suffix in ['.raw.wav', '.wav', '.txt.json']]
    extras += [p for p in (D / 'remotion/scripts').rglob('*')
               if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    for path in extras:
        manifest[os.path.relpath(path, D)] = digest(path)
    (D / 'source-sha256.json').write_text(json.dumps(dict(sorted(manifest.items())),
        ensure_ascii=False, indent=2) + '\n')
    print(f'{len(manifest)} P05 production inputs frozen')
