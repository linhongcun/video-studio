"""Insert the separately built methods narration without changing old PCM.

Run after the shared voice tools have built revisions/methods-insert/voice.wav.
The original 30 sentences and all old shot-local timings are reused exactly.
This is episode-specific assembly, not another TTS, onset, or mixing algorithm.
"""
from pathlib import Path
import copy
import hashlib
import json
import math
import re
import shutil
import sys
import wave

import numpy as np

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
BASE = D / 'revisions/methods-before'
INSERT = D / 'revisions/methods-insert'
FPS, SR, SAMPLES_PER_FRAME, INSERT_AT = 30, 48000, 1600, 1574
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from onset_rule import Rule
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import lufs


def read(path):
    return json.loads(path.read_text())


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_pcm(path):
    with wave.open(str(path)) as wav:
        assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (1, 2, SR), path
        assert wav.getcomptype() == 'NONE', path
        return wav.readframes(wav.getnframes())


def shift_word_shot(shot, offset):
    result = copy.deepcopy(shot)
    for key in ('startFrame', 'endFrame', 'onsetFrame', 'speechStartFrame', 'speechEndFrame'):
        result[key] += offset
    for sentence in result['sentences']:
        for key in ('startFrame', 'endFrame', 'onsetFrame'):
            sentence[key] += offset
        for token in sentence['chars'] + sentence['words']:
            for key in ('startFrame', 'endFrame'):
                token[key] += offset
    return result


baseline = read(BASE / 'baseline.json')
for rel, expected in baseline['files'].items():
    assert sha(BASE / rel) == expected, f'Archived baseline changed: {rel}'
assert baseline['insertFrame'] == INSERT_AT
old_sb = read(BASE / 'storyboard.json')
old_words = read(BASE / 'words.json')
old_build = read(BASE / 'voice/build.json')
insert_build = read(INSERT / 'voice/build.json')
old_pcm = load_pcm(BASE / 'voice.wav')
new_pcm = load_pcm(INSERT / 'voice.wav')
insert_frames = insert_build['summary']['frames']
old_frames = old_sb['meta']['durationInFrames']
assert len(old_pcm) == old_frames * SAMPLES_PER_FRAME * 2
assert len(new_pcm) == insert_frames * SAMPLES_PER_FRAME * 2
assert insert_build['summary']['sha'] == sha(INSERT / 'voice.wav')
assert old_build['summary']['sha'] == sha(BASE / 'voice.wav')
cut = INSERT_AT * SAMPLES_PER_FRAME * 2
pcm = old_pcm[:cut] + new_pcm + old_pcm[cut:]
with wave.open(str(D / 'voice.wav'), 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(SR)
    wav.writeframes(pcm)
public_voice = D / 'remotion/public/audio/voice.wav'
public_voice.parent.mkdir(parents=True, exist_ok=True)
assert not public_voice.is_symlink()
shutil.copyfile(D / 'voice.wav', public_voice)
total_frames = old_frames + insert_frames
samples = np.frombuffer(pcm, '<i2').astype(float) / 32767
rule = Rule(samples, SR)

script = (D / 'script.md').read_text()
sections = {}
for number, slug, body in re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)', script, re.S):
    sections[f'{int(number):02d}-{slug}'] = {
        'number': int(number),
        'narration': re.search(r'^旁白：(.*)$', body, re.M)[1],
        'visual': re.search(r'^画面：(.*)$', body, re.M)[1],
    }
new_rows = copy.deepcopy(insert_build['sentences'])
assert [r['shot'] for r in new_rows] == ['16-options'] * 2 + ['17-redis'] * 3
for row in new_rows:
    for key in ('startFrame', 'endFrame'):
        row[key] += INSERT_AT
    for key in ('startSample', 'endSample'):
        row[key] += INSERT_AT * SAMPLES_PER_FRAME
    stem = f"{row['id']}-{row['take']}"
    for suffix in ('.wav', '.txt.json'):
        shutil.copyfile(INSERT / f'voice/takes/{stem}{suffix}', D / f'voice/takes/{stem}{suffix}')
