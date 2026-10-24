"""Check frozen-input, caption and semantic timing invariants for this production."""
from pathlib import Path
import hashlib,json,re,wave
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sb=json.loads((D/'storyboard.json').read_text());w=json.loads((D/'words.json').read_text());b=json.loads((D/'voice/build.json').read_text())
assert w['scriptSha256']==sha(D/'script.md')
assert w['audioSha256']==sha(D/'voice.wav')
assert (D/'voice.wav').read_bytes()==(D/'remotion/public/audio/voice.wav').read_bytes()
shots=[q for sc in sb['scenes'] for q in sc['shots']]
assert len(shots)==12 and sum(q['durationInFrames'] for q in shots)==w['durationFrames']==sb['meta']['durationInFrames']
assert not sb['meta'].get('pendingAudio') and not sb['meta'].get('provisionalTiming')
with wave.open(str(D/'voice.wav')) as a:
 assert a.getframerate()==48000 and a.getnchannels()==1 and a.getnframes()==w['durationFrames']*1600
for q in shots:
 assert ''.join(s['text'] for s in q['subtitles'])==q['narration'],q['id']
 assert q['subtitles'][0]['from']==0 and q['subtitles'][-1]['to']==q['durationInFrames']-1
 for a,z in zip(q['subtitles'],q['subtitles'][1:]):assert a['to']+1==z['from']
 for e in q['elements']:
  assert q['durationInFrames']-e['appearFrame']>=63
 for v in q['voice']:assert abs(q['from']+v['localStart']-v['wavStart'])<.5
for name,d in sb['meta']['covers']['sizes'].items():
 for r in d['textBoxes']:
  assert r['y']+r['h']<d.get('bottom15Y',d['height'])
  if name=='4x3':assert r['x']>=315 and r['x']+r['w']<=1125
for row in b['sentences']:
 sent=next(q for q in json.loads((D/'voice/sents.json').read_text()) if q['id']==row['id'])
 text=json.loads((D/'voice/takes'/f"{row['id']}-{row['take']}.txt.json").read_text())
 assert text==sent['tts'],row['id']
assert not b['summary']['inner_dropouts']
assert b['summary']['max_join_sample_jump']<.02
assert abs(b['summary']['track_lufs']+16)<.3
print(f"PASS: {len(shots)} shots; {len(b['sentences'])} narration sentences; {w['durationFrames']} frames; captions, voice placement, sources and cover safety bounds")
