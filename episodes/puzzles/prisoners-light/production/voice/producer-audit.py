#!/usr/bin/env python3
"""Read-only P10 source-cut and assembled-track signal audit using shared helpers."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,re,sys,wave
import numpy as np
from scipy.signal import resample_poly
D=Path(__file__).resolve().parents[1]
R=next(p for p in D.parents if (p/'AGENTS.md').is_file())
sys.path.insert(0,str(R/'episodes/_shared/voice'))
import common
sys.path.insert(0,str(R/'episodes/_shared'))
from onset_rule import Rule

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text())
def pcm(p):
 with wave.open(str(p),'rb')as w:
  info={'rate':w.getframerate(),'channels':w.getnchannels(),'width':w.getsampwidth(),'samples':w.getnframes()}
  assert info['rate']==48000 and info['channels']==1 and info['width']==2
  return np.frombuffer(w.readframes(w.getnframes()),'<i2').copy(),info

def max_quiet(y):
 bins=np.abs(y[:len(y)//480*480]).reshape(-1,480).max(1)>0.005
 run=maximum=0
 for active in bins:
  run=0 if active else run+1;maximum=max(maximum,run)
 return maximum/100

ap=argparse.ArgumentParser(__doc__);ap.add_argument('--stage',choices=['candidates','final'],required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
out=D/'voice'/a.out;assert not out.exists(),'Use a new output name; preserve earlier audit bytes.'
sents=read('voice/sents.json');picks=read('voice/picks.json')if(D/'voice/picks.json').exists()else{}
assert len(sents)==28
script=(D/'script.md').read_text();sections=re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)',script,re.S)
assert len(sections)==14
narration=[]
for n,slug,body in sections:
 text=re.search(r'^旁白：(.*)$',body,re.M)[1]
 narration.extend(re.findall(r'[^。！？]+[。！？]',text))
assert narration==[s['text']for s in sents]
rows=[];flags=[]
for s in sents:
 take=picks.get(s['id'],'a');stem=D/'voice/takes'/f'{s["id"]}-{take}'
 wav=stem.with_suffix('.wav');raw=stem.with_suffix('.raw.wav');txt=stem.with_suffix('.txt.json')
 assert json.loads(txt.read_text())==s['tts']
 samples,info=pcm(wav);source=common.load(str(wav));cut,tail=common.cut(source)
 active=np.flatnonzero(np.abs(cut)>.01);assert len(active)
 leading=float(active[0]/48000);trailing=float((len(cut)-1-active[-1])/48000)
 issues=[]
 if tail<.15:issues.append('last separator tail under 150ms; source-cut review required')
 if trailing<.15:issues.append('post-cut margin above-0.01 sample under 150ms; acoustic trimming-risk guard, not proven missing word')
 if np.abs(source).max()>=.999:issues.append('source reaches near full scale')
 row={'id':s['id'],'take':take,'takeSHA256':sha(wav),'rawSHA256':sha(raw),'requestSHA256':sha(txt),'sourceSamples':info['samples'],'sourceRate':info['rate'],'sharedCutSamples':len(cut),'tailAfterLastGapSeconds':tail,'cutLeadingAbove01Seconds':leading,'cutTrailingBelow01Seconds':trailing,'cutMaxSilenceAt005Seconds':max_quiet(cut),'sourcePeak':float(np.abs(source).max()),'flags':issues}
 rows.append(row);flags.extend({'id':s['id'],'take':take,'finding':issue}for issue in issues)
report={'executor':'Codex P10 voice producer AI agent','checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':a.stage,'scriptSHA256':sha(D/'script.md'),'exactNarrationAndRequestText':True,'sentences':rows,'flags':flags,'sharedToolSHA256':{str(p.relative_to(R)):sha(p)for p in [R/'episodes/_shared/voice/common.py',R/'episodes/_shared/voice/build.py',R/'episodes/_shared/onset_rule.py']},'asrModel':'none','wordAlignment':False,'fullSemanticListening':False,'limitations':['Shared cut/onset imported without copying algorithms.','Signal checks do not establish spoken-word or tone correctness. No ASR, phoneme alignment or full semantic listening performed.','150ms candidate guard is a review flag rather than proof of actual truncation; inner silence can be natural punctuation.']}
if a.stage=='final':
 assert not flags,'Resolve selected candidate flags before track acceptance.'
 build=read('voice/build.json');words=read('words.json');board=read('storyboard.json')
 samples,info=pcm(D/'voice.wav');assert info['samples']==build['summary']['samples']==words['durationFrames']*1600
 assert words['audioSha256']==sha(D/'voice.wav') and words['scriptSha256']==sha(D/'script.md')
 public=D/'remotion/public/audio/voice.wav';assert public.is_file()and not public.is_symlink()and public.read_bytes()==(D/'voice.wav').read_bytes()
 intervals=[];position=0
 for row in build['sentences']:
  start,end=row['startSample'],row['endSample'];part,_=pcm(D/'voice/sentences'/f'{row["id"]}.wav')
  assert np.array_equal(samples[start:end],part)
  intervals.append((position,start));position=end
 intervals.append((position,len(samples)))
 assert len(intervals)==29 and all(not np.any(samples[x:y])for x,y in intervals)
 fl=samples.astype(np.float32)/32767;rule=Rule(fl,48000);onsets=[]
 all_sentences=[s for shot in words['shots']for s in shot['sentences']]
 for sent in all_sentences:
  r=rule.onset(sent['startFrame'],min(sent['endFrame'],sent['startFrame']+30))
  assert r['source']=='pause' and abs(r['onset']-sent['onsetFrame'])<1e-6
  reference=math.floor(sent['startFrame']);delta=reference-r['onset'];assert -6<=delta<=2,(sent['id'],delta)
  onsets.append({'id':sent['id'],'onsetFrame':r['onset'],'referenceFrame':reference,'referenceDefinition':'floor of measured sentence start, not an undeclared visual term cue','referenceMinusOnsetFrames':delta,'rule':r['source']+'/'+r['kind']})
 shots=[s for scene in board['scenes']for s in scene['shots']];assert len(shots)==14
 assert sum(s['durationInFrames']for s in shots)==words['durationFrames']
 assert all(abs(s['from']+v['localStart']-v['wavStart'])<=.5 for s in shots for v in s['voice'])
 tp=20*math.log10(float(np.abs(resample_poly(fl,4,1)).max()));lufs=common.lufs(fl)
 assert abs(lufs+16)<=.3 and tp<=-2
 report.update(voiceSHA256=sha(D/'voice.wav'),wordsSHA256=sha(D/'words.json'),storyboardSHA256=sha(D/'storyboard.json'),frames=words['durationFrames'],samples=info['samples'],seconds=info['samples']/48000,actualIntegratedLUFS=lufs,actualTruePeakDBTP=tp,publicVoiceCopyByteIdentical=True,selectedSentencePCMMatchesWholeTrack=True,silentGapPCMZero=True,silentIntervals=len(intervals),sentenceOnsets=onsets,shotTimings=[{'id':s['id'],'scriptShot':s['scriptShot'],'from':s['from'],'durationInFrames':s['durationInFrames'],'voice':s['voice']}for s in shots],sharedBuildFlags={'innerDropouts':build['summary']['inner_dropouts'],'maxJoinSampleJump':build['summary']['max_join_sample_jump'],'maxNeighbourLUFSDiff':build['summary']['max_neighbour_lufs_diff']},declaredLabelCues=len(read('voice/cues.json')),status='passed-signal-screening')
else:report['status']='review-required'if flags else'passed-candidate-signal-screening'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output':str(out),'status':report['status'],'flags':flags,'sentences':len(rows),'frames':report.get('frames'),'seconds':report.get('seconds')},ensure_ascii=False))
