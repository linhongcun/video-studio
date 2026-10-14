# EP.09 消息队列 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用
ids=["hook","sync","async","peak","producer","recap"]
SPLIT={"hook":[2,3],"sync":[3,2],"async":[2,2],"peak":[3,2],"producer":[2,2],"recap":[2,1]}
SCRIPT='/workspace/sorkin-backup/message-queue/script.md'
HOLDS={"producer-1":24}  # 2026-10-14：导演定标签只调出现时机、不加 hold（30 已撤回，改由 _audit/labelfix.py 提前淡入）
#  # 打记号动画收尾需要约 0.8 秒画面停留（「记号」在句中偏后；2026-10-14 前为「划掉」）；Knoll timing 已含则不重复加
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
