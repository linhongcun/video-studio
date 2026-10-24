from pathlib import Path
import hashlib,json,re,wave
D=Path(__file__).resolve().parent
sb=json.loads((D/'storyboard.json').read_text());w=json.loads((D/'words.json').read_text());cv=json.loads((D/'covers.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
checks['script_sha']=w['scriptSha256']==sha(D/'script.md')
checks['audio_sha']=w['audioSha256']==sha(D/'voice.wav')
checks['voice_real_copy']=not (D/'remotion/public/audio/voice.wav').is_symlink() and sha(D/'voice.wav')==sha(D/'remotion/public/audio/voice.wav')
with wave.open(str(D/'voice.wav')) as a: checks['exact_samples']=a.getframerate()==48000 and a.getnchannels()==1 and a.getnframes()==w['durationFrames']*1600
shots=[s for sc in sb['scenes'] for s in sc['shots']]
checks['frames']=sum(s['durationInFrames'] for s in shots)==w['durationFrames']==sb['meta']['durationInFrames']
checks['script_captions']=all(''.join(q['text'] for q in s['subtitles'])==s['narration'] for s in shots)
checks['caption_bounds']=all(0<=q['from']<=q['to']<s['durationInFrames'] for s in shots for q in s['subtitles'])
checks['label_lifetime']=all(s['durationInFrames']-e['appearFrame']>=63 for s in shots for e in s['elements'] if e.get('cueText'))
checks['voice_positions']=all(abs(s['from']+v['localStart']-v['wavStart'])<.5 and 0<=v['wavStart']<v['wavEnd']<=w['durationFrames'] for s in shots for v in s['voice'])
checks['covers_embedded']=sb['meta']['covers']==cv
checks['cover_safety_metadata']=all(315<=q['x'] and q['x']+q['w']<=1125 and q['y']+q['h']<918 for q in cv['sizes']['4x3']['textBoxes'])
r=dict(checks=checks,all_passed=all(checks.values()),frames=w['durationFrames'],shots=len(shots),sentences=sum(len(s['subtitles']) for s in shots),wordAlignment=False,independentListening=False,notes='Layout inspected from rendered phase images; sentence acoustic timing only, not ASR.')
(D/'precheck-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(r,ensure_ascii=False))
raise SystemExit(not r['all_passed'])
