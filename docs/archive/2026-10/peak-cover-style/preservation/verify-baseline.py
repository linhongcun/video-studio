from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess
ROOT=Path('/workspace/video-studio');OUT=Path('/workspace/work/peak-cover-qa');P=OUT/'protection-baseline.json'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
b=json.loads(P.read_text());findings=[]
for n,v in b['protected'].items():
 p=ROOT/n
 now={'exists':p.exists(),'isSymlink':p.is_symlink(),'sha256':sha(p) if p.is_file() else None,'bytes':p.stat().st_size if p.is_file() else None}
 if now!=v:findings.append({'path':n,'before':v,'after':now})
frozen=[]
for f in b['frozenManifests']:
 matches=0;bad=[]
 for e in f['entries']:
  p=ROOT/e['path'];actual=sha(p) if p.is_file() else None
  if actual==e['expectedSha256']:matches+=1
  else:bad.append({'path':e['path'],'expected':e['expectedSha256'],'actual':actual})
 frozen.append({'manifest':f['manifest'],'declarations':f['declarations'],'matches':matches,'findings':bad})
now=set(filter(None,subprocess.check_output(['git','-C',str(ROOT),'ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0')))
known=set(b['protected'])|set(b['allowedImages'])|set(b['allowedSidecars']);unknown=[n for n in sorted(now-known) if any(n.startswith('episodes-codex/'+s+'/') for s in b['slugs'])]
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'baselineSha256':sha(P),'baseSha':b['baseSha'],'protectedPaths':len(b['protected']),'protectedFindings':findings,'unknownTargetSourcePaths':unknown,'frozenManifests':frozen,'passed':not findings and not unknown and all(not x['findings'] for x in frozen)}
(OUT/'protection-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
