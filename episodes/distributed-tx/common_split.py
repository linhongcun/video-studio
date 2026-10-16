# EP.21 分布式事务（脚本 v0.26.0 v4 分界返工：26 章 + 四张章节卡）镜头拆分：按句数，句子不拆开。章节 id = script.md「## n. id｜」
import re,os
ids=["hook","signal","local","pc-open","pc-prepare","pc-commit","pc-cost","pc-wrap","tcc-open","tcc-try","tcc-confirm","tcc-cost","tcc-wrap","saga-open","saga-do","saga-compensate","saga-cost","saga-wrap","msg-open","msg-half","msg-check","msg-deliver","msg-cost","msg-wrap","eventual","recap"]
SPLIT={"hook":[3],"signal":[1,1],"local":[1,1],"pc-open":[2],"pc-prepare":[1,1],"pc-commit":[1],"pc-cost":[2],"pc-wrap":[1],"tcc-open":[2],"tcc-try":[1],"tcc-confirm":[1,1],"tcc-cost":[1],"tcc-wrap":[1],"saga-open":[2],"saga-do":[2],"saga-compensate":[1,1],"saga-cost":[1,1],"saga-wrap":[1],"msg-open":[2],"msg-half":[1,1],"msg-check":[2],"msg-deliver":[1,1],"msg-cost":[1],"msg-wrap":[1],"eventual":[1],"recap":[1,1]}
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

# v4 章节卡：每种实现前一张独立章节卡（无旁白，Knoll 在配音里插同长静音）。卡长 CARD 帧：名字 0→4 帧淡入，完整显示到转场（crossfade 4）开始 = 70 帧 ≥69
CARD=78
CARDS={"pc-open":("card-1","第一种 · 两阶段提交","#E8B53A"),"tcc-open":("card-2","第二种 · 预留确认取消","#2FA38A"),"saga-open":("card-3","第三种 · 补偿事务","#8E6BBF"),"msg-open":("card-4","第四种 · 可靠消息","#C9733A")}
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
