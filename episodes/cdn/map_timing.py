# 把 Knoll 的 MiMo 实测 timing（每章一个镜头，键 <chapter>-1，如 why-1 … recap-1）映射到本分镜 13 个镜头；章节起点、总帧数与 Knoll 一致，scale=1
# 用法：cp <Knoll 的 cdn timing.json> timing.mimo.json && python3 map_timing.py && python3 gen.py && python3 validate.py
import json
from pathlib import Path
from common_split import ids,SPLIT,apply_holds
H=Path(__file__).resolve().parent
K=json.load(open(H/"timing.mimo.json")); out={}
SHOTS=[f"{c}-{k+1}" for c in ids for k in range(len(SPLIT[c]))]
PER_SHOT=list(K)==SHOTS   # Knoll 已按 13 个镜头切好（EP.05 实测即此格式）：直接用，scale 1
if PER_SHOT:
    for sid in SHOTS:
        v=dict(K[sid]); n=SPLIT[v.get("chapter",sid.rsplit("-",1)[0])][int(sid.rsplit("-",1)[1])-1]
        assert len(v["sentences"])==n,(sid,len(v["sentences"]),n); assert v.get("scale",1)==1 and not v.get("provisional")
        v["source"]=f"/workspace/share/ep5-timing.json:{sid}"; out[sid]=v
for ch in ([] if PER_SHOT else ids):
    n=SPLIT[ch]; k=K[f"{ch}-1"]; S=k["sentences"]; assert len(S)==sum(n),(ch,len(S))
    starts=[];j=0
    for m in n: starts.append(round(30*S[j]["start"])); j+=m
    ends=starts[1:]+[k["duration"]]; i=0
    for x,(m,a,b) in enumerate(zip(n,starts,ends)):
        q=[dict(text=s["text"],start=round(s["start"]-a/30,3),dur=s["dur"]) for s in S[i:i+m]];i+=m
        af=round(30*(q[-1]["start"]+q[-1]["dur"]))
        out[f"{ch}-{x+1}"]=dict(audioSec=round(af/30,3),audioFrames=af,duration=b-a,chapterOffsetFrames=a,chapter=ch,provisional=False,engine=k.get("engine","mimo"),voice=k.get("voice","冰糖"),scale=1,source=f"timing.mimo.json:{ch}-1",sentences=q)
if any('extraHold' in v for v in out.values()): print('extraHold 已在实测 timing 内，不重复加')
else: apply_holds(out)
json.dump(out,open(H/"timing.json","w"),ensure_ascii=False,indent=1)
print(sum(v['duration'] for v in out.values()),{s:v['duration'] for s,v in out.items()})
