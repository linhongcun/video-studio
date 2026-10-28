from pathlib import Path
import subprocess,json,hashlib,datetime,argparse,collections
REPO=Path('/workspace/video-studio');OUT=Path('/workspace/work/kafka-upstream-integration')
BASE='d7a5d7682080232617a03cc988b7c25cb50446f4';UP='3b0ac58f8f86bb7a755107ec28c69bde6cdc0c6e';KAFKA='986ad9f9'
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
def blob(p):
 if not p.exists():return None
 h=hashlib.sha1();h.update(('blob '+str(p.stat().st_size)+'\0').encode())
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
def paths(a,b):return git('diff','--name-only',a+'..'+b).decode().splitlines()
def tree(commit):
 result={}
 for row in git('ls-tree','-r','-z',commit).split(b'\0'):
  if not row:continue
  header,p=row.split(b'\t',1);mode,kind,oid=header.decode().split();result[p.decode()]={'mode':mode,'kind':kind,'gitBlob':oid}
 return result
def prepare():
 kafka=git('rev-parse',KAFKA).decode().strip();changed=paths(BASE,UP);local=paths(BASE,kafka);overlap=sorted(set(changed)&set(local));ut=tree(UP);bt=tree(BASE)
 manifestPaths=['episodes-codex/message-queue/revisions/kafka-intro/message-queue/source-sha256.json','episodes-codex/message-queue/source-sha256.json','episodes-codex/message-queue/revisions/mq-intro/message-queue/source-sha256.json'];freezes=[]
 for name in manifestPaths:
  p=REPO/name;r=json.loads(p.read_text());resolved={str((p.parent/q).resolve().relative_to(REPO)) for q in r};freezes.append({'manifest':name,'manifestSha256':sha(p),'declarations':len(r),'uniqueResolvedPaths':len(resolved),'upstreamIntersection':sorted(set(changed)&resolved)})
 pure=sorted(set(changed)-set(overlap));delta=[]
 for p in pure:
  delta.append({'path':p,'base':bt.get(p),'upstream':ut.get(p),'expectation':'Must equal exact upstream blob/mode, or remain absent if upstream deleted.'})
 pbase=REPO/'not-used';baseline=Path('/workspace/work/mq-cover-qa/kafka-scope-baseline.json');br=json.loads(baseline.read_text());protected=br['protectedFiles'];protectPaths=set(protected) if isinstance(protected,dict) else {x['path'] for x in protected}
 supplement=Path('/workspace/work/mq-cover-qa/kafka-scope-authorized-supplement.json');extra=set(json.loads(supplement.read_text())['additionalAuthorizedReplacementFiles']);effectiveProtectPaths=protectPaths-extra
 report={'schemaVersion':1,'preparedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':BASE,'upstream':UP,'kafkaCommit':kafka,'upstreamPathCount':len(changed),'kafkaChangedPathCount':len(local),'overlappingPaths':overlap,'pureUpstreamPathCount':len(pure),'freezeIntersectionAudit':freezes,'originalKafkaScopeBaselineSha256':sha(baseline),'originalKafkaScopeProtectedPaths':len(protectPaths),'effectiveProtectedPathsAfterExistingSupplement':len(effectiveProtectPaths),'originalAuthorizedSupplementSha256':sha(supplement),'upstreamTouchesPriorProtectedPaths':sorted(set(changed)&protectPaths),'expectedPureUpstreamFiles':delta,'upstreamAllChangedPaths':changed,'siteChangedPaths':[p for p in changed if p.startswith('site/')],'source':{'method':'Read-only pinned Git object diffs and frozen manifest resolution; no index or working-tree mutation. Old preservation baseline is preserved, not rewritten.'}}
 (OUT/'upstream-delta.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'upstreamPaths':len(changed),'localKafkaPaths':len(local),'pureUpstream':len(pure),'overlappingPaths':overlap,'freezeIntersections':[x['upstreamIntersection'] for x in freezes],'priorProtectedTouched':len(report['upstreamTouchesPriorProtectedPaths'])}))
def verify():
 r=json.loads((OUT/'upstream-delta.json').read_text());checks=[]
 for item in r['expectedPureUpstreamFiles']:
  p=REPO/item['path'];u=item['upstream'];actual=blob(p);mode=('120000' if p.is_symlink() else '100755' if p.stat().st_mode&0o111 else '100644') if p.exists() else None;checks.append({'path':item['path'],'expectedGitBlob':u['gitBlob'] if u else None,'actualGitBlob':actual,'expectedMode':u['mode'] if u else None,'actualMode':mode,'passed':actual==(u['gitBlob'] if u else None) and mode==(u['mode'] if u else None),'sha256':sha(p) if p.exists() else None})
 baseline=Path('/workspace/work/mq-cover-qa/kafka-scope-baseline.json');baselineUnchanged=sha(baseline)==r['originalKafkaScopeBaselineSha256'];freezeChecks=[]
 for f in r['freezeIntersectionAudit']:
  p=REPO/f['manifest'];freezeChecks.append({'manifest':f['manifest'],'sha256':sha(p),'expectedSha256':f['manifestSha256'],'passed':sha(p)==f['manifestSha256']})
 integrated=subprocess.run(['git','merge-base','--is-ancestor',UP,'HEAD'],cwd=REPO).returncode==0
 v={'schemaVersion':1,'integratedHeadIncludesUpstream':integrated,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'currentHead':git('rev-parse','HEAD').decode().strip(),'pinnedUpstream':UP,'expectedPlanSha256':sha(OUT/'upstream-delta.json'),'pureUpstreamFileCount':len(checks),'pureUpstreamPassed':all(x['passed'] for x in checks),'checks':checks,'failed':[x['path'] for x in checks if not x['passed']],'oldBaselineUnchanged':baselineUnchanged,'freezeManifestIdentityChecks':freezeChecks,'passed':integrated and all(x['passed'] for x in checks) and baselineUnchanged and all(x['passed'] for x in freezeChecks),'scope':'Only pure upstream paths, original baseline bytes and freeze-manifest identity. Overlapping policy/site files require separate semantic preservation review.'}
 (OUT/'upstream-preservation-verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v[k] for k in ['currentHead','pureUpstreamFileCount','pureUpstreamPassed','failed','oldBaselineUnchanged','passed']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args();verify() if a.verify else prepare()
