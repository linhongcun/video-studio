"""Bind approved narration and shared-voice measurements to this episode.

Reads sentence envelopes measured by voice/build-metadata.py. Does not perform
speech synthesis, trim audio, infer interior word timings, or implement onset.
"""
from pathlib import Path
import hashlib
import json
import math
import re

D = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


script = (D / 'script.md').read_text()
plan = json.loads((D / 'content-plan.json').read_text())
words = json.loads((D / 'words.json').read_text())
sections = re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)', script, re.S)
assert len(plan) == len(sections) == len(words['shots']) == 20
assert words['scriptSha256'] == sha(D / 'script.md')
assert words['audioSha256'] == sha(D / 'voice.wav')
assert not words.get('wordAlignment', False)
source = ('voice.wav ' + sha(D / 'voice.wav') + ' + words.json ' +
          sha(D / 'words.json') + ' + script.md ' + sha(D / 'script.md'))
shots = []
for entry, section, ws in zip(plan, sections, words['shots']):
    number, slug, body = section
    assert int(entry['id']) == int(number)
    assert entry['slug'] == slug
    assert ws['id'] == f'{int(number):02d}-{slug}'
    start, duration = ws['startFrame'], ws['durationFrames']
    narration = re.search(r'^旁白：(.*)$', body, re.M)[1]
    visual = re.search(r'^画面：(.*)$', body, re.M)[1]
    sentences = ws['sentences']
    assert len(sentences) == 2
    assert ''.join(s['text'] for s in sentences) == narration == entry['narration']
    captions = []
    for index, sent in enumerate(sentences):
        first = 0 if index == 0 else math.floor(sent['startFrame']) - start
        last = (math.floor(sentences[index + 1]['startFrame']) - start - 1
                if index + 1 < len(sentences) else duration - 1)
        captions.append(dict(text=sent['text'], **{'from': first}, to=last,
                             duration=last-first+1))
    labels, elements = {}, []
    for index, cue in enumerate(entry['cues']):
        sent = sentences[cue['sentence']]
        assert sent['text'].startswith(cue['term'])
        onset = sent['onsetFrame'] - start
        frame = max(1, math.floor(onset)-2)
        labels[cue['term']] = frame
        elements.append(dict(id=f'label{number}_{index}', type='text',
            text=cue['term'], cueText=cue['term'], appearFrame=frame,
            renderBinding='Main.tsx term label uses cueFrames.labels',
            cueOnset=dict(sentence=sent['id'], asrFrame=None,
                          onsetLocal=onset, rule='shared acoustic sentence onset', delay=0)))
    shots.append(dict(id=f'{int(number):02d}', scriptShot=int(number),
        chapterId=entry['chapterId'], visualType=entry['visualType'],
        **{'from': start}, durationInFrames=duration, narration=narration,
        subtitles=captions,
        voice=[dict(id=s['id'], wavStart=s['startFrame'], wavEnd=s['endFrame'],
                    localStart=s['startFrame']-start, localEnd=s['endFrame']-start)
               for s in sentences],
        cueFrames=dict(labels=labels,
            sentences=[math.floor(s['startFrame'])-start for s in sentences],
            sentenceEnds=[math.ceil(s['endFrame'])-start for s in sentences],
            sentenceOnsets=[s['onsetFrame']-start for s in sentences]),
        timing=dict(source=source, wavFrom=ws['speechStartFrame'],
                    wavTo=ws['speechEndFrame'],
                    holdFrames=0,
                    naturalPauseFrames=ws['endFrame']-math.ceil(ws['speechEndFrame']),
                    holdReason='Whole audio stays in place; only recorded sentence/shot pauses, no added timing hold.'),
        frame='canvas', camera=None, boxShot=False, mapShot=False,
        scriptVisual=visual, direction=visual, title=entry['title'],
        sampleState=entry['state'], plannedActions=entry['actions'],
        elements=elements, animations=[], transition=dict(type='cut', durationInFrames=0)))

covers = json.loads((D / 'covers.json').read_text())
sb = dict(meta=dict(title='AI 能回答问题，怎么才能真正帮你办事？',
    episode=22, slug='agent-intro-v1', width=1920, height=1080, fps=30,
    durationInFrames=words['durationFrames'], finalVideoFrames=words['durationFrames'],
    draft=False, provisionalTiming=False, pendingAudio=False, timingSource=source,
    onsetRule=dict(module='episodes/_shared/onset_rule.py',
        checker='episodes/_shared/label_onset_strict.py', window=[-6, 2],
        frameFormula='max(1, floor(onsetLocal) - 2) + d'),
    style='Deep full-canvas mechanism animation; same example order; model requests, application execution, tool results and feedback shown as separate observable actions. No fake application shell or metaphor.',
    visualRevision=1, visualDirection='visual-direction.md',
    userScope='A01 concept entry before tool/schema/loop implementation lessons; only order/policy reads and a sourced recommendation, no refund execution.',
    palette=dict(bg='#0F172A', text='#E5E7EB'),
    sampleDataLabel='示例数据 · 订单8124 · 示例政策',
    boxShots=[], mapShots=[], devtoolsShots=[], covers=covers,
    discussionQuestion='模型提出了工具调用请求，是否表示查询已经执行？',
    audioReview='Measured TTS sentence envelopes and acoustic sentence-initial cues; no word ASR or claim of full human listening.'),
    assets=dict(new=[], reuse=[], procedural=dict(description='See knoll-props.md and remotion/src/Main.tsx.')),
    scenes=[])
for entry in plan:
    cid = entry['chapterId']
    if any(scene['chapterId'] == cid for scene in sb['scenes']):
        continue
    group = [shot for shot in shots if shot['chapterId'] == cid]
    sb['scenes'].append(dict(id=cid, chapterId=cid, title=entry['chapterTitle'],
        **{'from': group[0]['from']},
        durationInFrames=sum(shot['durationInFrames'] for shot in group), shots=group))
save(D / 'storyboard.json', sb)


def stamp(frame):
    ms = round(frame / 30 * 1000)
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'


captions = []
for sent in [sent for ws in words['shots'] for sent in ws['sentences']]:
    captions.append(f"{len(captions)+1}\n{stamp(sent['startFrame'])} --> {stamp(sent['endFrame'])}\n{sent['text']}\n")
(D / 'captions.srt').write_text('\n'.join(captions))
print(f'Assembled {len(shots)} shots, {len(captions)} measured sentence captions, {words["durationFrames"]} frames.')
