from pathlib import Path
import concurrent.futures,threading,subprocess,json,hashlib,datetime
root=Path.cwd();w=root/'work/leetcode-video-style';slugs=[e['slug'] for e in json.loads((root/'episodes-codex/_shared/leetcode-video/identities-v1.json').read_text())['episodes']]
for slug in slugs:
 d=json.loads((w/'preflight'/slug/'qa-report.json').read_text());assert d['status']=='passed',slug
 for path,h in d['sourceSHA256'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==h,(slug,path)
for slug in slugs:
 with (w/f'{slug}-freeze.log').open('w') as log:subprocess.run(['python3','episodes-codex/_shared/leetcode-video/render.py',slug,'--freeze'],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
 p=root/f'episodes-codex/{slug}/revisions/leetcode-style/source-sha256.json';d=json.loads(p.read_text());print(json.dumps({'slug':slug,'status':'frozen','inputs':len(d['inputs']),'fonts':len(d.get('externalInputs',{}))}),flush=True)
stop=threading.Event();(w/'render-complete').mkdir(exist_ok=True)
def one(slug):
 marker=w/'render-complete'/f'{slug}.json'
 if marker.exists():return json.loads(marker.read_text())
 if stop.is_set():return {'slug':slug,'status':'not-started-after-failure'}
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();print(json.dumps({'slug':slug,'status':'render-started','at':start}),flush=True)
 with (w/f'{slug}-render.log').open('w') as log:r=subprocess.run(['python3','episodes-codex/_shared/leetcode-video/render.py',slug,'--render'],cwd=root,stdout=log,stderr=subprocess.STDOUT)
 row={'slug':slug,'exitCode':r.returncode,'startedAtUTC':start,'finishedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 if r.returncode:
  stop.set();(w/'render-failed.json').write_text(json.dumps(row)+'\n');print(json.dumps(row),flush=True);return row
 p=root/f'episodes-codex/{slug}/revisions/leetcode-style/render-result.json';d=json.loads(p.read_text());assert d['visualRevision']=='leetcode-style-v1'
 row.update(status='render-complete',sha256=d['sha256'],frames=d['frames']);temp=marker.with_suffix('.tmp');temp.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');temp.replace(marker);print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(one,slugs))
(w/'render-run.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if all(x.get('exitCode')==0 for x in rows) else 1)
