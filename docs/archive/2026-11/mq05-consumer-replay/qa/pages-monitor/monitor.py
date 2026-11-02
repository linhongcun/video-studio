#!/usr/bin/env python3
"""Read-only monitoring of the explicitly authorized post-Release Pages run."""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, subprocess, time

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
A=ROOT/'docs/archive/2026-11/mq05-consumer-replay'
OUT=Path(__file__).resolve().parent
REPO='linhongcun/video-studio'
RUN=41423515242
HEAD='8eb1b603e7fb7fdaead04fe4d3892f52864f4e75'
release_path=A/'github-release.json'
release=json.loads(release_path.read_text())
published=release['publishedAt']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.now(timezone.utc).isoformat()

def request(label, endpoint):
    file=OUT/(label+'.json')
    assert not file.exists(), 'Retain every previous attempt'
    cmd=['gh','api','-H','Cache-Control: no-cache',endpoint]
    started=utc()
    try:
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
        status=result.returncode; stdout=result.stdout; stderr=result.stderr
    except subprocess.TimeoutExpired as exc:
        status='timeout';stdout=(exc.stdout or b'').decode() if isinstance(exc.stdout,bytes) else (exc.stdout or '');stderr='Read-only gh api exceeded45s'
    file.write_text(stdout)
    (OUT/(label+'.stderr.txt')).write_text(stderr)
    receipt={'fetchedAtUTC':started,'finishedAtUTC':utc(),'command':cmd,'exit':status,'responseFile':file.relative_to(ROOT).as_posix(),'responseSHA256':sha(file)}
    (OUT/(label+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    if status!=0:return None,receipt
    try:return json.loads(stdout),receipt
    except json.JSONDecodeError:return None,receipt

def emit(value):print(json.dumps(value,ensure_ascii=False),flush=True)

for iteration in range(1,61):
    tag=f'{iteration:03d}'
    reads=[('run',f'repos/{REPO}/actions/runs/{RUN}'),('jobs',f'repos/{REPO}/actions/runs/{RUN}/jobs'),('deployments',f'repos/{REPO}/deployments?sha={HEAD}&environment=github-pages&per_page=10')]
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending={name:pool.submit(request,tag+'-'+name,endpoint) for name,endpoint in reads}
        results={name:f.result() for name,f in pending.items()}
    run,run_receipt=results['run']; jobs_data,jobs_receipt=results['jobs'];deployments,deploy_receipt=results['deployments']
    if not isinstance(run,dict) or not isinstance(jobs_data,dict) or not isinstance(deployments,list):
        emit({'iteration':iteration,'atUTC':utc(),'observation':'read error retained; no status inference'})
        time.sleep(30);continue
    assert run['id']==RUN and run['head_sha']==HEAD and run['event']=='workflow_dispatch' and run['created_at']>=published
    jobs=jobs_data.get('jobs',[])
    summary={'iteration':iteration,'atUTC':utc(),'runStatus':run['status'],'runConclusion':run['conclusion'],'jobs':[{'id':j['id'],'name':j['name'],'status':j['status'],'conclusion':j['conclusion'],'activeSteps':[s['name'] for s in j.get('steps',[]) if s['status']=='in_progress']} for j in jobs],'deployments':len(deployments)}
    matches=[]
    for deployment in deployments:
        assert deployment['sha']==HEAD
        statuses,status_receipt=request(tag+f'-deployment-{deployment["id"]}-statuses',f'repos/{REPO}/deployments/{deployment["id"]}/statuses?per_page=10')
        if not isinstance(statuses,list):continue
        for status in statuses:
            log_url=status.get('log_url') or ''
            if status['state']=='success' and f'/actions/runs/{RUN}' in log_url:
                matches.append({'deployment':deployment,'status':status,'statusReceipt':status_receipt})
    summary['matchingSuccessfulDeploymentIds']=[m['deployment']['id'] for m in matches]
    emit(summary)
    if run['status']=='completed' and run['conclusion']!='success':
        fail=OUT/'failed.json';fail.write_text(json.dumps({'runReceipt':run_receipt,'jobsReceipt':jobs_receipt,'summary':summary,'scope':'Actual completed workflow failure; no cancellation/retry/source mutation was attempted.'},indent=2)+'\n')
        raise SystemExit(2)
    build=[j for j in jobs if j['name']=='build'];deploy=[j for j in jobs if j['name']=='deploy']
    if run['status']=='completed' and run['conclusion']=='success' and build and deploy and all(j['status']=='completed' and j['conclusion']=='success' for j in build+deploy) and matches:
        accepted={'kind':'post-release-pages-workflow-and-deployment-success','pass':True,'acceptedAtUTC':utc(),'release':{'file':release_path.relative_to(ROOT).as_posix(),'sha256':sha(release_path),'tag':release['tagName'],'publishedAt':published,'url':release['url']},'run':{'id':RUN,'url':run['html_url'],'headSHA':HEAD,'event':run['event'],'createdAt':run['created_at'],'runStartedAt':run.get('run_started_at'),'updatedAt':run['updated_at'],'status':run['status'],'conclusion':run['conclusion']},'buildAndDeployJobs':[{'id':j['id'],'name':j['name'],'url':j['html_url'],'status':j['status'],'conclusion':j['conclusion'],'startedAt':j['started_at'],'completedAt':j['completed_at']} for j in build+deploy],'successfulDeploymentProofs':[{'id':m['deployment']['id'],'sha':m['deployment']['sha'],'ref':m['deployment']['ref'],'createdAt':m['deployment']['created_at'],'statusId':m['status']['id'],'state':m['status']['state'],'statusCreatedAt':m['status']['created_at'],'logURL':m['status']['log_url'],'environmentURL':m['status'].get('environment_url'),'statusRawReceipt':m['statusReceipt']} for m in matches],'rawProofs':{'run':run_receipt,'jobs':jobs_receipt,'deployments':deploy_receipt},'limits':['Control-plane workflow, job and same-head same-run deployment success only. No canonical HTTP/media/browser delivery claim; root/publication own those checks.','All timestamps are retained exactly as returned and observed with UTC fetch times. Status projection timestamps are not inferred execution order.','Read-only gh API calls only. No run was canceled, redispatched or modified by this monitor.']}
        target=A/'pages-release-deployment.json';assert not target.exists()
        target.write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n')
        (OUT/'accepted.json').write_text(json.dumps({'artifact':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'acceptedAtUTC':accepted['acceptedAtUTC']},indent=2)+'\n')
        emit({'GO':True,'artifact':str(target.relative_to(ROOT)),'sha256':sha(target),'runURL':run['html_url'],'deploymentIds':[m['deployment']['id'] for m in matches]})
        break
    time.sleep(30)
else:
    emit({'GO':False,'reason':'bounded monitor exhausted; all snapshots retained'})
    raise SystemExit(3)
