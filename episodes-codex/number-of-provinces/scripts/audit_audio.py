"""Read-only audio preflight; reuse the sole shared cut/onset/place implementations."""
from pathlib import Path
import datetime, hashlib, json, re, shutil, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
EP=Path(__file__).resolve().parents[1];ROOT=EP.parents[1]
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pcm(path):
    with wave.open(str(path)) as wav:
        info=(wav.getframerate(),wav.getnchannels(),wav.getsampwidth(),wav.getnframes())
        data=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').copy()
    return info,data
sys.path.insert(0,str(ROOT/'episodes/_shared/voice'));import common
source_files=['script.md','voice.wav','remotion/public/audio/voice.wav','voice/sents.json','voice/picks.json','voice/build.json','voice/params.json','voice/substitutions.md','voice/place.json','voice/cues.json','voice/cue_tests.json','voice/shot_frames.json','voice/script-narration-sha256.json','words.json','storyboard.json','plan.json','qa-timing.json','label-onset-strict.txt','episode-config.json','prepare_code_endcard.py']
sources={name:sha(EP/name) for name in source_files}
shared_files=['episodes/_shared/voice/common.py','episodes/_shared/voice/prep.py','episodes/_shared/voice/gen.py','episodes/_shared/voice/build.py','episodes/_shared/onset_rule.py','episodes/_shared/label_onset_strict.py','episodes/_shared/place_v2.py','episodes-codex/_shared/assemble_sentence_episode.py','episodes-codex/_shared/check_sentence_episode.py']
shared={name:sha(ROOT/name) for name in shared_files}
assert sources['voice.wav']==sources['remotion/public/audio/voice.wav']=='253a3250c0ce97682488deed6ed08790ab0bc46748102409b37f199a7aea5dff'
build=read(EP/'voice/build.json');sents=read(EP/'voice/sents.json');picks=read(EP/'voice/picks.json');sb=read(EP/'storyboard.json');words=read(EP/'words.json')
rows=build['sentences'];frames=sb['meta']['durationInFrames'];assert len(rows)==len(sents)==24
shots=[shot for scene in sb['scenes'] for shot in scene['shots']];assert len(shots)==12
info,track=pcm(EP/'voice.wav');assert info==(48000,1,2,frames*1600)
assert build['summary']['sha']==sources['voice.wav'] and words['audioSha256']==sources['voice.wav'] and words['scriptSha256']==sources['script.md']
assert build['summary']['samples']==len(track) and build['summary']['frames']==words['durationFrames']==frames
cut_rows=[];waveforms=[];selected=[];guard=dict(sources)
with tempfile.TemporaryDirectory(prefix='province-audio-independent-') as temporary:
    tmp=Path(temporary);(tmp/'voice').mkdir();shutil.copy2(EP/'script.md',tmp/'script.md');shutil.copy2(EP/'voice/params.json',tmp/'voice/params.json')
    prep=subprocess.run([sys.executable,str(ROOT/'episodes/_shared/voice/prep.py'),'--dir',str(tmp)],capture_output=True,text=True,check=True)
    assert read(tmp/'voice/sents.json')==sents
    for index,(row,sent) in enumerate(zip(rows,sents)):
        assert row['id']==sent['id'] and row['text']==sent['text'] and row['tts']==sent['tts']
        assert row['take']==picks[row['id']]
        stem=EP/'voice/takes'/f"{row['id']}-{row['take']}"
        wav,raw,txt=[Path(str(stem)+suffix) for suffix in ['.wav','.raw.wav','.txt.json']]
        assert read(txt)==row['tts']
        files={str(path.relative_to(EP)):sha(path) for path in [wav,raw,txt]};guard.update(files);selected.append({'id':row['id'],'files':files})
        # Same actual raw-to-WAV conversion as shared gen.py, independently replayed.
        converted=tmp/f'{index}.wav'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-ar','48000','-ac','1',str(converted)],check=True)
        converted_info,converted_pcm=pcm(converted);take_info,take_pcm=pcm(wav)
        assert converted_info==take_info and np.array_equal(converted_pcm,take_pcm)
        x=common.load(str(wav));cut,tail=common.cut(x);nz=np.where(np.abs(cut)>1e-4)[0];assert len(nz);cut=cut[:nz[-1]+1]
        start,end=row['startSample'],row['endSample'];assert len(cut)==end-start and round(tail,2)==row['tailCut']
        sentence_info,sentence=pcm(EP/f"voice/sentences/{row['id']}.wav")
        assert sentence_info==(48000,1,2,end-start) and np.array_equal(sentence,track[start:end])
        left=cut.astype(np.float64);right=sentence.astype(np.float64);left-=left.mean();right-=right.mean()
        correlation=float(np.dot(left,right)/(np.linalg.norm(left)*np.linalg.norm(right)));assert correlation>.99,(row['id'],correlation)
        cut_rows.append({'id':row['id'],'text':row['text'],'selectedWAVsha256':sha(wav),'rawToWAVPCMExact':True,'actualSharedCutTailSeconds':float(tail),'reportedTailCutSeconds':row['tailCut'],'keptSamples':len(cut),'sourceSamples':len(x),'sentencePCMEqualsWholeTrackSlice':True,'sourceCutVsNormalizedSentenceCorrelation':correlation})
        if index in [0,6,12,23]:waveforms.append((row['id'],x,cut))
    onset_file=tmp/'onset.txt'
    subprocess.run([sys.executable,str(ROOT/'episodes/_shared/label_onset_strict.py'),'--dir',str(EP),'--out',str(onset_file)],capture_output=True,text=True,check=True)
    onset_text=onset_file.read_text();assert '3 cues, 0 fail, 0 approved exceptions' in onset_text
    assert sha(onset_file)==sources['label-onset-strict.txt']
    placement=tmp/'place.json'
    subprocess.run([sys.executable,str(ROOT/'episodes/_shared/place_v2.py'),'--dir',str(EP),'--mode','whole','--no-copy','--report',str(placement)],capture_output=True,text=True,check=True)
    place=read(placement);assert place['sha']==sources['voice.wav'] and not place['violations'] and place['maxOffsetFrames']==0
    assert sha(placement)==sources['voice/place.json']
