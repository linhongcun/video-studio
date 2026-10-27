import concurrent.futures, datetime, hashlib, json, urllib.request
from pathlib import Path
ROOT=Path('/workspace/video-studio')
OUT=Path('/workspace/work/leetcode-online');OUT.mkdir(exist_ok=True)
BASE='https://linhongcun.github.io/video-studio/'
catalog=json.loads((ROOT/'episodes-codex/_shared/leetcode-covers/catalog.json').read_text())
jobs=[]
for ep in catalog['episodes']:
 slug=ep['slug'];prefix='episodes/'+slug+'/'
 for f in ['cover-16x9.jpg','video.mp4']:
  p=ROOT/prefix/f;jobs.append({'path':prefix+f,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'bytes'})
 p=ROOT/'site/dist'/prefix/'captions.vtt'
 if p.exists():jobs.append({'path':prefix+'captions.vtt','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'bytes'})
 jobs.append({'path':prefix,'contains':[prefix+'cover-16x9.jpg'],'kind':'page'})
jobs.append({'path':'series/leetcode/','contains':['episodes/'+e['slug']+'/' for e in catalog['episodes']],'kind':'page'})
jobs.append({'path':'changelog/','contains':['v0.79.1'],'kind':'page'})
def fetch(j):
 r={'url':BASE+j['path'],'kind':j['kind']}
 try:
  req=urllib.request.Request(r['url'],headers={'User-Agent':'video-studio-cover-verification'})
  with urllib.request.urlopen(req,timeout=90) as response:
   h=hashlib.sha256();data=[];size=0
   while block:=response.read(1024*1024):
    h.update(block);size+=len(block)
    if j['kind']=='page' or j['path'].endswith('.jpg'):data.append(block)
   r.update(status=response.status,bytes=size,sha256=h.hexdigest(),finalUrl=response.url)
  if j['kind']=='bytes':
   r['expectedSha256']=j['sha256'];r['passed']=r['sha256']==j['sha256']
  else:
   text=b''.join(data).decode();r['missing']=[x for x in j['contains'] if x not in text];r['passed']=not r['missing']
  if data and j['path'].endswith('.jpg'):
   p=OUT/Path(j['path']).parent.name;p.mkdir(exist_ok=True);(p/'cover-16x9.jpg').write_bytes(b''.join(data))
 except Exception as e:r.update(passed=False,error=str(e))
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(fetch,jobs))
now=datetime.datetime.now(datetime.timezone.utc)
report={'checkedAt':now.isoformat(),'method':'complete canonical HTTPS GET; no range or cache-busting query','requests':results,'passed':all(r['passed'] for r in results),'requestCount':len(results),'totalBytes':sum(r.get('bytes',0) for r in results)}
p=OUT/('report-'+now.strftime('%Y%m%dT%H%M%SZ')+'.json');p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if report['passed']:(OUT/'online-verification.json').write_text(p.read_text())
print(json.dumps({'passed':report['passed'],'requests':len(results),'bytes':report['totalBytes'],'failed':[r for r in results if not r['passed']],'report':str(p)},ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
