"""Independent final packet/audio/endcard measurements; reuse shared full-decode receipts."""
from pathlib import Path
from fractions import Fraction
import datetime,hashlib,importlib.util,json,re,subprocess,wave
import numpy as np
from PIL import Image
EP=Path(__file__).resolve().parents[1];ROOT=next(p for p in EP.parents if (p/'AGENTS.md').is_file());MOVIE=EP/'video.mp4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
movie_sha=sha(MOVIE);OUT=EP/f'remotion/out/qa-independent-{movie_sha[:12]}';OUT.mkdir(parents=True,exist_ok=True)
manifest_file=EP/'source-sha256.json';manifest=read(manifest_file);manifest_sha=sha(manifest_file);assert manifest
for name,digest in manifest.items():assert sha(EP/name)==digest,name
qa=read(EP/'qa-audio-preflight.json');assert qa['status']=='passed';audio_qa_sha=sha(EP/'qa-audio-preflight.json')
for name,digest in qa['sourceSHA256'].items():assert sha(EP/name)==digest,name
for name,digest in qa['sharedImplementationSHA256'].items():assert sha(ROOT/name)==digest,name
sb=read(EP/'storyboard.json');card=sb['meta']['unvoicedEndCard'];body_frames=sb['meta']['durationInFrames'];fps=sb['meta']['fps'];assert fps==30 and card['durationInFrames']==150 and card['from']+150==body_frames
rendered=read(EP/'render-result.json');body_receipt=read(EP/'body-render-result.json');appendix=read(EP/'reference-appendix.json');preservation=read(EP/'reference-appendix-media-check.json');references=read(EP/'references.json');mix=read(EP/'mix-report.json')
body=EP/'remotion/out/body.mp4';body_sha=sha(body)
assert body_sha==body_receipt['sha256']==appendix['inputs']['bodySHA256']==preservation['bodySHA256']
assert rendered['sha256']==appendix['outputSHA256']==preservation['outputSHA256']==movie_sha
final_frames=rendered['frames'];appended=final_frames-body_frames
assert body_receipt['frames']==appendix['bodyFrames']==preservation['bodyFrames']==body_frames
assert final_frames==appendix['finalVideoFrames']==preservation['finalFrames'] and preservation['appendedFrames']==appended and preservation['passed']
assert appended==150 and all(page['durationInFrames']==150 for page in appendix['appendix']['pages']) if all('durationInFrames' in page for page in appendix['appendix']['pages']) else appended==150
for key in ['bodyDecodedFramesAndTimestampsEqual','outputVideoTimelineContinuous','audioPacketsAndTimingEqual']:assert preservation[key]
assert appendix['inputs']['referencesSHA256']==sha(EP/'references.json')
assert appendix['presentation']=='title-author' and appendix['layout']['renderedFields']==['title','credit'] and not appendix['layout']['quotesRendered']
assert appendix['bibliography']==[{'id':s['id'],'title':s['title'],'credit':s.get('author') or s['organization']} for s in references['sources']]
assert appendix['inputs']['generatorSHA256']==sha(ROOT/'episodes-codex/_shared/leetcode-video/references.py')
for key,path in [('themeSHA256',ROOT/'episodes-codex/_shared/leetcode-video/style-v1.json'),('fontSHA256',Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')),('boldFontSHA256',Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'))]:assert appendix['inputs'][key]==sha(path)
for page in appendix['appendix']['pages']:assert page['sha256']==sha(EP/'revisions/reference-endcards'/page['file'])
for key,path in [('oldEngineSHA256','episodes-codex/_shared/append_references.py'),('originalRendererSHA256','episodes-codex/_shared/append_references_original.py')]:assert appendix['dependencies'][key]==sha(ROOT/path)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(MOVIE)]))
video=next(stream for stream in probe['streams'] if stream['codec_type']=='video');audio=next(stream for stream in probe['streams'] if stream['codec_type']=='audio')
assert int(video['nb_frames'])==final_frames and Fraction(video['r_frame_rate'])==fps and (video['width'],video['height'])==(1920,1080)
assert audio['codec_name']=='aac' and int(audio['sample_rate'])==48000
packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts,duration','-of','json',str(MOVIE)]))['packets'];assert len(packets)==final_frames
video_base=Fraction(video['time_base']);expected_step=Fraction(1,fps)
assert sorted(Fraction(int(packet['pts']))*video_base for packet in packets)==[Fraction(i,fps) for i in range(final_frames)]
assert all((int(b['dts'])-int(a['dts']))*video_base==expected_step for a,b in zip(packets,packets[1:]))
assert all(int(packet['duration'])*video_base==expected_step for packet in packets)
spec=importlib.util.spec_from_file_location('province_shared_media_engine',ROOT/'episodes-codex/_shared/append_references.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
aac=shared.audio_packets(MOVIE);assert len(aac)==preservation['audioPacketCount'];assert shared.sequence_hash(aac)==preservation['audioPacketPayloadAndTimingSHA256']
assert all(packet['pts']==packet['dts'] for packet in aac)
assert all(int(b['pts'])==int(a['pts'])+int(a['duration']) for a,b in zip(aac,aac[1:]))
audio_base=Fraction(audio['time_base']);audio_end=(int(aac[-1]['pts'])+int(aac[-1]['duration']))*audio_base
assert abs(float(audio_end)-float(audio['duration']))<1e-5
# The only final-audio decode: stereo EBU measurement, then explicit mono output
# for source consistency diagnostics. No separate repeated loudness decode.
decoded=OUT/'decoded-mix.f32';audio_log=OUT/'audio-ebur128.log'
command=['ffmpeg','-hide_banner','-nostats','-y','-i',str(MOVIE),'-map','0:a:0','-af','ebur128=peak=true,aformat=channel_layouts=mono','-ar','48000','-f','f32le',str(decoded)]
result=subprocess.run(command,capture_output=True,text=True,check=True);audio_log.write_text(result.stderr);actual=np.fromfile(decoded,dtype='<f4').astype(np.float64)
with wave.open(str(EP/'voice.wav')) as wav:
    assert (wav.getframerate(),wav.getnchannels(),wav.getsampwidth())==(48000,1,2)
    voice=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(np.float64)/32767
assert sha(EP/'voice.wav')==qa['voice']['sha256']
lufs=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',result.stderr)[-1]);peak=float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',result.stderr)[-1]);assert abs(lufs+16)<=.3 and peak<=-2

