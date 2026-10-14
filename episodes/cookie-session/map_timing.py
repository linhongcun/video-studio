# 把 Knoll 的 MiMo 实测 timing（每章一个镜头，键 <chapter>-1）映射成本分镜的 12 个镜头；章节起点、总帧数与 Knoll 一致，scale=1
import json
from pathlib import Path
from common_split import ids,SPLIT
H=Path(__file__).resolve().parent
K=json.load(open(H/"timing.mimo.json")); out={}
for ch in ids:
    n=SPLIT[ch]; k=K[f"{ch}-1"]; S=k["sentences"]; assert len(S)==sum(n),(ch,len(S))
    starts=[];j=0
    for m in n: starts.append(round(30*S[j]["start"])); j+=m
    ends=starts[1:]+[k["duration"]]; i=0
    for x,(m,a,b) in enumerate(zip(n,starts,ends)):
        q=[dict(text=s["text"],start=round(s["start"]-a/30,3),dur=s["dur"]) for s in S[i:i+m]];i+=m
        af=round(30*(q[-1]["start"]+q[-1]["dur"]))
        out[f"{ch}-{x+1}"]=dict(audioSec=round(af/30,3),audioFrames=af,duration=b-a,chapterOffsetFrames=a,provisional=False,engine="mimo",voice="冰糖",scale=1,source=f"timing.mimo.json:{ch}-1",sentences=q)
# extraHold：纯画面停留，配音不动。holdAt=镜头内插入点（None=镜头末尾，语音之后）；插入点之后的句子整体后移 hold 帧
HOLDS={"set-cookie-1":(341,45),"session-2":(None,45),"protect-2":(None,45),"recap-2":(None,45)}  # 2026-10-14：send-2 +20 已撤回（导演定不加 hold）
import os as _o  # 2026-10-14 Nolan：术语标签的最短 hold（_audit/labelfix.py 写 label_holds.json），加在镜头末尾
_LH=json.load(open(H/"label_holds.json")) if (H/"label_holds.json").is_file() else {}
for _s,_v in _LH.items():
    if _s in HOLDS and HOLDS[_s][0] is not None: continue   # 已有镜头中间的 hold（set-cookie-1）：标签 hold 另记 labelHold，下面单独加在镜头末尾
    HOLDS[_s]=(None,HOLDS.get(_s,(None,0))[1]+_v)
acc=0
for sid,v in out.items():
    v["knollChapterOffsetFrames"]=v["chapterOffsetFrames"]; v["globalShift"]=acc
    if sid in HOLDS:
        at,h=HOLDS[sid]; at=v["duration"] if at is None else at
        for q in v["sentences"]:
            if round(30*q["start"])>=at: q["start"]=round(q["start"]+h/30,3)
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=at
        q=v["sentences"][-1]; v["audioFrames"]=round(30*(q["start"]+q["dur"])); v["audioSec"]=round(v["audioFrames"]/30,3)
        acc+=h
# 镜头中间已有 hold 的镜头，标签 hold 单独加在镜头末尾（labelHold；validate 的句子起点检查把它算进之后镜头的累计偏移）
_acc=0
for sid,v in out.items():
    v["globalShift"]=v.get("globalShift",0)+_acc
    if sid in _LH and sid in HOLDS and HOLDS[sid][0] is not None:
        v["duration"]+=_LH[sid]; v["labelHold"]=_LH[sid]; _acc+=_LH[sid]
json.dump(out,open(H/"timing.json","w"),ensure_ascii=False,indent=1)
print(sum(v['duration'] for v in out.values()),{s:v['duration'] for s,v in out.items()})
