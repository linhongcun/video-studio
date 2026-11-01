"""Inspect the encoded output and assert its identity to frozen production timing."""
from pathlib import Path
import hashlib,json,subprocess,sys
D=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(D/'freeze.py'),'--verify'],check=True)
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(D/'video.mp4')]))
v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
w=json.loads((D/'words.json').read_text());frames=w['durationFrames']
assert v['codec_name']=='h264' and v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='30/1'
assert int(v['nb_read_frames'])==int(v['nb_frames'])==frames
assert a['codec_name']=='aac' and int(a['sample_rate'])==48000
assert abs(float(p['format']['duration'])-frames/30)<.1
r=subprocess.run(['ffmpeg','-v','error','-i',str(D/'video.mp4'),'-f','null','-'],capture_output=True,text=True,check=True)
assert not r.stderr.strip(),r.stderr
mix=json.loads((D/'remotion/out/mix-report.json').read_text());(D/'mix-report.json').write_text(json.dumps(mix,ensure_ascii=False,indent=2)+'\n')
assert abs(mix['final_LUFS']+16)<=.3 and mix['true_peak_dBTP']<=-2
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'sha256':sha(D/'video.mp4'),'bytes':(D/'video.mp4').stat().st_size,'frames':frames,'fps':30,'seconds':frames/30,'containerSeconds':float(p['format']['duration']),'width':1920,'height':1080,'videoCodec':'h264','audioCodec':'aac','sampleRate':48000,'finalLUFS':mix['final_LUFS'],'truePeakDBTP':mix['true_peak_dBTP'],'sourceInputs':len(json.loads((D/'source-sha256.json').read_text())),'voiceSha256':w['audioSha256'],'fullDecode':'passed','asrPerformed':False,'independentListeningPerformed':False,'covers':{k:sha(D/f'cover-{k}.jpg') for k in ['16x9','4x3','3x4']}}
(D/'render-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
