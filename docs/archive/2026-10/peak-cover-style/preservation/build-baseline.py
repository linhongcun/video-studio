from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path('/workspace/video-studio');OUT=Path('/workspace/work/peak-cover-qa');BASE='d3c163eff2a550255e8c81c1eea631178b7aaa58'
SLUGS=['rate-limit','idempotency','circuit-breaker','degradation']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def rel(p):return str(p.relative_to(ROOT))
tracked=set(filter(None,subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z']).decode().split('\0')))
assert subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()==BASE
allowed_images=set();allowed_sidecars=set();contracts=[]
for slug in SLUGS:
 meta=json.loads((ROOT/'episodes'/slug/'meta.json').read_text());assert meta['series']=='peak';production=str(Path(meta['sourcePath']).parent);assert production=='episodes-codex/'+slug
 roots=[(production,['png','jpg']),('episodes/'+slug,['jpg'])]
 for root,exts in roots:
  images=[root+'/cover-'+s+'.'+ext for s in ['16x9','3x4','4x3'] for ext in exts]+[root+'/poster.jpg']
  allowed_images.update(images);allowed_sidecars.add(root+'/cover-style.json')
  contracts.append({'slug':slug,'root':root,'images':images,'sidecar':root+'/cover-style.json'})
protected={n for n in tracked if n.startswith('episodes/') or any(n.startswith('episodes-codex/'+s+'/') for s in SLUGS) or n.endswith('/source-sha256.json') or n.startswith('episodes-codex/_shared/')}
for n in tracked:
 if n.startswith('episodes-codex/') and Path(n).name in {'cover-16x9.png','cover-16x9.jpg','cover-3x4.png','cover-3x4.jpg','cover-4x3.png','cover-4x3.jpg','poster.jpg','cover-style.json'}:protected.add(n)
protected-=allowed_images|allowed_sidecars
freezes=[];frozen_paths=set();frozen_findings=[]
for slug in SLUGS:
 for p in sorted((ROOT/'episodes-codex'/slug).glob('**/source-sha256.json')):
  d=json.loads(p.read_text());entries=[]
  for key,value in d.items():
   assert isinstance(value,str) and len(value)==64,(p,key)
   q=(p.parent/key).resolve();assert q.is_relative_to(ROOT),(p,key)
   n=rel(q);frozen_paths.add(n);protected.add(n)
   found=sha(q) if q.is_file() else None
   e={'key':key,'path':n,'expectedSha256':value,'exists':q.is_file(),'actualSha256':found,'matched':found==value};entries.append(e)
   if not e['matched']:frozen_findings.append({'manifest':rel(p),**e})
  freezes.append({'manifest':rel(p),'declarations':len(entries),'entries':entries})
assert not ((allowed_images|allowed_sidecars)&frozen_paths)
records={}
for n in sorted(protected):
 p=ROOT/n
 records[n]={'exists':p.exists(),'isSymlink':p.is_symlink(),'sha256':sha(p) if p.is_file() else None,'bytes':p.stat().st_size if p.is_file() else None}
meta_paths=[n for n in tracked if n.startswith('episodes/') and n.endswith('/meta.json')]
base={'schemaVersion':1,'recordedAt':datetime.now(timezone.utc).isoformat(),'baseSha':BASE,'scope':'Cover-only protection captured before installation; do not rewrite to bless changed outputs.','slugs':SLUGS,'allowedImages':sorted(allowed_images),'allowedSidecars':sorted(allowed_sidecars),'outputContracts':contracts,'protected':records,'publishedMeta':{n:records[n] for n in sorted(meta_paths)},'frozenManifests':freezes,'frozenFindings':frozen_findings,'frozenTargetIntersection':sorted((allowed_images|allowed_sidecars)&frozen_paths)}
p=OUT/'protection-baseline.json';assert not p.exists(),'Baseline already captured; never overwrite.';p.write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n')
summary={'baseSha':BASE,'baselineSha256':sha(p),'protectedPaths':len(records),'allowedImages':len(allowed_images),'allowedSidecars':len(allowed_sidecars),'publishedMeta':len(meta_paths),'freezeCounts':{f['manifest']:f['declarations'] for f in freezes},'frozenDeclarations':sum(f['declarations'] for f in freezes),'frozenFindings':frozen_findings,'frozenTargetIntersection':base['frozenTargetIntersection']}
(OUT/'baseline-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2))
