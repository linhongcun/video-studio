# EP.20 全局唯一 ID（脚本 v0.25.0 定稿）镜头拆分：按句数，句子不拆开。章节 id = script.md「## n. id｜」
import re
ids=["hook","signal","clash","autoinc","need","snowflake","clock","counter","recap"]
SPLIT={"hook":[1,1],"signal":[1,1],"clash":[1],"autoinc":[1,1],"need":[1],"snowflake":[1,1,1],"clock":[1],"counter":[1],"recap":[2]}
SCRIPT="/workspace/sorkin-backup/global-id/script.md"
TTS={}
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
def subtext(s): return s
def narration():
    t=open(SCRIPT).read().split("---",1)[1].split("\n---")[0];out={}
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
        S=SENT(s); assert len(S)==sum(SPLIT[c]),(c,len(S),S); print(c,SPLIT[c],len(S),[len(re.findall(r"[\u4e00-\u9fff]",x)) for x in S])
