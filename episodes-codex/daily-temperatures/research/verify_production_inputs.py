"""Source/geometry precheck only; intentionally does not render media or infer audio."""
from pathlib import Path
import hashlib
import json
import re
from PIL import ImageFont

EP = Path(__file__).resolve().parents[1]
read = lambda name: json.loads((EP / name).read_text())
source = (EP/'solution.py').read_text()
source_sha = hashlib.sha256(source.encode()).hexdigest()
script = (EP/'script.md').read_text()
plan, sb, covers = read('plan.json'), read('storyboard.json'), read('covers.json')
sections = re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)',script,re.S)
assert len(sections) == len(plan) == 14
assert len({p['chapterId'] for p in plan}) == 4
narration = []
for (number,slug,body), item in zip(sections,plan):
    assert number == item['id'] and slug == item['slug']
    text = re.search(r'^旁白：(.*)$',body,re.M)[1]
    assert len(re.findall('[。？！]',text)) == 2
    assert ''.join(re.findall(r'[^。？！]+[。？！]',text)) == text
    narration.append(text)
    for cue in item['cues']:
        assert re.findall(r'[^。？！]+[。？！]',text)[cue['sentence']].startswith(cue['term'])
assert '单调栈' not in ''.join(narration[:4])
assert narration[4].split('。')[1].startswith('单调栈')
assert read('solution.json')['lines'] == source.splitlines()
assert read('solution.json')['sourceSha256'] == source_sha
assert read('research/trace.json')['sourceSha256'] == source_sha
assert read('research/algorithm-check.json')['sourceSha256'] == source_sha
article = (EP/'article.mdx').read_text()
assert re.search(r'```python\n(.*?)```',article,re.S)[1] == source
shots = [sh for scene in sb['scenes'] for sh in scene['shots']]
assert len(shots) == 14
assert sb['meta']['provisionalTiming'] and sb['meta']['pendingAudio']
assert len([sub for sh in shots for sub in sh['subtitles']]) == 28
card = sb['meta']['unvoicedEndCard']
assert card['durationInFrames'] == 150
assert card['from'] + 150 == sb['meta']['durationInFrames']
assert shots[-1]['from'] + shots[-1]['codeCardFrom'] == card['from']
assert shots[-1]['subtitles'][-1]['to'] < shots[-1]['codeCardFrom']
assert not (EP/'voice.wav').exists(), 'Phase1 must not pretend audio exists'
assert not (EP/'words.json').exists(), 'Phase1 must not create artificial voice timings'
font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
mono='/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf'
font_measurements=[]
for size,cfg in covers['sizes'].items():
    for element in cfg['elements']:
        if size=='4x3':
            assert element['x']>=315 and element['x']+element['w']<=1125
            assert element['y']+element['h']<918
        if element['type']=='text':
            font=ImageFont.truetype(font_path,element['fontSize'])
            width=max(font.getlength(line) for line in element['text'].splitlines())
            assert width <= element['w'], (size,element['id'],width,element['w'])
            font_measurements.append(dict(size=size,id=element['id'],fixedFontSize=element['fontSize'],
                                          measuredWidth=round(width,2),available=element['w']))
code_font=ImageFont.truetype(mono,36)
code_width=max(code_font.getlength(line) for line in source.splitlines())
assert code_width <= 1580
assert 222+(len(source.splitlines())-1)*52<920
main = (EP/'remotion/src/Main.tsx').read_text()
assert 'caseData.events[id]' in main
assert 'data-trace-event' in main
assert 'function dailyTemperatures' not in main
assert not re.search(r'auto.?shrink|scale\s*\([^)]*font',main,re.I)
report=dict(status='pass',scope='Static source/geometry only; no image or audio generated',
            solutionSha256=source_sha,shots=14,sentences=28,chapters=4,
            narrationCharacters=sum(map(len,narration)),
            draftFrames=sb['meta']['durationInFrames'],draftSeconds=sb['meta']['durationInFrames']/30,
            provisionalTiming=True,pendingAudio=True,codeCardFrames=150,codeFixedFontSize=36,
            codeMeasuredMaxWidth=round(code_width,2),codeAvailableWidth=1580,
            coverFontMeasurements=font_measurements,
            cover4x3='Declared content elements x315..1125 and bottom<918; actual rendered image still pending',
            limits=['No rendered static/dynamic inspection','No TTS or real onset','No ASR or human listening'])
(EP/'research/phase1-source-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','shots','sentences','chapters','narrationCharacters','draftSeconds','codeMeasuredMaxWidth']}))
