# EP.10 限流 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用；章节 id 用 Sorkin 建议的（文章锚点）
ids=["hook","no-limit","limit","token-bucket","breaker","recap"]
SPLIT={"hook":[3,2],"no-limit":[2,1],"limit":[3,2],"token-bucket":[3,2],"breaker":[2,1],"recap":[2,1]}
SCRIPT='/workspace/sorkin-backup/rate-limit/script.md'
HOLDS={"breaker-2":14}  # 「降级」在句尾只剩 10 帧 → 分镜加 14 帧停留到 24（Knoll timing 不含；已有 extraHold/origDuration 则不重复加）
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
