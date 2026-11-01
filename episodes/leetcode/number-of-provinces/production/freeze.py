"""Pin actual new-episode inputs; audio and core freeze algorithms stay shared."""

# Resolve episode storage independently of its series and revision depth.
import sys as _layout_sys
from pathlib import Path as _LayoutPath
_layout_root = next(parent for parent in _LayoutPath(__file__).resolve().parents
                    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
_layout_sys.path.insert(0, str(_layout_root / 'episodes/_shared'))
from episode_paths import production_directory, publication_directory, resolve_repo_path, episode_slug, resolve_frozen_path
from pathlib import Path
import hashlib,json,os,subprocess,sys
EP=Path(__file__).resolve().parent;ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if '--verify'in sys.argv:
 m=read(EP/'source-sha256.json')
 for rel,expected in m.items():assert sha(resolve_frozen_path(EP/'source-sha256.json', rel))==expected,rel
 print(f'{len(m)} frozen inputs unchanged.');raise SystemExit(0)
subprocess.run([sys.executable,str(ROOT/'episodes/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
m=read(EP/'source-sha256.json')
paths=[EP/n for n in ['solution.py','solution.json','prepare_code_endcard.py','render_body.py','freeze.py','references.json','remotion/scripts/qa.mjs','remotion/scripts/covers.mjs']]
paths += [p for p in (EP/'research').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
paths += [ROOT/'episodes/_shared'/n for n in ['render_with_references.py','append_references_bibliography.py','append_references_original.py','append_references.py','requirements-reference-appendix.txt']]
paths += [ROOT/'site/scripts/check-references.mjs',
          ROOT / 'episodes/_shared/episode_paths.py',
          ROOT / 'site/scripts/episode-paths.mjs']
for source in read(EP/'references.json')['sources']:
 paths += [resolve_repo_path(source['verification']['evidence'], root=ROOT),resolve_repo_path(source['titleEvidence']['evidence'], root=ROOT)]
 if source.get('quotation'):paths.append(resolve_repo_path(source['quotation']['evidence'], root=ROOT))
article=EP/'article-sources.json'
if article.exists():
 paths.append(article)
 for source in read(article)['sources']:
  paths += [resolve_repo_path(source['verification']['evidence'], root=ROOT),resolve_repo_path(source['quotation']['evidence'], root=ROOT)]
  if source.get('titleEvidence'):paths.append(resolve_repo_path(source['titleEvidence']['evidence'], root=ROOT))
for p in paths:m[os.path.relpath(p,EP)]=sha(p)
(EP/'source-sha256.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f'{len(m)} actual production inputs frozen.')
