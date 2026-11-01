"""Freeze the actual local production inputs after preflight review."""
from pathlib import Path
import argparse
import hashlib
import json
import wave

D = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--verify', action='store_true', help='Read-only check of the frozen manifest and inputs.')
args = parser.parse_args()
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

sb = json.loads((D/'storyboard.json').read_text())
words = json.loads((D/'words.json').read_text())
total_frames = sb['meta']['durationInFrames']
assert sb['meta']['finalVideoFrames'] == words['durationFrames'] == total_frames
assert total_frames > 0
assert words['audioSha256'] == digest(D/'voice.wav')
assert words['scriptSha256'] == digest(D/'script.md')
assert (D/'voice.wav').read_bytes() == (D/'remotion/public/audio/voice.wav').read_bytes()
assert not (D/'remotion/public/audio/voice.wav').is_symlink()
assert sb['meta']['covers'] == json.loads((D/'covers.json').read_text())
with wave.open(str(D/'voice.wav')) as wav:
    assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (1, 2, 48000)
    assert wav.getnframes() == total_frames * 1600
for rel in ('voice.wav', 'words.json', 'script.md'):
    assert digest(D/rel) in sb['meta']['timingSource'], f'Missing complete timing-source SHA: {rel}'
build = json.loads((D/'voice/build.json').read_text())
assert build['summary']['frames'] == total_frames
assert build['summary']['sha'] == digest(D/'voice.wav')
offset = 0
for shot in [s for scene in sb['scenes'] for s in scene['shots']]:
    assert shot['from'] == offset
    assert shot['timing']['holdFrames'] == 0
    assert ''.join(s['text'] for s in shot['subtitles']) == shot['narration']
    assert shot['subtitles'][0]['from'] == 0
    assert shot['subtitles'][-1]['to'] == shot['durationInFrames']-1
    for a,b in zip(shot['subtitles'],shot['subtitles'][1:]):
        assert a['to']+1 == b['from']
    for voice in shot['voice']:
        assert abs(shot['from']+voice['localStart']-voice['wavStart']) <= .5
    offset += shot['durationInFrames']
assert offset == total_frames
raw = (D/'storyboard.json').read_bytes()
sha8 = digest(D/'storyboard.json')[:8]
if args.verify:
    manifest = json.loads((D/'source-sha256.json').read_text())
    for rel, expected in manifest.items():
        assert digest(D/rel) == expected, rel
    assert (D/f'storyboard.{sha8}.json').read_bytes() == raw
    assert (D/'remotion/src/placeholders/storyboard.json').read_bytes() == raw
    print(f'Verified {len(manifest)} frozen inputs; {total_frames} frames; storyboard {sha8}.')
    raise SystemExit(0)
(D/f'storyboard.{sha8}.json').write_bytes(raw)
(D/'remotion/src/placeholders').mkdir(parents=True,exist_ok=True)
(D/'remotion/src/placeholders/storyboard.json').write_bytes(raw)
files = [
    'storyboard.json',f'storyboard.{sha8}.json','words.json','script.md','voice.wav',
    'covers.json','visual-direction.md','assemble.py','assemble-methods.py','freeze.py','check-final.py',
    'article.mdx','research.md','pronunciation.md','captions.srt',
    'voice/picks.json','voice/params.json','voice/sents.json','voice/build.json',
    'voice/cues.json','voice/shot_frames.json',
    'voice/cue_tests.json','methods-reuse-proof.json',
    'remotion/remotion.config.ts','remotion/tsconfig.json','remotion/package.json',
    'remotion/package-lock.json','remotion/public/audio/voice.wav',
    '../../episodes/_shared/theme/pageTheme.ts',
    '../../episodes/_shared/music/mix_bgm.py','../../episodes/_shared/music/Wallpaper.mp3',
    '../../episodes/_shared/onset_rule.py','../../episodes/_shared/place_v2.py',
    '../../episodes/_shared/label_onset_strict.py',
    '../../episodes/_shared/voice/prep.py','../../episodes/_shared/voice/gen.py',
    '../../episodes/_shared/voice/build.py',
]
for rel in ('render-methods.py', 'splice-plan-methods.json'):
    if (D/rel).is_file():
        files.append(rel)
# Both the archival baseline and separately built insertion are actual inputs
# of assemble-methods.py. Keep the earlier manifest discrepancy as recorded in
# baseline.json; these snapshots do not retroactively change the old freeze.
for folder in ('revisions/methods-before', 'revisions/methods-insert'):
    files += [str(p.relative_to(D)) for p in sorted((D/folder).rglob('*'))
              if p.is_file() and '__pycache__' not in p.parts]
files += [str(p.relative_to(D)) for p in sorted((D/'remotion/src').rglob('*')) if p.is_file()]
files += [str(p.relative_to(D)) for p in sorted((D/'remotion/scripts').glob('*.mjs'))]
picks = json.loads((D/'voice/picks.json').read_text())
for sid,take in picks.items():
    files.extend([f'voice/takes/{sid}-{take}.wav',f'voice/takes/{sid}-{take}.txt.json'])
save(D/'source-sha256.json',{rel:digest(D/rel) for rel in dict.fromkeys(files)})
print(f'Frozen storyboard {sha8}; {len(dict.fromkeys(files))} actual inputs; {total_frames} frames.')
