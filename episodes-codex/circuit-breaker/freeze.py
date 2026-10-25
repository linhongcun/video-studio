"""Freeze the actual production inputs before bundling; never validates an old MP4."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys

D = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

# A verification request must never regenerate or rewrite this manifest.
if sys.argv[1:] == ['--verify']:
    manifest = json.loads((D/'source-sha256.json').read_text())
    changed = [relative for relative, expected in manifest.items()
               if not (D/relative).is_file() or sha(D/relative) != expected]
    assert not changed, changed
    print(f'{len(manifest)} frozen inputs verified; no files written')
    raise SystemExit(0)
if sys.argv[1:]:
    raise SystemExit('Usage: freeze.py [--verify]')

sb = json.loads((D/'storyboard.json').read_text())
words = json.loads((D/'words.json').read_text())
assert not sb['meta'].get('provisionalTiming') and not sb['meta'].get('pendingAudio')
assert words['scriptSha256'] == sha(D/'script.md')
assert words['audioSha256'] == sha(D/'voice.wav')
assert (D/'voice.wav').read_bytes() == (D/'remotion/public/audio/voice.wav').read_bytes()
assert sb['meta']['durationInFrames'] == words['durationFrames']
snapshot = D/f'storyboard.{sha(D/"storyboard.json")[:8]}.json'
shutil.copy2(D/'storyboard.json', snapshot)
shutil.copy2(D/'storyboard.json', D/'remotion/src/placeholders/storyboard.json')
files = [D/f for f in ['script.md','article.mdx','research.md','pronunciation.md',
    'episode.json','assemble.py','freeze.py','verify-freeze.py','visual-direction.md','knoll-props.md',
    'storyboard.json','words.json','covers.json','voice.wav','voice/params.json',
    'voice/picks.json','voice/sents.json','voice/build.json','voice/substitutions.md',
    'remotion/package.json','remotion/package-lock.json','remotion/remotion.config.ts',
    'remotion/tsconfig.json','remotion/public/audio/voice.wav']]
files += [snapshot]
files += [p for p in (D/'remotion/src').rglob('*') if p.is_file()]
files += [p for p in (D/'remotion/scripts').rglob('*') if p.is_file()]
files += [D/'navigation.md', D.parent/'_shared/branch-map/index.ts']
picks = json.loads((D/'voice/picks.json').read_text())
for row in json.loads((D/'voice/sents.json').read_text()):
    stem = f"{row['id']}-{picks.get(row['id'],'a')}"
    files += [D/'voice/takes'/f'{stem}.wav', D/'voice/takes'/f'{stem}.txt.json']
files += [D/'../../episodes/_shared'/f for f in [
    'onset_rule.py','voice/prep.py','voice/gen.py','voice/build.py','voice/common.py',
    'tts/mimo_say.py','theme/pageTheme.ts','music/mix_bgm.py','music/Wallpaper.mp3']]
# Keep the original complete body's dependencies, including later identity work.
ROOT = D.parents[1]
# Original-title/quotation appendix inputs are separate from retained body history.
files += [D/'references.json', D/'article.mdx', D/'remotion/package.json',
    ROOT/'episodes-codex/_shared/append_references_original.py',
    ROOT/'episodes-codex/_shared/append_references.py',
    ROOT/'episodes-codex/_shared/render_with_references.py',
    ROOT/'episodes-codex/_shared/requirements-reference-appendix.txt',
    ROOT/'site/scripts/check-references.mjs',
    ROOT/'episodes/_shared/theme/pageTheme.ts']
for source in json.loads((D/'references.json').read_text())['sources']:
    evidence_paths = [source['verification']['evidence'], source['titleEvidence']['evidence']]
    if 'quotation' in source:
        evidence_paths.append(source['quotation']['evidence'])
    files.extend(ROOT/evidence for evidence in evidence_paths)
# Keep parent references portable instead of writing workspace absolute paths.
manifest = {os.path.relpath(p, D):sha(p) for p in sorted(set(files))}
(D/'source-sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'{len(manifest)} frozen inputs; storyboard {sha(D/"storyboard.json")}')
