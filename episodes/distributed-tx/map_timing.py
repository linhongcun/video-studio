# Knoll timeline.json → EP.20 镜头 timing（db-lock 骨架）。用法：python3 -B map_timing.py /workspace/share/ep20/timeline.json（或 timeline.estimate.json）
# 接受三种格式：①按本分镜镜头 id（hook-1…recap-2）各带 sentences；②每章一个镜头（hook-1/ch1-1 … 带全章 sentences，start 为章内秒）；
# ③逐句列表 [{id:"ch1-1",start,dur,...}] 或 {sentences:[...]}，start 为全片秒（章节边界 = 下一章第一句开始，最后一章到 total/末句+60 帧）
import json,re,sys
from pathlib import Path
from common_split import ids,SPLIT,apply_holds,SCRIPT,tts,narration,SENT,add_cards
H=Path(__file__).resolve().parent
K=json.load(open(sys.argv[1] if len(sys.argv)>1 else H/"timing.knoll.json"))
if isinstance(K,dict) and isinstance(K.get("shots"),dict): K=K["shots"]
SHOTS=[f"{c}-{k+1}" for c in ids for k in range(len(SPLIT[c]))]
N=lambda t:re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',t)
SS=[N(x) for s in narration() for x in SENT(tts(s))]
out={}
RENAME={};PEND=[]   # EP.20 无改名
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
    PAD=0   # v4r2：片尾 60 帧由 ChannelBranding 自动追加，分镜不再留 60 帧（Nolan 审 2026-10-16）
    L=K["sentences"] if isinstance(K,dict) else K
    # 改名待重配机制（EP.18 留下，本期 RENAME 为空）
    PEND=[]
    for q in L:
        for a,b in RENAME.items():
            if a in q["text"]: q["text"]=q["text"].replace(a,b);q["tts_text"]=(q.get("tts_text") or "").replace(a,b);PEND.append(q["id"])
    # v4：Knoll 把开场三小句配成一条 ch1-1（op2-b，0.2 s 停顿）→ 按 Knoll 实测小句比例 1.93/1.65/0.82（停顿 0.2）拆成 ch1-1a/b/c，供镜头内对位
    L2=[]
    for q in L:
        P_=SENT(q["text"])
        if len(P_)>1:
            W_=[1.93,1.65,0.82] if len(P_)==3 else [len(x) for x in P_];tot=q["end"]-q["start"];g_=0.2*(len(P_)-1);k_=(tot-g_)/sum(W_);t_=q["start"]
            for j,(x,w_) in enumerate(zip(P_,W_)): L2.append(dict(q,id=q["id"]+"abc"[j],text=x,tts_text=x,start=round(t_,3),end=round(t_+w_*k_,3),splitFrom=q["id"]));t_+=w_*k_+0.2
        else: L2.append(q)
    L=L2
    by={i:[] for i in range(len(ids))}
    for q in L:
        ci=int(q.get("chapter") or re.match(r'ch(\d+)',q["id"]).group(1))-1; by[ci].append(q)
    # EP.17（Knoll 2026-10-15）：章间 0.6 s 已在 narration.wav 里 → 章 = 本章首句起 → 下一章首句起（不再补章尾 60 帧）；只在全片结尾（末句止）补 PAD 帧
    C0=[min(q["start"] for q in by[i]) for i in range(len(ids))]
    END=max(q["end"] for q in L)
    for i,c in enumerate(ids):
        Q=sorted(by[i],key=lambda q:q["start"]); c0=Q[0]["start"]
        S=[dict(text=q["text"],tts=q.get("tts_text"),start=round(q["start"]-c0,3),dur=round(q["dur"] if "dur" in q else q["end"]-q["start"],3),src=q.get("id")) for q in Q]
        nxt=round(30*C0[i+1]) if i+1<len(ids) else round(30*END)+PAD
        chap_from(c,S,nxt-round(30*c0))
if isinstance(K,dict) and K.get("estimate"):   # make_timing.py 生成的暂定时间轴（字数估算）
    for v in out.values(): v.update(provisional=True,engine="estimate",basis=K.get("basis"))
if PEND:
    for v in out.values(): v.update(pendingRevoice=PEND)
KT=[N(tts(q["text"])) for s in SHOTS for q in out[s]["sentences"]]
if KT!=SS: raise SystemExit(f"timing 与当前脚本不一致：{next((i,a,b) for i,(a,b) in enumerate(zip(KT+['']*99,SS)) if a!=b)}")
apply_holds(out)
out=add_cards(out)
json.dump(out,open(H/"timing.json","w"),ensure_ascii=False,indent=1)
print('knoll',sum(v['duration'] for v in out.values()),{s:v['duration'] for s,v in out.items()})
