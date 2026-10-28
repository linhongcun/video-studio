"""Move the dedicated clean preview worktree to an authorized exact candidate and build once."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse, json, subprocess, time

p=argparse.ArgumentParser(); p.add_argument('candidate'); args=p.parse_args()
ROOT=Path('/workspace/work/video-studio'); SITE=Path('/workspace/work/video-studio-sitecheck'); OUT=ROOT/'work/redis-cache-style/siteqa'
def git(*a): return subprocess.check_output(['git',*a],cwd=SITE,text=True).strip()
assert not git('status','--porcelain'), 'Dedicated preview worktree must be clean before changing its exact candidate.'
before=git('rev-parse','HEAD')
old=json.loads(subprocess.check_output(['git','show',before+':site/package-lock.json'],cwd=SITE,text=True))['packages']; old.pop('',None)
new=json.loads(subprocess.check_output(['git','show',args.candidate+':site/package-lock.json'],cwd=SITE,text=True))['packages']; new.pop('',None)
assert old==new, 'Candidate dependency packages differ from retained installed dependency tree; install actual candidate lock before building.'
subprocess.run(['git','checkout','--detach',args.candidate],cwd=SITE,check=True)
candidate=git('rev-parse','HEAD'); assert candidate==git('rev-parse',args.candidate)
report={'candidate':candidate,'priorPreviewCandidate':before,'startedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),'dependencyPackages':len(new),'allNonRootLockPackagesEqualToRetainedInstall':True,'command':['npm','--prefix','site','run','build']}
start=time.monotonic()
with (OUT/'build.log').open('w') as log:
    result=subprocess.run(report['command'],cwd=SITE,stdout=log,stderr=subprocess.STDOUT)
report.update(exitCode=result.returncode,seconds=round(time.monotonic()-start,3),finishedAt=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'))
(OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n'); (OUT/'candidate.txt').write_text(candidate+'\n')
assert result.returncode==0, 'Read preserved build.log; do not modify production to satisfy QA assumptions.'
assert not git('status','--porcelain','--untracked-files=no')
print(json.dumps(report))
