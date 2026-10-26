from pathlib import Path
import datetime,hashlib,importlib.util,json,re,subprocess,wave
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];EP=ROOT/'episodes-codex/daily-temperatures';MOVIE=EP/'video.mp4';OUT=EP/('remotion/out/qa-independent-derive-'+hashlib.sha256(MOVIE.read_bytes()).hexdigest()[:12]);OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
movie_sha=sha(MOVIE)
manifest_path=EP/'source-sha256.json';freeze_sha=sha(manifest_path);manifest=read(manifest_path);assert len(manifest)>=200
for n,h in manifest.items():assert sha(EP/n)==h,n
qa=read(EP/'qa-audio-preflight.json');assert qa['status']=='passed';qa_sha=sha(EP/'qa-audio-preflight.json')
for n,h in qa['sourceSHA256'].items():assert sha(EP/n)==h,n
for n,h in qa['sharedImplementationSHA256'].items():assert sha(ROOT/n)==h,n
rr=read(EP/'render-result.json');br=read(EP/'body-render-result.json');app=read(EP/'reference-appendix.json');apc=read(EP/'reference-appendix-media-check.json');mix=read(EP/'mix-report.json');refs=read(EP/'references.json')
body=EP/'remotion/out/body.mp4';assert sha(body)==br['sha256']==app['inputs']['bodySHA256']==apc['bodySHA256'];assert rr['sha256']==app['outputSHA256']==apc['outputSHA256']==movie_sha
assert rr['frames']==app['finalVideoFrames']==apc['finalFrames']==5308 and br['frames']==app['bodyFrames']==apc['bodyFrames']==5158 and apc['appendedFrames']==150 and apc['passed']
for key in ['bodyDecodedFramesAndTimestampsEqual','outputVideoTimelineContinuous','audioPacketsAndTimingEqual']:assert apc[key]
assert app['inputs']['referencesSHA256']==sha(EP/'references.json');assert app['presentation']=='title-author' and app['layout']['renderedFields']==['title','credit'] and not app['layout']['quotesRendered']
assert app['bibliography']==[{'id':s['id'],'title':s['title'],'credit':s.get('author') or s['organization']} for s in refs['sources']]
assert app['inputs']['generatorSHA256']==sha(ROOT/'episodes-codex/_shared/append_references_bibliography.py')
for key,p in [('themeSHA256',ROOT/'episodes/_shared/theme/pageTheme.ts'),('fontSHA256',Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')),('boldFontSHA256',Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'))]:assert app['inputs'][key]==sha(p)
for page in app['appendix']['pages']:assert page['sha256']==sha(EP/'revisions/reference-endcards'/page['file'])
for key,path in [('oldEngineSHA256','episodes-codex/_shared/append_references.py'),('originalRendererSHA256','episodes-codex/_shared/append_references_original.py')]:assert app['dependencies'][key]==sha(ROOT/path)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(MOVIE)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');assert int(v['nb_frames'])==5308 and v['r_frame_rate']=='30/1' and (v['width'],v['height'])==(1920,1080);assert a['codec_name']=='aac' and int(a['sample_rate'])==48000
vp=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts,duration','-of','json',str(MOVIE)]))['packets'];assert len(vp)==5308
assert sorted(int(p['pts']) for p in vp)==[n*1000 for n in range(5308)];assert [int(p['dts']) for p in vp]==[(n-2)*1000 for n in range(5308)];assert all(int(p['duration'])==1000 for p in vp)
spec=importlib.util.spec_from_file_location('retained_append_media',ROOT/'episodes-codex/_shared/append_references.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
ap=shared.audio_packets(MOVIE);assert len(ap)==apc['audioPacketCount'];assert shared.sequence_hash(ap)==apc['audioPacketPayloadAndTimingSHA256']
assert all(p['pts']==p['dts'] for p in ap);assert all(int(b['pts'])==int(a0['pts'])+int(a0['duration']) for a0,b in zip(ap,ap[1:]));end_samples=int(ap[-1]['pts'])+int(ap[-1]['duration']);assert abs(end_samples/48000-float(a['duration']))<1e-9
# One audio-only decode supplies both actual mix loudness and source-window diagnostics.
decoded=OUT/'decoded-mix.f32';stderr_file=OUT/'audio-ebur128.log';command=['ffmpeg','-hide_banner','-nostats','-y','-i',str(MOVIE),'-map','0:a:0','-ar','48000','-ac','1','-af','ebur128=peak=true','-f','f32le',str(decoded)]
r=subprocess.run(command,capture_output=True,text=True,check=True);stderr_file.write_text(r.stderr);Y=np.fromfile(decoded,dtype='<f4').astype(np.float64)
with wave.open(str(EP/'voice.wav')) as w:assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(48000,1,2);X=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64)/32767
assert sha(EP/'voice.wav')==qa['voice']['sha256']=='d8b4952e0802e952f6cb01a68eccd3b502bdc2e82d0e6ac790f77bd8993b6e80'
lufs=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r.stderr)[-1]);tp=float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',r.stderr)[-1]);assert abs(lufs+16)<=.3 and tp<=-2

