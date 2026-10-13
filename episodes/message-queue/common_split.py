# EP.09 消息队列 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用
ids=["hook","sync","async","peak","producer","recap"]
SPLIT={"hook":[2,3],"sync":[3,2],"async":[2,2],"peak":[3,2],"producer":[2,2],"recap":[2,1]}
SCRIPT='/workspace/sorkin-backup/message-queue/script.md'
HOLDS={"producer-1":24}  # 划掉动画收尾需要约 0.8 秒画面停留（「划掉」在句末）；Knoll timing 已含则不重复加
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]
        if "extraHold" in v or "origDuration" in v or v.get("holdIncluded"): continue
        v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
