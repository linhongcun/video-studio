import json,sys
from pathlib import Path
EP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(EP))
from three_sum_trace import trace
data={'label':'官方示例1与明确标注的补充示例','main':trace([-1,0,1,2,-1,-4]),
      'duplicates':trace([-2,0,0,2,2]),'zeros':trace([0,0,0]),'none':trace([0,1,1])}
(EP/'trace/main-example.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
for name,run in data.items():
 if isinstance(run,dict):
  print(name,run['result'])
  for i,e in enumerate(run['events']):print(i,e['kind'],e['i'],e['l'],e['r'],e['total'],e.get('nextL',e.get('nextR','')))
