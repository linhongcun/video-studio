"""Separate Kafka remake protection scope. Never rewrites the prior cover-only baseline."""
from pathlib import Path
from collections import Counter
import hashlib,json,datetime,subprocess,sys
R=Path('/workspace/video-studio').resolve();W=Path('/workspace/work/mq-cover-qa');BASE=W/'kafka-scope-baseline.json';OLD=W/'preservation-baseline.json';SUPPLEMENT=W/'kafka-scope-authorized-supplement.json'
HEAD='d7a5d7682080232617a03cc988b7c25cb50446f4'
ALLOW_NAMES=['video.mp4','meta.json','script.md','storyboard.json','words.json','covers.json','article.mdx','article-sources.json','references.json','reference-appendix.json','reference-appendix-media-check.json','cover-16x9.jpg','cover-4x3.jpg','cover-3x4.jpg','poster.jpg','cover-style.json','article/01.jpg','article/02.jpg','article/03.jpg','article/04.jpg']
ALLOWED={f'episodes/message-queue/{n}' for n in ALLOW_NAMES}
# These current handbooks/classification files are authorized for Kafka direction.
# They are not part of the old production freeze manifests.
POLICY_EXCLUDED={'site/src/content/series.json','site/src/lib/learning.ts'}
SKIP_PARTS={'node_modules','.git','__pycache__','.cache'}
NEW_PREFIX='episodes-codex/message-queue/revisions/kafka-intro/'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def record(p):
 p=p.resolve();k=str(p.relative_to(R))
 if not p.exists():return {'path':k,'state':'missing'}
 if not p.is_file():return {'path':k,'state':'not-file'}
 return {'path':k,'state':'present','bytes':p.stat().st_size,'sha256':sha(p)}
def old_source_files():
 base=R/'episodes-codex/message-queue'
 return sorted(str(p.relative_to(R)) for p in base.rglob('*') if p.is_file() and not str(p.relative_to(R)).startswith(NEW_PREFIX) and not any(x in p.parts for x in SKIP_PARTS))
def other_published_files():
 return sorted(str(p.relative_to(R)) for d in (R/'episodes').iterdir() if d.is_dir() and d.name!='message-queue' and (d/'meta.json').exists() for p in d.rglob('*') if p.is_file() and not any(x in p.parts for x in SKIP_PARTS))
def prior_shared_files():
 return sorted(str(p.relative_to(R)) for name in ['leetcode-covers','puzzles-covers','database-covers','design-pattern-covers'] for p in (R/'episodes-codex/_shared'/name).rglob('*') if p.is_file())
