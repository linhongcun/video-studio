"""Verify actual encoding and extract representative frames, without changing media."""
from pathlib import Path
import hashlib,json,subprocess,re
D=Path(__file__).resolve().parent
v=D/'video.mp4'
sb=json.loads((D/'storyboard.json').read_text());expected=sb['meta']['durationInFrames']
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(v)]))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert video['width']==1920 and video['height']==1080
assert video['r_frame_rate']=='30/1'
assert int(video.get('nb_read_frames',video.get('nb_frames',0)))==expected
assert abs(float(video['duration'])-expected/30)<.04
assert int(audio['sample_rate'])==48000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((D/'source-sha256.json').read_text())
assert all(sha(D/p)==s for p,s in manifest.items()),'production inputs changed after freezing'
mix=json.loads((D/'remotion/out/mix-report.json').read_text())
paths={str(v.name):sha(v)}
for size in ['16x9','4x3','3x4']:
 p=D/f'cover-{size}.png'
 assert p.exists()
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-q:v','2',str(D/f'cover-{size}.jpg')],check=True)
 paths[f'cover-{size}.jpg']=sha(D/f'cover-{size}.jpg')
out=Path('/tmp')/(D.name+'-codex-final');out.mkdir(exist_ok=True)
shots=[q for sc in sb['scenes'] for q in sc['shots']]
frames=sorted(set([0,expected-1]+[q['from']+round((q['durationInFrames']-1)*p) for q in shots for p in [0,.1,.55,.95,1]]))
expr='+'.join(f'eq(n,{f})' for f in frames)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(v),'-vf',f"select='{expr}',scale=960:540",'-vsync','0',str(out/'%03d.png')],check=True)
check=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(v),'-vf','blackdetect=d=0.15:pix_th=0.05,freezedetect=n=-50dB:d=6','-an','-f','null','-'],capture_output=True,text=True,check=True)
lines=[r for r in check.stderr.splitlines() if 'black_start:' in r or 'freeze_' in r]
assert not any('black_start:' in q for q in lines),'encoded video contains black interval'
(out/'sampling.json').write_text(json.dumps(dict(frames=frames,notes=lines),indent=2)+'\n')
(D/'render-result.json').write_text(json.dumps(dict(videoSha256=sha(v),frames=expected,seconds=expected/30,width=1920,height=1080,fps=30,audioSampleRate=int(audio['sample_rate']),mix=mix,hashes=paths,sourceManifestVerified=True,decodedFrameSamples=dict(directory=str(out),frames=frames),blackAndFreezeNotes=lines),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(sha256=sha(v),frames=expected,seconds=expected/30,mix=mix,notes=lines),ensure_ascii=False))
