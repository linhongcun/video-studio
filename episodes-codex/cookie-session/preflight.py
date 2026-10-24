"""Checks concrete timeline, frozen-sentence captions, acoustic labels and cover geometry."""
from pathlib import Path
import json,re,hashlib,wave
D=Path(__file__).resolve().parent
load=lambda p:json.loads((D/p).read_text())
sb=load('storyboard.json');w=load('words.json');covers=load('covers.json');shots=[q for sc in sb['scenes'] for q in sc['shots']]
sha=lambda p:hashlib.sha256((D/p).read_bytes()).hexdigest()
assert w['scriptSha256']==sha('script.md') and w['audioSha256']==sha('voice.wav')
assert sb['meta']['covers']==covers
with wave.open(str(D/'voice.wav')) as a: assert a.getnframes()==w['durationFrames']*1600 and a.getframerate()==48000
start=0;labels=[]
for q in shots:
 assert q['from']==start;start+=q['durationInFrames']
 assert ''.join(x['text'] for x in q['subtitles'])==q['narration']
 assert q['subtitles'][0]['from']==0 and q['subtitles'][-1]['to']==q['durationInFrames']-1
 assert all(a['to']+1==b['from'] for a,b in zip(q['subtitles'],q['subtitles'][1:]))
 for e in q['elements']:
  assert q['durationInFrames']-e['appearFrame']>=63
  labels.append(e['text'])
assert start==w['durationFrames']==sb['meta']['durationInFrames']
for size,d in covers['sizes'].items():
 for b in d['textBoxes']:
  assert b['x']>=0 and b['x']+b['w']<=d['width'] and b['y']>=0 and b['y']+b['h']<=d['bottom15Y']
  if size=='4x3':assert b['x']>=315 and b['x']+b['w']<=1125 and b['y']+b['h']<918
assert not w['wordAlignment'] and w['asrModel']=='none'
print('PASS',len(shots),'shots',sum(len(s['subtitles']) for s in shots),'sentence captions',start,'frames; labels',labels,'; 3 cover sizes; ASR unavailable explicitly recorded')
