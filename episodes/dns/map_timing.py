# 把 Knoll 的 MiMo 实测 timing（每章一个镜头）映射成本分镜的 14 个镜头；章节起点、总帧数与 Knoll 一致，scale=1
import json
from pathlib import Path
H=Path(__file__).resolve().parent
K=json.load(open(H/"timing.mimo.json"))
SPLIT={"phonebook":[2,2],"cache":[2,1],"resolver":[2,2],"iterative":[2,2,1],"ttl":[1,1,1],"recap":[1,1]}
SID={"iterative":["iterative-1a","iterative-1b","iterative-2"]}
out={}
for ch,n in SPLIT.items():
    k=K[f"{ch}-1"];S=k["sentences"];assert len(S)==sum(n),(ch,len(S))
    i=0;ids=SID.get(ch,[f"{ch}-{j+1}" for j in range(len(n))])
    starts=[];j=0
    for m in n: starts.append(round(30*S[j]["start"]));j+=m
    ends=starts[1:]+[k["duration"]]
    for sid,m,a,b in zip(ids,n,starts,ends):
        q=[dict(text=s["text"],start=round(s["start"]-a/30,3),dur=s["dur"]) for s in S[i:i+m]];i+=m
        af=round(30*(q[-1]["start"]+q[-1]["dur"]))
        out[sid]=dict(audioSec=round(af/30,3),audioFrames=af,duration=b-a,chapterOffsetFrames=a,provisional=False,engine="mimo",voice="冰糖",scale=1,source="timing.mimo.json:"+ch+"-1",sentences=q)
json.dump(out,open(H/"timing.json","w"),ensure_ascii=False,indent=1)
print(sum(v['duration'] for v in out.values()),{s:(v['duration'],v['audioFrames']) for s,v in out.items()})
