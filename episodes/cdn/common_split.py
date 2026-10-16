# EP.05 CDN 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用
ids=["why","origin","edge","dns","miss","recap"]
SPLIT={"why":[1,2],"origin":[2,2],"edge":[2,3],"dns":[2,2],"miss":[2,1,2],"recap":[2,2]}
import os as _os;SCRIPT=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'script.md')
# extraHold：纯画面停留（镜头末尾，语音之后），与 timing 来源无关；暂定和实测 timing 都加
HOLDS={"miss-2":30}
def apply_holds(out,label_only=False):
    import json as _j
    _p=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'label_holds.json')
    LH=_j.load(open(_p)) if _os.path.isfile(_p) else {}   # 2026-10-16 stock-qa（Nolan 定）：术语标签最短 hold（_audit/labelfix.py → label_holds.json），镜头末尾静音
    for sid in (set(LH) if label_only else set(HOLDS)|set(LH)):
        h=(0 if label_only else HOLDS.get(sid,0))+LH.get(sid,0); v=out[sid]
        if label_only and 'extraHold' in v: v['duration']+=h; v['extraHold']+=h; v['labelHold']=LH[sid]; continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
        if sid in LH: v["labelHold"]=LH[sid]
    return out
