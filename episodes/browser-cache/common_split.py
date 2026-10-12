# EP.07 浏览器缓存 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用
ids=["hook","first","second","freshness","revalidate","recap"]
SPLIT={"hook":[1,2],"first":[1,2],"second":[1,2],"freshness":[3,2],"revalidate":[3,2],"recap":[1,2]}
SCRIPT='/workspace/sorkin-backup/browser-cache/script.md'
HOLDS={}  # extraHold（镜头末尾纯画面停留）；本期暂无。Knoll timing 已含则不重复加
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
