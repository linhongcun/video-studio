"""Audit sentence timing and provenance; this is not an ASR/transcript check."""
from pathlib import Path
import hashlib
import json
import re
import wave
import sys

assert len(sys.argv) == 2, 'Usage: check_sentence_episode.py EPDIR'
D = Path(sys.argv[1]).resolve()
config = json.loads((D / 'episode-config.json').read_text())
plan = json.loads((D / 'plan.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sb = json.loads((D / 'storyboard.json').read_text())
words = json.loads((D / 'words.json').read_text())
script = (D / 'script.md').read_text()
shots = [sh for sc in sb['scenes'] for sh in sc['shots']]
narrations = re.findall(r'^旁白：(.*)$', script, re.M)
assert len(shots) == len(narrations) == config['shotCount']
assert len(sb['scenes']) == len({p['chapterId'] for p in plan})
assert words['scriptSha256'] == sha(D / 'script.md')
assert words['audioSha256'] == sha(D / 'voice.wav')
assert (D / 'voice.wav').read_bytes() == (D / 'remotion/public/audio/voice.wav').read_bytes()
end_card = sb['meta'].get('unvoicedEndCard')
if end_card is not None:
    assert end_card['kind'] == 'full-python-solution'
    assert isinstance(end_card['from'], int) and isinstance(end_card['durationInFrames'], int)
    assert end_card['durationInFrames'] > 0
    assert end_card['from'] + end_card['durationInFrames'] == words['durationFrames']
    assert shots[-1]['from'] < end_card['from']
    assert shots[-1]['codeCardFrom'] == end_card['from'] - shots[-1]['from']
    assert max(v['wavEnd'] for sh in shots for v in sh['voice']) <= end_card['from']
with wave.open(str(D / 'voice.wav')) as audio:
    assert (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) == (48000, 1, 2)
    assert audio.getnframes() == words['durationFrames'] * 1600
    if end_card is not None:
        audio.setpos(end_card['from'] * 1600)
        assert not any(audio.readframes(end_card['durationInFrames'] * 1600)), 'End card overlaps narration'
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
    caption_end = (end_card['from'] - sh['from'] - 1
                   if end_card is not None and sh is shots[-1] else sh['durationInFrames'] - 1)
    assert previous == caption_end
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
assert labels == [c['term'] for p in plan for c in p['cues']]
assert len(set(labels)) <= 3
assert caption_count == 2 * config['shotCount']
assert not sb['meta']['provisionalTiming'] and not sb['meta']['pendingAudio']
result = dict(shots=len(shots), sentences=caption_count, chapters=len(sb['scenes']), frames=cursor,
              labels=labels, sentenceCaptionsExact=True, continuousCaptions=end_card is None,
              wholeAudioPlacement=True, sampleCount=True,
              scriptSHA256=sha(D / 'script.md'), audioSHA256=sha(D / 'voice.wav'),
              limitation='Sentence boundaries and first-name acoustic cues only; no word ASR or interior alignment.')
if end_card is not None:
    result.update(continuousNarrationCaptions=True, unvoicedEndCardFrames=end_card['durationInFrames'],
                  unvoicedEndCardFrom=end_card['from'], endCardVoiceSilence=True)
(D / 'qa-timing.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