old_rows = copy.deepcopy(old_build['sentences'])
for row in old_rows:
    if row['startSample'] >= INSERT_AT * SAMPLES_PER_FRAME:
        for key in ('startFrame', 'endFrame'):
            row[key] += insert_frames
        for key in ('startSample', 'endSample'):
            row[key] += insert_frames * SAMPLES_PER_FRAME
rows = sorted(old_rows + new_rows, key=lambda r: r['startSample'])
assert len({r['id'] for r in rows}) == len(rows) == 35
for index, row in enumerate(rows):
    if index:
        row['gapBefore'] = round((row['startSample'] - rows[index - 1]['endSample']) / SR, 4)
for shot, section in sections.items():
    assert ''.join(r['text'] for r in rows if r['shot'] == shot) == section['narration'], shot
splices = [dict(pair=f"{left['id']}->{right['id']}",
                lufs_diff=round(abs(left['lufs'] - right['lufs']), 2),
                gapFrames=round((right['startSample'] - left['endSample']) / SAMPLES_PER_FRAME, 1))
           for left, right in zip(rows, rows[1:])]
jumps = [float(np.max(np.abs(np.diff(samples[max(0, p - 480):p + 480]))))
         for row in rows for p in (row['startSample'], row['endSample'])]
save(D / 'voice/build.json', dict(
    summary=dict(extraAfter={**old_build['summary']['extraAfter'], **insert_build['summary']['extraAfter']},
                 track_lufs=lufs(samples), peak=float(np.max(np.abs(samples))),
                 max_neighbour_lufs_diff=max(s['lufs_diff'] for s in splices),
                 max_join_sample_jump=max(jumps),
                 inner_dropouts=[r['id'] for r in rows if r.get('maxInnerSilenceS', 0) >= .5],
                 samples=len(samples), frames=total_frames, seconds=total_frames / FPS,
                 sha=sha(D / 'voice.wav'),
                 assemblyMethod='Original PCM prefix + separately built insertion PCM + original PCM suffix; no track renormalization.'),
    sentences=rows, splices=splices))
save(D / 'voice/sents.json', [{key: r[key] for key in ('id', 'shot', 'text', 'tts')} for r in rows])
save(D / 'voice/picks.json', {r['id']: r['take'] for r in rows})

new_word_shots = []
new_starts = {'16-options': INSERT_AT,
              '17-redis': math.floor(next(r['startFrame'] for r in new_rows if r['shot'] == '17-redis'))}
for shot_id in ('16-options', '17-redis'):
    sentences = []
    for row in [r for r in new_rows if r['shot'] == shot_id]:
        start, end = row['startFrame'], row['endFrame']
        measured = rule.onset(start, min(end, start + 30))
        assert measured['source'] == 'pause', (row['id'], measured)
        normalized = re.sub(r'[^\u4e00-\u9fffA-Za-z0-9.]', '', row['text'])
        tokens = [dict(ch=char, startFrame=measured['onset'], endFrame=end,
                       timingUnit='sentence envelope', measuredOnset=(index == 0),
                       source='TTS sentence boundary; no interior character alignment')
                  for index, char in enumerate(normalized)]
        sentences.append(dict(id=row['id'], text=row['text'], take=row['take'],
                              startFrame=start, endFrame=end, onsetFrame=measured['onset'],
                              asr='', asrCoverage=None, chars=tokens,
                              words=[dict(w=normalized, startFrame=measured['onset'], endFrame=end)],
                              note='Only sentence onset is measured. Character envelopes are not word timestamps.'))
    start = new_starts[shot_id]
    end = new_starts['17-redis'] if shot_id == '16-options' else INSERT_AT + insert_frames
    new_word_shots.append(dict(id=shot_id, sentences=sentences,
                               onsetFrame=sentences[0]['onsetFrame'],
                               speechStartFrame=sentences[0]['startFrame'],
                               speechEndFrame=sentences[-1]['endFrame'],
                               startFrame=start, endFrame=end, durationFrames=end - start))
