"""Check audible sentence placement and caption/cue provenance, without ASR."""
from pathlib import Path
import hashlib
import json
import re
import wave

D = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sb = json.loads((D / 'storyboard.json').read_text())
words = json.loads((D / 'words.json').read_text())
plan = json.loads((D / 'content-plan.json').read_text())
shots = [shot for scene in sb['scenes'] for shot in scene['shots']]
narrations = re.findall(r'^旁白：(.*)$', (D / 'script.md').read_text(), re.M)
assert len(shots) == len(plan) == len(narrations) == 20
assert len(sb['scenes']) == 5
assert words['scriptSha256'] == sha(D / 'script.md')
assert words['audioSha256'] == sha(D / 'voice.wav')
assert (D / 'voice.wav').read_bytes() == (D / 'remotion/public/audio/voice.wav').read_bytes()
with wave.open(str(D / 'voice.wav')) as audio:
    assert (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) == (48000, 1, 2)
    assert audio.getnframes() == words['durationFrames'] * 1600
cursor, count, labels = 0, 0, []
for shot, narration, ws in zip(shots, narrations, words['shots']):
    assert shot['from'] == cursor == ws['startFrame']
    assert shot['durationInFrames'] == ws['durationFrames']
    assert shot['narration'] == narration
    assert ''.join(caption['text'] for caption in shot['subtitles']) == narration
    assert [caption['text'] for caption in shot['subtitles']] == [sent['text'] for sent in ws['sentences']]
    previous = -1
    for caption in shot['subtitles']:
        assert caption['from'] == previous + 1
        assert caption['to'] >= caption['from']
        previous = caption['to']
        count += 1
    assert previous == shot['durationInFrames'] - 1
    for element in shot['elements']:
        sent = next(s for s in ws['sentences'] if s['id'] == element['cueOnset']['sentence'])
        assert sent['text'].startswith(element['cueText'])
        assert -6 <= shot['from'] + element['appearFrame'] - sent['onsetFrame'] <= 2
        assert shot['durationInFrames'] - element['appearFrame'] >= 63
        labels.append(element['cueText'])
    for voice in shot['voice']:
        assert abs(shot['from'] + voice['localStart'] - voice['wavStart']) < 0.5
        assert voice['wavEnd'] <= words['durationFrames']
    cursor += shot['durationInFrames']
assert cursor == words['durationFrames'] == sb['meta']['durationInFrames'] == sb['meta']['finalVideoFrames']
assert count == 40 and labels == ['模型', '工具', '智能体']
assert not sb['meta']['pendingAudio'] and not sb['meta']['provisionalTiming']
report = dict(shots=len(shots), sentences=count, chapters=len(sb['scenes']),
    frames=cursor, labels=labels, continuousCaptions=True, captionsExact=True,
    wholeAudioPlacement=True, sampleCount=True, scriptSHA256=sha(D/'script.md'),
    audioSHA256=sha(D/'voice.wav'),
    limitation='Sentence envelopes and shared acoustic cue onsets; no interior word ASR or full human listening.')
(D / 'qa-timing.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
