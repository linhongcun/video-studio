from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,time,hashlib
Q=Path(__file__).resolve().parent;REPO='linhongcun/video-studio';RUN=41302647076;HEAD='8980122436a8400eb3dc4d64cd12bad0ff8d863c';RELEASE='2026-11-01T11:36:35Z';URL=f'https://github.com/{REPO}/actions/runs/{RUN}'
now=lambda:datetime.now(timezone.utc).isoformat()
def get(label,endpoint,folder):
 start=now();r=subprocess.run(['gh','api','--method','GET','-H','Cache-Control: no-cache',endpoint],capture_output=True,text=True,timeout=45);dest=folder/(label+('.json'if r.returncode==0 else '-error.txt'));dest.write_text(r.stdout);(folder/(label+'.stderr.txt')).write_text(r.stderr);meta={'atUTC':start,'finishedAtUTC':now(),'endpoint':endpoint,'exitCode':r.returncode,'responseFile':dest.name};(folder/(label+'.meta.json')).write_text(json.dumps(meta,indent=2)+'\n');return json.loads(r.stdout)if r.returncode==0 else None
for i in range(1,61):
 folder=Q/f'poll-{i:03}';folder.mkdir(exist_ok=False);endpoints={'run':f'repos/{REPO}/actions/runs/{RUN}','jobs':f'repos/{REPO}/actions/runs/{RUN}/jobs','deployments':f'repos/{REPO}/deployments?sha={HEAD}&per_page=10'}
 with ThreadPoolExecutor(max_workers=3)as pool:fs={label:pool.submit(get,label,ep,folder)for label,ep in endpoints.items()};results={label:f.result()for label,f in fs.items()}
 run=results['run'];jobs=results['jobs'];depls=results['deployments'];summary={'atUTC':now(),'runID':RUN,'expectedHead':HEAD,'run':{k:run.get(k)for k in ['status','conclusion','head_sha','created_at','updated_at']}if run else None,'jobs':[],'deployments':[]}
 if jobs:
  for j in jobs['jobs']:
   summary['jobs'].append({k:j.get(k)for k in ['id','name','status','conclusion','started_at','completed_at'] }|{'activeSteps':[s['name']for s in j.get('steps',[])if s['status']=='in_progress']})
 if depls:
  for dep in depls:
   st=get('deployment-'+str(dep['id'])+'-statuses',f'repos/{REPO}/deployments/{dep["id"]}/statuses?per_page=10',folder)
   summary['deployments'].append({'id':dep['id'],'sha':dep['sha'],'environment':dep['environment'],'created_at':dep['created_at'],'states':[{k:s.get(k)for k in ['id','state','created_at','updated_at','log_url','environment_url','description']}for s in(st or [])]})
 (folder/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
 validRun=run and run['id']==RUN and run['head_sha']==HEAD and run['event']=='workflow_dispatch'and run['created_at']>RELEASE and run['status']=='completed'and run['conclusion']=='success'
 validJobs=jobs and all(j['status']=='completed'and j['conclusion']=='success'for j in jobs['jobs'])and {'build','deploy'}.issubset(set(j['name']for j in jobs['jobs']))
 proof=[{'deploymentID':dep['id'],'status':s}for dep in summary['deployments']for s in dep['states']if dep['sha']==HEAD and s['state']=='success'and f'/actions/runs/{RUN}'in(s.get('log_url')or'')]
 if validRun and validJobs and proof:
  result={'status':'GO','atUTC':now(),'runID':RUN,'runURL':URL,'headSHA':HEAD,'releasePublishedAtUTC':RELEASE,'runCreatedAtUTC':run['created_at'],'runAndAllJobsCompletedSuccess':True,'sameRunDeploymentSuccess':proof,'evidenceDirectory':folder.name,'scope':'Read-only GitHub control-plane proofs; no canonical delivery HTTP/native-browser acceptance claim.'};(Q/'accepted.json').write_text(json.dumps(result,indent=2)+'\n');print('ACCEPTED '+json.dumps(result),flush=True);break
 if run and run['status']=='completed'and run['conclusion']in ['failure','cancelled','timed_out','action_required']:
  print('TERMINAL_NON_SUCCESS_REQUIRES_READ_ONLY_DIAGNOSIS',flush=True);break
 time.sleep(30)
