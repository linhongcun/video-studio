import itertools,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from solution import Solution
from course_schedule_trace import trace
def has_cycle(num,edges):
 g={c:set() for c in range(num)}
 for a,b in edges:g[b].add(a)
 state={}
 def visit(u):
  state[u]=1
  for v in g[u]:
   if state.get(v)==1:return True
   if state.get(v,0)==0 and visit(v):return True
  state[u]=2
  return False
 return any(visit(c) for c in range(num) if state.get(c,0)==0)
class TestCourseSchedule(unittest.TestCase):
 def check(self,num,edges):
  edges=[list(e) for e in edges]
  want=not has_cycle(num,edges)
  self.assertEqual(Solution().canFinish(num,[list(e) for e in edges]),want,edges)
  run=trace(num,edges)
  self.assertEqual(run['result'],want,edges)
  self.assertEqual(len(run['events'][-1]['done']),num if want else num-len(run['events'][-1]['remaining']))
  learned=set()
  q=[]
  for e in run['events']:
   if e['kind']=='enqueue':
    self.assertEqual(e['indegrees'][e['node']],0,e)
    q.append(e['node'])
   if e['kind']=='release' and e['entered']:
    self.assertEqual(e['indegrees'][e['to']],0,e)
   if e['kind']=='learn':
    learned.add(e['node'])
    self.assertNotIn(e['node'],e['queue'],e)
   if e['kind']=='blocked':
    self.assertTrue(all(e['indegrees'][c]>0 for c in e['remaining']),e)
 def test_official_and_edges(self):
  for num,edges in [(2,[[1,0]]),(2,[[1,0],[0,1]]),(4,[[1,0],[2,0],[3,1],[3,2]]),
                    (4,[[1,0],[2,1],[3,2],[1,3]]),(4,[]),(1,[]),(5,[[1,4],[2,4],[3,1],[3,2]]),
                    (3,[[0,1],[0,2],[1,2]]),(3,[[1,0],[1,2],[0,1]])]:
   self.check(num,edges)
 def test_exhaustive_small(self):
  for num in (1,2,3):
   pairs=[[a,b] for a in range(num) for b in range(num) if a!=b]
   for k in range(0,4):
    for combo in itertools.combinations(pairs,k):
     self.check(num,combo)
   for combo in itertools.product(pairs,repeat=2):
    self.check(num,combo)
if __name__=='__main__':unittest.main()