assert not np.any(track[:rows[0]['startSample']]);gaps=[]
for a,b in zip(rows,rows[1:]):
    gap=b['startSample']-a['endSample'];assert gap>=0 and not np.any(track[a['endSample']:b['startSample']])
    expected=16800 if a['shot']==b['shot'] else 33600+round(build['summary']['extraAfter'].get(a['shot'],0)*48000)
    assert gap==expected,(a['id'],b['id'],gap,expected)
    gaps.append({'from':a['id'],'to':b['id'],'samples':gap,'allZeroPCM':True})
assert len(gaps)==23 and not np.any(track[rows[-1]['endSample']:])
card=sb['meta']['unvoicedEndCard'];assert card['durationInFrames']==150 and card['from']+150==frames
assert not np.any(track[card['from']*1600:]) and rows[-1]['endSample']<card['from']*1600
assert shots[-1]['from']+shots[-1]['codeCardFrom']==card['from']
assert max(shot['from']+sub['to'] for shot in shots for sub in shot['subtitles'])==card['from']-1
stderr=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(EP/'voice.wav'),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr
lufs=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',stderr)[-1]);peak=float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',stderr)[-1]);assert abs(lufs+16)<=.2 and peak<=-2
assert not np.any((track==32767)|(track==-32768)) and build['summary']['inner_dropouts']==[]
# Actual selected signals and actual shared retained signals, not mock diagrams.
out=ROOT/'docs/archive/2026-10/number-of-provinces';out.mkdir(parents=True,exist_ok=True)
image=Image.new('RGB',(1600,1000),'#101a2d');draw=ImageDraw.Draw(image);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for row_index,(sid,x,y) in enumerate(waveforms):
    for column,(name,array) in enumerate([('selected take incl. discard tail',x),('actual shared retained cut',y)]):
        left=50+column*790;top=30+row_index*245;middle=top+123;width=720
        draw.text((left,top),f'{sid}: {name}',font=font,fill='#d8e8ff');draw.text((left,top+25),f'{len(array)/48000:.5f} s; {len(array)} samples',font=font,fill='#97aec9')
        draw.line((left,middle,left+width,middle),fill='#45607d');scale=65/max(.1,float(np.abs(array).max()))
        for i in range(width):
            chunk=array[int(i*len(array)/width):max(int((i+1)*len(array)/width),int(i*len(array)/width)+1)]
            draw.line((left+i,middle-float(chunk.max())*scale,left+i,middle-float(chunk.min())*scale),fill='#5dd6c0')
