# EP.14 数据库索引（脚本 v0.19.0）镜头拆分（按句数，句子不拆开）——make_timing / map_timing / gen / validate 共用；章节 id = article.mdx 锚点
ids=["hook","scan","index","btree","more","recap"]
SPLIT={"hook":[2,2],"scan":[2,2],"index":[2,2],"btree":[2,2],"more":[3,2],"recap":[1,1]}
SCRIPT='/workspace/sorkin-backup/db-index/script.md'
# pronunciation.md：配音文本「B+树」写「B 加树」（只改送 TTS 的文字；字幕/标签写「B+ 树」）
TTS={"B+树":"B 加树"}
SUB={"B+树":"B+ 树"}   # 字幕显示写法
def tts(s):
    for a,b in TTS.items(): s=s.replace(a,b)
    return s
def subtext(s):
    for a,b in SUB.items(): s=s.replace(a,b)
    return s
HOLDS={}   # 设计 hold：无。标签 hold 只由 _audit/labelfix.py 按需算（label_holds.json）
def _label_holds():
    import json as _j,os as _o
    p=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'label_holds.json')
    return _j.load(open(p)) if _o.path.isfile(p) else {}
def apply_holds(out):
    LH=_label_holds()
    for sid,lh in LH.items():
        v=out[sid]
        if v.get("holdIncluded") or not lh: continue
        v.setdefault("origDuration",v["duration"]); v.setdefault("holdAt",v["origDuration"])
        v["duration"]=v["origDuration"]+lh; v["extraHold"]=lh; v["labelHold"]=lh
    return out
