from pathlib import Path
import argparse,hashlib,json,subprocess
Q=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--clips',nargs='+',required=True);ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args()
out=a.out_dir.resolve();assert out.is_relative_to(Q) and not out.exists();out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'kind':'independent-decoded-clip-sequence','samples':[],'clips':[],'visualReviewed':False,'scope':'Actually decoded short source clips, sequence sampling every15frames plus exact end; no semantic audio-listening or final BT709-media claim.'}
for name in a.clips:
 d=Q/name;r=json.loads((d/'short-clip-review.json').read_text());assert r['machinePass']
 video=d/'motion-with-original-voice.mp4';assert sha(video)==r['files'][str(video)]
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames','-of','json',str(video)]))['streams'][0]
 assert int(info['nb_frames'])==r['frames'],(name,info,r['frames'])
 local=list(range(0,r['frames'],15))
 if r['frames']-1 not in local:local.append(r['frames']-1)
 dest=out/name;dest.mkdir()
 filt='select='+f'not(mod(n,15))+eq(n,{r["frames"]-1})'
 subprocess.run(['ffmpeg','-v','error','-i',str(video),'-vf',filt.replace(',','\\,'),'-fps_mode','vfr','-threads','1',str(dest/'decoded-%04d.png')],check=True)
 paths=sorted(dest.glob('decoded-*.png'));assert len(paths)==len(local),(name,len(paths),len(local))
 for n,p in zip(local,paths):result['samples'].append({'frame':r['first']+n,'label':name+f' local {n}','file':str(p),'sha256':sha(p)})
 result['clips'].append({'name':name,'reportSha256':sha(d/'short-clip-review.json'),'videoSha256':sha(video),'first':r['first'],'last':r['last'],'decodedVideoFrames':int(info['nb_frames']),'retainedFrames':len(paths),'resolution':[info['width'],info['height']]})
(out/'decoded-sequences.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'clips':len(result['clips']),'actualDecodedSamples':len(result['samples']),'report':str(out/'decoded-sequences.json')}))
