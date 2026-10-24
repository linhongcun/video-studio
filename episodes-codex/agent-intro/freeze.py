"""Freeze real production inputs after all authors stop writing, before encode."""
from pathlib import Path
import hashlib
import json
import os
import shutil

D = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sb = json.loads((D/'storyboard.json').read_text())
words = json.loads((D/'words.json').read_text())
assert words['scriptSha256'] == sha(D/'script.md')
assert words['audioSha256'] == sha(D/'voice.wav')
assert (D/'voice.wav').read_bytes() == (D/'remotion/public/audio/voice.wav').read_bytes()
assert sb['meta']['durationInFrames'] == words['durationFrames']
assert not sb['meta'].get('pendingAudio') and not sb['meta'].get('provisionalTiming')
snapshot = D / f'storyboard.{sha(D/"storyboard.json")[:8]}.json'
shutil.copy2(D/'storyboard.json', snapshot)
shutil.copy2(D/'storyboard.json', D/'remotion/src/placeholders/storyboard.json')
names = ['script.md','article.mdx','research.md','pronunciation.md','content-plan.json',
    'assemble.py','freeze.py','check-timing.py','check-final.py','visual-direction.md',
    'knoll-props.md','storyboard.json','words.json','covers.json','voice.wav',
    'voice/params.json','voice/picks.json','voice/sents.json','voice/build.json',
    'voice/substitutions.md','voice/input-freeze.json',
    'voice/build-metadata.py','voice/audit-takes.py',
    'remotion/package.json','remotion/package-lock.json','remotion/remotion.config.ts',
    'remotion/tsconfig.json','remotion/public/audio/voice.wav']
files = [D/name for name in names] + [snapshot]
files += [p for p in (D/'remotion/src').rglob('*') if p.is_file()]
files += [p for p in (D/'remotion/scripts').rglob('*') if p.is_file()]
picks = json.loads((D/'voice/picks.json').read_text())
for row in json.loads((D/'voice/sents.json').read_text()):
    stem = f"{row['id']}-{picks.get(row['id'],'a')}"
    files += [D/'voice/takes'/f'{stem}.wav', D/'voice/takes'/f'{stem}.txt.json']
    raw = D/'voice/takes'/f'{stem}.raw.wav'
    if raw.exists():
        files.append(raw)
files += [D/'../../episodes/_shared'/name for name in [
    'onset_rule.py','voice/prep.py','voice/gen.py','voice/build.py','voice/common.py',
    'tts/mimo_say.py','theme/pageTheme.ts','music/mix_bgm.py','music/Wallpaper.mp3']]
manifest = {os.path.relpath(p, D):sha(p) for p in sorted(set(files))}
(D/'source-sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'{len(manifest)} frozen inputs; storyboard {sha(D/"storyboard.json")}')
