from pathlib import Path
import json,hashlib,subprocess
from datetime import datetime,timezone
R=Path('/workspace/video-studio'); W=Path('/workspace/work/redis-cover-qa')
b=json.loads((W/'protection-baseline.json').read_text()); findings=[]
for rel,v in b['protected'].items():
 p=R/rel
 if not (p.is_file() or p.is_symlink()): findings.append({'path':rel,'kind':'missing'});continue
 raw=str(p.readlink()).encode() if p.is_symlink() else p.read_bytes()
 h=hashlib.sha256(raw).hexdigest()
 if h!=v['sha256']: findings.append({'path':rel,'kind':'changed','expected':v['sha256'],'actual':h})
freeze=[]
for m in b['redisFreezeManifests']:
 rows=m['rows']; matched=0
 for x in rows:
  p=R/x['path']; actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
  matched+=actual==x['expectedSha256']
 freeze.append({'manifest':m['manifest'],'declarations':len(rows),'matches':matched})
 newbad=[]
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0')
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=R).decode().split('\0')
contract=json.loads((W/'output-contract-correction.json').read_text())
assert contract['baselineSha256']==hashlib.sha256((W/'protection-baseline.json').read_bytes()).hexdigest()
known=set(b['protected'])|set(b['allowedExistingOutputChanges'])|set(contract['effectiveAllowedNewPairedOutputs'])
for p in tracked+untracked:
 if p and (p.startswith('episodes/redis-skiplist/') or p.startswith('episodes-codex/redis-skiplist/')) and p not in known: newbad.append(p)
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'baselineSha256':hashlib.sha256((W/'protection-baseline.json').read_bytes()).hexdigest(),'baseSha':b['baseSha'],'protectedPaths':len(b['protected']),'protectedFindings':findings,'unknownRedisPaths':newbad,'redisFreezeManifests':freeze,'passed':not findings and not newbad and all(x['matches']==x['declarations'] for x in freeze)}
(W/'protection-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
