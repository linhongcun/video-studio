from pathlib import Path
import json,hashlib,subprocess
from datetime import datetime,timezone
R=Path('/workspace/video-studio');W=Path('/workspace/work/redis-cover-qa');D=W/'upstream-integration'
BASE='2b418a9da0155fb29357c186238ed78feab0b8ed';UP='a442ab1c8d67aa1e2df12dfe4aeac782d2fcd120';COVER='edcf720e00e2fb11af559356c24368acab3fc157';MERGE='16e2576f581896e6c8215df7d3bd53f94cf974b7'
def git(*args):return subprocess.check_output(['git','-C',str(R),*args])
def raw(ref,path):return git('show',f'{ref}:{path}')
def h(data):return hashlib.sha256(data).hexdigest()
paths=git('diff','--name-only','-z',BASE,UP).decode().strip('\0').split('\0');assert len(paths)==24
b=json.loads((W/'protection-baseline.json').read_text());protected=set(b['protected']);frozen={x['path'] for m in b['redisFreezeManifests'] for x in m['rows']}
intersections={'originalProtected':sorted(protected.intersection(paths)),'redisFrozen':sorted(frozen.intersection(paths))};assert not any(intersections.values())
rows=[];overlap={'docs/archive/README.md','site/package.json','site/package-lock.json'}
for p in paths:
 expected=raw(UP,p);line=git('ls-tree',UP,'--',p).decode().strip();mode,kind,blob=line.split('\t')[0].split(' ');actual=(R/p).read_bytes()
 exact=p not in overlap
 if exact:
  assert actual==expected,p
  assert raw(MERGE,p)==expected,p
  assert git('ls-tree',MERGE,'--',p).decode().strip().split('\t')[0].split(' ')[0]==mode,p
 rows.append({'path':p,'upstreamGitBlob':blob,'mode':mode,'upstreamSha256':h(expected),'integratedWorkingSha256':h(actual),'exactRequired':exact,'exact':actual==expected})
for ref in [COVER,UP]:assert git('merge-base','--is-ancestor',ref,MERGE)==b''
parents=git('show','-s','--format=%P',MERGE).decode().split();assert parents==[COVER,UP]
semantic=[]
p='docs/archive/README.md';final=(R/p).read_text()
for ref,label in [(COVER,'Redis cover parent index'),(UP,'new distributed upstream index')]:
 lines={x for x in raw(ref,p).decode().splitlines() if x.strip()}
 assert lines<=set(final.splitlines());semantic.append({'path':p,'check':label+' all nonempty lines preserved','passed':True})
for p in ['site/package.json','site/package-lock.json']:
 actual=json.loads((R/p).read_text());up=json.loads(raw(UP,p));assert actual['version']=='0.86.1'
 actual['version']=up['version']
 if p.endswith('lock.json'):
  assert actual['packages']['']['version']=='0.86.1';actual['packages']['']['version']=up['packages']['']['version']
 assert actual==up,p
 semantic.append({'path':p,'check':'Exactly full upstream JSON except version fields0.86.1; dependency graph unchanged','passed':True})
source=(R/'site/src/lib/learning.ts').read_text();series=json.loads((R/'site/src/content/series.json').read_text())
assert "seriesIds: ['request', 'cache', 'peak']" in source
assert "id: 'distributed'" in source and "seriesIds: ['distributed']" in source
assert "id: 'redis'" in source and "seriesIds: ['redis']" in source
assert series['distributed']['crossSeriesNavigation'] is False and series['distributed']['order']==14
assert series['redis']['crossSeriesNavigation'] is False
semantic += [{'path':'site/src/lib/learning.ts','check':'Distributed standalone track retained, removed from systems membership; Redis standalone entry retained','passed':True},{'path':'site/src/content/series.json','check':'Distributed crossSeriesNavigation=false/order14 and Redis standalone metadata retained','passed':True}]
subprocess.run(['python',str(W/'verify-baseline.py')],check=True,cwd=R,stdout=subprocess.DEVNULL)
pr=json.loads((W/'protection-verification.json').read_text());assert pr['passed']
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'independent redis_scope_qa agent','passed':True,'baseSha':BASE,'upstreamSha':UP,'coverParentSha':COVER,'mergeSha':MERGE,'exactMergeParents':parents,'baselineSha256':h((W/'protection-baseline.json').read_bytes()),'upstreamPathCount':len(paths),'intersections':intersections,'upstreamPaths':rows,'exactNonOverlappingUpstreamFiles':sum(x['exactRequired'] for x in rows),'semanticChecks':semantic,'protectedPathsStillOriginal':pr['protectedPaths'],'redisFreezeDeclarations':436,'all436FrozenDeclarationsMatch':all(x['matches']==x['declarations'] for x in pr['redisFreezeManifests']),'originalBaselineUnchanged':True,'legitimateProtectedDelta':[],'newVersion':'0.86.1','limits':['Readonly Git/working bytes and source semantics; does not replace parent site build or UI smoke.','No baseline rewrite or repo/git/issue mutations by reviewer.']}
(D/'integration-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['passed','mergeSha','upstreamPathCount','exactNonOverlappingUpstreamFiles','intersections','protectedPathsStillOriginal','redisFreezeDeclarations','newVersion']},ensure_ascii=False,indent=2));print('reportSha256',h((D/'integration-report.json').read_bytes()))
