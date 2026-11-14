import json
import subprocess
import sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(P/'scripts/check_plan_cues.py')],check=True)
config=json.loads((P/'episode-config.json').read_text())
plan=json.loads((P/'plan.json').read_text())
trace=json.loads((P/config['algorithmTrace']).read_text())
fps=30; shot_frames=90; card_frames=round(config['unvoicedEndCard']['durationSeconds']*fps)
shots=[]; scenes=[]
for i,item in enumerate(plan):
 start=i*shot_frames; duration=shot_frames+(card_frames if i==len(plan)-1 else 0)
 labels={c['term']:[0,shot_frames//2][c['sentence']] for c in item['cues']}
 labels.update({a['cue']:[0,shot_frames//2][a['sentence']] for a in item['actions']})
 shot={'id':item['id'],'scriptShot':int(item['id']),'slug':item['slug'],'visualType':item['visualType'],'chapterId':item['chapterId'],'chapterTitle':item['chapterTitle'],'from':start,'durationInFrames':duration,'cueFrames':{'sentences':[0,shot_frames//2],'labels':labels},'subtitles':[],'voice':[],'elements':[{'id':'cue-'+item['id']+'-'+str(j),'type':'text','text':c['term'],'cueText':c['term'],'appearFrame':[0,shot_frames//2][c['sentence']],'x':130,'y':165,'w':1100,'h':80,'fontSize':52} for j,c in enumerate(item['cues'])],'actionCues':item['actions'],'scriptVisual':item['visual'],'traceEvents':item['traceEvents']}
 if i==len(plan)-1: shot['codeCardFrom']=shot_frames
 shots.append(shot)
 if scenes and scenes[-1]['chapterId']==item['chapterId']:
  scenes[-1]['shots'].append(shot);scenes[-1]['durationInFrames']+=duration
 else: scenes.append({'id':item['chapterId'],'chapterId':item['chapterId'],'title':item['chapterTitle'],'from':start,'durationInFrames':duration,'shots':[shot]})
duration=len(plan)*shot_frames+card_frames
story={'meta':{'title':config['title'],'episode':config['episode'],'episodePart':config['episodePart'],'slug':config['slug'],'width':1920,'height':1080,'fps':fps,'durationInFrames':duration,'draft':True,'provisionalTiming':True,'pendingAudio':True,'layoutPreviewOnly':True,'timingSource':'layout placeholder only; no audio timing','style':config['style'],'visualRevision':1,'visualDirection':'visual-direction.md','userScope':config['userScope'],'sampleDataLabel':config['sampleDataLabel'],'covers':json.loads((P/'covers.json').read_text()),'discussionQuestion':config['discussionQuestion'],'unvoicedEndCard':{'kind':'full-python-solution','from':(len(plan)-1)*shot_frames+shot_frames,'durationInFrames':card_frames,'codeSource':'solution.py','displaySource':'solution.json','timingStatus':'placeholder'}},'assets':{'new':[],'reuse':[],'procedural':{'description':'LC56 vector animation from trace; no audio timing.'}},'scenes':scenes}
out=P/'remotion/src/placeholders/storyboard.json'
out.write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n')
print(f'Wrote layout-only storyboard: {out.relative_to(P)} ({duration} frames).')