word_shots = [shift_word_shot(s, insert_frames if s['startFrame'] >= INSERT_AT else 0)
              for s in old_words['shots']]
word_shots = sorted(word_shots + new_word_shots, key=lambda s: s['startFrame'])
words = copy.deepcopy(old_words)
words.update(scriptSha256=sha(D / 'script.md'), audioSha256=sha(D / 'voice.wav'),
             durationFrames=total_frames, shots=word_shots,
             onsetTable=[dict(shot=s['id'], sentence=s['sentences'][0]['id'], onsetFrame=s['onsetFrame'],
                              source='acoustic sentence onset') for s in word_shots])
save(D / 'words.json', words)
source = f"voice.wav SHA256={sha(D / 'voice.wav')} + words.json SHA256={sha(D / 'words.json')} + script.md SHA256={sha(D / 'script.md')}"

new_shots, new_cues = [], []
for ws in new_word_shots:
    section = sections[ws['id']]
    start, duration = ws['startFrame'], ws['durationFrames']
    subtitles = []
    for index, sentence in enumerate(ws['sentences']):
        fr = 0 if index == 0 else math.floor(sentence['startFrame']) - start
        to = math.floor(ws['sentences'][index + 1]['startFrame']) - start - 1 if index + 1 < len(ws['sentences']) else duration - 1
        subtitles.append(dict(text=sentence['text'], **{'from': fr}, to=to, duration=to - fr + 1))
    term, key = ('UUID', 'uuidLabel') if ws['id'] == '16-options' else ('Redis', 'redisLabel')
    sentence = next(s for s in ws['sentences'] if s['text'].startswith(term))
    onset = sentence['onsetFrame'] - start
    appear = max(1, math.floor(onset) - 2)
    cues = {key: appear, 'sentences': [math.floor(s['startFrame']) - start for s in ws['sentences']]}
    elements = [dict(id=key, type='text', text=term, cueText=term, appearFrame=appear,
                     x=130, y=180, w=800, h=80, fontSize=58,
                     cueOnset=dict(sentence=sentence['id'], asrFrame=None, onsetLocal=onset,
                                   rule='pause/acoustic sentence onset', delay=0))]
    new_cues.append(dict(shot=ws['id'], cue=term, sentence=sentence['id'], onsetFrame=sentence['onsetFrame']))
    new_shots.append(dict(id=str(section['number']), scriptShot=section['number'], chapterId='methods',
                          **{'from': start}, durationInFrames=duration, narration=section['narration'],
                          subtitles=subtitles,
                          voice=[dict(id=s['id'], wavStart=s['startFrame'], wavEnd=s['endFrame'],
                                      localStart=s['startFrame'] - start, localEnd=s['endFrame'] - start)
                                 for s in ws['sentences']],
                          cueFrames=cues,
                          timing=dict(source=source, wavFrom=ws['speechStartFrame'], wavTo=ws['speechEndFrame'],
                                      holdFrames=0, naturalGapFrames=ws['endFrame'] - math.ceil(ws['speechEndFrame']),
                                      holdReason='The complete assembled PCM is placed unchanged; pauses exist in the audio.'),
                          frame='canvas', camera=None, boxShot=False, mapShot=False,
                          scriptVisual=section['visual'], direction=section['visual'], elements=elements,
                          animations=[], transition=dict(type='cut', durationInFrames=0)))
sb = copy.deepcopy(old_sb)
sb['meta'].update(title='分布式 ID：两个订单，怎么撞成同一个号了？', slug='global-id-methods-v2',
                  durationInFrames=total_frames, finalVideoFrames=total_frames,
                  timingSource=source, visualRevision=2,
                  methodsInsertion=dict(fromFrame=INSERT_AT, durationInFrames=insert_frames,
                                        narrationSource='revisions/methods-insert/voice.wav',
                                        baseline='revisions/methods-before/baseline.json'))
