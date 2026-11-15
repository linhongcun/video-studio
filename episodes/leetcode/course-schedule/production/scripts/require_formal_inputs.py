import hashlib
import json
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
storyboard_path = EP / 'storyboard.json'
voice_path = EP / 'voice.wav'
words_path = EP / 'words.json'
placeholder_path = EP / 'remotion/src/placeholders/storyboard.json'
if not storyboard_path.is_file() or not voice_path.is_file() or not words_path.is_file():
    raise SystemExit('Formal render requires assembled storyboard.json, voice.wav, and words.json.')

storyboard_bytes = storyboard_path.read_bytes()
if not placeholder_path.is_file() or placeholder_path.read_bytes() != storyboard_bytes:
    raise SystemExit('Formal render requires the frozen storyboard copied to the Remotion input.')
meta = json.loads(storyboard_bytes).get('meta', {})
if any(meta.get(flag) for flag in ('draft', 'provisionalTiming', 'pendingAudio', 'layoutPreviewOnly')):
    raise SystemExit('Formal render refuses draft, provisional, pending-audio, or layout-only storyboards.')
timing_source = meta.get('timingSource', '')
for label, path in (('voice.wav', voice_path), ('words.json', words_path), ('script.md', EP / 'script.md')):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if f'{label} {digest}' not in timing_source:
        raise SystemExit(f'Formal render requires timingSource bound to the current {label} SHA-256.')
print('Formal storyboard and voice timing inputs are present.')
