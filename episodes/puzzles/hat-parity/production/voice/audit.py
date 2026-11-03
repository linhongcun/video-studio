#!/usr/bin/env python3
"""Recompute selected-take and whole-track signal facts using shared cut/onset."""
from pathlib import Path
import argparse, datetime, hashlib, json, re, sys
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
D=Path(__file__).resolve().parents[1]
R=next(p for p in D.parents if (p/'AGENTS.md').is_file())
sys.path.insert(0,str(R/'episodes/_shared/voice'))
import common
sys.path.insert(0,str(R/'episodes/_shared'))
from onset_rule import Rule
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
write=lambda p,obj:p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
p=argparse.ArgumentParser(__doc__);p.add_argument('--takes-only',action='store_true');a=p.parse_args()
v=D/'voice'; sents=read(v/'sents.json'); picks=read(v/'picks.json')
assert len(sents)==28 and len(set(s['id'] for s in sents))==28
narrations=re.findall(r'^旁白：(.*)$',(D/'script.md').read_text(),re.M)
assert ''.join(s['text'] for s in sents)==''.join(narrations)
rows=[]; flags=[]
for s in sents:
 k=picks.get(s['id'],'a'); path=v/'takes'/f"{s['id']}-{k}.wav"
 textpath=path.with_suffix('.txt.json'); rawpath=path.with_name(path.stem+'.raw.wav')
 assert path.is_file() and rawpath.is_file() and read(textpath)==s['tts']
 x,sr=sf.read(path); assert sr==48000 and x.ndim==1
 cut,tail=common.cut(common.load(str(path)))
 active=np.flatnonzero(np.abs(cut)>.01); assert len(active)>0
 silence=np.max(np.abs(cut[:len(cut)//480*480].reshape(-1,480)),axis=1)<=.005
 runs=re.findall('1+',''.join('1' if y else '0' for y in silence))
 inner=max(map(len,runs),default=0)/100
 risks=[]
 if tail<.25:risks.append('throwaway tail below250ms')
 if inner>=.5:risks.append('source sentence silence at least500ms; review cue only')
 if np.any(np.abs(x)>=.9999):risks.append('source clipped sample')
 row=dict(id=s['id'],take=k,takeSHA256=sha(path),rawSHA256=sha(rawpath),requestSHA256=sha(textpath),sourceFrames=len(x),sourceRate=sr,sharedCutSamples=len(cut),tailAfterLastGapSeconds=float(tail),cutLeadingAbove01Seconds=float(active[0]/sr),cutTrailingBelow01Seconds=float((len(cut)-1-active[-1])/sr),cutMaxSilenceAt005Seconds=inner,sourcePeak=float(np.max(np.abs(x))),flags=risks)
 rows.append(row)
 if risks:flags.append(dict(id=s['id'],flags=risks))
report=dict(executor='Codex P08 voice producer',checkedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage='selected-takes' if a.takes_only else 'selected-takes-and-whole-track',exactNarrationAndRequestText=True,sentences=rows,flags=flags,sharedToolSHA256={str(p.relative_to(R)):sha(p) for p in [R/'episodes/_shared/voice/common.py',R/'episodes/_shared/voice/build.py',R/'episodes/_shared/onset_rule.py']},limitations=['Shared cut/onset are imported without copying algorithms.','Signal checks do not establish spoken word or tone correctness. No ASR, phoneme alignment or complete semantic listening was performed.','Long internal silence is a review cue, not an established dropout.'])
candidate=read(v/'candidate-a-tail-flag.json'); candidatepath=v/'takes'/f"{candidate['id']}-a.wav"
candidatecut,candidatetail=common.cut(common.load(str(candidatepath)))
assert sha(candidatepath)==candidate['sourceSHA256'] and len(candidatecut)==candidate['sharedCutSamples']
assert abs(float(candidatetail)-candidate['tailAfterLastGapSeconds'])<1e-8
assert picks[candidate['id']]=='b'
report['retainedCandidate']=dict(id=candidate['id'],candidate='a',sourceSHA256=sha(candidatepath),sharedCutSamples=len(candidatecut),tailAfterLastGapSeconds=float(candidatetail),selectedInstead='b',recordMatchesRecomputedSignal=True,scope='Short throwaway tail risk; no spoken-word error established.')
if not a.takes_only:
 build=read(v/'build.json'); audio,sr=sf.read(D/'voice.wav'); words=read(D/'words.json'); board=read(D/'storyboard.json')
 assert sr==48000 and audio.ndim==1 and len(audio)==build['summary']['samples']==build['summary']['frames']*1600
 assert sha(D/'voice.wav')==build['summary']['sha']==words['audioSha256']
 assert words['scriptSha256']==sha(D/'script.md') and words['asrModel']=='none' and words['wordAlignment'] is False
 assert not (D/'remotion/public/audio/voice.wav').is_symlink()
 assert (D/'voice.wav').read_bytes()==(D/'remotion/public/audio/voice.wav').read_bytes()
 for s,r in zip(sents,build['sentences']):
  assert (s['id'],s['text'],s['tts'])==(r['id'],r['text'],r['tts'])
  y,ysr=sf.read(v/'sentences'/f"{s['id']}.wav")
  assert ysr==sr and np.array_equal(audio[r['startSample']:r['endSample']],y)
 gaps=[(0,build['sentences'][0]['startSample'])]+[(x['endSample'],y['startSample']) for x,y in zip(build['sentences'],build['sentences'][1:])]+[(build['sentences'][-1]['endSample'],len(audio))]
 assert all(np.max(np.abs(audio[x:y]),initial=0)==0 for x,y in gaps)
 shots=[sh for sc in board['scenes'] for sh in sc['shots']]
 assert len(shots)==14 and sum(sh['durationInFrames'] for sh in shots)==words['durationFrames']
 rule=Rule(audio,sr); onsets=[]
 for sh,ws in zip(shots,words['shots']):
  assert sh['from']==ws['startFrame']
  for i,s in enumerate(ws['sentences']):
   measured=rule.onset(s['startFrame'],min(s['endFrame'],s['startFrame']+30))
   assert measured['source']=='pause' and abs(measured['onset']-s['onsetFrame'])<1e-6
   cue=sh['from']+sh['cueFrames']['sentences'][i]; diff=cue-measured['onset']
   assert -6<=diff<=2
   onsets.append(dict(id=s['id'],onsetFrame=measured['onset'],cueAbsoluteFrame=cue,cueMinusOnsetFrames=diff,rule=measured['source']+'/'+measured['kind']))
 report.update(voiceSHA256=sha(D/'voice.wav'),scriptSHA256=sha(D/'script.md'),wordsSHA256=sha(D/'words.json'),storyboardSHA256=sha(D/'storyboard.json'),frames=build['summary']['frames'],samples=len(audio),seconds=len(audio)/sr,actualIntegratedLUFS=build['summary']['track_lufs'],actualTruePeakDBTP=float(20*np.log10(np.max(np.abs(resample_poly(audio,4,1))))),publicVoiceCopyByteIdentical=True,selectedSentencePCMMatchesWholeTrack=True,silentGapPCMZero=True,sentenceOnsets=onsets,sharedBuildFlags=build['summary']['inner_dropouts'])
report['status']='signal-flags-require-review' if flags else 'passed-signal-screening'
out=D/'qa'/('voice-selected-takes.json' if a.takes_only else 'voice-producer.json'); out.parent.mkdir(exist_ok=True)
write(out,report)
print(json.dumps(dict(status=report['status'],sentences=len(rows),flags=flags,frames=report.get('frames'),report=str(out.relative_to(R))),ensure_ascii=False))
