# Knoll 实测 timing → 本分镜 12 个镜头（scale 1；章节起点、总帧数与 Knoll 一致）。用法：python3 -B map_timing.py <knoll timing 文件>
# 接受三种格式：①按本分镜镜头 id（hook-1…recap-2）各带 sentences；②每章一个镜头（hook-1/ch1-1 … 带全章 sentences，start 为章内秒）；
# ③逐句列表 [{id:"ch1-1",start,dur,...}] 或 {sentences:[...]}，start 为全片秒（章节边界 = 下一章第一句开始，最后一章到 total/末句+60 帧）
import json,re,sys
from pathlib import Path
from common_split import ids,SPLIT,apply_holds,SCRIPT,tts
H=Path(__file__).resolve().parent
K=json.load(open(sys.argv[1] if len(sys.argv)>1 else H/"timing.knoll.json"))
if isinstance(K,dict) and isinstance(K.get("shots"),dict): K=K["shots"]
SHOTS=[f"{c}-{k+1}" for c in ids for k in range(len(SPLIT[c]))]
N=lambda t:re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',t)
SS=[N(x) for s in re.findall(r'- 旁白：(.+)',open(SCRIPT).read()) for x in re.findall(r'[^。？]+[。？]',tts(s))]
out={}
def chap_from(ch,S,dur):   # S：本章句子（章内秒）
    n=SPLIT[ch]; starts=[];j=0
    for m in n: starts.append(round(30*S[j]["start"])); j+=m
    ends=starts[1:]+[dur]; i=0
    for x,(m,a,b) in enumerate(zip(n,starts,ends)):
        q=[dict(text=s["text"],start=max(0.0,round(s["start"]-a/30,3)),dur=s["dur"],**({"src":s["src"]} if "src" in s else {})) for s in S[i:i+m]];i+=m
        af=round(30*(q[-1]["start"]+q[-1]["dur"]))
        out[f"{ch}-{x+1}"]=dict(audioSec=round(af/30,3),audioFrames=af,duration=b-a,chapterOffsetFrames=a,chapter=ch,provisional=False,engine="knoll",scale=1,sentences=q)
if isinstance(K,dict) and set(SHOTS)<=set(K):
    for sid in SHOTS: v=dict(K[sid]); v["provisional"]=False; v.setdefault("scale",1); out[sid]=v
elif isinstance(K,dict) and all(any(k in K for k in (f"{c}-1",f"ch{i+1}-1",f"ch{i+1}")) for i,c in enumerate(ids)) and not isinstance(K.get("sentences"),list):
    for i,c in enumerate(ids):
        k=next(K[x] for x in (f"{c}-1",f"ch{i+1}",f"ch{i+1}-1") if x in K); chap_from(c,k["sentences"],k["duration"])
else:
    # ③ Knoll timeline.json（2026-10-14）：{duration, sentences:[{id:"ch1-1",chapter,text,tts_text,start,end}]}，start/end 为 narration.wav 全片秒
    #    章 = 该章第一句开始 → 最后一句结束 + 章尾留白 PAD 帧（同 make_timing 规则；Knoll 按此在章尾插静音，章间原有间隔不用）
    PAD=60
    L=K["sentences"] if isinstance(K,dict) else K
    by={i:[] for i in range(len(ids))}
    for q in L:
        ci=int(q.get("chapter") or re.match(r'ch(\d+)',q["id"]).group(1))-1; by[ci].append(q)
    for i,c in enumerate(ids):
        Q=sorted(by[i],key=lambda q:q["start"]); c0=Q[0]["start"]
        S=[dict(text=q.get("tts_text") or q.get("tts") or q["text"],start=round(q["start"]-c0,3),dur=round(q["dur"] if "dur" in q else q["end"]-q["start"],3),src=q.get("id")) for q in Q]
        chap_from(c,S,round(30*(S[-1]["start"]+S[-1]["dur"]))+PAD)
KT=[N(tts(q["text"])) for s in SHOTS for q in out[s]["sentences"]]
if KT!=SS: raise SystemExit(f"timing 与当前脚本不一致：{next((i,a,b) for i,(a,b) in enumerate(zip(KT+['']*99,SS)) if a!=b)}")
apply_holds(out)
json.dump(out,open(H/"timing.json","w"),ensure_ascii=False,indent=1)
print('knoll',sum(v['duration'] for v in out.values()),{s:v['duration'] for s,v in out.items()})
