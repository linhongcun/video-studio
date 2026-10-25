"""Audit the actual encoded output; does not change render inputs or audio."""
from pathlib import Path
import hashlib,json,re,subprocess,shutil
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((D/'source-sha256.json').read_text())
for rel,value in manifest.items():assert sha(D/rel)==value,rel
cover_inputs=[D/'covers.json',D/'production.json',D/'remotion/src/Cover.tsx']
cover_outputs=[D/f'cover-{size}.png' for size in ['16x9','4x3','3x4']]
if any(not p.exists() or p.stat().st_mtime<max(q.stat().st_mtime for q in cover_inputs) for p in cover_outputs):
    subprocess.run(['node','scripts/covers.mjs'],cwd=D/'remotion',check=True)
for size in ['16x9','4x3','3x4']:
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(D/f'cover-{size}.png'),'-q:v','2',str(D/f'cover-{size}.jpg')],check=True)
shutil.copy2(D/'cover-3x4.jpg',D/'poster.jpg')
S=json.loads((D/'storyboard.json').read_text());shots=[q for c in S['scenes']for q in c['shots']];expected=S['meta']['durationInFrames'];v=D/'video.mp4'
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(v)]))
vs=next(s for s in p['streams']if s['codec_type']=='video');au=next(s for s in p['streams']if s['codec_type']=='audio')
assert(vs['width'],vs['height'],vs['avg_frame_rate'])==(1920,1080,'30/1')
assert int(vs['nb_frames'])==expected
assert au['codec_name']=='aac' and int(au['sample_rate'])==48000
r=subprocess.run(['ffmpeg','-v','error','-nostats','-i',str(v),'-progress','pipe:1','-f','null','-'],capture_output=True,text=True,check=True)
assert 'progress=end'in r.stdout
assert int(re.findall(r'^frame=(\d+)$',r.stdout,re.M)[-1])==expected
assert not r.stderr.strip(),r.stderr
mix=json.loads((D/'remotion/out/mix-report.json').read_text())
assert abs(mix['final_LUFS']+16)<0.3
assert mix['true_peak_dBTP']<=-2
frames=sorted(set([0,expected-1]+[q['from']+min(q['durationInFrames']-1,round(q['durationInFrames']*.65))for q in shots]+[q['from']-1 for q in shots[1:]]+[q['from']for q in shots[1:]]))
out=Path('/tmp')/f'{D.name}-encoded';out.mkdir(exist_ok=True)
select='+'.join(f'eq(n,{f})'for f in frames)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(v),'-an','-vf',f"select='{select}',scale=960:540",'-fps_mode','vfr',str(out/'frame-%03d.png')],check=True)
assert len(list(out.glob('frame-*.png')))==len(frames)
(out/'frames.json').write_text(json.dumps([{'frame':f,'file':str(out/f'frame-{i:03d}.png')}for i,f in enumerate(frames,1)],indent=2)+'\n')
rep={'visualRevision':S['meta']['visualRevision'],'width':1920,'height':1080,'fps':vs['avg_frame_rate'],'frames':expected,'decodedFrames':expected,'seconds':float(p['format']['duration']),'audio':au['codec_name'],'audioSampleRate':int(au['sample_rate']),'finalLUFS':mix['final_LUFS'],'truePeakDBTP':mix['true_peak_dBTP'],'bytes':v.stat().st_size,'sha256':sha(v),'voiceSha256':sha(D/'voice.wav'),'coverSha256':{size:sha(D/f'cover-{size}.jpg') for size in ['16x9','4x3','3x4']},'sourceInputsVerified':len(manifest),'sampledEncodedFrames':frames,'wordAlignment':False,'checks':'Frozen inputs, format, actual decode count, complete audio/video decode and loudness passed. Encoded visual samples still require review.','limitations':'Sentence boundaries and acoustic sentence onsets; no word-level ASR or human listening claimed.'}
(D/'render-result.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps(rep,ensure_ascii=False))
for rel,value in manifest.items():assert sha(D/rel)==value,rel
