from pathlib import Path
import sys,json,hashlib,datetime
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'episodes/_shared/voice'));import common
D=Path(__file__).resolve().parents[1];V=D/'voice';b=json.loads((V/'build.json').read_text());sents=json.loads((V/'sents.json').read_text());rows=[];flags=[]
audio,sr=sf.read(D/'voice.wav');assert sr==48000 and audio.ndim==1;assert len(audio)==b['summary']['samples']==b['summary']['frames']*1600
assert hashlib.sha256((D/'voice.wav').read_bytes()).hexdigest()==b['summary']['sha']
for s,row in zip(sents,b['sentences']):
 assert s['id']==row['id'] and s['text']==row['text'] and s['tts']==row['tts']
 take=V/'takes'/f"{s['id']}-{row['take']}.wav";txt=V/'takes'/f"{s['id']}-{row['take']}.txt.json";assert json.loads(txt.read_text())==s['tts']
 raw=common.load(str(take));cut,tail=common.cut(raw);sentence,r=sf.read(V/'sentences'/f"{s['id']}.wav");assert r==48000
 track=audio[row['startSample']:row['endSample']];assert np.array_equal(track,sentence)
 idx=np.flatnonzero(np.abs(cut)>.01);leading=idx[0]/48000 if len(idx) else None;ending=(len(cut)-1-idx[-1])/48000 if len(idx) else None
 peak=float(np.max(np.abs(raw)));clipped=int(np.sum(np.abs(raw)>=.9999));risk=[]
 if tail<.25:risk.append('throwaway tail under250ms')
 if row['maxInnerSilenceS']>=.5:risk.append('sentence silence at least500ms')
 if clipped:risk.append('raw clipped samples')
 if risk:flags.append({'id':s['id'],'risks':risk})
 rows.append({'id':s['id'],'takeSha256':hashlib.sha256(take.read_bytes()).hexdigest(),'tailAfterLastGapSeconds':round(tail,4),'cutLeadingAbove01Seconds':round(leading,4),'cutTrailingBelow01Seconds':round(ending,4),'selectedSentenceMatchesTrackPCM':True,'maxInnerSilenceSeconds':row['maxInnerSilenceS'],'rawPeak':peak,'rawClippedSamples':clipped,'flags':risk})
gaps=[(0,b['sentences'][0]['startSample'])]+[(a['endSample'],c['startSample'])for a,c in zip(b['sentences'],b['sentences'][1:])]+[(b['sentences'][-1]['endSample'],len(audio))]
assert all(np.max(np.abs(audio[a:z]),initial=0)==0 for a,z in gaps)
r={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'executor':'Codex independent QA agent','status':'pass-signal-screening'if not flags else 'signal-flags-require-review','voiceSha256':hashlib.sha256((D/'voice.wav').read_bytes()).hexdigest(),'samples':len(audio),'frames':len(audio)//1600,'loudnessFromSharedActualBuild':b['summary']['track_lufs'],'measuredTruePeakDbTP':float(20*np.log10(np.max(np.abs(resample_poly(audio,4,1))))),'sourceBuildSha256':hashlib.sha256((V/'build.json').read_bytes()).hexdigest(),'all20TextsAndTtsRequestRecordsMatched':True,'all20SelectedSentencePcmMatchActualTrack':True,'allSilentGapPcmZero':True,'sentences':rows,'flags':flags,'limitations':['Shared cut implementation is reused rather than copied or replaced.','Amplitude, pauses, truncation risk and request text provenance checked. No phoneme/word recognition or full human semantic listening was performed.','No signal flag does not establish all spoken words/tones are correct.']}
(D/'qa/voice-independent.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':r['status'],'sentences':len(rows),'flags':flags,'tailMin':min(x['tailAfterLastGapSeconds']for x in rows),'innerSilenceMax':max(x['maxInnerSilenceSeconds']for x in rows),'truePeakDbTP':r['measuredTruePeakDbTP']},ensure_ascii=False))