plot=out/'audio-waveforms.png';image.save(plot)
for name,digest in guard.items():assert sha(EP/name)==digest,name
for name,digest in shared.items():assert sha(ROOT/name)==digest,name
report={'status':'passed-numeric-awaiting-waveform-view','checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checkedBy':'independent /root/next_lc_research;not involved in voice generation/assembly','voice':{'sha256':sources['voice.wav'],'sampleRate':48000,'channels':1,'sampleWidthBytes':2,'samples':len(track),'frames':frames,'seconds':frames/30,'publicCopyExact':True},'sentences':len(rows),'shots':len(shots),'selectedTakeFiles':selected,'cutAndPCM':{'actuallyReplayedSharedCuts':24,'allRawToSelectedWAVPCMExact':True,'selectedTakeDetails':cut_rows,'wholeTrackSentenceSlicesExact':24,'leadingSilentSamples':rows[0]['startSample'],'gapsChecked':len(gaps),'gaps':gaps,'trailingSilentSamples':len(track)-rows[-1]['endSample'],'allGapsAndTailZero':True,'actualWaveformPlot':str(plot.relative_to(ROOT)),'actualWaveformPlotSHA256':sha(plot),'waveformVisualReview':'pending separate actual-image viewing'},'loudness':{'actualIntegratedLUFS':lufs,'actualTruePeakDBTP':peak,'clippedFullScaleSamples':0,'ebur128Summary':stderr[stderr.rfind('Summary:'):],'source':'actual ffmpeg ebur128=peak=true'},'codeCard':{'from':card['from'],'toInclusive':frames-1,'frames':150,'silentSourceSamples':240000,'allZeroPCM':True,'lastCaptionGlobalTo':card['from']-1},'onset':{'independentSharedReplayExact':True,'text':onset_text,'cueCount':3,'failed':0,'scope':'Complete sentence-prefix acoustic anchors,not interior word ASR.'},'wholePlacement':{'independentSharedNoCopyReplayExact':True,**place},'sharedPrepScratchReplayExact':True,'sourceSHA256':sources,'sharedImplementationSHA256':shared,'buildSummary':build['summary'],'freeze':{'status':'audio identities guarded before/after;full-production freeze bound by root later'},'measurementEvidence':{'script':str(Path(__file__).relative_to(ROOT)),'scriptSHA256':sha(Path(__file__))},'limitations':['No ASR,full human listening or learner effect measurement.','Waveform inspection is a signal-retention/shape check,not Mandarin listening or word validation.','All24 selected cuts were actually replayed now;no historical audioQA borrowed.','Source voice zeroPCM during Python card does not require mixed BGM/AAC to be silent.','Formal encoded media and browser review are subsequent checks.']}
(EP/'qa-audio-preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(EP/'qa-audio-preflight.md').write_text(f'''# 独立音频预检\n\n数值检查通过，实际波形图查看待单独补证。声轨SHA256 `{sources['voice.wav']}`，48kHz单声道16位，{frames}帧/{frames/30:.6f}秒，public副本完全一致。24个新选中take的raw→WAV PCM实际重放全同；24次唯一共享load/cut的保留样本数及discard尾切与build一致，24句切片与整轨PCM逐样本全等。\n\n起始、23处间隔与尾部全零；Python{card['from']}..{frames-1}正好150帧/5秒，240000个源voice样本全零、字幕到{card['from']-1}。独立共享句首起音3/0通过，wholeplace无拷贝复核0偏移/无violations，与制作报告全文SHA相同。实际{lufs:.1f}LUFS/{peak:.1f}dBTP，无削波与内部dropout。\n\n实际信号图见`docs/archive/2026-10/number-of-provinces/audio-waveforms.png`，生成本身不等于实际查看。没有逐字ASR、全片人工听辨或学习效果声明；正式编码与网站另验。\n''')
print(json.dumps({'status':report['status'],'voiceSHA256':sources['voice.wav'],'replayedNewCuts':24,'exactSentencePCMSlices':24,'integratedLUFS':lufs,'truePeakDBTP':peak,'minCutCorrelation':min(r['sourceCutVsNormalizedSentenceCorrelation'] for r in cut_rows),'waveform':str(plot),'qaSHA256':sha(EP/'qa-audio-preflight.json')},ensure_ascii=False))
