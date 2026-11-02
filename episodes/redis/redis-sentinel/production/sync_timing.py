#!/usr/bin/env python3
"""Bind teaching stages and article figures to this episode's measured voice.

No inference of interior word timestamps. Each action has a readable actual window.
"""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
board=json.loads((D/'storyboard.json').read_text());model=json.loads((D/'model.json').read_text())
shots=[s for scene in board['scenes'] for s in scene['shots']]
timing={}
for shot in shots:
    stages=model['shots'][shot['id']];duration=shot['durationInFrames'];windows=[]
    for index,stage in enumerate(stages):
        start=round(index*duration/len(stages));end=round((index+1)*duration/len(stages))
        windows.append({'index':index,'modelState':stage['id'],'from':start,'to':end,'globalFrom':shot['from']+start,'globalTo':shot['from']+end})
    timing[shot['id']]=windows
out={'fps':30,'bodyFrames':board['meta']['durationInFrames'],'audioTimingSource':board['meta']['timingSource'],'definition':'Equal readable stage windows within measured shot envelopes; no internal word alignment claims.','shots':timing}
(D/'model-timing.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
plan=json.loads((D/'plan.json').read_text())
for item in plan:item['actualStateWindows']=timing[item['id']]
(D/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
figures=[]
for shotid,index,file in [('07',1,'01-authorization.jpg'),('11',4,'02-promotion.jpg')]:
    shot=next(s for s in shots if s['id']==shotid);window=timing[shotid][index];frame=window['globalTo']-2
    figures.append({'shot':shotid,'modelState':window['modelState'],'frame':frame,'seconds':frame/30,'file':'article/'+file})
article=D/'article.mdx';text=article.read_text();text=text.replace('seekTo={75}',f'seekTo={{{figures[0]["seconds"]}}}').replace('seekTo={130}',f'seekTo={{{figures[1]["seconds"]}}}')
article.write_text(text)
(D/'article-figure-plan.json').write_text(json.dumps({'fps':30,'figures':figures},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'bodyFrames':out['bodyFrames'],'figures':figures,'timingSHA256':hashlib.sha256((D/'model-timing.json').read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
