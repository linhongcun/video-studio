# 本期镜头拆分（按句数）——make_timing / map_timing / gen 共用
ids=["stateless","set-cookie","send","session","protect","recap"]
SPLIT={"stateless":[3,2],"set-cookie":[3],"send":[2,2],"session":[2,2],"protect":[2,1],"recap":[1,1]}
import os as _os;SCRIPT=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'script.md')
