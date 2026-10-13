import json,subprocess,math
import soundfile as sf
OLD='/workspace/vs-work/feat-cache-voice/episodes/browser-cache'
K=json.load(open(OLD+'/timing.mimo.json'))
CH={}
for ch in ['hook','first','second']:
    S=[]
    for k,v in K.items():
        if v['chapter']==ch:
            for s in v['sentences']: S.append(dict(text=s['text'],start=round(v['chapterOffsetFrames']/30+s['start'],3),dur=s['dur']))
    w=f'{OLD}/remotion/public/audio/ch/{ch}-1.wav'
    CH[ch]=(w,S,sf.info(w).duration)
for ch in ['freshness','revalidate']:
    w=f'{ch}-final.wav';CH[ch]=(w,json.load(open(f'{ch}-final.json')),sf.info(w).duration)
w=f'{OLD}/remotion/public/audio/ch/recap-1.wav';S=[]
for k in ['recap-1','recap-2']:
    v=K[k];S+=[dict(text=s['text'],start=round(v['chapterOffsetFrames']/30+s['start'],3),dur=s['dur']) for s in v['sentences']]
CH['recap']=(w,S,sf.info(w).duration)
MAP=[("hook","hook",[1,2]),("first","first",[1,2]),("second","second",[1,2]),("freshness","freshness",[3,2]),("revalidate","revalidate",[2,2,2]),("recap","recap",[1,2])]
out={};g=0;subprocess.run(['mkdir','-p','shots'])
for ch,sh,n in MAP:
    wav,S,adur=CH[ch];assert len(S)==sum(n),(ch,len(S))
    end=S[-1]['start']+S[-1]['dur'];dur=round(30*end)+10+(24 if ch=='revalidate' else 0)
    st=[];j=0
    for m in n: st.append(round(30*S[j]['start']));j+=m
    en=st[1:]+[dur];i=0
    for x,(m,a,b) in enumerate(zip(n,st,en)):
        q=[dict(text=s['text'],start=round(s['start']-a/30,3),dur=s['dur']) for s in S[i:i+m]];i+=m
        af=round(30*(q[-1]['start']+q[-1]['dur']));sid=f'{sh}-{x+1}'
        out[sid]=dict(start=g,duration=b-a,audioFrames=af,audioSec=round(af/30,3),chapter=ch,chapterOffsetFrames=a,engine='mimo',model='mimo-v2.5-tts',voice='冰糖',gap=0.28,scale=1,provisional=False,revoiced=ch in('freshness','revalidate'),holdFrames=24 if sid=='revalidate-3' else 0,sentences=q)
        assert af<=b-a,(sid,af,b-a)
        subprocess.run(['ffmpeg','-y','-v','error','-i',wav,'-af',f'atrim={a/30:.4f}:{b/30:.4f},asetpts=N/SR/TB,apad,atrim=0:{(b-a)/30:.4f}','-ar','48000','-ac','1',f'shots/{sid}.wav'],check=True)
        g+=b-a
json.dump(dict(fps=30,total=g,shots=out),open('/workspace/share/ep7v122-timing.json','w'),ensure_ascii=False,indent=1)
open('list.txt','w').write(''.join(f"file 'shots/{s}.wav'\n" for s in out))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','list.txt','-c:a','libmp3lame','-b:a','192k','/workspace/share/ep7v122-voice.mp3'],check=True)
for s,v in out.items(): print(s,v['start'],v['duration'],v['audioFrames'],len(v['sentences']))
print('total',g)
