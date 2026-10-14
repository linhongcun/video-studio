# EP.10 限流 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用；章节 id 用 Sorkin 建议的（文章锚点）
ids=["hook","no-limit","limit","token-bucket","breaker","recap"]
SPLIT={"hook":[3,2],"no-limit":[2,1],"limit":[3,2],"token-bucket":[3,2],"breaker":[2,1],"recap":[2,1]}
SCRIPT='/workspace/sorkin-backup/rate-limit/script.md'
HOLDS={"breaker-2":14}  # 2026-10-14：导演定不再加 hold（limit-1 +50 / breaker-1 +53 已撤回，改由 _audit/labelfix.py 提前淡入）
#  # 「降级」在句尾只剩 10 帧 → 分镜加 14 帧停留到 24（Knoll timing 不含；已有 extraHold/origDuration 则不重复加）
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
