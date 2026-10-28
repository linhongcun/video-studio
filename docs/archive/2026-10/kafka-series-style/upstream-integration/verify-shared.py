from pathlib import Path
import subprocess,json,re,hashlib,datetime
R=Path('/workspace/video-studio');W=Path('/workspace/work/kafka-upstream-integration');UP='3b0ac58f8f86bb7a755107ec28c69bde6cdc0c6e';K='986ad9f9086f3cd04a901239e454688e0688df3b'
def show(ref,p):return subprocess.check_output(['git','show',ref+':'+p],cwd=R,text=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
def gitblob(p):
 if not p.exists():return None
 h=hashlib.sha1();h.update(('blob '+str(p.stat().st_size)+'\0').encode())
 with p.open('rb') as f:
  while q:=f.read(1048576):h.update(q)
 return h.hexdigest()
checks=[]
def ck(n,ok,detail=''):checks.append({'name':n,'passed':bool(ok),'detail':detail})
for file in ['docs/archive/README.md','docs/lessons-learned.md','docs/production-memory.md','docs/render.md','docs/successful-practices.md']:
 diff=subprocess.check_output(['git','diff','--unified=0','d7a5d7682080232617a03cc988b7c25cb50446f4..'+UP,'--',file],cwd=R,text=True);added=[l[1:] for l in diff.splitlines() if l.startswith('+') and not l.startswith('+++') and l[1:].strip()];c=(R/file).read_text();ck(file+' upstream MySQL evidence retained',all(l in c for l in added),str(len(added))+'nonempty lines')
u=show(UP,'docs/RULES.md');c=(R/'docs/RULES.md').read_text();ck('RULES MySQL scope paragraph retained',next(l for l in u.splitlines() if l.startswith('- 数据库学习方向当前统一显示为MySQL')) in c);ck('RULES both MySQL and Kafka cover entries retained','_shared/mysql-covers/README.md' in c and '_shared/kafka-covers/README.md' in c)
c=(R/'docs/pipeline.md').read_text();ck('pipeline current MySQL links retained',c.count('_shared/mysql-covers/README.md')>=2 and '数据库使用[数据库系列入口]' not in c);expectedKafkaSegment=re.search(r'Kafka消息队列使用.*?正文沿不可变style-v1；',show(K,'docs/pipeline.md')).group();ck('pipeline authored Kafka entry retained exactly',expectedKafkaSegment in c)
file='site/src/content/series.json';c=json.loads((R/file).read_text());u=json.loads(show(UP,file));k=json.loads(show(K,file));ck('series database object equals upstream',c['database']==u['database']);ck('series Kafka object equals authored commit',c['message-queue']==k['message-queue'])
def track(t,ident):
 m=re.search(r"\{\n    id: '"+re.escape(ident)+r"',.*?\n  \},",t,re.S);assert m,ident;return m.group(0)
file='site/src/lib/learning.ts';c=(R/file).read_text();ck('learning database definition equals upstream',track(c,'database')==track(show(UP,file),'database'));ck('learning Kafka definition equals authored commit',track(c,'message-queue')==track(show(K,file),'message-queue'))
file='site/src/pages/index.astro';c=(R/file).read_text()
for ident,ref,label in [('database',UP,'MySQL'),('message-queue',K,'Kafka')]:
 pat=r"track.id === '"+re.escape(ident)+r"' \? '[^']+'";a=re.search(pat,c);b=re.search(pat,show(ref,file));ck('home '+label+' subtitle retained',a and b and a.group()==b.group())
for file in ['site/package.json','site/package-lock.json']:
 c=json.loads((R/file).read_text());u=json.loads(show(UP,file));version=c.get('version');c.pop('version',None);u.pop('version',None)
 if 'packages' in c:c['packages'][''].pop('version',None);u['packages'][''].pop('version',None)
 ck(file+' dependency/config tree unchanged except release version',c==u);ck(file+' patch version0.84.1',version=='0.84.1',version)
ui=json.loads((W/'ui-source-reuse.json').read_text());uiWorking=[]
for item in ui['files']:
 p=R/item['path'];actual=gitblob(p);uiWorking.append({'path':item['path'],'expectedGitBlob':item['upstreamGitBlob'],'actualGitBlob':actual,'passed':actual==item['upstreamGitBlob']})
ck('47 unchanged UI/runtime/script resources equal upstream in merged tree',all(x['passed'] for x in uiWorking),str(len(uiWorking)))
# Preserve old scope: delta changes exactly48DB publication paths; never rewrite old baseline.
bp=Path('/workspace/work/mq-cover-qa/kafka-scope-baseline.json');sp=Path('/workspace/work/mq-cover-qa/kafka-scope-authorized-supplement.json');b=json.loads(bp.read_text());s=json.loads(sp.read_text());plan=json.loads((W/'upstream-delta.json').read_text());extra=set(s['additionalAuthorizedReplacementFiles']);protected={p:v for p,v in b['protectedFiles'].items() if p not in extra};changed=set(plan['upstreamAllChangedPaths']);ut={}
for row in subprocess.check_output(['git','ls-tree','-r','-z',UP],cwd=R).split(b'\0'):
 if not row:continue
 head,p=row.split(b'\t',1);ut[p.decode()]=head.decode().split()[2]
oldChecks=[]
for p,old in protected.items():
 path=R/p
 if p in changed:
  actual=gitblob(path);expected=ut.get(p);ok=actual==expected;rule='exact upstream blob';actualState={'gitBlob':actual};expectState={'gitBlob':expected}
 else:
  actualState={'path':p,'state':'present','bytes':path.stat().st_size,'sha256':sha(path)} if path.is_file() else {'path':p,'state':'missing'};expectState=old;ok=actualState==old;rule='original immutable baseline bytes/state'
 oldChecks.append({'path':p,'rule':rule,'expected':expectState,'actual':actualState,'passed':ok})
ck('original baseline and existing authorization supplement bytes unchanged',sha(bp)==plan['originalKafkaScopeBaselineSha256'] and sha(sp)==plan['originalAuthorizedSupplementSha256'])
ck('effective old scope1826 preserved with exact upstream delta for48paths',len(oldChecks)==1826 and sum(x['rule']=='exact upstream blob' for x in oldChecks)==48 and all(x['passed'] for x in oldChecks))
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();report={'schemaVersion':1,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mergeHead':head,'upstream':UP,'authoredKafkaCommit':K,'checks':checks,'passed':all(x['passed'] for x in checks),'failed':[x for x in checks if not x['passed']],'workingUIResources':uiWorking,'effectiveOldProtection':{'oldBaselineSha256':sha(bp),'unchangedSupplementSha256':sha(sp),'total':len(oldChecks),'useOriginalBaseline':sum(x['rule'].startswith('original') for x in oldChecks),'useExactUpstream':sum(x['rule'].startswith('exact') for x in oldChecks),'checks':oldChecks,'failed':[x['path'] for x in oldChecks if not x['passed']]},'note':'Root already reported fresh full site build and160freeze verification; this independent report verifies source/data integration and preservation, not a newly executed UI test.'}
(W/'final-shared-and-preservation-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'mergeHead':head,'checks':len(checks),'passed':report['passed'],'failed':report['failed'],'uiResources':len(uiWorking),'effectiveProtected':len(oldChecks),'originalPaths':report['effectiveOldProtection']['useOriginalBaseline'],'upstreamPaths':report['effectiveOldProtection']['useExactUpstream']},ensure_ascii=False))
