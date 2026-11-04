#!/usr/bin/env python3
"""Independently rerun existing shared voice build and measure selected sentence data.

Reads current P08 inputs; writes only qa/voice-independent* and a disposable
scratch rebuild. It does not request TTS, modify picks or replace production PCM.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, shutil, re, subprocess, sys, tempfile, wave
import numpy as np

D=Path(__file__).resolve().parents[1]
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file())
Q=D/'qa'
sys.path.insert(0,str(ROOT/'episodes/_shared/voice'))
import common
sys.path.insert(0,str(ROOT/'episodes/_shared'))
from onset_rule import Rule


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(report):
 (Q/'voice-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def wav(p):
 with wave.open(str(p)) as f:
  params=dict(channels=f.getnchannels(),sampleWidth=f.getsampwidth(),sampleRate=f.getframerate(),sampleCount=f.getnframes())
  pcm=f.readframes(f.getnframes())
 return params,pcm


def main():
 report={'executor':'Codex independent selected-voice signal QA','status':'running','checks':{},'limitations':['No ASR or interior-word alignment.','No full semantic listening or phonetic/pronunciation judgement.','Tail durations describe shared cut selection; they do not identify the spoken phonemes.'],'notPerformed':['TTS regeneration','production input mutation','speech recognition','full semantic listening']}
 assert not (Q/'voice-independent.json').exists(),'Preserve earlier result; use a new named checker for another attempt.'
 save(report)
 names=['script.md','words.json','storyboard.json','voice.wav','remotion/public/audio/voice.wav','voice/sents.json','voice/params.json','voice/picks.json','voice/build.json']
 sents=read(D/'voice/sents.json');picks=read(D/'voice/picks.json');build=read(D/'voice/build.json');words=read(D/'words.json')
 script=(D/'script.md').read_text();sections=re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)',script,re.S)
 original=[]
 for n,slug,body in sections:
  text=re.search(r'^旁白：(.*)$',body,re.M)[1]
  for i,s in enumerate(re.findall(r'.+?[。？！]',text),1):original.append({'id':f'{int(n):02d}-{slug}-{i}','shot':f'{int(n):02d}-{slug}','text':s})
 assert len(original)==len(sents)==len(build['sentences'])==28
 assert [r['id'] for r in original]==[r['id'] for r in sents]==[r['id'] for r in build['sentences']]
 for expected,source,row in zip(original,sents,build['sentences']):
  assert expected['text']==source['text']==row['text']
  assert source['tts']==source['text']+'好。'
  chosen=picks.get(source['id'],'a');assert row['take']==chosen
  path=f"voice/takes/{source['id']}-{chosen}.wav";names+=[path,path.replace('.wav','.txt.json')]
  assert read(D/path.replace('.wav','.txt.json'))==source['tts']
  names += [f"voice/sentences/{source['id']}.wav"]
 names+=['voice/takes/07-remove-black-2-a.wav','voice/takes/07-remove-black-2-b.wav']
 before={n:sha(D/n) for n in sorted(set(names))}
 report['inputSHA256']=before
 report['sharedToolSHA256']={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'episodes/_shared/voice/build.py',ROOT/'episodes/_shared/voice/common.py',ROOT/'episodes/_shared/onset_rule.py']}
 report['checks']['scriptAndSubmittedTTS']={'pass':True,'shots':len(sections),'sentences':28,'allExactScriptSentences':True,'allSelectedRequestTextExact':True,'ttsSuffix':'好。','picks':picks}
 selected=[]
 for source in sents:
  chosen=picks.get(source['id'],'a');p=D/f"voice/takes/{source['id']}-{chosen}.wav"
  x=common.load(str(p));assert len(x)>0
  clipped,tail=common.cut(x)
  nonzero=np.where(np.abs(clipped)>1e-4)[0];assert len(nonzero)
  trimmed=clipped[:nonzero[-1]+1]
  row=next(r for r in build['sentences'] if r['id']==source['id'])
  assert len(trimmed)==row['endSample']-row['startSample']
  assert round(tail,2)==row['tailCut']
  selected.append({'id':source['id'],'take':chosen,'sourceSamples48k':len(x),'canonicalCutAppendedTailSeconds':tail,'postFadeTrimSamples':len(trimmed),'buildStartSample':row['startSample'],'buildEndSample':row['endSample'],'sampleCountExact':True})
 excluded=[]
 for choice in ['a','b']:
  p=D/f'voice/takes/07-remove-black-2-{choice}.wav';x=common.load(str(p));y,tail=common.cut(x)
  excluded.append({'take':choice,'sha256':sha(p),'canonicalCutAppendedTailSeconds':tail,'selected':choice==picks.get('07-remove-black-2','a'),'assessment':'The appended tail is unusually short in a; b has a materially longer detected tail. These are signal durations, not a phonetic judgement.'})
 report['checks']['canonicalCutRecalculation']={'pass':True,'sentences':selected,'candidate07Comparison':excluded,'definition':'common.cut returns time after the selected final >=150ms gap; this is the detected appended tail, not a measurement of narration removed.'}
 save(report)
 with tempfile.TemporaryDirectory(prefix='p08_voice_independent_') as tmp:
  scratch=Path(tmp);vd=scratch/'voice';(vd/'takes').mkdir(parents=True)
  for name in ['sents.json','params.json','picks.json']:(vd/name).write_bytes((D/'voice'/name).read_bytes())
  for source in sents:
   name=f"{source['id']}-{picks.get(source['id'],'a')}.wav"
   shutil.copyfile(D/'voice/takes'/name,vd/'takes'/name)
  result=subprocess.run([sys.executable,str(ROOT/'episodes/_shared/voice/build.py'),'--dir',str(scratch)],capture_output=True)
  (Q/'voice-independent-shared-build.log').write_bytes(result.stdout+result.stderr)
  assert result.returncode==0,'Original shared rebuild failed; preserved log has details.'
  assert sha(scratch/'voice.wav')==sha(D/'voice.wav')
  rebuilt=read(vd/'build.json')
  assert rebuilt['summary']['sha']==sha(D/'voice.wav')
  assert rebuilt['summary']['samples']==build['summary']['samples']
  rebuiltSentences=[]
  for source in sents:
   p=f"sentences/{source['id']}.wav";assert sha(vd/p)==sha(D/'voice'/p)
   rebuiltSentences.append({'id':source['id'],'pcmWavSHA256':sha(vd/p),'byteIdentical':True})
 report['checks']['canonicalRebuild']={'pass':True,'command':'python3 episodes/_shared/voice/build.py --dir <disposable scratch copy of exact current parameters/picks/selected takes>','noCopiedAlgorithm':True,'voiceSHA256':sha(D/'voice.wav'),'wholeWavByteIdentical':True,'sentences':rebuiltSentences}
 fmt,pcm=wav(D/'voice.wav');assert fmt['channels']==1 and fmt['sampleWidth']==2 and fmt['sampleRate']==48000
 assert fmt['sampleCount']==words['durationFrames']*1600==build['summary']['samples']
 for row in build['sentences']:
  _,part=wav(D/f"voice/sentences/{row['id']}.wav")
  assert part==pcm[row['startSample']*2:row['endSample']*2]
 public=D/'remotion/public/audio/voice.wav'
 assert public.is_file() and not public.is_symlink() and public.read_bytes()==(D/'voice.wav').read_bytes()
 assert words['audioSha256']==sha(D/'voice.wav') and words['scriptSha256']==sha(D/'script.md')
 assert words['asrModel']=='none' and words['wordAlignment'] is False
 report['checks']['pcmPlacement']={'pass':True,'format':fmt,'all28SentencePCMByteSlicesExact':True,'publicWavIsEntityAndWholeBytesEqual':True,'bodyFrames':words['durationFrames'],'wordAlignment':False,'asrModel':'none'}
 samples=np.frombuffer(pcm,'<i2').astype(float)/32767;rule=Rule(samples,48000);onsets=[]
 for shot in words['shots']:
  for s in shot['sentences']:
   actual=rule.onset(s['startFrame'],min(s['endFrame'],s['startFrame']+30))
   assert actual['source']=='pause' and abs(actual['onset']-s['onsetFrame'])<1e-9
   onsets.append({'id':s['id'],'storedOnsetFrame':s['onsetFrame'],'recomputedOnsetFrame':actual['onset'],'source':actual['source'],'kind':actual['kind'],'equal':True})
 assert len(onsets)==28
 report['checks']['sentenceOnsets']={'pass':True,'sharedRuleUsed':True,'rows':onsets,'scope':'Sentence starts only; no inferred interior word alignment.'}
 after={n:sha(D/n) for n in before};assert after==before
 report['productionInputsUnchanged']=True
 report['checkedAtUTC']=datetime.now(timezone.utc).isoformat()
 report['checkedAtMeaning']='Observed after the actual computation completed.'
 report['status']='passed';report['passed']=True
 save(report)
 print(json.dumps({'passed':True,'voiceSHA256':sha(D/'voice.wav'),'bodyFrames':words['durationFrames'],'sentences':28,'selected07':picks.get('07-remove-black-2','a'),'report':str((Q/'voice-independent.json').relative_to(ROOT))}))

if __name__=='__main__':
 try:main()
 except Exception as error:
  target=Q/'voice-independent.json'
  if target.is_file():
   report=read(target);report.update(status='failed',passed=False,errorType=type(error).__name__,error=str(error),failedAtUTC=datetime.now(timezone.utc).isoformat());save(report)
  raise
