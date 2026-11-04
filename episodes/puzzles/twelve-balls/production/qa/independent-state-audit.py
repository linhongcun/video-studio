#!/usr/bin/env python3
"""Audit actual rendered P06 DOM states; reads production and writes a new QA report only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
D=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def ids(s):return [int(x) for x in s.split(',') if x]
def cases(s):return [x for x in s.split(',') if x]
def ball(c):return int(c[:-1])
def main():
 p=argparse.ArgumentParser();p.add_argument('--preview',required=True);p.add_argument('--out-name',required=True);a=p.parse_args()
 preview=D/'qa'/f'{a.preview}.json';out=D/'qa'/f'{a.out_name}.json';assert not out.exists(),'Preserve old QA result'
 r=read(preview);model=read(D/'model-data.json');nodes={n['prefix']:n for n in model['nodes']};allids=list(range(1,13));checks=[];failures=[]
 def check(ok,kind,frame,detail=None):
  row={'frame':frame,'kind':kind,'pass':bool(ok)}
  if detail is not None:row['detail']=detail
  checks.append(row)
  if not ok:failures.append(row)
 for sample in r['samples']:
  f=sample['frame'];q=int(sample['shot']);states=sample['metrics']['states'];attrs=[s['attrs'] for s in states]
  bs=[s for s in attrs if 'data-ball' in s];groups=[s for s in attrs if 'data-current-candidates' in s];nav=next((s for s in attrs if 'data-navigation-prefix' in s),None)
  if bs:
   check(sorted(int(b['data-ball']) for b in bs)==allids,'twelve-physical-entities',f)
   check(len(groups)==1,'one-current-candidate-set',f)
   if len(groups)!=1:continue
   cs=cases(groups[0]['data-current-candidates']);normal=ids(groups[0]['data-known-normal']);expectedNormal=[i for i in allids if all(ball(c)!=i for c in cs)]
   check(normal==expectedNormal,'normal-inferred-only-from-current-candidates',f,{'normal':normal,'candidates':cs})
   prefix=nav['data-navigation-prefix'] if nav else ''
   expected=nodes[prefix]['candidates'] if prefix in nodes else [t['answer'] for t in model['traces'] if t['path']==prefix]
   if q==3 and prefix:expected=nodes['']['partitions'][prefix]
   check(cs==expected,'candidates-match-branch-prefix',f,{'prefix':prefix,'candidates':cs,'expected':expected})
   for b in bs:
    i=int(b['data-ball']);own=[c for c in cs if ball(c)==i]
    check(cases(b['data-candidates'])==own,'ball-hypotheses-stay-with-identity',f,{'ball':i})
    check((b['data-ball-normal']=='true')==(i in normal),'ball-normal-label-matches-inference',f,{'ball':i})
    if b['data-ball-confirmed']=='true':check(len(cs)==1 and i==ball(cs[0]) and q in [8,11,14],'confirmation-only-after-final-result',f,{'ball':i,'candidates':cs})
  for b in attrs:
   if 'data-left-balls' not in b:continue
   left,right=ids(b['data-left-balls']),ids(b['data-right-balls'])
   check(len(set(left+right))==len(left+right) and all(x in allids for x in left+right),'one-physical-ball-on-at-most-one-side',f,{'left':left,'right':right})
   check(len(left)==len(right) or b['data-construction-only']=='true','equal-pan-count-or-explicit-construction',f,{'left':left,'right':right,'construction':b['data-construction-only']})
   if q==6:check(b['data-construction-only']=='true','incomplete-three-v-two-never-executed',f)
  if nav:
   used=nav['data-actual-weighings']
   check(used=='hypothetical' or 0<=int(used)<=3,'at-most-three-actual-weighings',f)
   if q in [9,10,11,12,13,14]:check(used=='hypothetical','alternate-paths-do-not-increment-main-count',f)
   if q in [5,6,7]:check(used=='1','construction-does-not-submit-weighing',f)
   if q==8:
    prefix=nav['data-navigation-prefix'];check(used=={'L':'1','LL':'2','LLB':'3'}[prefix],'main-count-updates-with-observed-result',f)
  for g in attrs:
   if 'data-results-for-prefix' in g:check(g['data-result-kind'] in ['candidate-predictions','last-weighing-predictions'],'predictions-not-an-actual-path',f)
  check(sample['metrics']['subtitles']==0,'actual-unsubtitled-preview',f)
  check(not sample['violations'],'rendered-geometry-invariant',f,sample['violations'])
 result={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'executor':'Codex independent rendered-state audit','preview':str(preview.relative_to(D)),'previewSHA256':sha(preview),'modelSHA256':sha(D/'model-data.json'),'samples':len(r['samples']),'checks':len(checks),'passed':not failures,'failures':failures,'rows':checks,'scope':'Actual rendered DOM identities, candidate/normal inference, branch restoration and count invariants; visual motion and semantic narration remain separate reviews.'}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['rows']},ensure_ascii=False))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()