def correlation(left,right):
    assert len(left)==len(right) and len(left)>100
    left=left-left.mean();right=right-right.mean()
    return float(np.dot(left,right)/(np.linalg.norm(left)*np.linalg.norm(right)))
lag_scores=[]
for lag in [-1600,-480,-160,-96,0,96,160,480,1600]:
    begin=max(0,-lag);end=min(len(voice),len(actual)-lag)
    lag_scores.append({'lagSamples':lag,'correlation':correlation(voice[begin:end],actual[begin+lag:end+lag])})
best=max(lag_scores,key=lambda row:row['correlation']);lag=best['lagSamples'];assert best['correlation']>.9
build=read(EP/'voice/build.json');windows=[]
for row in build['sentences']:
    begin,end=row['startSample'],row['endSample'];score=correlation(voice[begin:end],actual[begin+lag:end+lag]);assert score>.9,(row['id'],score)
    windows.append({'id':row['id'],'correlation':score,'startSample':begin,'endSample':end})
assert len(windows)==26
# Only last narrated frame + Python150 + references150 are decoded here.
start=card['from']-1;scan_count=final_frames-start;assert scan_count==301
seek=start/fps-.0005;scan_log=OUT/'endcards-showinfo.log';scan_command=['ffmpeg','-hide_banner','-nostats','-ss',str(seek),'-i',str(MOVIE),'-map','0:v:0','-an','-vf','showinfo','-frames:v',str(scan_count),'-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
indices=[start,card['from'],card['from']+75,body_frames-1,body_frames,body_frames+75,final_frames-1]
return_index=max(i for i,line in enumerate(read(EP/'solution.json')['lines']) if line.strip()=='return count');baseline=188+return_index*33
roi=[194,baseline-30,1780,baseline+10]
# ROI derives from the current frozen CodeCard's actual fixed line geometry.
assert sha(EP/'remotion/src/leetcode-style/CodeCard.tsx')==manifest['remotion/src/leetcode-style/CodeCard.tsx']
results={};frame_bytes=1920*1080*3
with scan_log.open('wb') as log:
    process=subprocess.Popen(scan_command,stdout=subprocess.PIPE,stderr=log);assert process.stdout
    for index in range(scan_count):
        raw=process.stdout.read(frame_bytes)
        while len(raw)<frame_bytes:
            piece=process.stdout.read(frame_bytes-len(raw))
            if not piece:break
            raw+=piece
        assert len(raw)==frame_bytes,(index,len(raw))
        frame=start+index;image=np.frombuffer(raw,dtype=np.uint8).reshape(1080,1920,3)
        if frame in indices:Image.fromarray(image).save(OUT/f'frame-{frame:04d}.png')
        if frame==start:continue
        kind='python' if frame<body_frames else 'references'
        if kind not in results:results[kind]={'fromFrame':frame,'toInclusive':frame,'scanned':0,'hashes':[],'maxFullFrameMAE255':0.,'first':image.copy()}
        row=results[kind];row['toInclusive']=frame;row['scanned']+=1;row['hashes'].append(hashlib.sha256(raw).hexdigest())
        difference=float(np.abs(image.astype(np.int16)-row['first'].astype(np.int16)).mean());row['maxFullFrameMAE255']=max(row['maxFullFrameMAE255'],difference)
        if kind=='python':
            patch=image[roi[1]:roi[3],roi[0]:roi[2]];ink=int(np.count_nonzero(patch[:,:,1]>150));row.setdefault('returnInk',[]).append(ink)
    assert process.stdout.read(1)==b'' and process.wait()==0
showinfo=scan_log.read_text();times=[float(value) for value in re.findall(r'\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([-\d.]+)',showinfo)]
assert len(times)>=scan_count and round((seek+times[0])*fps)==start and round((seek+times[scan_count-1])*fps)==final_frames-1
for kind,row in results.items():
    assert row['scanned']==150 and row['maxFullFrameMAE255']<.5
    hashes=row.pop('hashes');row['uniqueRGBHashes']=len(set(hashes));row['frameHashSequenceSHA256']=hashlib.sha256(json.dumps(hashes).encode()).hexdigest();row.pop('first')
    if kind=='python':
        values=row.pop('returnInk');row['returnROI']=roi;row['returnInkMinMax']=[min(values),max(values)];assert min(values)>100 and max(values)-min(values)<30
previews=[{'frame':frame,'file':str((OUT/f'frame-{frame:04d}.png').relative_to(EP)),'sha256':sha(OUT/f'frame-{frame:04d}.png')} for frame in indices]
for name,digest in manifest.items():assert sha(EP/name)==digest,name
assert sha(manifest_file)==manifest_sha and sha(MOVIE)==movie_sha and sha(EP/'qa-audio-preflight.json')==audio_qa_sha
report={'status':'measured-awaiting-actual-image-review','checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'movie':{'path':'video.mp4','sha256':movie_sha,'bytes':MOVIE.stat().st_size,'frames':final_frames,'fps':fps,'width':1920,'height':1080,'containerSeconds':float(probe['format']['duration'])},'body':{'sha256':body_sha,'frames':body_frames},'freeze':{'sha256':manifest_sha,'checked':len(manifest),'allMatchBeforeAndAfter':True},'audioPreflight':{'path':'qa-audio-preflight.json','sha256':audio_qa_sha,'allSourceAndSharedIdentitiesMatch':True},'timeline':{'videoPackets':len(packets),'videoTimeBase':str(video_base),'allVideoPTSUniqueContinuous':True,'allVideoDTSContinuous':True,'AACPackets':len(aac),'allAACPTSDTSEqualContinuous':True,'audioPacketHashMatchesSharedReceipt':True,'firstAACPts':int(aac[0]['pts']),'packetEndSeconds':float(audio_end),'method':'Actual ffprobe packet reads and shared packet payload/time hash;reuse already-executed full-decode/framemd5 preservation receipts.'},'audio':{'actualIntegratedLUFS':lufs,'actualTruePeakDBTP':peak,'bestLagSamples':lag,'bestLagFrames':lag/1600,'lagScores':lag_scores,'bestGlobalCorrelation':best['correlation'],'perSentenceAtBestLag':windows,'minSentenceCorrelation':min(row['correlation'] for row in windows),'sourceVoiceSHA256':sha(EP/'voice.wav'),'method':'One actual mixed-AAC decode supplies EBU measurement and mono diagnostics;Pearson against26 current source-voice windows,not ASR or onset alignment.','ebur128Summary':result.stderr[result.stderr.rfind('Summary:'):],'stderrSHA256':sha(audio_log)},'card':results['python'],'referencesCard':{**results['references'],'sourceIds':appendix['appendix']['sourceIds'],'presentation':appendix['presentation'],'bibliography':appendix['bibliography'],'layout':appendix['layout']},'referenceAudioEndpoint':{'referenceStartsSeconds':body_frames/fps,'packetEndSeconds':float(audio_end),'aacTailPastReferenceBoundarySeconds':float(audio_end)-body_frames/fps,'noNewAACPackets':True,'packetAndPCMIdentityEvidence':'Actual independent packet sequence matches same-body/final shared reference media preservation receipt.'},'previews':previews,'sharedPreservationEvidence':{'bodyFullDecode':{'path':'body-render-result.json','sha256':sha(EP/'body-render-result.json'),'bodySHA256':body_receipt['sha256'],'checks':body_receipt['checks']},'appendixFullDecodeAndPreservation':{'path':'reference-appendix-media-check.json','sha256':sha(EP/'reference-appendix-media-check.json'),**preservation},'defaultRendererResult':{'path':'render-result.json','sha256':sha(EP/'render-result.json'),'finalSHA256':rendered['sha256']},'referenceManifest':{'path':'reference-appendix.json','sha256':sha(EP/'reference-appendix.json'),'generatorAndSourcesCurrent':True}},'mix':mix,'measurementEvidence':{'script':str(Path(__file__).relative_to(ROOT)),'scriptSHA256':sha(Path(__file__)),'audioDecodeCommand':command,'endcardsDecodeCommand':scan_command,'decodedFinalVideoFramesOnly':scan_count,'outputDirectory':str(OUT.relative_to(EP))},'limits':['No ASR,full human listening or learner effect measurement.','Whole-video decodability and complete body/PCM preservation already executed by shared check/appender and pinned by hashes;no repeated full-video decode here.','Actual image viewing remains separate;this measured artifact is not a final QA pass until reviewed.']}
(OUT/'measurements.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'movieSHA256':movie_sha,'frames':final_frames,'AACPackets':len(aac),'audioLUFS':lufs,'truePeakDBTP':peak,'minSentenceCorrelation':report['audio']['minSentenceCorrelation'],'cards':results,'images':previews},ensure_ascii=False))
