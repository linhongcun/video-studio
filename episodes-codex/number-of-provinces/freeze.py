"""Pin actual new-episode inputs; audio and core freeze algorithms stay shared."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if '--verify'in sys.argv:
 m=read(EP/'source-sha256.json')
 for rel,expected in m.items():assert sha(EP/rel)==expected,rel
 print(f'{len(m)} frozen inputs unchanged.');raise SystemExit(0)
subprocess.run([sys.executable,str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
m=read(EP/'source-sha256.json')
paths=[EP/n for n in ['solution.py','solution.json','prepare_code_endcard.py','render_body.py','freeze.py','references.json','remotion/scripts/qa.mjs','remotion/scripts/covers.mjs']]
paths += [p for p in (EP/'research').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
paths += [ROOT/'episodes-codex/_shared'/n for n in ['render_with_references.py','append_references_bibliography.py','append_references_original.py','append_references.py','requirements-reference-appendix.txt']]
paths += [ROOT/'site/scripts/check-references.mjs']
for source in read(EP/'references.json')['sources']:
 paths += [ROOT/source['verification']['evidence'],ROOT/source['titleEvidence']['evidence']]
 if source.get('quotation'):paths.append(ROOT/source['quotation']['evidence'])
article=EP/'article-sources.json'
if article.exists():
 paths.append(article)
 for source in read(article)['sources']:
  paths += [ROOT/source['verification']['evidence'],ROOT/source['quotation']['evidence']]
  if source.get('titleEvidence'):paths.append(ROOT/source['titleEvidence']['evidence'])
for p in paths:m[os.path.relpath(p,EP)]=sha(p)
(EP/'source-sha256.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f'{len(m)} actual production inputs frozen.')
