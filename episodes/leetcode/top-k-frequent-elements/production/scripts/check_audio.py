"""Independent read-only take metadata/signal/PCM checks; no ASR claim."""
from pathlib import Path
import hashlib,json,sys,wave,subprocess
import numpy as np
from scipy.signal import resample_poly
EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'AGENTS.md').is_file())
sys.path.insert(0,str(ROOT/'episodes/_shared/voice'))
import common
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wav(p):
 with wave.open(str(p),'rb') as w:
  assert w.getnchannels()==1 and w.getsampwidth()==2
  return w.getframerate(),np.frombuffer(w.readframes(w.getnframes()),'<i2')
build=json.loads((EP/'voice/build.json').read_text());sr,track=wav(EP/'voice.wav');picks=json.loads((EP/'voice/picks.json').read_text())
rows=[]
for s in build['sentences']:
 stem=EP/'voice/takes'/f"{s['id']}-{picks.get(s['id'],'a')}";take=stem.with_suffix('.wav');raw=stem.with_suffix('.raw.wav');txt=stem.with_suffix('.txt.json')
 raw_sr,rpcm=wav(raw);take_sr,pcm=wav(take)
 exact=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(raw),'-ar','48000','-ac','1','-f','s16le','-']),'<i2')
 cut,tail=common.cut(common.load(str(take)));cut=cut[:np.flatnonzero(np.abs(cut)>1e-4)[-1]+1]
 sentence_sr,spcm=wav(EP/'voice/sentences'/f"{s['id']}.wav")
 checks={'ttsMetadataMatches':json.loads(txt.read_text())==s['tts'],'rawRate24k':raw_sr==24000,'takeRate48k':take_sr==48000,'resamplingExact':np.array_equal(pcm,exact),'sentencePcmMatchesTrack':np.array_equal(spcm,track[s['startSample']:s['endSample']]),'noClipping':not np.any(np.abs(pcm.astype(np.int32))>=32767),'signalPresent':bool(np.any(pcm)),'tailAtLeast150ms':tail>=.15,'cutSamplesMatch':len(cut)==s['endSample']-s['startSample']}
 rows.append({'id':s['id'],'checks':{k:bool(v) for k,v in checks.items()},'tailSeconds':tail,'maxInnerSilenceSeconds':s['maxInnerSilenceS'],'hashes':{p.name:sha(p) for p in [take,raw,txt]}})
 assert all(checks.values()),rows[-1]
assert sr==48000 and len(track)==build['summary']['samples'] and len(track)%1600==0
assert sha(EP/'voice.wav')==build['summary']['sha']
assert not build['summary']['inner_dropouts'],build['summary']['inner_dropouts']
assert np.array_equal(track,wav(EP/'remotion/public/audio/voice.wav')[1])
card=json.loads((EP/'storyboard.json').read_text())['meta']['unvoicedEndCard'];assert not np.any(track[card['from']*1600:])
truepeak=float(20*np.log10(np.abs(resample_poly(track.astype(float)/32768,4,1)).max()))
report={'passed':True,'executor':'Codex root','audioSha256':sha(EP/'voice.wav'),'samples':len(track),'frames':len(track)//1600,'trackLufs':build['summary']['track_lufs'],'truePeakDbtp4x':truepeak,'takeChecks':rows,'asrPerformed':False,'semanticListeningPerformed':False,'wordAlignmentPerformed':False,'limitation':'No faster-whisper package or cached official recognition model present; signal/metadata checks cannot establish spoken word or pronunciation accuracy. No semantic listening or human review is claimed.'}
(EP/'qa/audio-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Audio metadata, 32 take signals, exact resampling/track PCM, code-card silence checked; no ASR or semantic listening.')
