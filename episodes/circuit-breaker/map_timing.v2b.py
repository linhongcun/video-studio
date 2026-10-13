# 把 Knoll 的 MiMo 实测 timing（每章一个镜头，键 <chapter>-1，如 why-1 … recap-1）映射到本分镜镜头（v0.12.1：12 个，按句数拆）；章节起点、总帧数与 Knoll 一致，scale=1
# 用法：cp <Knoll 的 ep12 timing.json> timing.mimo.json && python3 map_timing.py && python3 gen.py && python3 validate.py
import json,re
from pathlib import Path
from common_split import ids,SPLIT,apply_holds
H=Path(__file__).resolve().parent
K=json.load(open(H/"timing.mimo.json")); out={}
if "shots" in K and isinstance(K["shots"],dict): K=K["shots"]   # EP.08 格式：{fps,total,shots:{...}}
SHOTS=[f"{c}-{k+1}" for c in ids for k in range(len(SPLIT[c]))]
PER_SHOT=set(K)==set(SHOTS)
# EP.12 第 2 版：防止误用旧（第 1 版脚本）timing——逐句对比 timing 文字与当前脚本（送 TTS 文字）
from common_split import SCRIPT,tts
_N=lambda t:re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',t)
_S=[_N(x) for s in re.findall(r'- 旁白：(.+)',open(SCRIPT).read()) for x in re.findall(r'[^。？]+[。？]',tts(s))]
_K=[_N(q["text"]) for v in (K.values() if isinstance(K,dict) else []) for q in v.get("sentences",[])]
if _K and _K!=_S: raise SystemExit(f"timing 与当前脚本不一致（旧版 timing？）：第一处不同 {next((i,a,b) for i,(a,b) in enumerate(zip(_K+['']*99,_S)) if a!=b)}")   # Knoll 已按 13 个镜头切好（EP.05 实测即此格式）：直接用，scale 1
if PER_SHOT:
    for sid in SHOTS:
        v=dict(K[sid])
        # v0.9.1 删掉开头/结尾「我是 IT小村」。旧配音（v0.9.0）的 timing 里还有这两句：过渡期先丢掉这两条句子，其余句子时间不动、镜头时长不动，标 voPending；Knoll 新 timing 到后不会触发
        keep=[q for q in v["sentences"] if "我是IT小村" not in re.sub(r"\s","",q["text"])]
        if len(keep)!=len(v["sentences"]): v["sentences"]=keep; v["voPending"]=True; v["droppedLines"]="我是 IT小村（v0.9.1 删除，等新配音）"
        n=SPLIT[sid.rsplit("-",1)[0]][int(sid.rsplit("-",1)[1])-1]   # Knoll 的 chapter 名（warehouse/prep）与本分镜 id 不同，按镜头 id 前缀[int(sid.rsplit("-",1)[1])-1]
        assert len(v["sentences"])==n,(sid,len(v["sentences"]),n); assert v.get("scale",1)==1 and not v.get("provisional")
        v["source"]=f"/workspace/share/ep12-timing.json:{sid}"; out[sid]=v
if not PER_SHOT and any(k.endswith("-2") for k in K):   # v0.12.1：按镜头的 timing 但镜头不齐（如还是旧的 12 镜头，没有 hit-miss-3）→ 直接报出来
    raise SystemExit(f"timing 镜头与分镜不一致：缺 {sorted(set(SHOTS)-set(K))}，多 {sorted(set(K)-set(SHOTS))}")
for ch in ([] if PER_SHOT else ids):
    n=SPLIT[ch]; k=K[f"{ch}-1"]; S=k["sentences"]; assert len(S)==sum(n),(ch,len(S))
    starts=[];j=0
    for m in n: starts.append(round(30*S[j]["start"])); j+=m
    ends=starts[1:]+[k["duration"]]; i=0
    for x,(m,a,b) in enumerate(zip(n,starts,ends)):
        q=[dict(text=s["text"],start=round(s["start"]-a/30,3),dur=s["dur"]) for s in S[i:i+m]];i+=m
        af=round(30*(q[-1]["start"]+q[-1]["dur"]))
        out[f"{ch}-{x+1}"]=dict(audioSec=round(af/30,3),audioFrames=af,duration=b-a,chapterOffsetFrames=a,chapter=ch,provisional=False,engine=k.get("engine","mimo"),voice=k.get("voice","冰糖"),scale=1,source=f"timing.mimo.json:{ch}-1",sentences=q)
apply_holds(out)  # 逐镜头检测：已含 extraHold 的镜头不重复加
json.dump(out,open(H/"timing.json","w"),ensure_ascii=False,indent=1)
print(sum(v['duration'] for v in out.values()),{s:v['duration'] for s,v in out.items()})
