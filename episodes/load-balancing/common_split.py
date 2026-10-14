# EP.06 负载均衡 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用
ids=["queue","spof","solution","methods","health","recap"]
SPLIT={"queue":[2,2],"spof":[1,2],"solution":[1,2],"methods":[3,2],"health":[3,2],"recap":[1,2]}
SCRIPT='/workspace/sorkin-backup/load-balancing/script.md'
# extraHold：纯画面停留（镜头末尾，语音之后）。本期暂无
HOLDS={"spof-1":30}  # Nolan：spof-1 末尾 +30 帧
def _label_holds():  # 2026-10-14 Nolan：术语标签不得早于旁白，不够 60 帧时由 _audit/labelfix.py 算出最短 hold 写进 label_holds.json（镜头末尾静音，Knoll 同步插静音）
    import json as _j,os as _o
    p=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'label_holds.json')
    return _j.load(open(p)) if _o.path.isfile(p) else {}
def apply_holds(out):
    LH=_label_holds()
    for sid in list(HOLDS)+[x for x in LH if x not in HOLDS]:
        v=out[sid]
        if v.get("holdIncluded"): continue
        h=HOLDS.get(sid,0); h0=v.get("extraHold",0) if "origDuration" in v else 0   # Knoll timing 已含旧 hold 时只补差额
        lh=LH.get(sid,0); add=max(0,h-h0)+lh
        if not add: continue
        v.setdefault("origDuration",v["duration"]); v.setdefault("holdAt",v["origDuration"])
        v["duration"]+=add; v["extraHold"]=max(h,h0)+lh; v["labelHold"]=lh
    return out
