"""Audit sentence timing and provenance; this is not an ASR/transcript check."""
from pathlib import Path
import hashlib
import json
import re
import wave

D = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sb = json.loads((D / 'storyboard.json').read_text())
words = json.loads((D / 'words.json').read_text())
script = (D / 'script.md').read_text()
shots = [sh for sc in sb['scenes'] for sh in sc['shots']]
narrations = re.findall(r'^旁白：(.*)$', script, re.M)
assert len(shots) == len(narrations) == 20
assert len(sb['scenes']) == 5
assert words['scriptSha256'] == sha(D / 'script.md')
assert words['audioSha256'] == sha(D / 'voice.wav')
assert (D / 'voice.wav').read_bytes() == (D / 'remotion/public/audio/voice.wav').read_bytes()
with wave.open(str(D / 'voice.wav')) as audio:
    assert (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) == (48000, 1, 2)
    assert audio.getnframes() == words['durationFrames'] * 1600
cursor = 0
labels = []
caption_count = 0
for sh, narration, word_shot in zip(shots, narrations, words['shots']):
    assert sh['from'] == cursor == word_shot['startFrame']
    assert sh['durationInFrames'] == word_shot['durationFrames']
    assert sh['narration'] == narration
    assert ''.join(s['text'] for s in sh['subtitles']) == narration
    assert [s['text'] for s in sh['subtitles']] == [s['text'] for s in word_shot['sentences']]
    previous = -1
    for caption in sh['subtitles']:
        assert caption['from'] == previous + 1
        assert caption['to'] >= caption['from']
        previous = caption['to']
        caption_count += 1
    assert previous == sh['durationInFrames'] - 1
    for element in sh['elements']:
        if not element.get('cueText'):
            continue
        term = element['cueText']
        sent = next(s for s in word_shot['sentences'] if s['id'] == element['cueOnset']['sentence'])
        assert sent['text'].startswith(term)
        assert sh['durationInFrames'] - element['appearFrame'] >= 63
        labels.append(term)
    for voice in sh['voice']:
        assert abs(sh['from'] + voice['localStart'] - voice['wavStart']) < 1e-6
        assert voice['wavEnd'] <= words['durationFrames']
    cursor += sh['durationInFrames']
assert cursor == sb['meta']['durationInFrames'] == sb['meta']['finalVideoFrames'] == words['durationFrames']
assert labels == ['本地事务', '分布式事务', '最终一致']
assert caption_count == 40
assert not sb['meta']['provisionalTiming'] and not sb['meta']['pendingAudio']
result = dict(shots=20, sentences=40, chapters=5, frames=cursor,
              labels=labels, sentenceCaptionsExact=True, continuousCaptions=True,
              wholeAudioPlacement=True, sampleCount=True,
              scriptSHA256=sha(D / 'script.md'), audioSHA256=sha(D / 'voice.wav'),
              limitation='Sentence boundaries and first-name acoustic cues only; no word ASR or interior alignment.')
(D / 'qa-timing.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
