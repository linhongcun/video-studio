# EP.06 负载均衡 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用
ids=["queue","spof","solution","methods","health","recap"]
SPLIT={"queue":[2,2],"spof":[1,2],"solution":[1,2],"methods":[3,2],"health":[3,2],"recap":[1,2]}
SCRIPT='/workspace/sorkin-backup/load-balancing/script.md'
# extraHold：纯画面停留（镜头末尾，语音之后）。本期暂无
HOLDS={"spof-1":30}  # Nolan：spof-1 末尾 +30 帧
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue  # Knoll 的 timing 已含 hold（ep6-timing.json 会含 spof-1 +30）：不重复加
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
