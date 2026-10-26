"""Freeze the actual local production inputs after preflight review."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import wave

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--verify', action='store_true', help='Read-only check of the frozen manifest and inputs.')
parser.add_argument('--profile', choices=('methods', 'tradeoffs'), help='Require the already assembled profile; never reassemble inputs.')
args = parser.parse_args()
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

sb = json.loads((D/'storyboard.json').read_text())
words = json.loads((D/'words.json').read_text())
profile = sb['meta'].get('assemblyProfile', {'name': 'methods', 'baseline': 'revisions/methods-before',
                                          'insertion': 'revisions/methods-insert', 'proof': 'methods-reuse-proof.json'})
profile_name = profile['name']
assert args.profile is None or args.profile == profile_name, 'Assembled storyboard has another profile.'
script_rel = words.get('script', 'script.md')
total_frames = sb['meta']['durationInFrames']
assert sb['meta']['finalVideoFrames'] == words['durationFrames'] == total_frames
assert total_frames > 0
assert words['audioSha256'] == digest(D/'voice.wav')
assert words['scriptSha256'] == digest(D/script_rel)
assert (D/'voice.wav').read_bytes() == (D/'remotion/public/audio/voice.wav').read_bytes()
assert not (D/'remotion/public/audio/voice.wav').is_symlink()
assert sb['meta']['covers'] == json.loads((D/'covers.json').read_text())
with wave.open(str(D/'voice.wav')) as wav:
    assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (1, 2, 48000)
    assert wav.getnframes() == total_frames * 1600
for rel in ('voice.wav', 'words.json', script_rel):
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
    print(f'Verified {profile_name}: {len(manifest)} frozen inputs; {total_frames} frames; storyboard {sha8}.')
    raise SystemExit(0)
# This reference-only revision consumes the already assembled profile. Never
# rewrite a body snapshot/placeholder merely to freeze a new citation appendix.
assert (D/f'storyboard.{sha8}.json').read_bytes() == raw
assert (D/'remotion/src/placeholders/storyboard.json').read_bytes() == raw
files = [
    'storyboard.json',f'storyboard.{sha8}.json','words.json','script.md','voice.wav',
    'covers.json','visual-direction.md','assemble.py','assemble-methods.py','freeze.py','check-final.py',
    'article.mdx','research.md','pronunciation.md','captions.srt',
    'voice/picks.json','voice/params.json','voice/sents.json','voice/build.json',
    'voice/cues.json','voice/shot_frames.json',
    'voice/cue_tests.json',profile['proof'],script_rel,
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
# Freeze exactly the selected insertion and its provenance. Historical methods
# inputs stay untouched and are only selected by an explicit methods profile.
config_source = profile.get('configSource', '')
if config_source and ':' not in config_source:
    files.append(config_source)
for folder in dict.fromkeys([profile['baseline'], profile['insertion'], *profile.get('archives', [])]):
    files += [str(p.relative_to(D)) for p in sorted((D/folder).rglob('*'))
              if p.is_file() and '__pycache__' not in p.parts]
files += [str(p.relative_to(D)) for p in sorted((D/'remotion/src').rglob('*')) if p.is_file()]
files += [str(p.relative_to(D)) for p in sorted((D/'remotion/scripts').glob('*.mjs'))]
picks = json.loads((D/'voice/picks.json').read_text())
for sid,take in picks.items():
    files.extend([f'voice/takes/{sid}-{take}.wav',f'voice/takes/{sid}-{take}.txt.json'])
# Preserve the original 200-input profile record separately from current
# article/research/entry wiring. This is not a claim that the retained MP4 was
# re-rendered from the expanded reference input set.
archive = D/'revisions/reference-endcards'
history = archive/'before-source-sha256.json'
assert digest(history) == 'ed02996a2ef55c2f6a18ee8cd3175538edabe78139ab7bb013ee1105f253471a', 'Archived profile record changed'
original = json.loads(history.read_text())
relocated = {
    'article.mdx': archive/'before-article.mdx',
    'research.md': archive/'before-research.md',
    'freeze.py': archive/'before-freeze.py',
    'remotion/package.json': archive/'before-remotion-package.json',
}
for relative, expected in original.items():
    path = relocated.get(relative, D/relative)
    assert path.is_file() and digest(path) == expected, ('Original profile input changed', relative)
subprocess.run(['node', str(ROOT/'site/scripts/check-references.mjs'), '--sources', str(D)],
               cwd=ROOT, check=True)
reference_inputs = [history, *relocated.values(), D/'references.json',
    ROOT/'episodes-codex/_shared/append_references_bibliography.py',
    ROOT/'episodes-codex/_shared/append_references_original.py',
    ROOT/'episodes-codex/_shared/append_references.py',
    ROOT/'episodes-codex/_shared/render_with_references.py',
    ROOT/'episodes-codex/_shared/requirements-reference-appendix.txt',
    ROOT/'site/scripts/check-references.mjs', ROOT/'episodes/_shared/theme/pageTheme.ts']
for source in json.loads((D/'references.json').read_text())['sources']:
    records = [source['verification'], source['titleEvidence']]
    if 'quotation' in source:
        records.append(source['quotation'])
    reference_inputs += [ROOT/record['evidence'] for record in records]
# Bibliographic supplements are real dependencies, not merely paths mentioned
# inside the source JSON. Retain their byte-exact files with the recorded SHA.
for evidence in dict.fromkeys(ROOT/record['evidence'] for source in
        json.loads((D/'references.json').read_text())['sources']
        for record in [source['verification'], source['titleEvidence'],
                       *([source['quotation']] if 'quotation' in source else [])]):
    for supplement in json.loads(evidence.read_text()).get('titleOnlySupplements', []):
        path = ROOT/supplement['savedPath']
        assert path.resolve().is_relative_to(ROOT) and path.is_file(), path
        assert digest(path) == supplement['sha256'], ('Title evidence changed', path)
        reference_inputs.append(path)
for path in reference_inputs:
    assert path.resolve().is_relative_to(ROOT) and path.is_file(), path
    files.append(os.path.relpath(path, D))
current = {rel:digest(D/rel) for rel in dict.fromkeys(files)}
assert set(original) <= set(current), 'An original profile input key was dropped'
save(D/'source-sha256.json',current)
print(f'Frozen {profile_name}: storyboard {sha8}; {len(dict.fromkeys(files))} actual inputs; {total_frames} frames.')
