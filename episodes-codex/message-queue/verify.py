"""Check actual episode timing, captions, safety geometry and frozen files."""
from pathlib import Path
import hashlib,json,subprocess,sys,wave
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=json.loads((D/'storyboard.json').read_text());W=json.loads((D/'words.json').read_text());C=json.loads((D/'covers.json').read_text())
shots=[q for s in S['scenes'] for q in s['shots']]
assert W['scriptSha256']==sha(D/'script.md')
assert W['audioSha256']==sha(D/'voice.wav')
assert (D/'voice.wav').read_bytes()==(D/'remotion/public/audio/voice.wav').read_bytes()
with wave.open(str(D/'voice.wav')) as a:
 assert a.getframerate()==48000 and a.getnchannels()==1 and a.getnframes()==W['durationFrames']*1600
pos=0
for q in shots:
 assert q['from']==pos and q['durationInFrames']>0
 assert q['timing']['holdFrames']==0
 assert ''.join(s['text'] for s in q['subtitles'])==q['narration']
 assert q['subtitles'][0]['from']==0 and q['subtitles'][-1]['to']==q['durationInFrames']-1
 for a,b in zip(q['subtitles'],q['subtitles'][1:]):assert a['to']+1==b['from']
 for v in q['voice']:
  assert abs(q['from']+v['localStart']-v['wavStart'])<.5
  assert v['wavEnd']<=W['durationFrames']
 for e in q['elements']:
  if e.get('cueText'):assert q['durationInFrames']-e['appearFrame']>=63
 pos+=q['durationInFrames']
assert pos==W['durationFrames']==S['meta']['durationInFrames']
assert S['meta']['covers']==C
for size,s in C['sizes'].items():
 for b in s['textBoxes']:
  assert b['y']+b['h']<s['bottom15Y']
  assert b['x']>=0 and b['x']+b['w']<=s['width']
  if size=='4x3':assert 315<=b['x'] and b['x']+b['w']<=1125
report={'shots':len(shots),'sentences':sum(len(q['sentences']) for q in W['shots']),'frames':pos,'seconds':pos/30,'audioSha256':W['audioSha256'],'captionExact':True,'wholeTrackOffset':0,'coverSafeGeometry':True}
if (D/'source-sha256.json').exists():
 m=json.loads((D/'source-sha256.json').read_text());bad=[p for p,h in m.items() if sha(D/p)!=h];assert not bad,bad
 report['frozenInputs']=len(m)
if '--final' in sys.argv:
 f=D/'video.mp4';j=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]))
 v=next(s for s in j['streams'] if s['codec_type']=='video');a=next(s for s in j['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'30/1')
 assert int(v['nb_read_frames'])==pos
 assert v['codec_name']=='h264' and a['codec_name']=='aac'
 report.update(videoSha256=sha(f),videoFrames=int(v['nb_read_frames']),videoCodec=v['codec_name'],audioCodec=a['codec_name'],width=v['width'],height=v['height'],fps=30)
 report['mixReport']=json.loads((D/'remotion/out/mix-report.json').read_text())
 (D/'render-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
else:(D/'preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
