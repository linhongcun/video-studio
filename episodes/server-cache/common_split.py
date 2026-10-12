# EP.08 服务端缓存 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用
ids=["hook","no-cache","hit-miss","ttl","invalidate","recap"]
SPLIT={"hook":[2,2],"no-cache":[2,2],"hit-miss":[2,2],"ttl":[1,2],"invalidate":[2,2],"recap":[1,2]}
SCRIPT='/workspace/sorkin-backup/server-cache/script.md'
HOLDS={}  # extraHold（镜头末尾纯画面停留）；本期暂无。Knoll timing 已含则不重复加
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
