# EP.05 CDN 镜头拆分（按句数）——make_timing / map_timing / gen / validate 共用
ids=["why","origin","edge","dns","miss","recap"]
SPLIT={"why":[1,2],"origin":[2,2],"edge":[2,3],"dns":[2,2],"miss":[2,1,2],"recap":[2,2]}
SCRIPT='/workspace/sorkin-backup/cdn/script.md'
# extraHold：纯画面停留（镜头末尾，语音之后），与 timing 来源无关；暂定和实测 timing 都加
HOLDS={"miss-2":30}
def apply_holds(out):
    for sid,h in HOLDS.items():
        v=out[sid]; v["origDuration"]=v["duration"]; v["duration"]+=h; v["extraHold"]=h; v["holdAt"]=v["origDuration"]
    return out
