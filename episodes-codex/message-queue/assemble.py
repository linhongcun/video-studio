"""Assemble sentence-timed local review assets after shared voice/build.py.

No ASR or inferred word timestamps: each sentence is one timing token. Only
sentence-initial cues may be synchronized with the shared acoustic onset rule.
The official Whisper model is unavailable under this environment's network policy.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import sys
import wave

import numpy as np

D = Path(__file__).resolve().parent
EPISODE = json.loads((D/'episode.json').read_text())
ROOT = D.parents[1]
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from onset_rule import Rule


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


build = json.loads((D / 'voice/build.json').read_text())
with wave.open(str(D / 'voice.wav')) as w:
    sr = w.getframerate()
    samples = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32767
rule = Rule(samples, sr)
script = (D / 'script.md').read_text()
sections = re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)', script, re.S)
words_shots = []
for n, slug, body in sections:
    rows = [r for r in build['sentences'] if r['shot'] == f'{int(n):02d}-{slug}']
    sentences = []
    for r in rows:
        start, end = r['startFrame'], r['endFrame']
        measured = rule.onset(start, min(end, start + 30))
        assert measured['source'] == 'pause', (r['id'], measured)
        text = re.sub(r'[^\u4e00-\u9fffA-Za-z0-9.]', '', r['text'])
        # Compatibility with the existing character-search checker: every
        # character carries its entire sentence envelope, NOT an inferred word
        # time. Only index 0 has a measured character onset and is used as a cue.
        tokens = [dict(ch=char, startFrame=measured['onset'], endFrame=end,
                       timingUnit='sentence envelope', measuredOnset=(i == 0),
                       source='TTS sentence boundary; no interior character alignment')
                  for i, char in enumerate(text)]
        sentences.append(dict(id=r['id'], text=r['text'], take=r['take'],
                              startFrame=start, endFrame=end, onsetFrame=measured['onset'],
                              asr='', asrCoverage=None, chars=tokens,
                              words=[dict(w=text, startFrame=measured['onset'], endFrame=end)],
                              note='Only sentence onset is measured. Character envelopes are not word timestamps.'))
    words_shots.append(dict(id=rows[0]['shot'], sentences=sentences,
                            onsetFrame=sentences[0]['onsetFrame'],
                            speechStartFrame=sentences[0]['startFrame'],
                            speechEndFrame=sentences[-1]['endFrame'],
                            startFrame=0 if not words_shots else math.floor(sentences[0]['startFrame'])))
for i, s in enumerate(words_shots):
    s['endFrame'] = words_shots[i+1]['startFrame'] if i+1 < len(words_shots) else build['summary']['frames']
    s['durationFrames'] = s['endFrame'] - s['startFrame']
words = dict(script='script.md', scriptSha256=sha(D/'script.md'), fps=30,
             audio='voice.wav', audioSha256=sha(D/'voice.wav'),
             durationFrames=build['summary']['frames'], asrModel='none',
             timingMethod='Measured TTS sentence boundaries and shared acoustic onset rule; not ASR.',
             wordAlignment=False, shots=words_shots,
             onsetTable=[dict(shot=s['id'], sentence=s['sentences'][0]['id'], onsetFrame=s['onsetFrame'],
                              source='acoustic sentence onset') for s in words_shots])
save(D/'words.json', words)

source = f"voice.wav {sha(D/'voice.wav')[:8]} + words.json {sha(D/'words.json')[:8]} + script.md {sha(D/'script.md')[:8]}"
shots = []
cues = []
for (n, slug, body), ws in zip(sections, words_shots):
    start = ws['startFrame']
    narration = re.search(r'^旁白：(.*)$', body, re.M)[1]
    visual = re.search(r'^画面：(.*)$', body, re.M)[1]
    subs = []
    for i, sent in enumerate(ws['sentences']):
        fr = 0 if i == 0 else max(0, math.floor(sent['startFrame']) - start)
        to = (math.floor(ws['sentences'][i+1]['startFrame']) - start - 1
              if i+1 < len(ws['sentences']) else ws['durationFrames'] - 1)
        subs.append(dict(text=sent['text'], **{'from':fr}, to=to, duration=to-fr+1))
    elements = []
    cue_frames = {}
    # These labels start their own sentence, so no estimated interior word cue is used.
    for term, number, key in EPISODE['terms']:
        if int(n) == number:
            sent = next(s for s in ws['sentences'] if s['text'].startswith(term))
            onset = sent['onsetFrame'] - start
            fr = max(1, math.floor(onset)-2)
            cue_frames[key] = fr
            elements.append(dict(id=key, type='text', text=term, cueText=term,
                                 appearFrame=fr, x=130,y=165,w=500,h=80,fontSize=58,
                                 cueOnset=dict(sentence=sent['id'], asrFrame=None,
                                               onsetLocal=onset,rule='pause/acoustic sentence onset',delay=0)))
            cues.append(dict(shot=ws['id'],cue=term,sentence=sent['id'],onsetFrame=sent['onsetFrame']))
    cue_frames['sentences'] = [math.floor(s['startFrame'])-start for s in ws['sentences']]
    shot = dict(id=f'{int(n):02d}', scriptShot=int(n), chapterId=slug,
                **{'from':start}, durationInFrames=ws['durationFrames'],
                narration=narration, subtitles=subs,
                voice=[dict(id=s['id'],wavStart=s['startFrame'],wavEnd=s['endFrame'],
                            localStart=s['startFrame']-start,localEnd=s['endFrame']-start) for s in ws['sentences']],
                cueFrames=cue_frames,
                timing=dict(source=source,wavFrom=ws['speechStartFrame'],wavTo=ws['speechEndFrame'],
                            holdFrames=0,
                            holdReason='Natural sentence pauses; minimum shot 7.5s.'),
                frame='canvas', camera=None,boxShot=False,mapShot=False,
                scriptVisual=visual,direction=visual,elements=elements,animations=[],
                transition=dict(type='cut',durationInFrames=0))
    shots.append(shot)
save(D/'voice/cues.json', cues)
save(D/'voice/cue_tests.json', [[c['shot'],c['cue']] for c in cues])
covers = json.loads((D/'covers.json').read_text()) if (D/'covers.json').exists() else {}
sb = dict(meta=dict(title=EPISODE['title'],episode=EPISODE['ep'],slug=EPISODE['slug']+'-codex-v1',
                    width=1920,height=1080,fps=30,durationInFrames=words['durationFrames'],finalVideoFrames=words['durationFrames'],
                    draft=True,provisionalTiming=False,pendingAudio=False,
                    timingSource=source,
                    onsetRule=dict(module='episodes/_shared/onset_rule.py',checker='episodes/_shared/label_onset_strict.py',window=[-6,2]),
                    style='One causal data example; progressive reveal and continuous request identity; dark canvas, no physical metaphor or fake window.',
                    visualRevision=EPISODE.get('visualRevision',1),navigationRevision=EPISODE.get('navigationRevision'),visualDirection='visual-direction.md',
                    palette=dict(bg='#0F172A',text='#E5E7EB'),
                    sampleDataLabel='教学示例 · 数值非生产参数',
                    boxShots=[],mapShots=[],devtoolsShots=[],covers=covers,
                    
                    audioReview='No automatic ASR available. Sentence-boundary captions; final listening review pending.'),
          assets=dict(new=[],reuse=[],procedural=dict(description='See knoll-props.md and remotion/src/Main.tsx.')),
          scenes=[])
# Preserve meaningful scene groups so the eventual site can use real chapter starts.
for cid, title, first, last in EPISODE['scenes']:
    group = [q for q in shots if first <= q['scriptShot'] <= last]
    for q in group: q['chapterId'] = cid
    sb['scenes'].append(dict(id=cid,chapterId=cid,title=title,**{'from':group[0]['from']},durationInFrames=sum(q['durationInFrames'] for q in group),shots=group))
save(D/'storyboard.json', sb)
save(D/'voice/shot_frames.json', dict(fps=30,durationFrames=words['durationFrames'],
                                     audioSha256=words['audioSha256'],shots=words_shots))

# Captions keep the actual narration; no speech speed or audio is changed.
def stamp(frame):
    ms = round(frame/30*1000)
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
captions=[]
for sent in [s for ws in words_shots for s in ws['sentences']]:
    captions.append(f"{len(captions)+1}\n{stamp(sent['startFrame'])} --> {stamp(sent['endFrame'])}\n{sent['text']}\n")
(D/'captions.srt').write_text('\n'.join(captions))
print(f"Assembled {len(shots)} shots, {len(build['sentences'])} measured sentences, {words['durationFrames']} frames.")
