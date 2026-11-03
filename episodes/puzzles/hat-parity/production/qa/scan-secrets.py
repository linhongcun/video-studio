#!/usr/bin/env python3
"""Run canonical credential rules and distinguish unchanged historical evidence."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess,sys
R=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file())
D=Path(__file__).resolve().parent
BASE='60f92e6f7550b1ef4a450b6ebdae67d1888733f2'
CHECKER=R/'episodes/_shared/tests/secret_scan.py'
spec=importlib.util.spec_from_file_location('canonical_secret_rules',CHECKER)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def names(args):return set(filter(None,subprocess.check_output(['git',*args],cwd=R).decode().split('\0')))
paths=names(['diff','--name-only','-z',BASE])|names(['ls-files','-z','--others','--exclude-standard'])
flags=[];text=0;skipped=0
for rel in sorted(paths):
 p=R/rel
 if p.name=='.env' or p.name.endswith('.env'):flags.append({'path':rel,'line':0,'rule':'env file not ignored'});continue
 if not p.is_file():continue
 if p.resolve()==CHECKER or p.stat().st_size>2_000_000:skipped+=1;continue
 raw=p.read_bytes()
 if b'\0' in raw[:8192]:skipped+=1;continue
 text+=1
 for n,line in enumerate(raw.decode('utf-8','replace').split('\n'),1):
  for name,rx in m.PAT:
   if rx.search(line):flags.append({'path':rel,'line':n,'rule':name})
prior=R/'episodes/puzzles/birthday-paradox/production/qa/secret-scan-review.json'
pins=json.loads(prior.read_text())['preExistingFlagProof']['files']
proof=[]
for f in pins:
 p=R/f['path'];digest=hashlib.sha256(p.read_bytes()).hexdigest()
 base=hashlib.sha256(subprocess.check_output(['git','show',BASE+':'+f['path']],cwd=R)).hexdigest()
 assert digest==base==f['workingSHA256'] and f['path'] not in paths
 proof.append({'path':f['path'],'sha256':digest,'flags':f['flagCount']})
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'baseline':BASE,'canonicalCheckerSHA256':hashlib.sha256(CHECKER.read_bytes()).hexdigest(),'method':'Original canonical PAT and identical skip rules over changes since task baseline plus nonignored untracked paths. No scanner modification.','paths':len(paths),'textFiles':text,'skippedByOriginalRules':skipped,'flags':flags,'passed':not flags,'wholeRepositoryStatus':'Canonical full scan remains FAIL on 282 locations in 25 unchanged baseline evidence files; not reported as clean.','historicalProof':{'priorReview':str(prior.relative_to(R)),'priorReviewSHA256':hashlib.sha256(prior.read_bytes()).hexdigest(),'files':proof}}
(D/'secret-scan-current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':not flags,'paths':len(paths),'flags':flags,'unchangedHistoricalFiles':len(proof)},ensure_ascii=False));sys.exit(bool(flags))
