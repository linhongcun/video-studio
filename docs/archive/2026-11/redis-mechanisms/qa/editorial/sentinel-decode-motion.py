from pathlib import Path
from PIL import Image
import hashlib,json,subprocess,wave,datetime
Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p in sorted(Q.glob('sentinel-clip-*/short-clip-review.json')):
    r=json.loads(p.read_text())
    if not r.get('machinePass'):continue
    out=p.parent/'decoded-review'
    if out.exists():continue
    out.mkdir()
    mp4=p.parent/'motion-with-original-voice.mp4'
    n=r['frames'];frames=list(range(0,n,30))
    if frames[-1]!=n-1:frames.append(n-1)
    expr='+'.join(f'eq(n\\,{f})' for f in frames)
    cmd=['ffmpeg','-v','error','-i',str(mp4),'-vf','select='+expr,'-vsync','0',str(out/'decoded-%03d.png')]
    dec=subprocess.run(cmd,capture_output=True,text=True)
    if dec.returncode:raise RuntimeError(dec.stderr)
    probe_cmd=['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(mp4)]
    pr=subprocess.run(probe_cmd,capture_output=True,text=True,check=True)
    probe=json.loads(pr.stdout)
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert int(video['nb_read_frames'])==n
    samples=[]
    for i,local in enumerate(frames,1):
        img=out/f'decoded-{i:03}.png'
        im=Image.open(img).convert('RGB')
        crop=im.crop((48,488,912,533))
        dark=sum(max(px)<100 for px in crop.getdata())
        samples.append({'frame':r['first']+local,'localFrame':local,'label':f'{p.parent.name} local{local} original{r["first"]+local}','file':str(img),'sha256':sha(img),'captionRegion':{'rect':[48,488,912,533],'darkPixelThreshold':100,'darkPixelCount':dark,'totalPixels':crop.width*crop.height,'pass':dark==0}})
    full=Path(r['production'])/'voice.wav';pcm=p.parent/'original-voice-interval.wav'
    with wave.open(str(full),'rb') as wav:
        wav.setpos(r['first']*1600);exact=wav.readframes(n*1600)
    with wave.open(str(pcm),'rb') as wav:
        info={'sampleRate':wav.getframerate(),'channels':wav.getnchannels(),'sampleWidth':wav.getsampwidth(),'samples':wav.getnframes()}
        actual=wav.readframes(wav.getnframes())
    report={'kind':'actual-bounded-preview-decode-and-original-voice-sample-review','createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'shortClipReport':str(p),'shortClipReportSHA256':sha(p),'mp4':str(mp4),'mp4SHA256':sha(mp4),'resolvedComposition':r['resolvedComposition'],'samples':samples,'videoProbe':video,'fullProbe':probe,'extraction':{'command':cmd,'returncode':dec.returncode,'stderr':dec.stderr},'voicePCM':{**info,'sourceVoiceSHA256':sha(full),'startSampleInclusive':r['first']*1600,'endSampleExclusive':(r['last']+1)*1600,'rawPCMSHA256':hashlib.sha256(actual).hexdigest(),'equalToExactOriginalPCMInterval':actual==exact},'machinePass':all(x['captionRegion']['pass'] for x in samples) and actual==exact,'visualReviewed':False,'limits':'Actual sampled decoded preview frames; full short clip decode checked separately. PCM equality proves provenance, not semantic listening. No final full media or formal color review.'}
    (out/'decoded-motion-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'clip':p.parent.name,'decodedSamples':len(samples),'frames':n,'machinePass':report['machinePass']}),flush=True)
