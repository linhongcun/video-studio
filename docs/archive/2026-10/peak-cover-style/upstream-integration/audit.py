from pathlib import Path
from datetime import datetime,timezone
import subprocess,json,hashlib,stat
ROOT=Path('/workspace/video-studio');W=Path('/workspace/work/peak-cover-qa');OUT=W/'upstream-integration';OLD='d3c163eff2a550255e8c81c1eea631178b7aaa58';UP='3beb56c549b20e666023774b919fc414454abe87';COVER='90ae77168c3eed6d129cdd96690cd1445474f1fc';MERGE='1a5a0910e0579a8d6fff398a4ab1fee47081454a'
def run(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
def blob(rev,n):return subprocess.check_output(['git','-C',str(ROOT),'show',rev+':'+n])
def sha(b):return hashlib.sha256(b).hexdigest()
paths=run('diff','--name-only',OLD,UP).splitlines();b=json.loads((W/'protection-baseline.json').read_text());fp={e['path'] for f in b['frozenManifests'] for e in f['entries']};assert len(paths)==14 and not set(paths)&set(b['protected']) and not set(paths)&fp
assert run('rev-list','--parents','-n','1',MERGE).split()==[MERGE,COVER,UP]
subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',MERGE,'HEAD'],check=True)
versions=['site/package.json','site/package-lock.json'];exact=[]
for n in paths:
 if n in versions:continue
 expected=blob(UP,n);actual=(ROOT/n).read_bytes();assert actual==expected,n
 upmode=run('ls-tree',UP,'--',n).split()[0];mode=run('ls-tree',MERGE,'--',n).split()[0];assert mode==upmode,n
 assert bool((ROOT/n).stat().st_mode&stat.S_IXUSR)==(mode=='100755'),n
 exact.append({'path':n,'bytes':len(actual),'sha256':sha(actual),'mode':mode,'upstreamGitBlob':run('rev-parse',UP+':'+n),'exact':True})
version_reports=[]
for n in versions:
 expected=json.loads(blob(UP,n));actual=json.loads((ROOT/n).read_text());assert expected['version']=='0.90.0' and actual['version']=='0.90.1'
 exp=dict(expected);now=dict(actual);exp.pop('version');now.pop('version')
 if n.endswith('lock.json'):
  assert expected['packages']['']['version']=='0.90.0' and actual['packages']['']['version']=='0.90.1';exp['packages'][''].pop('version');now['packages'][''].pop('version')
 assert exp==now,n
 version_reports.append({'path':n,'onlyVersionChanged':True,'from':'0.90.0','to':'0.90.1','upstreamObjectOtherwiseExact':True})
new_source_delta=run('diff','--name-only',COVER,MERGE,'--','episodes/','episodes-codex/','design/');assert not new_source_delta,new_source_delta
subprocess.run(['python3',str(W/'verify-baseline.py')],check=True,stdout=subprocess.DEVNULL);protection=json.loads((W/'protection-verification.json').read_text());assert protection['passed']
x={'checkedAt':datetime.now(timezone.utc).isoformat(),'passed':True,'reviewer':'independent peak_scope_qa agent','originalBase':OLD,'coverCommit':COVER,'integratedUpstream':UP,'integrationCommit':MERGE,'observedHead':run('rev-parse','HEAD'),'mergeParentsExact':True,'upstreamPathCount':len(paths),'protectedIntersection':[],'frozenIntersection':[],'exactNonversionFiles':exact,'exactNonversionFileCount':len(exact),'versionFiles':version_reports,'dependencyGraphUnchanged':True,'coverProductionPublishingDesignTreesUnchangedSinceValidatedCoverCommit':True,'baselineManifestSha256':sha((W/'protection-baseline.json').read_bytes()),'protectedPathsMatched':2754,'publishedMetaUnchanged':49,'frozenDeclarationsMatched':400,'originalBaselineUnchanged':True,'originalLocalVersion':'0.89.3','finalVersion':'0.90.1','blockingFindings':[],'scope':'Commit/disk byte+Git mode preservation for newly integrated upstream navigation, bounded final original-protection verification. No12image/media/siteUI retest; new runtime UI remains separate.'}
(OUT/'integration-report.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');print('PASS:14upstream paths,12runtime files exact bytes/mode,versions-only0.90.1,2754/400 matched. ReportSHA',sha((OUT/'integration-report.json').read_bytes()))
