import itertools,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from solution import Solution
from three_sum_trace import trace
def oracle(a):
 return {tuple(sorted(t)) for t in itertools.combinations(a,3) if sum(t)==0}
class TestThreeSum(unittest.TestCase):
 def check(self,a):
  result=Solution().threeSum(a);run=trace(a);want=oracle(a)
  self.assertEqual({tuple(t) for t in result},want,a)
  self.assertEqual(len(result),len(want),a)
  self.assertEqual(run['result'],result,a)
  for e in run['events']:
   if e['kind'] in ('hit','low','high'):
    self.assertTrue(e['i']<e['l']<e['r'],e)
    self.assertEqual(e['total'],sum(run['sorted'][j] for j in (e['i'],e['l'],e['r'])))
   if e['kind']=='low':
    self.assertTrue(all(run['sorted'][e['i']]+run['sorted'][e['l']]+run['sorted'][k]<0 for k in range(e['l']+1,e['r']+1)))
   if e['kind']=='high':
    self.assertTrue(all(run['sorted'][e['i']]+run['sorted'][k]+run['sorted'][e['r']]>0 for k in range(e['l'],e['r'])))
 def test_official_and_edges(self):
  for a in [[-1,0,1,2,-1,-4],[0,1,1],[0,0,0],[0]*7,[-2,0,0,2,2],[-2,-2,0,0,2,2],[-5,-4,-3],[1,2,3],[-100000,0,100000]]:
   self.check(a)
 def test_exhaustive_multisets(self):
  for n in range(3,9):
   for a in itertools.combinations_with_replacement(range(-3,4),n):self.check(list(a))
if __name__=='__main__':unittest.main()
