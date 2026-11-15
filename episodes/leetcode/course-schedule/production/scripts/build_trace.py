import json,sys
from pathlib import Path
EP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(EP))
from course_schedule_trace import trace
data={'label':'官方示例与明确标注的教学补例',
 'main':trace(4,[[1,0],[2,0],[3,1],[3,2]]),
 'cycle':trace(4,[[1,0],[2,1],[3,2],[1,3]]),
 'twoCycle':trace(2,[[1,0],[0,1]]),
 'empty':trace(4,[]),
 'isolated':trace(4,[[1,0]])}
(EP/'trace/main-example.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
for name,run in data.items():
 if not isinstance(run,dict):continue
 print(name,run['result'])
 for i,e in enumerate(run['events']):print(i,e['kind'],e.get('from'),e.get('to'),e.get('node'),e['indegrees'],e.get('queue'),e.get('done'))
