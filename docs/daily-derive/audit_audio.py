"""Independent evidence collector; actual cut/onset/place algorithms stay shared."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,tempfile,wave
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];EP=ROOT/'episodes-codex/daily-temperatures';BEFORE=EP/'revisions/derive-before';OLDER=EP/'revisions/problem-fit-opening-before';PY=sys.executable
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED_VOICE='d8b4952e0802e952f6cb01a68eccd3b502bdc2e82d0e6ac790f77bd8993b6e80'
source_names=['script.md','voice.wav','remotion/public/audio/voice.wav','voice/sents.json','voice/picks.json','voice/build.json','voice/params.json','voice/place-derive.json','voice/cues.json','voice/cue_tests.json','voice/shot_frames.json','voice/script-narration-sha256.json','words.json','storyboard.json','plan.json','qa-timing.json','label-onset-derive.txt','episode-config.json','voice/derive-provenance.json','voice/derive-phase-alignment.json','prepare_code_endcard.py']
sources={n:sha(EP/n) for n in source_names};assert sources['voice.wav']==EXPECTED_VOICE==sources['remotion/public/audio/voice.wav']
shared_names=['episodes/_shared/voice/common.py','episodes/_shared/voice/build.py','episodes/_shared/voice/prep.py','episodes/_shared/onset_rule.py','episodes/_shared/label_onset_strict.py','episodes/_shared/place_v2.py','episodes-codex/_shared/check_sentence_episode.py','episodes-codex/_shared/assemble_sentence_episode.py']
shared={n:sha(ROOT/n) for n in shared_names}
sys.path.insert(0,str(ROOT/'episodes/_shared/voice'));import common
build=read(EP/'voice/build.json');sents=read(EP/'voice/sents.json');picks=read(EP/'voice/picks.json');provenance=read(EP/'voice/derive-provenance.json');params=read(EP/'voice/params.json');sb=read(EP/'storyboard.json');words=read(EP/'words.json')
assert len(build['sentences'])==len(sents)==len(provenance['rows'])==30
assert provenance['new']==4 and provenance['reused']==26 and provenance['scriptSHA256']==sources['script.md']
old_data={}
for folder in [BEFORE,OLDER]:
 qa=read(folder/'qa-audio-preflight.json');assert qa['status']=='passed'
 for n,h in qa['sharedImplementationSHA256'].items():assert shared[n]==h,(folder,n)
 old_data[str(folder.relative_to(EP))]={'build':read(folder/'voice/build.json'),'qa':qa,'manifest':read(folder/'source-sha256.json'),'folder':folder}
with tempfile.TemporaryDirectory(prefix='daily-derive-shared-prep-') as tmp:
 d=Path(tmp);(d/'voice').mkdir();shutil.copy2(EP/'script.md',d/'script.md');shutil.copy2(EP/'voice/params.json',d/'voice/params.json')
 prep=subprocess.run([PY,str(ROOT/'episodes/_shared/voice/prep.py'),'--dir',str(d)],capture_output=True,text=True,check=True)
 assert read(d/'voice/sents.json')==sents;prep_first_line=prep.stdout.splitlines()[0]
def pcm(path):
 with wave.open(str(path)) as w:
  info=(w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes());data=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
 return info,data
info,track=pcm(EP/'voice.wav');assert info==(48000,1,2,5158*1600)
new_by={s['id']:s for s in build['sentences']};sent_by={s['id']:s for s in sents};new_cut=[];reuse=[];details=[];file_checks=[];guard=dict(sources);groups={};waveforms=[]
for p in provenance['rows']:
 row=new_by[p['id']];assert row['text']==p['text']==sent_by[p['id']]['text'];assert row['tts']==p['tts']==sent_by[p['id']]['tts'];assert row['take']==picks[row['id']]=='derive'
 for f in p['files']:
  assert sha(EP/f['source'])==sha(EP/f['target'])==f['sha256'];guard[f['source']]=f['sha256'];guard[f['target']]=f['sha256'];file_checks.append(f)
 assert read(EP/f"voice/takes/{row['id']}-derive.txt.json")==row['tts']
 start,end=row['startSample'],row['endSample'];assert start<end
 sentence_info,sentence=pcm(EP/f"voice/sentences/{row['id']}.wav");assert sentence_info==(48000,1,2,end-start);assert np.array_equal(sentence,track[start:end])
 detail={'id':row['id'],'origin':p['status'],'text':row['text'],'tts':row['tts'],'selectedWAVsha256':sha(EP/f"voice/takes/{row['id']}-derive.wav"),'reportedTailCutSeconds':row['tailCut'],'keptSamples':end-start,'sentencePCMEqualsWholeTrackSlice':True}
 if p['status']=='new-approved':
  x=common.load(str(EP/f"voice/takes/{row['id']}-derive.wav"));y,tail=common.cut(x)
  nz=np.where(np.abs(y)>1e-4)[0];assert len(nz);y=y[:nz[-1]+1]
  assert len(y)==end-start and round(tail,2)==row['tailCut']
  detail.update(actualSharedCutTailSeconds=float(tail),actualSharedRetainedSamples=len(y),newCutReplayed=True,selectedInputSamples=len(x),sourceLast100msRMS=float(np.sqrt(np.mean(x[-4800:]**2))),cutLast20msPeak=float(np.abs(y[-960:]).max()),cutLastSample=float(y[-1]))
  new_cut.append(detail);waveforms.append((row['id'],x,y))
 else:
  assert p['status'] in ['reused-latest','reused-prior-pure-problem']
  key=next(k for k in old_data if p['files'][0]['source'].startswith(k+'/'))
  old=old_data[key];oldrow=next(s for s in old['build']['sentences'] if (s['text'],s['tts'])==(row['text'],row['tts']))
  assert oldrow['tailCut']==row['tailCut'] and oldrow['endSample']-oldrow['startSample']==end-start
  olddetail=next(x for x in old['qa']['cutAndPCM']['selectedTakeDetails'] if x['id']==oldrow['id'])
  oldhash=olddetail.get('selectedWAVsha256',olddetail.get('WAVsha256'));assert oldhash==detail['selectedWAVsha256']
  assert olddetail['keptSamples']==end-start
  for f in p['files']:assert old['manifest'][f['source'].removeprefix(key+'/')]==f['sha256']
  delta=start-oldrow['startSample'];assert delta==end-oldrow['endSample']
  visual_reuse=row['shot'].split('-',1)[1] not in ['problem','stack-basics','name'];
  if visual_reuse:assert delta%1600==0
  groups.setdefault(str(delta),[]).append(row['id'])
  detail.update(oldId=oldrow['id'],baseline=key,sampleDelta=delta,frameDelta=delta/1600,requiresPictureReuseIntegerPhase=visual_reuse,cutEvidence='Actual prior shared cut reused by exact text/TTS/raw/WAV/txt, retained length/tailCut and identical shared implementation; this run checks the new assembled PCM independently.')
  reuse.append(detail)
 details.append(detail)
assert len(new_cut)==4 and len(reuse)==26 and len(file_checks)==90
assert not np.any(track[:14400]);gaps=[]
for a,b in zip(build['sentences'],build['sentences'][1:]):
 gap=b['startSample']-a['endSample'];assert gap>=0 and not np.any(track[a['endSample']:b['startSample']])
 expected=16800 if a['shot']==b['shot'] else 33600+round(build['summary']['extraAfter'].get(a['shot'],0)*48000)
 assert gap==expected,(a['id'],b['id'],gap,expected)
 gaps.append({'from':a['id'],'to':b['id'],'samples':gap,'extraAfterSamples':0 if a['shot']==b['shot'] else round(build['summary']['extraAfter'].get(a['shot'],0)*48000),'allPCMZero':True})
assert not np.any(track[build['sentences'][-1]['endSample']:])
card=sb['meta']['unvoicedEndCard'];assert card['from']==5008 and card['durationInFrames']==150 and card['from']+150==5158;assert not np.any(track[card['from']*1600:]);assert max(x['endSample'] for x in build['sentences'])<card['from']*1600
assert build['summary']['sha']==sources['voice.wav'];assert build['summary']['samples']==len(track) and build['summary']['frames']==5158 and words['durationFrames']==5158 and words['audioSha256']==sources['voice.wav'] and words['scriptSha256']==sources['script.md']
old_plan=read(BEFORE/'plan.json');new_plan=read(EP/'plan.json');oldshots=[s for c in read(BEFORE/'storyboard.json')['scenes'] for s in c['shots']];shots=[s for c in sb['scenes'] for s in c['shots']];ob={p['slug']:s for p,s in zip(old_plan,oldshots)};local=[]
for p,s in zip(new_plan,shots):
 if p['slug'] in ['problem','stack-basics','name']:continue
 old=ob[p['slug']]
 for key in ['narration','subtitles','cueFrames','durationInFrames','codeCardFrom']:
  assert old.get(key)==s.get(key),(p['slug'],key)
 local.append({'slug':p['slug'],'oldId':old['id'],'newId':s['id'],'oldFrom':old['from'],'newFrom':s['from'],'durationInFrames':s['durationInFrames'],'allLocalNarrationSubtitlesCuesDurationAndCodeBoundaryExact':True})
assert len(local)==12
phase=read(EP/'voice/derive-phase-alignment.json');initial=read(EP/'revisions/derive-phase-initial/voice/build.json');assert phase['initialBuildSHA256']==sha(EP/'revisions/derive-phase-initial/voice/build.json');assert phase['baselineBuildSHA256']==sha(BEFORE/'voice/build.json');assert phase['extraAfterSamples']=={'01-problem':1232,'04-stack-basics':1118,'06-name':593}
assert {k:round(v*48000) for k,v in params['extraAfter'].items()}==phase['extraAfterSamples']
for a,b in zip(initial['sentences'],build['sentences']):assert (a['id'],a['text'],a['tts'],a['take'],a['endSample']-a['startSample'])==(b['id'],b['text'],b['tts'],b['take'],b['endSample']-b['startSample'])
independent_onset=Path('/tmp/daily-derive-independent-onset.txt');subprocess.run([PY,str(ROOT/'episodes/_shared/label_onset_strict.py'),'--dir',str(EP),'--out',str(independent_onset)],capture_output=True,text=True,check=True);onset=independent_onset.read_text();assert '3 cues, 0 fail, 0 approved exceptions' in onset;assert sha(independent_onset)==sources['label-onset-derive.txt']
independent_place=Path('/tmp/daily-derive-independent-place.json');subprocess.run([PY,str(ROOT/'episodes/_shared/place_v2.py'),'--dir',str(EP),'--mode','whole','--report',str(independent_place)],capture_output=True,text=True,check=True);place=read(independent_place);assert place['sha']==sources['voice.wav'] and place['maxOffsetFrames']==0 and not place['violations'];assert sha(independent_place)==sources['voice/place-derive.json']
measured=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(EP/'voice.wav'),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr
lufs=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',measured)[-1]);true_peak=float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',measured)[-1]);assert -16.2<=lufs<=-15.8 and true_peak<=-2.0
clipping=int(np.count_nonzero((track==32767)|(track==-32768)));assert clipping==0;assert build['summary']['inner_dropouts']==[] and build['summary']['max_neighbour_lufs_diff']<=1.0
# Actual signal plot, not a mock audio picture. Full source retains sentinel;
# the adjacent plot shows the returned shared-cut/kept signal.
plot=Path(__file__).parent/'audio-waveforms.png';im=Image.new('RGB',(1600,1000),'#101a2d');draw=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
for ri,(sid,x,y) in enumerate(waveforms):
 for ci,(label,arr) in enumerate([('selected WAV including sentinel',x),('shared cut / retained signal',y)]):
  left=55+ci*790;top=35+ri*240;w=710;h=145;draw.text((left,top),f'{sid}: {label}',font=font,fill='#d8e8ff');draw.text((left,top+24),f'{len(arr)/48000:.5f} s / {len(arr)} samples',font=font,fill='#a1b4cf');cy=top+115;draw.line((left,cy,left+w,cy),fill='#4c607c',width=1)
  for i in range(w):
   chunk=arr[int(i*len(arr)/w):max(int((i+1)*len(arr)/w),int(i*len(arr)/w)+1)]
   lo=float(chunk.min());hi=float(chunk.max());scale=63/max(.1,float(np.abs(arr).max()));draw.line((left+i,cy-hi*scale,left+i,cy-lo*scale),fill='#56d8c6',width=1)
im.save(plot)
for name,h in guard.items():assert sha(EP/name)==h,name
for name,h in shared.items():assert sha(ROOT/name)==h,name
labels=[e['cueText'] for s in shots for e in s['elements'] if e.get('cueText')];assert len(labels)==3
report={'status':'passed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'checkedBy':'derivation_audit','scope':'Independent source-voice preflight for analysis-before-monotonic-stack revision. Four fresh selected takes replayed through shared cut;26 actual prior cuts reused by complete source and shared implementation identities. All30 new assembled sentence PCM slices and29 gaps checked. Final encoded media and visual QA are separate.','blockingIssues':[],
 'voice':{'sha256':sources['voice.wav'],'publicCopyExact':True,'sampleRate':48000,'channels':1,'sampleWidthBytes':2,'samples':len(track),'frames':5158,'seconds':5158/30},
 'textAndTakes':{'sharedPrepScratchReplay':True,'prepFirstLine':prep_first_line,'sentences':30,'shots':15,'reusedSentences':26,'newSentences':4,'exactSourceTargetFiles':90,'reusedRawWAVTextFiles':78,'newRawWAVTextFiles':12,'sourceTargetFiles':file_checks},
 'sourceReuse':{'baselineAudioQAs':[{'file':str((v['folder']/'qa-audio-preflight.json').relative_to(EP)),'sha256':sha(v['folder']/'qa-audio-preflight.json'),'buildSHA256':sha(v['folder']/'voice/build.json'),'sourceManifestSHA256':sha(v['folder']/'source-sha256.json')} for v in old_data.values()],'oldSharedImplementationsExact':len(shared),'actualPriorCutRowsReused':26,'selectedDetails':reuse},
 'cutAndPCM':{'sharedImplementation':'episodes/_shared/voice/common.py load/cut plus build.py retained-nonzero endpoint','selectedTakesActuallyReplayedNow':4,'selectedPriorCutsReusedByIdentity':26,'allTailCutsAndRetainedSampleCountsMatchBuild':True,'sentencePCMEqualsCurrentWholeTrackSlices':30,'leadingGapSamples':14400,'interSentenceGapsChecked':len(gaps),'gaps':gaps,'allGapsAndTrailingPaddingZeroPCM':True,'trailingSilentSamples':len(track)-build['sentences'][-1]['endSample'],'newCutDetails':new_cut,'selectedTakeDetails':details,'actualWaveformPlot':str(plot.relative_to(ROOT)),'actualWaveformPlotSHA256':sha(plot),'waveformVisualReview':'Pending separate actual-image inspection; not implied by numeric pass.'},
 'wholePlacement':{'report':'voice/place-derive.json','independentOutputSHA256':sha(independent_place),**place},
 'onset':{'report':'label-onset-derive.txt','independentOutputSHA256':sha(independent_onset),'cuePrefixes':labels,'totalCues':3,'failed':0,'approvedExceptions':0,'text':onset,'scope':'Complete sentence-prefix acoustic cues; no word-internal ASR alignment.'},
 'loudness':{'method':'Actual ffmpeg ebur128=peak=true on final source voice','integratedLUFS':lufs,'truePeakDbTP':true_peak,'clippedFullScalePCMSamples':clipping,'actualPeakInt16':int(np.abs(track.astype(np.int32)).max())},'buildQualitySummary':build['summary'],
 'codeCard':{'from':5008,'toInclusive':5157,'frames':150,'seconds':5,'silentSourceVoiceSamples':240000,'allZeroPCM':True,'lastNarrativeCaptionGlobalTo':shots[-1]['from']+shots[-1]['subtitles'][-1]['to'],'lastSpeechEndFrame':build['sentences'][-1]['endSample']/1600,'scope':'Zero PCM is source voice only. Mixed AAC may contain BGM; reference appendix is separately appended.'},
 'localTimingPreservation':{'sampleDeltaGroups':groups,'unchangedOldShots':local,'allOldLocalTimesExact':True,'allowTailFrameAdjustment':False},
 'phaseHistory':{'report':'voice/derive-phase-alignment.json','sha256':sources['voice/derive-phase-alignment.json'],'initialBuildSHA256':phase['initialBuildSHA256'],'extraAfterSamples':phase['extraAfterSamples'],'actualSpecialGaps':[g for g in gaps if g['extraAfterSamples']],'all30TakesAndRetainedDurationsUnchangedBetweenInitialAndAlignedBuild':True,'interpretation':'Only nonnegative1232/1118/593 zero-sample additions after fresh shots. No speech trimming or rate change.'},
 'sentenceTiming':read(EP/'qa-timing.json'),'freeze':{'status':'not-yet-bound','scope':'Audio identities are guarded before/after this actual audit. Root must later bind the production freeze while these identities stay unchanged.'},
 'sourceSHA256':sources,'sharedImplementationSHA256':shared,'measurementEvidence':{'script':str(Path(__file__).relative_to(ROOT)),'scriptSHA256':sha(Path(__file__)),'sharedPrepOutputComparedInTemporaryDirectory':True,'independentOnsetAndWholePlaceReplayed':True},
 'limits':['No word-level ASR, full human listening or learner outcome performed or claimed.','26 prior actual cut proofs reused by exact source and shared implementation identities; not26 freshly rerun cuts.','New global normalization may change full-track PCM; no old/new whole-track PCM identity claimed.','Waveform inspection is a signal/retention check, not Mandarin listening or transcript verification.','Final encoded-media, cover and algorithm checks are separate; this report does not claim them.']}
(EP/'qa-audio-preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=f'''# 独立音频预检：先推导再引出单调栈\n\n结论：PASS，无阻塞。绑定voice SHA256 `{sources['voice.wav']}`；48kHz单声道16位、{len(track):,}样本、5158帧/{5158/30:.6f}秒；public副本完全一致。\n\n- 隔离目录实际重放共享prep，30句完全匹配；26旧句78份raw/WAV/txt完整身份、旧cut长度与尾切、8共享实现保持，复用旧实际cut证据。4新句12来源文件全同，4次实际共享load/cut的尾切与保留样本数吻合build。\n- 30句sentence WAV与整轨PCM切片全等；起始14400样本、29处间隙、尾部{len(track)-build['sentences'][-1]['endSample']}样本全零。01/04/06之后仅增加1232/1118/593零样本，未裁语音或变速。12旧镜局部字幕、cue、持续帧及closing代码卡边界精确保持，无±1帧放宽。\n- 独立重放共享wholeplace为0偏移、无violations；三个完整句首prefix的声学起音均通过，独立输出SHA等于制作报告。\n- 实测整轨{lufs:.1f} LUFS/{true_peak:.1f} dBTP、0满幅削波，无内部dropout；Python5008..5157完整5秒，240000个源voice样本全零，字幕到5007。资料另追加150帧，不延长voice正文。\n- 四新句的真实源波形与共享cut保留波形图见[audio-waveforms.png](../../docs/daily-derive/audio-waveforms.png)；生成本身不代表已实际查看，独立目视结果另行补充。\n\n本报告先锁定音频身份，生产冻结待root在输入稳定后绑定。没有逐字ASR、全片人工听辨或学习效果测量；不将旧QA冒称新执行，也不要求混音后的BGM/AAC全静音。\n'''
(EP/'qa-audio-preflight.md').write_text(md)
print(json.dumps({'status':'passed','voiceSHA256':sources['voice.wav'],'newSharedCuts':4,'priorCutsReused':26,'exactSentencePCMSlices':30,'integratedLUFS':lufs,'truePeakDbTP':true_peak,'qaJSONSHA256':sha(EP/'qa-audio-preflight.json'),'waveform':str(plot)},ensure_ascii=False))
