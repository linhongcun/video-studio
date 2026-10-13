# EP.11 幂等 镜头拆分（按句数，句子不拆开）——make_timing / map_timing / gen / validate 共用；章节 id 用 Sorkin 建议的（文章锚点）
ids=["hook","duplicate","ticket","unique-id","retry","recap"]
SPLIT={"hook":[3,2],"duplicate":[3,2],"ticket":[2,2],"unique-id":[3,2],"retry":[2,2],"recap":[2,1]}
SCRIPT='/workspace/sorkin-backup/idempotency/script.md'
HOLDS={"ticket-2":14}  # 「就叫幂等。」后音频实测只剩 10 帧 → 分镜加 14 帧停留到 24（Knoll timing 不含；已有 extraHold/origDuration/holdIncluded 则不重复加）
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
