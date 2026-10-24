"""Freeze the actual production inputs before bundling; never validates an old MP4."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys

assert len(sys.argv) == 2, 'Usage: freeze_sentence_episode.py EPDIR'
D = Path(sys.argv[1]).resolve()
ROOT = Path(__file__).resolve().parents[2]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

sb = json.loads((D/'storyboard.json').read_text())
words = json.loads((D/'words.json').read_text())
assert not sb['meta'].get('provisionalTiming') and not sb['meta'].get('pendingAudio')
assert words['scriptSha256'] == sha(D/'script.md')
assert words['audioSha256'] == sha(D/'voice.wav')
assert (D/'voice.wav').read_bytes() == (D/'remotion/public/audio/voice.wav').read_bytes()
assert sb['meta']['durationInFrames'] == words['durationFrames']
assert sb['meta']['covers'] == json.loads((D/'covers.json').read_text()), 'Reassemble after changing covers'
config = json.loads((D/'episode-config.json').read_text())
assert sb['meta']['title'] == config['title']
assert len(words['shots']) == config['shotCount']
assert sum(sh['durationInFrames'] for sc in sb['scenes'] for sh in sc['shots']) == words['durationFrames']
snapshot = D/f'storyboard.{sha(D/"storyboard.json")[:8]}.json'
shutil.copy2(D/'storyboard.json', snapshot)
shutil.copy2(D/'storyboard.json', D/'remotion/src/placeholders/storyboard.json')
files = [D/f for f in ['script.md','article.mdx','research.md','pronunciation.md',
    'plan.json','episode-config.json','visual-direction.md','knoll-props.md',
    'storyboard.json','words.json','covers.json','voice.wav','voice/params.json',
    'voice/picks.json','voice/sents.json','voice/build.json','voice/substitutions.md','voice/script-narration-sha256.json',
    'remotion/package.json','remotion/package-lock.json','remotion/remotion.config.ts',
    'remotion/tsconfig.json','remotion/public/audio/voice.wav']]
files += [snapshot]
files += [ROOT/'episodes-codex/_shared'/f for f in ['assemble_sentence_episode.py','freeze_sentence_episode.py','check_sentence_episode.py','check_encoded_episode.py']]
# Navigation is a production dependency shared by the revised short episodes.
# Freeze its actual source alongside the local graph/shot mapping in remotion/src.
navigation = ROOT/'episodes-codex/_shared/branch-map'
if navigation.is_dir():
    files += [p for p in navigation.rglob('*') if p.is_file() and p.suffix in {'.ts', '.tsx', '.json'}]
files += [p for p in (D/'remotion/src').rglob('*') if p.is_file()]
picks = json.loads((D/'voice/picks.json').read_text())
for row in json.loads((D/'voice/sents.json').read_text()):
    stem = f"{row['id']}-{picks.get(row['id'],'a')}"
    files += [D/'voice/takes'/f'{stem}.wav', D/'voice/takes'/f'{stem}.txt.json']
    raw = D/'voice/takes'/f'{stem}.raw.wav'
    if raw.exists():
        files.append(raw)
files += [ROOT/'episodes/_shared'/f for f in [
    'onset_rule.py','voice/prep.py','voice/gen.py','voice/build.py','voice/common.py',
    'tts/mimo_say.py','theme/pageTheme.ts','music/mix_bgm.py','music/Wallpaper.mp3']]
# Keep parent references portable instead of writing workspace absolute paths.
manifest = {os.path.relpath(p, D):sha(p) for p in sorted(set(files))}
(D/'source-sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'{len(manifest)} frozen inputs; storyboard {sha(D/"storyboard.json")}')
