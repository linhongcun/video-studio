from pathlib import Path
from collections import Counter
import hashlib,json,datetime,subprocess,re,sys
R=Path('/workspace/video-studio').resolve();W=Path('/workspace/work/mq-cover-qa');BASE=W/'preservation-baseline.json';TARGETS=['message-queue'];MUTABLE_DIRS={'episodes/message-queue','episodes-codex/message-queue/revisions/mq-intro/message-queue'};PRIOR=['leetcode-covers','puzzles-covers','database-covers','design-pattern-covers'];PUZZLES=['horse-racing','bridge-torch','water-jug','monty-hall','egg-drop'];COVER=re.compile(r'^(?:cover-(?:16x9|4x3|3x4)\.(?:png|jpg|svg)|poster\.jpg)$')
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
 return sorted(str(p.relative_to(R)) for name in PRIOR for p in (R/'episodes-codex/_shared'/name).rglob('*') if p.is_file())
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
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();initialGitStatus=subprocess.check_output(['git','status','--porcelain','-uno'],cwd=R,text=True)
tracked=subprocess.check_output(['git','ls-tree','-r',head,'--','episodes','episodes-codex'],cwd=R,text=True);tree={}
for line in tracked.splitlines():
 info,p=line.split('\t',1);parts=info.split();tree[p]=parts[-1]
published=[]
for p in (R/'episodes').glob('*/meta.json'):
 m=json.loads(p.read_text())
 if m.get('series')=='message-queue' and not m.get('draft'):published.append(m)
assert {m['slug'] for m in published}==set(TARGETS),'Published MQ catalog changed; do not silently reduce baseline.'
oldcovers=[];frozen=[]
explicit=['video.mp4','voice.wav','meta.json','script.md','article.mdx','storyboard.json','words.json','references.json','reference-appendix.json','reference-appendix-media-check.json','render-result.json','source-sha256.json','covers.json','remotion/src/Cover.tsx','remotion/scripts/covers.mjs','remotion/package.json','remotion/package-lock.json']
for slug in TARGETS:
 for root in ['episodes','episodes-codex']:
  base=R/root/slug
  for n in explicit:record(base/n)
  # Every existing tracked source/history file, excluding only mutable cover output
  # files in active production and publishing directories. Former root covers remain protected.
  prefix=str(base.relative_to(R))+'/'
  for rel in tree:
   if rel.startswith(prefix) and not (str(Path(rel).parent) in MUTABLE_DIRS and (COVER.fullmatch(Path(rel).name) or Path(rel).name=='cover-style.json')):record(R/rel)
 # Current active source and prior root manifests are both retained. Every declared
 # path is resolved against its own manifest directory and compared independently.
 for f in (R/'episodes-codex'/slug).rglob('source-sha256.json'):
  declared=json.loads(f.read_text());entries=[];record(f)
  for k,expect in declared.items():
   actual=record(f.parent/k);entries.append({'key':k,'expectedSha256':expect,'actualPath':actual['path'],'actualState':actual['state'],'matchesDeclared':actual.get('sha256')==expect if actual['state']=='present' else None})
  frozen.append({'manifest':str(f.relative_to(R)),'entries':entries,'counts':{'declared':len(entries),'actualStates':dict(Counter(x['actualState'] for x in entries)),'matches':sum(x['matchesDeclared'] is True for x in entries),'presentMismatch':sum(x['matchesDeclared'] is False for x in entries)}})
for directory in sorted(MUTABLE_DIRS):
 for p in (R/directory).iterdir():
  if p.is_file() and COVER.fullmatch(p.name):
   rel=str(p.relative_to(R));oldcovers.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'gitBlob':tree.get(rel),'baselineCommit':head})
other=nonbatch_covers();shared=shared_sources()
for rel in other+shared:record(R/rel)
# Preserve the freshly merged puzzle video/template work without taking ignored
# dependency caches as source authority or restoring earlier published media.
puzzles=[]
for rel in tree:
 parts=Path(rel).parts
 if len(parts)>2 and parts[1] in PUZZLES and (parts[0]=='episodes' or 'cover-continuity' in parts):puzzles.append(record(R/rel)['path'])
for rel in ['site/src/content/series.json','docs/RULES.md']:
 # RULES receives the new template entry, so only series classification is frozen.
 if rel!='docs/RULES.md':record(R/rel)
entries=[x for f in frozen for x in f['entries']]
d={'schemaVersion':1,'purpose':'MQ01 cover-only preservation baseline from latest main. All MQ published non-cover files, tracked production/history files, both root and active revision freeze manifests and every declared path are protected. Only active production revision cover outputs and publishing episode-root cover outputs may change; former root production covers remain protected. All other published covers, four prior shared cover templates, and newly merged puzzle cover-continuity source/current publication files are protected. Optional explicit absent paths are separate from missing frozen entries.','capturedAt':stamp(),'head':head,'initialTrackedGitStatus':initialGitStatus,'targets':TARGETS,'mutableCoverDirectories':sorted(MUTABLE_DIRS),'publishedIdentity':[{'slug':m['slug'],'ep':m['ep'],'title':m['title'],'series':m['series'],'sourcePath':m['sourcePath'],'episodePart':m.get('episodePart')} for m in published],'frozenManifests':frozen,'files':cache,'nonBatchPublishedCovers':other,'priorSharedTemplateFiles':shared,'puzzlesLatestPreservedPaths':sorted(set(puzzles)),'mutableOldCoverOutputs':oldcovers,'summary':{'protectedUniquePaths':len(cache),'protectedStates':dict(Counter(x['state'] for x in cache.values())),'frozenManifests':len(frozen),'frozenEntries':len(entries),'frozenActualStates':dict(Counter(x['actualState'] for x in entries)),'frozenDeclaredMatches':sum(x['matchesDeclared'] is True for x in entries),'frozenPresentMismatch':sum(x['matchesDeclared'] is False for x in entries),'nonBatchPublishedCoverPaths':len(other),'priorSharedTemplatePaths':len(shared),'sharedCacheFiles':sum('__pycache__' in x for x in shared),'puzzlesLatestPreservedPaths':len(set(puzzles)),'mutableExistingCoverOutputs':len(oldcovers),'mutableCoverOutputsRecoverableFromBaselineGit':sum(x['gitBlob'] is not None for x in oldcovers)}}
BASE.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'baseline':str(BASE),'sha256':sha(BASE),'summary':d['summary'],'frozenManifests':[{'path':f['manifest'],**f['counts']} for f in frozen]},ensure_ascii=False,indent=2))