def correlation(x,y):
 assert len(x)==len(y) and len(x)>100
 xx=x-x.mean();yy=y-y.mean();return float(np.dot(xx,yy)/(np.linalg.norm(xx)*np.linalg.norm(yy)))
lag_scores=[]
for lag in [-1600,-480,-160,-96,0,96,160,480,1600]:
 start=max(0,-lag);stop=min(len(X),len(Y)-lag);lag_scores.append({'lagSamples':lag,'correlation':correlation(X[start:stop],Y[start+lag:stop+lag])})
best=max(lag_scores,key=lambda x:x['correlation']);lag=best['lagSamples'];assert best['correlation']>.9
build=read(EP/'voice/build.json');sentences=[]
for row in build['sentences']:
 st,en=row['startSample'],row['endSample'];c=correlation(X[st:en],Y[st+lag:en+lag]);assert c>.9,(row['id'],c);sentences.append({'id':row['id'],'correlation':c,'startSample':st,'endSample':en})
assert len(sentences)==30
cardmix=Y[5008*1600:5158*1600];rms=float(np.sqrt(np.mean(cardmix**2)))
# Decode only the last301 frames: last narrated frame, Python150, references150.
start=5007;seek=5007/30-.0005;scan_log=OUT/'endcards-showinfo.log';scan_command=['ffmpeg','-hide_banner','-nostats','-ss',str(seek),'-i',str(MOVIE),'-map','0:v:0','-an','-vf','showinfo','-frames:v','301','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
results={};indices=[5007,5008,5083,5157,5158,5233,5307];framesize=1920*1080*3
with scan_log.open('wb') as log:
 proc=subprocess.Popen(scan_command,stdout=subprocess.PIPE,stderr=log)
 assert proc.stdout
 for i in range(301):
  buf=proc.stdout.read(framesize)
  while len(buf)<framesize:
   piece=proc.stdout.read(framesize-len(buf))
   if not piece:break
   buf+=piece
  assert len(buf)==framesize,(i,len(buf));fr=start+i;image=np.frombuffer(buf,dtype=np.uint8).reshape(1080,1920,3)
  if fr in indices:Image.fromarray(image).save(OUT/f'frame-{fr:04d}.png')
  if fr==5007:continue
  key='python' if fr<5158 else 'references'
  if key not in results:results[key]={'fromFrame':fr,'toInclusive':fr,'scanned':0,'uniqueRGBHashes':set(),'maxFullFrameMAE255':0.0,'hashes':[],'first':image.copy()}
  q=results[key];q['toInclusive']=fr;q['scanned']+=1;digest=hashlib.sha256(buf).hexdigest();q['uniqueRGBHashes'].add(digest);q['hashes'].append(digest)
  mae=float(np.abs(image.astype(np.int16)-q['first'].astype(np.int16)).mean());q['maxFullFrameMAE255']=max(q['maxFullFrameMAE255'],mae)
  if key=='python':
   roi=image[758:818,120:1800];base=q['first'][758:818,120:1800];ink=int(np.count_nonzero(np.all(roi>135,axis=2)));q.setdefault('returnInk',[]).append(ink);q['maxReturnMAE255']=max(q.get('maxReturnMAE255',0.0),float(np.abs(roi.astype(np.int16)-base.astype(np.int16)).mean()))
 assert proc.stdout.read(1)==b''
 assert proc.wait()==0
showinfo=scan_log.read_text();times=[float(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([-\d.]+)',showinfo)];assert len(times)>=301,len(times);assert round((seek+times[0])*30)==5007 and round((seek+times[300])*30)==5307,(times[0],times[300])
for key,q in results.items():
 assert q['scanned']==150 and q['maxFullFrameMAE255']<.5
 q['uniqueRGBHashes']=len(q['uniqueRGBHashes']);q['frameHashSequenceSHA256']=hashlib.sha256(json.dumps(q.pop('hashes')).encode()).hexdigest();q.pop('first')
 if key=='python':
  values=q.pop('returnInk');q['returnROI']=[120,758,1800,818];q['returnInkMinMax']=[min(values),max(values)];assert min(values)>1000 and max(values)-min(values)<20
images=[{'frame':fr,'file':str((OUT/f'frame-{fr:04d}.png').relative_to(EP)),'sha256':sha(OUT/f'frame-{fr:04d}.png')} for fr in indices]
for n,h in manifest.items():assert sha(EP/n)==h,n
assert sha(manifest_path)==freeze_sha and sha(MOVIE)==movie_sha and sha(EP/'qa-audio-preflight.json')==qa_sha
m={'status':'measured-awaiting-actual-image-review','checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'movie':{'path':'video.mp4','sha256':movie_sha,'bytes':MOVIE.stat().st_size,'frames':5308,'fps':30,'width':1920,'height':1080,'containerSeconds':float(probe['format']['duration'])},'body':{'path':'remotion/out/body.mp4','sha256':sha(body),'bytes':body.stat().st_size,'frames':5158,'containerSeconds':br['seconds']},'freeze':{'sha256':freeze_sha,'checked':len(manifest),'allMatchBeforeAndAfter':True},'audioPreflight':{'path':'qa-audio-preflight.json','sha256':qa_sha,'allSourceAndSharedIdentitiesStillMatch':True,'publicationInputExtension':qa.get('publicationInputExtension')},'timeline':{'videoPackets':len(vp),'allVideoPacketPTSUniqueContinuous30fps':True,'allVideoPacketDTSContinuous30fps':True,'videoDTSFrom':int(vp[0]['dts'])/30000,'videoDTSTo':int(vp[-1]['dts'])/30000,'lastVideoPTS':(5308-1)/30,'AACPackets':len(ap),'allAACPTSDTSEqualAndContinuous':True,'firstAACPtsSamples':int(ap[0]['pts']),'packetEndSeconds':end_samples/48000,'aacPacketHashMatchesAppenderReceipt':True,'method':'Actual ffprobe stream/packet reads; no repeated full-video decode. Shared receipt supplies already-executed full decoded PTS/framemd5 preservation.'},'audio':{'actualIntegratedLUFS':lufs,'actualTruePeakDBTP':tp,'EBUSummary':r.stderr[r.stderr.rfind('Summary:'):],'stderrSHA256':sha(stderr_file),'decodedScalarSamples':len(Y),'monoDownmixForConsistency':True,'sourceComparisonLagScores':lag_scores,'bestLagSamples':lag,'bestLagFrames':lag/1600,'bestGlobalCorrelation':best['correlation'],'perSentenceAtBestLag':sentences,'minSentenceCorrelation':min(x['correlation'] for x in sentences),'diagnosticCompatible':True,'sourceVoiceSHA256':sha(EP/'voice.wav'),'cardMixedRMS':rms,'cardMixedRMSdBFS':float(20*np.log10(rms)),'method':'Pearson comparison of the actual mixed AAC with current source voice at its30 known sentence windows; not ASR, source separation or an onset algorithm. Mixed AAC is not source-WAV byte equality.'},'card':results['python'],'referencesCard':{**results['references'],'sourceIds':app['appendix']['sourceIds'],'presentation':app['presentation'],'bibliography':app['bibliography'],'layout':app['layout']},'referenceAudioEndpoint':{'referenceStartsSeconds':5158/30,'packetEndSeconds':end_samples/48000,'AACPacketTailPastReferenceBoundarySeconds':end_samples/48000-5158/30,'remainingReferenceVideoWithoutAudioSeconds':5308/30-end_samples/48000,'noNewAACPackets':True,'packetAndPCMIdentityEvidence':'Shared same-body/final reference-appendix-media-check.json verified packet payload/PTS/DTS and decoded PCM. Actual current packet sequence matched independently.'},'previews':images,'sharedPreservationEvidence':{'bodyFullDecode':{'path':'body-render-result.json','sha256':sha(EP/'body-render-result.json'),'bodySHA256':br['sha256'],'checks':br['checks']},'finalAppendixFullDecodeAndPreservation':{'path':'reference-appendix-media-check.json','sha256':sha(EP/'reference-appendix-media-check.json'),**apc},'defaultRendererResult':{'path':'render-result.json','sha256':sha(EP/'render-result.json'),'finalSHA256':rr['sha256']},'referenceManifest':{'path':'reference-appendix.json','sha256':sha(EP/'reference-appendix.json'),'generatorAndDependenciesCurrent':True,'sourceAndBibliographyCurrent':True}},'mix':mix,'measurementEvidence':{'script':str(Path(__file__).relative_to(ROOT)),'scriptSHA256':sha(Path(__file__)),'audioDecodeCommand':command,'endcardsDecodeCommand':scan_command,'last301DecodedFramesOnly':True,'firstDecodedGlobalFrameByShowinfo':round((seek+times[0])*30),'lastDecodedGlobalFrameByShowinfo':round((seek+times[300])*30),'outputDirectory':str(OUT.relative_to(EP))},'limits':['Actual final media packets, one audio-only decode and last301 video frames inspected. Full-video decodability and complete body/PCM preservation were already executed by the shared body checker/appender and bound by actual hashes; no redundant whole-video decode here.','No ASR, full human listening or learner outcome measurement. Source meanings/source titles and actual browser pause/fullscreen remain separate reviews.','Actual image review pending; this measured artifact is not yet a final QA pass.']}
(OUT/'measurements.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':m['status'],'movieSHA256':movie_sha,'frames':5308,'AACPackets':len(ap),'audioLUFS':lufs,'truePeakDBTP':tp,'bestLagSamples':lag,'minSentenceCorrelation':m['audio']['minSentenceCorrelation'],'cards':results,'images':images},ensure_ascii=False))
