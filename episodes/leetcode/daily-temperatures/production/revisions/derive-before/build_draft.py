"""Prepare explicitly provisional timing for editorial/source review only.

Run prepare_code_endcard.py after real voice build; never reuse these draft
sentence envelopes as measured onset times or release timing.
"""
from pathlib import Path
import hashlib
import json
import math
import re

EP = Path(__file__).resolve().parent
script = (EP / 'script.md').read_text()
config = json.loads((EP / 'episode-config.json').read_text())
plan = json.loads((EP / 'plan.json').read_text())
sections = re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)', script, re.S)
assert len(sections) == len(plan) == 14
scenes = []
offset = 0
for (n, slug, body), item in zip(sections, plan):
    assert item['id'] == n and item['slug'] == slug
    narration = re.search(r'^旁白：(.*)$', body, re.M)[1]
    sentences = re.findall(r'[^。？！]+[。？！]', narration)
    assert len(sentences) == 2 and ''.join(sentences) == narration
    duration = max(225, math.ceil(len(narration) * 6.2 + 16))
    second = round(duration * len(sentences[0]) / len(narration))
    card = 150 if n == '14' else 0
    labels = {cue['term']: second if cue['sentence'] else 1 for cue in item['cues']}
    shot = dict(id=n, scriptShot=int(n), visualType=item['visualType'], chapterId=item['chapterId'],
                **{'from': offset}, durationInFrames=duration + card,
                narration=narration, direction=re.search(r'^画面：(.*)$', body, re.M)[1],
                cueFrames=dict(sentences=[0, second], labels=labels),
                subtitles=[dict(text=sentences[0], **{'from': 0}, to=second-1),
                           dict(text=sentences[1], **{'from': second}, to=duration-1)],
                timing=dict(source='PROVISIONAL editorial pacing only; pendingAudio; no measured onset'),
                voice=[], elements=[], animations=[], frame='canvas')
    if card:
        shot['codeCardFrom'] = duration
        config['unvoicedEndCard']['from'] = offset + duration
    if not scenes or scenes[-1]['chapterId'] != item['chapterId']:
        scenes.append(dict(id=item['chapterId'], chapterId=item['chapterId'], title=item['chapterTitle'],
                           **{'from': offset}, durationInFrames=0, shots=[]))
    scenes[-1]['shots'].append(shot)
    scenes[-1]['durationInFrames'] += duration + card
    offset += duration + card
sb = dict(meta=dict(title=config['title'],episode=35,episodePart='LeetCode 739',slug='daily-temperatures',
                    width=1920,height=1080,fps=30,durationInFrames=offset,
                    provisionalTiming=True,pendingAudio=True,draft=True,
                    timingSource='PROVISIONAL editorial timing; no voice.wav or words.json exists',
                    style=config['style'],sampleDataLabel=config['sampleDataLabel'],
                    scriptSha256=hashlib.sha256((EP/'script.md').read_bytes()).hexdigest(),
                    unvoicedEndCard=config['unvoicedEndCard']), scenes=scenes)
(EP/'storyboard.json').write_text(json.dumps(sb,ensure_ascii=False,indent=2)+'\n')
(EP/'episode-config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
print(f'Draft only: {offset} frames ({offset/30:.2f}s), 14 shots, 28 sentences, last 150 frames code card.')
