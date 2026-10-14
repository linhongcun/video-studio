# EP.15 数据库事务（脚本 v0.20.0，待村长定稿）镜头拆分（hook-2 已并进 hook-1，Nolan 2026-10-14）：按句数，句子不拆开。章节 id = script.md「## n. id｜」
import re
ids=["hook","split","txn","commit","rollback","atomic","recap"]
SPLIT={"hook":[3],"split":[1,1],"txn":[1,1],"commit":[2,1],"rollback":[1,1],"atomic":[2,1],"recap":[1]}
SCRIPT='/workspace/sorkin-backup/db-transaction/script.md'
TTS={}   # pronunciation.md：无需改写送 TTS 的文字（回滚/倒放靠单独合成核对）
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
def subtext(s): return s
def narration():   # 本期脚本格式：每章「## n. id｜标题」下的正文段落
    t=open(SCRIPT).read().split('---',1)[-1];out={}
    for m in re.finditer(r'^## \d+\. (\w+)｜.*?\n(.*?)(?=^## |\Z)',t,re.S|re.M): out[m.group(1)]=''.join(x.strip() for x in m.group(2).splitlines())
    assert list(out)==ids,list(out); return [out[c] for c in ids]
SENT=lambda s:re.findall(r'[^。？]+[。？]',s)
HOLDS={}
def _label_holds():
    import json as _j,os as _o
    p=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'label_holds.json')
    return _j.load(open(p)) if _o.path.isfile(p) else {}
def apply_holds(out):
    for sid,lh in _label_holds().items():
        v=out[sid]
        if v.get("holdIncluded") or not lh: continue
        v.setdefault("origDuration",v["duration"]); v.setdefault("holdAt",v["origDuration"])
        v["duration"]=v["origDuration"]+lh; v["extraHold"]=lh; v["labelHold"]=lh
    return out
if __name__=='__main__':
    for c,s in zip(ids,narration()):
        S=SENT(s); assert len(S)==sum(SPLIT[c]),(c,len(S)); print(c,SPLIT[c],S)
