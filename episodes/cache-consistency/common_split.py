# EP.22 缓存和数据库一致性（v0.28.0 返工，11 章）镜头拆分：按句数，句子不拆开。章节 id = script.md「## n. id｜」（工具链沿用 EP.21）
import re,os
ids=["hook","copies","read","del","order","retry","replica","ttl","eventual","recap","ending"]
SPLIT={"hook":[3],"copies":[1,1,2,1,1],"read":[1,1,1,3],"del":[2,1,1,1,1,1,1,1,1],"order":[2,1,1,1,1,1,1,1,1],"retry":[1,1,1,1,1,1,1,1,1,1,1],"replica":[1,1,1,1,1,1,1,1],"ttl":[1,1,1,1,1,1],"eventual":[1,1,1],"recap":[2,1,1,1,1],"ending":[2,1]}
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

# 章节卡：第 3–7 章前各一张独立章节卡（无旁白，Knoll 在配音里插同长静音）。卡长 CARD 帧：名字 0→4 帧淡入，完整显示到转场（crossfade 4）开始 = 70 帧 ≥69
CARD=78
CARDS={"del":("card-1","第一层 · 删而不改","#1E293B"),"order":("card-2","第二层 · 先改库再删","#1E293B"),"retry":("card-3","第三层 · 删失败了怎么办","#1E293B"),"replica":("card-4","第四层 · 主从延迟","#1E293B"),"ttl":("card-5","兜底 · 过期时间","#1E293B")}
def add_cards(out):
    res={}
    for k,v in out.items():
        ch=v.get("chapter")
        if k.endswith("-1") and ch in CARDS:
            cid,name,col=CARDS[ch];ci=ids.index(ch)+1
            res[cid]=dict(card=True,name=name,background=col,duration=CARD,origDuration=0,labelHold=CARD,holdAt=0,extraHold=CARD,
                         insertBeforeSentence=f"ch{ci}-1",insertBeforeText=SENT(narration()[ci-1])[0],sentences=[],provisional=v.get("provisional",False),
                         note=f"章节卡静音 {CARD} 帧（{CARD/30:.2f} s），插在 ch{ci}-1 句首之前（上一章章间停顿之后）")
        res[k]=v
    return res