if '--verify' in sys.argv:
 b=json.loads(BASE.read_text());changes=[]
 supplement=json.loads(SUPPLEMENT.read_text()) if SUPPLEMENT.exists() else {'additionalAuthorizedReplacementFiles':{}}
 extra=supplement['additionalAuthorizedReplacementFiles']
 if extra:
  assert supplement['baselineSha256']==sha(BASE), 'Supplement is not bound to this baseline'
  assert set(extra)=={f'episodes/message-queue/{n}' for n in ['captions.srt','render-result.json','mix-report.json','pronunciation.md','research.md','references.md','README.md']}, 'Unexpected supplement authorization paths'
  assert all(b['protectedFiles'][key]==old for key,old in extra.items()), 'Supplement original SHA differs from baseline'
 protected={key:old for key,old in b['protectedFiles'].items() if key not in extra}
 authorized_before={**b['authorizedReplacementFiles'],**extra}
 for key,old in protected.items():
  now=record(R/key)
  if now!=old:changes.append({'before':old,'after':now})
 unexpected=[]
 # All existing bytes remain protected. Addition/deletion is separately audited
 # for old sources, other publication directories and prior shared templates.
 for key,current in [('oldMqSourceFiles',old_source_files()),('otherPublishedFiles',other_published_files()),('priorSharedTemplateFiles',prior_shared_files())]:
  added=sorted(set(current)-set(b[key]));removed=sorted(set(b[key])-set(current))
  if added or removed:unexpected.append({'scope':key,'added':added,'removed':removed})
 pub_now={str(p.relative_to(R)) for p in (R/'episodes/message-queue').rglob('*') if p.is_file()}
 known=set(b['mqPublishedFilesAtBaseline'])|set(authorized_before)
 unapproved_new=sorted(pub_now-known)
 if unapproved_new:unexpected.append({'scope':'MQ publication files outside explicit authorization list','added':unapproved_new})
 authorized=[]
 for key,old in authorized_before.items():
  now=record(R/key)
  if now!=old:authorized.append({'before':old,'after':now})
 result={'schemaVersion':1,'checkedAt':stamp(),'baselineSha256':sha(BASE),'originalCoverOnlyBaselineSha256':sha(OLD),'baselineHead':b['head'],'currentHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'authorizedSupplementSha256':sha(SUPPLEMENT) if SUPPLEMENT.exists() else None,'authorizedOutputPaths':len(authorized_before),'protectedPaths':len(protected),'protectedUnchanged':len(protected)-len(changes),'unapprovedChanges':changes,'unexpectedScopeChanges':unexpected,'authorizedChangedFiles':authorized,'passed':not changes and not unexpected}
 p=W/'kafka-scope-verification.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({**result,'authorizedChangedFiles':[x['after']['path'] for x in authorized]},ensure_ascii=False,indent=2));sys.exit(not result['passed'])
assert not BASE.exists(),'Baseline is immutable once created; add a separately reviewed scope supplement instead.'
old=json.loads(OLD.read_text());assert old['head']==HEAD
protected={k:v for k,v in old['files'].items() if k not in ALLOWED and k not in POLICY_EXCLUDED}
# Old active revision cover images become immutable historical assets now.
for x in old['mutableOldCoverOutputs']:
 if x['path'] not in ALLOWED:protected[x['path']]=record(R/x['path'])
oldsource=old_source_files();other=other_published_files();shared=prior_shared_files()
for rel in oldsource+other+shared:protected[rel]=record(R/rel)
# Protect all existing MQ publication files that are outside the explicit list.
pub=sorted(str(p.relative_to(R)) for p in (R/'episodes/message-queue').rglob('*') if p.is_file())
for rel in pub:
 if rel not in ALLOWED:protected[rel]=record(R/rel)
authorized={rel:record(R/rel) for rel in sorted(ALLOWED)}
# Independently confirm old freeze files/inputs retain original cover-stage SHA.
for key,v in old['files'].items():
 if key not in ALLOWED and key not in POLICY_EXCLUDED:assert record(R/key)==v,('changed before new scope capture',key)
tracked=subprocess.check_output(['git','status','--porcelain','-uno'],cwd=R,text=True)
b={'schemaVersion':1,'purpose':'Explicit Kafka remake scope, captured before publication replacement. Old cover-only baseline remains byte-identical history. Only the enumerated MQ publication files are authorized for replacement/addition; newly created Kafka revision files require their own new freeze. All old root/mq-intro inputs, images, media and277old freeze declarations remain protected. Every other episode publication file remains protected, excluding dependency/cache directories.','capturedAt':stamp(),'head':HEAD,'currentTrackedStatusAtCapture':tracked,'originalCoverOnlyBaseline':str(OLD),'originalCoverOnlyBaselineSha256':sha(OLD),'oldFrozenManifestCount':2,'oldFrozenEntryCount':277,'authorizedBy':'Root task message explicitly listing20publication output paths on2026-10-28; any additions require a separate supplement, not a rewritten baseline.','policyFilesNotProtected':sorted(POLICY_EXCLUDED),'newRevisionPrefixNotOldProtectedContent':NEW_PREFIX,'excludedCacheDirectoryNames':sorted(SKIP_PARTS),'authorizedReplacementFiles':authorized,'protectedFiles':protected,'mqPublishedFilesAtBaseline':pub,'oldMqSourceFiles':oldsource,'otherPublishedFiles':other,'priorSharedTemplateFiles':shared,'summary':{'protectedUniquePaths':len(protected),'protectedStates':dict(Counter(x['state'] for x in protected.values())),'authorizedOutputPaths':len(authorized),'authorizedBaselineStates':dict(Counter(x['state'] for x in authorized.values())),'oldMqActualSourcePaths':len(oldsource),'otherPublishedPaths':len(other),'otherEpisodeDirectories':len({Path(x).parts[1] for x in other}),'priorSharedTemplateFiles':len(shared),'oldFreezeDeclarations':277}}
BASE.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'baseline':str(BASE),'sha256':sha(BASE),'summary':b['summary']},ensure_ascii=False,indent=2))
