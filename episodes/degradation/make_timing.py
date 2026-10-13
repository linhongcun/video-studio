# 暂定 timing.json（无配音）：按第三期 MiMo「冰糖」实测校准（557 字 / 3937 帧，句内 4.842 字/秒，句间 0.28 秒，每章尾留 60 帧）
# 配音出来后：把 Knoll 的实测 timing（每章一个镜头，键 why-1 … recap-1）存为 timing.mimo.json → python3 map_timing.py 覆盖
import json,re
from pathlib import Path
from common_split import ids,SPLIT,apply_holds,SCRIPT,tts
HERE=Path(__file__).resolve().parent
cnt=lambda s:len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))
sentences=lambda s:re.findall(r'[^。？]+[。？]',s)
REF='/workspace/miyazaki-backup/_ref/video-studio/episodes/dns/'
K=json.load(open(REF+'timing.mimo.json'))
dns=re.findall(r'- 旁白：(.+)',open(REF+'script.md').read())
C=sum(cnt(s) for s in dns); D=sum(x['dur'] for v in K.values() for x in v['sentences'])
TOT=sum(v['duration'] for v in K.values())
RATE=C/D; GAP=0.28; PAD=60
narr=re.findall(r'- 旁白：(.+)',open(SCRIPT).read()); assert len(narr)==4
out={}
for ch,s in zip(ids,narr):
    S=sentences(tts(s)); assert len(S)==sum(SPLIT[ch]),(ch,len(S)); t=0; allq=[]
    for x in S:
        d=round(cnt(x)/RATE,3); allq.append(dict(text=x.strip(),start=round(t,3),dur=d)); t+=d+GAP
    chapF=round(30*(t-GAP))+PAD; i=0; starts=[]
    for m in SPLIT[ch]: starts.append(round(30*allq[i]['start'])); i+=m
    ends=starts[1:]+[chapF]; i=0
    for k,(m,a,b) in enumerate(zip(SPLIT[ch],starts,ends)):
        q=[dict(text=z['text'],start=round(z['start']-a/30,3),dur=z['dur']) for z in allq[i:i+m]]; i+=m
        af=round(30*(q[-1]['start']+q[-1]['dur']))
        out[f"{ch}-{k+1}"]=dict(audioSec=round(af/30,3),audioFrames=af,duration=b-a,chapterOffsetFrames=a,chapter=ch,provisional=True,engine="estimate",
            basis=f"EP.03 MiMo 冰糖 实测 {C} 字/{TOT} 帧（句内 {RATE:.3f} 字/秒，句间 {GAP} 秒，每章尾留 {PAD} 帧）",sentences=q)
apply_holds(out)
json.dump(out,open(HERE/"timing.json","w"),ensure_ascii=False,indent=1)
json.dump(out,open(HERE/"timing.provisional.json","w"),ensure_ascii=False,indent=1)
print(C,TOT,round(RATE,3),len(out),sum(v['duration'] for v in out.values()))
