from pathlib import Path
import hashlib, json, subprocess, datetime, sys
R=Path('/workspace/video-studio').resolve()
OUT=Path('/workspace/work/leetcode-cover-preservation-baseline.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
cache={}
def rec(p):
 p=p.resolve()
 try:rel=str(p.relative_to(R))
 except ValueError:return {'path':str(p),'state':'outside-repository-not-read'}
 if rel in cache:return cache[rel]
 if not p.exists(): d={'path':rel,'state':'missing'}
 elif not p.is_file():d={'path':rel,'state':'not-file'}
 else:d={'path':rel,'state':'present','bytes':p.stat().st_size,'sha256':sha(p)}
 cache[rel]=d;return d
if '--verify' in sys.argv:
 d=json.loads(OUT.read_text()); changed=[]; retained=[]
 for old in d['files'].values():
  new=rec(R/old['path'])
  if new!=old:changed.append({'before':old,'after':new})
  else:retained.append(old['path'])
 result={'baseline':str(OUT),'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'checked':len(d['files']),'unchanged':len(retained),'changes':changed,'passed':not changed}
 target=Path('/workspace/work/leetcode-cover-preservation-verification.json');target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({k:v for k,v in result.items() if k!='changes'},ensure_ascii=False));print('changes',json.dumps(changed[:20],ensure_ascii=False));sys.exit(bool(changed))
eps=[]
for p in (R/'episodes').glob('*/meta.json'):
 m=json.loads(p.read_text())
 if m.get('series')=='leetcode':eps.append((m['problemNumber'],p.parent.name))
eps.sort(); summaries=[]; explicit_names=['video.mp4','meta.json','script.md','article.mdx','storyboard.json','words.json','references.json','reference-appendix.json','reference-appendix-media-check.json','source-sha256.json','covers.json','render-result.json','remotion/src/Cover.tsx','remotion/scripts/covers.mjs','remotion/package.json','remotion/package-lock.json']
for number,slug in eps:
 explicit=[]
 for base in [R/'episodes'/slug,R/'episodes-codex'/slug]:
  for n in explicit_names:explicit.append(rec(base/n)['path'])
  art=base/'article'
  if art.exists():
   for f in art.rglob('*'):
    if f.is_file():explicit.append(rec(f)['path'])
 base=R/'episodes-codex'/slug; frozen=json.loads((base/'source-sha256.json').read_text()); entries=[]
 for k,expected in frozen.items():
  actual=rec(base/k)
  entries.append({'key':k,'expectedSha256':expected,'actualPath':actual['path'],'actualState':actual['state'],'matchesDeclared':actual.get('sha256')==expected if actual['state']=='present' else None})
 states={x:sum(e['actualState']==x for e in entries) for x in sorted(set(e['actualState'] for e in entries))}
 summaries.append({'problemNumber':number,'slug':slug,'explicitPaths':explicit,'frozenManifest':str((base/'source-sha256.json').relative_to(R)),'frozenEntries':entries,'counts':{'declared':len(entries),**states,'matchingDeclared':sum(e['matchesDeclared'] is True for e in entries),'presentMismatch':sum(e['matchesDeclared'] is False for e in entries)}})
d={'purpose':'Independent before-change preservation baseline for LeetCode cover-only refresh; generated covers deliberately excluded. Missing historical inputs retain missing status; declared hashes are not rewritten.','capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'episodes':summaries,'files':cache}
OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'baseline':str(OUT),'sha256':sha(OUT),'files':len(cache),'episodes':[{'slug':e['slug'],**e['counts']} for e in summaries]},ensure_ascii=False,indent=2))
