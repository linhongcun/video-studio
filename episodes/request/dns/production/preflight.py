"""Check the frozen timeline, captions, selected audio, cue windows and cover geometry."""
from pathlib import Path
import hashlib,json,re,wave
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
W=json.loads((D/'words.json').read_text());S=json.loads((D/'storyboard.json').read_text());C=json.loads((D/'covers.json').read_text())
assert W['scriptSha256']==sha(D/'script.md')
assert W['audioSha256']==sha(D/'voice.wav')
assert (D/'voice.wav').read_bytes()==(D/'remotion/public/audio/voice.wav').read_bytes()
assert S['meta']['covers']==C
ss=[s for c in S['scenes'] for s in c['shots']]
start=0
for s in ss:
 assert s['from']==start
 assert ''.join(x['text'] for x in s['subtitles'])==s['narration']
 last=-1
 for sub in s['subtitles']:
  assert sub['from']==last+1;last=sub['to']
 assert last==s['durationInFrames']-1
 for e in s['elements']:
  if e.get('cueText'):assert s['durationInFrames']-e['appearFrame']>=63
 start+=s['durationInFrames']
assert start==W['durationFrames']==S['meta']['durationInFrames']
with wave.open(str(D/'voice.wav'))as w:assert w.getnframes()==start*1600 and w.getframerate()==48000
for key,c in C['sizes'].items():
 for b in c['textBoxes']:
  assert b['y']+b['h']<c['bottom15Y']
  if key=='4x3':assert b['x']>=315 and b['x']+b['w']<=1125
B=json.loads((D/'voice/build.json').read_text())
assert not B['summary']['inner_dropouts']
assert B['summary']['max_join_sample_jump']<0.05
assert all(r['tailCut']>0.05 for r in B['sentences'])
if(D/'source-sha256.json').exists():
 for rel,value in json.loads((D/'source-sha256.json').read_text()).items():assert sha(D/rel)==value,rel
report={'frames':start,'shots':len(ss),'captions':sum(len(s['subtitles'])for s in ss),'voiceSha256':sha(D/'voice.wav'),'wordAlignment':False,'checks':'timeline, frozen narration captions, audio samples, cue hold >=63f, cover safe area, acoustic gaps and trim; not ASR or human listening','passed':True}
(D/'preflight-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
