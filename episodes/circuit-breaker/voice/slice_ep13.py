import json,subprocess,soundfile as sf
MAP=[('hook',[2,2]),('cascade',[2,2]),('breaker',[2,1,3]),('states',[3]),('half-open',[2,1]),('recap',[1,2])]
out={};g=0;subprocess.run(['mkdir','-p','shots']);chap={}
for ch,n in MAP:
    S=json.load(open(f'{ch}-final.json'));wav=f'{ch}-final.wav';assert len(S)==sum(n),ch
    end=S[-1]['start']+S[-1]['dur'];dur=round(30*end)+10
    chap[ch]=dict(audioSec=round(end,3),frames=dur,sentences=[dict(text=s['text'],tts=s.get('tts'),start=s['start'],dur=s['dur'],take=s['take']) for s in S])
    st=[];j=0
    for m in n: st.append(round(30*S[j]['start']));j+=m
    en=st[1:]+[dur];i=0
    for x,(m,a,b) in enumerate(zip(n,st,en)):
        q=[dict(text=s['text'],start=round(s['start']-a/30,3),dur=s['dur']) for s in S[i:i+m]];i+=m
        af=round(30*(q[-1]['start']+q[-1]['dur']));sid=f'{ch}-{x+1}'
        out[sid]=dict(start=g,duration=b-a,audioFrames=af,audioSec=round(af/30,3),chapter=ch,chapterOffsetFrames=a,engine='mimo',model='mimo-v2.5-tts',voice='冰糖',gap=0.28,scale=1,provisional=False,sentences=q)
        assert af<=b-a
        subprocess.run(['ffmpeg','-y','-v','error','-i',wav,'-af',f'atrim={a/30:.4f}:{b/30:.4f},asetpts=N/SR/TB,apad,atrim=0:{(b-a)/30:.4f}','-ar','48000','-ac','1',f'shots/{sid}.wav'],check=True)
        g+=b-a
json.dump(dict(fps=30,total=g,shots=out,chapters=chap),open('/workspace/share/ep13-timing.json','w'),ensure_ascii=False,indent=1)
open('list.txt','w').write(''.join(f"file 'shots/{s}.wav'\n" for s in out))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','list.txt','-c:a','libmp3lame','-b:a','192k','/workspace/share/ep13-voice.mp3'],check=True)
for c,v in chap.items(): print('CH',c,v['audioSec'],v['frames'])
for s,v in out.items(): print(s,v['start'],v['duration'],v['audioFrames'])
print('total',g)