scenes = []
for scene in sb['scenes']:
    if scene['from'] >= INSERT_AT:
        scene['from'] += insert_frames
    for shot in scene['shots']:
        shift = insert_frames if shot['from'] >= INSERT_AT else 0
        shot['from'] += shift
        for voice in shot['voice']:
            voice['wavStart'] += shift
            voice['wavEnd'] += shift
        shot['timing']['wavFrom'] += shift
        shot['timing']['wavTo'] += shift
        shot['timing']['source'] = source
    scenes.append(scene)
    if scene['id'] == 'local':
        scenes.append(dict(id='methods', chapterId='methods', title='分布式ID不止雪花',
                           **{'from': INSERT_AT}, durationInFrames=insert_frames, shots=new_shots))
sb['scenes'] = scenes
save(D / 'storyboard.json', sb)
old_cues = read(BASE / 'voice/cues.json')
for cue in old_cues:
    if cue['onsetFrame'] >= INSERT_AT:
        cue['onsetFrame'] += insert_frames
cues = sorted(old_cues + new_cues, key=lambda cue: cue['onsetFrame'])
save(D / 'voice/cues.json', cues)
save(D / 'voice/cue_tests.json', [[c['shot'], c['cue']] for c in cues])
save(D / 'voice/shot_frames.json', dict(fps=FPS, durationFrames=total_frames,
                                      audioSha256=sha(D / 'voice.wav'), shots=word_shots))

def stamp(frame):
    ms = round(frame / FPS * 1000)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'

captions = [f"{index + 1}\n{stamp(row['startFrame'])} --> {stamp(row['endFrame'])}\n{row['text']}\n"
            for index, row in enumerate(rows)]
(D / 'captions.srt').write_text('\n'.join(captions))
assert load_pcm(D / 'voice.wav')[:cut] == old_pcm[:cut]
assert load_pcm(D / 'voice.wav')[cut + len(new_pcm):] == old_pcm[cut:]

def shot_local_data(shot):
    local = copy.deepcopy(shot)
    del local['from']
    for voice in local['voice']:
        del voice['wavStart'], voice['wavEnd']
    for key in ('source', 'wavFrom', 'wavTo'):
        del local['timing'][key]
    return local

old_shots = [shot for scene in old_sb['scenes'] for shot in scene['shots']]
current_shots = {shot['id']: shot for scene in sb['scenes'] for shot in scene['shots']}
for old_shot in old_shots:
    assert shot_local_data(old_shot) == shot_local_data(current_shots[old_shot['id']]), old_shot['id']
save(D / 'methods-reuse-proof.json', dict(
    baselineCommit=baseline['commit'], insertionFrame=INSERT_AT, insertedFrames=insert_frames,
    oldFrames=old_frames, totalFrames=total_frames, oldSentenceCount=len(old_rows), newSentenceCount=len(new_rows),
    baselineVoiceSHA256=sha(BASE / 'voice.wav'), insertionVoiceSHA256=sha(INSERT / 'voice.wav'),
    assembledVoiceSHA256=sha(D / 'voice.wav'), baselineVideoSHA256=sha(BASE / 'video.mp4'),
    prefixPCMUnchanged=True, suffixPCMUnchanged=True,
    prefixPCMSHA256=sha_bytes(old_pcm[:cut]), suffixPCMSHA256=sha_bytes(old_pcm[cut:]),
    originalShotLocalTimingsUnchanged=True,
    oldManifestReview=dict(count=baseline['oldManifestCount'], matched=baseline['oldManifestMatched'],
                           mismatch=baseline['oldManifestMismatch']),
    scope='Only 16-options and 17-redis narration added. Original PCM preserved; old global timestamps shift by the exact whole-frame insertion. Original local visual/caption timing preserved. No ASR or word-level alignment claimed.'))
print(f'Inserted {insert_frames} frames at {INSERT_AT}; {len(scenes)} chapters, {len(word_shots)} shots, {len(rows)} sentences, {total_frames} total frames.')
