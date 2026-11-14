import hashlib,json,os,subprocess,sys
from pathlib import Path
EP=Path(__file__).resolve().parent
ROOT=next(p for p in EP.parents if (p/'AGENTS.md').exists())
manifest=EP/'source-sha256.json'
subprocess.run([sys.executable,str(EP/'scripts/require_formal_inputs.py')],check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if '--verify' in sys.argv:
 data=json.loads(manifest.read_text())
 for rel,h in data.items():assert sha((EP/rel).resolve())==h,rel
 print(f'{len(data)} frozen inputs unchanged.');raise SystemExit
subprocess.run([sys.executable,str(ROOT/'episodes/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
m=json.loads(manifest.read_text())
files=['plan.json','episode-config.json','covers.json','solution.py','solution.json','merge_trace.py','trace/linear-example.json','scripts/build_trace.py','storyboard-design.md','visual-direction.md','references.json','script.md','article.mdx','pronunciation.md','research.md','research/source-evidence.json','README.md','assemble.py','prepare_code_endcard.py','render.py','render_body.py','references_bt709.py','freeze.py','../publication/article/01.svg','qa/independent-review-6967f6a.md','qa/independent-rereview-df13a3e.md','cover-inputs/catalog.json','cover-inputs/diagrams.mjs','voice/params.json']
source_suffixes={'.py','.ts','.tsx','.json'}
files += [str(p.relative_to(EP)) for folder in ['scripts'] for p in (EP/folder).rglob('*')
          if p.is_file() and p.suffix in source_suffixes and '__pycache__' not in p.parts]
files += [str(p.relative_to(EP)) for p in (EP/'remotion/src').rglob('*')
          if p.is_file() and p.suffix in source_suffixes and '__pycache__' not in p.parts]
for rel in files:
 p=EP/rel
 if p.is_file():m[rel]=sha(p)
for rel in ['episodes/_shared/assemble_sentence_episode.py','episodes/_shared/freeze_sentence_episode.py','episodes/_shared/leetcode-video/Frame.tsx','episodes/_shared/leetcode-video/theme.ts']:
 p=ROOT/rel;m[os.path.relpath(p,EP)]=sha(p)
for rel in ['episodes/_shared/render_with_references.py','episodes/_shared/append_references_bibliography.py',
            'episodes/_shared/append_references_original.py','episodes/_shared/append_references.py',
            'episodes/_shared/requirements-reference-appendix.txt','episodes/_shared/leetcode-video/references.py',
            'episodes/_shared/leetcode-video/style-v1.json','episodes/_shared/puzzles-video/references.py',
            'site/scripts/check-references.mjs']:
 p=ROOT/rel;m[os.path.relpath(p,EP)]=sha(p)
manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f'{len(m)} LC56 production inputs frozen.')
