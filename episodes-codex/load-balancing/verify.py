"""Verify frozen production inputs and, when present, the actual encoded MP4."""
from pathlib import Path
import hashlib,json,subprocess,wave
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((D/'source-sha256.json').read_text())
changed=[name for name,h in manifest.items() if not (D/name).exists() or sha(D/name)!=h]
assert not changed,changed
sb=json.loads((D/'storyboard.json').read_text());W=json.loads((D/'words.json').read_text())
shots=[s for c in sb['scenes'] for s in c['shots']]
assert sb['meta']['durationInFrames']==sum(s['durationInFrames'] for s in shots)==W['durationFrames']
assert W['scriptSha256']==sha(D/'script.md') and W['audioSha256']==sha(D/'voice.wav')
assert sha(D/'voice.wav')==sha(D/'remotion/public/audio/voice.wav')
offset=0
for shot in shots:
 assert shot['from']==offset
 assert ''.join(s['text'] for s in shot['subtitles'])==shot['narration']
 assert shot['subtitles'][0]['from']==0 and shot['subtitles'][-1]['to']==shot['durationInFrames']-1
 for a,b in zip(shot['subtitles'],shot['subtitles'][1:]):assert a['to']+1==b['from']
 for v in shot['voice']:assert abs(shot['from']+v['localStart']-v['wavStart'])<=.5
 for el in shot['elements']:assert shot['durationInFrames']-el['appearFrame']>=63
 offset+=shot['durationInFrames']
with wave.open(str(D/'voice.wav')) as f:assert f.getnframes()*30==W['durationFrames']*f.getframerate()
cover=json.loads((D/'covers.json').read_text());assert sb['meta']['covers']==cover
s=cover['sizes']['4x3'];x=s['content']['x'];w=s['content']['w']
assert x>=315 and x+w<=1125
for box in s['textBoxes']:assert box['x']>=315 and box['x']+box['w']<=1125 and box['y']+box['h']<918
result=dict(frozenInputs=len(manifest),changedInputs=changed,frames=offset,fps=30,seconds=offset/30,audioSha256=sha(D/'voice.wav'),storyboardSha256=sha(D/'storyboard.json'),wordAlignment=False,asrReview='Unavailable; acoustic sentence onsets only, no full human listening claim')
if (D/'video.mp4').exists():
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(D/'video.mp4')]))
 v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
 assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='30/1'
 assert int(v['nb_frames'])==offset,(v['nb_frames'],offset)
 assert abs(float(p['format']['duration'])-offset/30)<.1
 digest=sha(D/'video.mp4');size=(D/'video.mp4').stat().st_size
 result.update(sha256=digest,videoSha256=digest,bytes=size,videoBytes=size,width=v['width'],height=v['height'],videoCodec=v['codec_name'],audioCodec=a['codec_name'],audio=a['codec_name'],audioSampleRate=int(a['sample_rate']),formatDuration=float(p['format']['duration']))
 decode=subprocess.run(['ffmpeg','-v','error','-i',str(D/'video.mp4'),'-f','null','-'],capture_output=True,text=True)
 assert decode.returncode==0,decode.stderr
 result['fullDecode']='passed'
 mix=D/'remotion/out/mix-report.json'
 if mix.exists():
  result['mix']=json.loads(mix.read_text())
  result['finalLUFS']=result['mix']['final_LUFS'];result['truePeakDBTP']=result['mix']['true_peak_dBTP']
 result['covers']={f'cover-{s}.jpg':sha(D/f'cover-{s}.jpg') for s in ['16x9','4x3','3x4']}
 result['checks']=dict(frozenInputsUnchanged=True,measuredSentenceTiming=True,wordLevelASR=False,fullHumanListening=False)
 (D/'render-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
