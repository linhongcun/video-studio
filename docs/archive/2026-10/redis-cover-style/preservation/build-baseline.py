from pathlib import Path
import json,subprocess,hashlib,shutil
from datetime import datetime,timezone
R=Path('/workspace/video-studio'); W=Path('/workspace/work/redis-cover-qa')
BASE='2b418a9da0155fb29357c186238ed78feab0b8ed'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==BASE
files=subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0'); files=[p for p in files if p]
cur='episodes-codex/redis-skiplist/revisions/height-choice/redis-skiplist'
allow=[f'episodes/redis-skiplist/cover-{size}.jpg' for size in ['16x9','3x4','4x3']]+[f'{cur}/cover-{size}.{ext}' for size in ['16x9','3x4','4x3'] for ext in ['png','jpg']]
newallow=[f'{d}/{name}' for d in ['episodes/redis-skiplist',cur] for name in ['cover.png','cover-style.json']]
assert set(allow)<=set(files)
protected=set(p for p in files if p.startswith('episodes/') or p.startswith('episodes-codex/redis-skiplist/') or p.endswith('source-sha256.json'))-set(allow)
freezes=[R/'episodes-codex/redis-skiplist/source-sha256.json',R/'episodes-codex/redis-skiplist/revisions/clear-parts/redis-skiplist/source-sha256.json',R/cur/'source-sha256.json']
freeze_details=[]
for m in freezes:
 v=json.loads(m.read_text()); rows=[]
 for key,expected in v.items():
  p=(m.parent/key).resolve(); assert p.is_relative_to(R)
  rel=p.relative_to(R).as_posix(); exists=p.is_file(); actual=hashlib.sha256(p.read_bytes()).hexdigest() if exists else None
  rows.append({'key':key,'path':rel,'expectedSha256':expected,'exists':exists,'actualSha256':actual,'matchesDeclared':actual==expected})
  if exists: protected.add(rel)
 freeze_details.append({'manifest':m.relative_to(R).as_posix(),'manifestSha256':hashlib.sha256(m.read_bytes()).hexdigest(),'declarations':len(v),'present':sum(x['exists'] for x in rows),'matches':sum(x['matchesDeclared'] for x in rows),'rows':rows})
assert not protected.intersection(allow)
entries={}
for rel in sorted(protected):
 p=R/rel
 if p.is_symlink(): raw=str(p.readlink()).encode(); kind='symlink'
 else: raw=p.read_bytes(); kind='file'
 entries[rel]={'kind':kind,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
meta=[]
for p in sorted((R/'episodes').glob('*/meta.json')):
 v=json.loads(p.read_text()); meta.append({'path':p.relative_to(R).as_posix(),'meta':v,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
by_name={p.stem:p for p in []}
v={'checkedAt':datetime.now(timezone.utc).isoformat(),'baseSha':BASE,'branch':'codex/redis-cover-style','scope':'Redis cover-only baseline; actual current media/source identity stays unchanged. Protect all tracked publishing files except 3 authorized Redis JPG outputs, all tracked old/current Redis production except 6 current image outputs, all 260 tracked source-sha256 manifests and additional real Redis frozen dependencies. Copied provenance manifests protected as historical bytes, not re-resolved as fresh freeze declarations.','allowedExistingOutputChanges':allow,'allowedNewPairedOutputs':newallow,'metaChangesAuthorized':False,'protectedPathCount':len(entries),'protected':entries,'publicationMetadataCount':len(meta),'publicationMetadata':meta,'redisFreezeManifests':freeze_details}
(W/'protection-baseline.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for name in ['redis-issue-search.json','redis-issue-body-search.json']:
 shutil.copyfile(W.parent/name,W/name)
summary={'baseSha':BASE,'protectedPathCount':len(entries),'publishingTrackedFiles':sum(p.startswith('episodes/') for p in files),'redisTrackedSourceFiles':sum(p.startswith('episodes-codex/redis-skiplist/') for p in files),'allTrackedFrozenManifestFiles':sum(p.endswith('source-sha256.json') for p in files),'authorizedExistingImages':len(allow),'newOutputs':newallow,'publicationMetadataCount':len(meta),'redisSeriesCount':sum(x['meta'].get('series')=='redis' for x in meta),'freezeSummary':[{k:x[k] for k in ['manifest','declarations','present','matches']} for x in freeze_details],'baselineSha256':hashlib.sha256((W/'protection-baseline.json').read_bytes()).hexdigest()}
(W/'baseline-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
