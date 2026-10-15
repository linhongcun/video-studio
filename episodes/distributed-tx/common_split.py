# EP.21 分布式事务（脚本 v0.26.0）镜头拆分：按句数，句子不拆开。章节 id = script.md「## n. id｜」
import re,os
ids=["hook","signal","local","prepare","commit","stuck","message","eventual","recap"]
SPLIT={"hook":[1,1],"signal":[2,1],"local":[1,1],"prepare":[1,2],"commit":[1,1],"stuck":[1],"message":[1,1,2],"eventual":[1],"recap":[2]}
SCRIPT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"script.md")
TTS={}
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
def subtext(s): return s
def narration():
    t=open(SCRIPT).read().split("\n---\n",1)[1].split("\n---")[0];out={}
    for m in re.finditer(r"^## \d+\. ([\w-]+)｜.*?\n(.*?)(?=^## |\Z)",t,re.S|re.M): out[m.group(1)]="".join(x.strip() for x in m.group(2).splitlines())
    assert list(out)==ids,list(out); return [out[c] for c in ids]
SENT=lambda s:re.findall(r"[^。？]+[。？]",s)
def _label_holds():
    import json as _j,os as _o
    p=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),"label_holds.json")
    return _j.load(open(p)) if _o.path.isfile(p) else {}
def apply_holds(out):
    for sid,lh in _label_holds().items():
        v=out[sid]
        if v.get("holdIncluded") or not lh: continue
        v.setdefault("origDuration",v["duration"]); v.setdefault("holdAt",v["origDuration"])
        v["duration"]=v["origDuration"]+lh; v["extraHold"]=lh; v["labelHold"]=lh
    return out
if __name__=="__main__":
    for c,s in zip(ids,narration()):
        S=SENT(s); assert len(S)==sum(SPLIT[c]),(c,len(S),S); print(c,SPLIT[c],len(S),S)
