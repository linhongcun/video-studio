from pathlib import Path
from collections import Counter
import hashlib,json,datetime,subprocess,re,sys
R=Path('/workspace/video-studio').resolve();W=Path('/workspace/work/design-pattern-cover-qa');BASE=W/'preservation-baseline.json';TARGETS=['strategy-pattern','observer-pattern','adapter-pattern'];COVER=re.compile(r'^(?:cover-(?:16x9|4x3|3x4)\.(?:png|jpg|svg)|poster\.jpg)$')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
cache={}
def record(p):
 p=p.resolve()
 try:k=str(p.relative_to(R))
 except ValueError:return {'path':str(p),'state':'outside-repository-not-read'}
 if k in cache:return cache[k]
 if not p.exists():d={'path':k,'state':'missing'}
 elif not p.is_file():d={'path':k,'state':'not-file'}
 else:d={'path':k,'state':'present','bytes':p.stat().st_size,'sha256':sha(p)}
 cache[k]=d;return d
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def nonbatch_covers():
 return sorted(str(p.relative_to(R)) for folder in (R/'episodes').iterdir() if folder.is_dir() and folder.name not in TARGETS for p in folder.iterdir() if p.is_file() and (COVER.fullmatch(p.name) or p.name=='cover-style.json'))
def shared_sources():
 return sorted(str(p.relative_to(R)) for name in ['leetcode-covers','puzzles-covers','database-covers'] for p in (R/'episodes-codex/_shared'/name).rglob('*') if p.is_file())
if '--verify' in sys.argv:
 b=json.loads(BASE.read_text());changes=[]
 for old in b['files'].values():
  now=record(R/old['path'])
  if now!=old:changes.append({'before':old,'after':now})
 universe=[]
 for key,current in [('nonBatchPublishedCovers',nonbatch_covers()),('priorSharedTemplateFiles',shared_sources())]:
  old=b[key];added=sorted(set(current)-set(old));removed=sorted(set(old)-set(current))
  if added or removed:universe.append({'scope':key,'added':added,'removed':removed})
 result={'schemaVersion':1,'checkedAt':stamp(),'baselineSha256':sha(BASE),'baselineHead':b['head'],'currentHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'checkedPaths':len(b['files']),'unchangedPaths':len(b['files'])-len(changes),'changes':changes,'universeChanges':universe,'passed':not changes and not universe};p=W/'preservation-verification.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({**result,'changes':changes[:15]},ensure_ascii=False,indent=2));sys.exit(not result['passed'])
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();initialGitStatus=subprocess.check_output(['git','status','--porcelain','-uno'],cwd=R,text=True);episodes=[];oldcovers=[]
tracked=subprocess.check_output(['git','ls-tree','-r',head,'--','episodes','episodes-codex'],cwd=R,text=True);tree={}
for line in tracked.splitlines():
 info,p=line.split('\t',1);parts=info.split();tree[p]=parts[-1]
explicit=['video.mp4','voice.wav','meta.json','script.md','article.mdx','storyboard.json','words.json','references.json','reference-appendix.json','reference-appendix-media-check.json','render-result.json','source-sha256.json','covers.json','remotion/src/Cover.tsx','remotion/scripts/covers.mjs','remotion/package.json','remotion/package-lock.json']
for slug in TARGETS:
 m=json.loads((R/'episodes'/slug/'meta.json').read_text());paths=[]
 for root in ['episodes','episodes-codex']:
  base=R/root/slug
  for n in explicit:paths.append(record(base/n)['path'])
  for folder in ['article','voice','remotion/src','remotion/public/audio']:
   for p in (base/folder).rglob('*'):
    if p.is_file():paths.append(record(p)['path'])
  for p in base.iterdir():
   if p.is_file() and (COVER.fullmatch(p.name)):
    d={'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p),'gitBlob':tree.get(str(p.relative_to(R))),'baselineCommit':head};oldcovers.append(d)
 base=R/'episodes-codex'/slug;f=base/'source-sha256.json';declared=json.loads(f.read_text());entries=[]
 for k,expect in declared.items():
  a=record(base/k);entries.append({'key':k,'expectedSha256':expect,'actualPath':a['path'],'actualState':a['state'],'matchesDeclared':a.get('sha256')==expect if a['state']=='present' else None})
 episodes.append({'slug':slug,'ep':m['ep'],'title':m['title'],'explicitPaths':sorted(set(paths)),'frozenManifest':str(f.relative_to(R)),'frozenEntries':entries,'frozenCounts':{'declared':len(entries),'actualStates':dict(Counter(e['actualState'] for e in entries)),'matchingDeclared':sum(e['matchesDeclared'] is True for e in entries),'presentMismatch':sum(e['matchesDeclared'] is False for e in entries)}})
other=nonbatch_covers();lc=shared_sources()
for p in other+lc:record(R/p)
record(R/'site/src/content/series.json')
for slug in TARGETS:
 for p in (R/'episodes'/slug).rglob('*'):
  if p.is_file() and not COVER.fullmatch(p.name) and p.name!='cover-style.json':record(p)
d={'schemaVersion':1,'purpose':'Before-change preservation baseline from latest a780862e for three design-patterns episodes. Current published non-cover files and site series configuration are protected, together with production video/audio/source/frozen cover inputs/manifests, all nonbatch published covers and all existing LeetCode/puzzles/database shared files (including pre-existing ignored caches if present). Optional explicit absent paths are distinguished from missing frozen inputs; frozen missing or mismatching inputs are recorded separately and never treated as optional.','capturedAt':stamp(),'head':head,'initialTrackedGitStatus':initialGitStatus,'targets':TARGETS,'episodes':episodes,'files':cache,'nonBatchPublishedCovers':other,'priorSharedTemplateFiles':lc,'mutableOldCoverOutputs':oldcovers,'summary':{'protectedUniquePaths':len(cache),'protectedStates':dict(Counter(x['state'] for x in cache.values())),'frozenEntries':sum(len(e['frozenEntries']) for e in episodes),'frozenActualStates':dict(Counter(x['actualState'] for e in episodes for x in e['frozenEntries'])),'frozenDeclaredMatches':sum(x['matchesDeclared'] is True for e in episodes for x in e['frozenEntries']),'frozenPresentMismatch':sum(x['matchesDeclared'] is False for e in episodes for x in e['frozenEntries']),'nonBatchPublishedCoverPaths':len(other),'priorSharedTemplatePaths':len(lc),'leetcodeSharedTemplatePaths':sum('/leetcode-covers/' in p for p in lc),'puzzlesSharedTemplatePaths':sum('/puzzles-covers/' in p for p in lc),'databaseSharedTemplatePaths':sum('/database-covers/' in p for p in lc),'sharedCacheFiles':sum('__pycache__' in p for p in lc),'mutableExistingCoverOutputs':len(oldcovers),'mutableCoverOutputsRecoverableFromBaselineGit':sum(x['gitBlob'] is not None for x in oldcovers)}}
BASE.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'baseline':str(BASE),'sha256':sha(BASE),'summary':d['summary'],'episodes':[{'slug':e['slug'],**e['frozenCounts']} for e in episodes]},ensure_ascii=False,indent=2))
