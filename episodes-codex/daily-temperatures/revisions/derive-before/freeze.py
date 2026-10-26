from pathlib import Path
import json,hashlib,subprocess,sys,os
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1]
if '--verify' in sys.argv:
 m=json.loads((EP/'source-sha256.json').read_text())
 for rel,expected in m.items():assert hashlib.sha256((EP/rel).read_bytes()).hexdigest()==expected,rel
 print(f'{len(m)} frozen inputs unchanged.');raise SystemExit(0)
subprocess.run([sys.executable,str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
m=json.loads((EP/'source-sha256.json').read_text())
extra=[EP/n for n in ['solution.py','solution.json','build_draft.py','prepare_code_endcard.py','freeze.py','remotion/scripts/qa.mjs','remotion/scripts/covers.mjs','render_problem_fit.py']]
extra += [p for p in (EP/'research').rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md']]
# This revision uses a separate thin voice orchestrator, not the initial batch.
extra += [ROOT/'docs/daily-monostack-opening'/n for n in
          ['prepare_audio.py','editorial-approval.json']]
extra += [EP/'voice/problem-fit-provenance.json', EP/'voice/problem-fit-phase-alignment.json', EP/'revisions/problem-fit-opening-before/baseline.json', EP/'revisions/problem-fit-opening-before/body-recovery.json', EP/'revisions/problem-fit-opening-before/article-snapshot-supplement.json']
# The shared splice tool pins all actual old/new pictures, source snapshots and
# selected takes. Add its final plan only after review/clip generation, never
# rewrite a freeze to claim old media used a different visual source.
plan_path=EP/'problem-fit-remix-plan.json'
if plan_path.is_file():
 plan=json.loads(plan_path.read_text());extra += [plan_path]
 extra += [EP/rel for rel in plan['inputSHA256']]
 review=EP/plan['visualReview']
 if review.is_file():extra.append(review)
# Default reference appendix is required for this replaced MP4.
extra += [EP/'references.json', EP/'article.mdx', EP/'remotion/package.json',
          EP/'reference-appendix-plan.json', ROOT/'episodes-codex/_shared/render_with_references.py',
          ROOT/'episodes-codex/_shared/append_references_original.py',
          ROOT/'episodes-codex/_shared/append_references.py',
          ROOT/'episodes-codex/_shared/requirements-reference-appendix.txt',
          ROOT/'site/scripts/check-references.mjs',
          ROOT/'episodes/_shared/theme/pageTheme.ts']
for source in json.loads((EP/'references.json').read_text())['sources']:
 evidence_paths=[source['verification']['evidence'],source['titleEvidence']['evidence']]
 if 'quotation' in source:evidence_paths.append(source['quotation']['evidence'])
 extra += [ROOT/evidence for evidence in evidence_paths]
extra += [ROOT/'episodes-codex/_shared/append_references_bibliography.py']
for p in extra:m[os.path.relpath(p,EP)]=hashlib.sha256(p.read_bytes()).hexdigest()
(EP/'source-sha256.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f'{len(m)} actual production inputs frozen.')

# Pin the actual selected source/target triples, including the approved four-take seed.
provenance=json.loads((EP/'voice/problem-fit-provenance.json').read_text())
for row in provenance['rows']:
 for item in row['files']:
  for field in ['source','target']:
   p=EP/item[field];m[os.path.relpath(p,EP)]=hashlib.sha256(p.read_bytes()).hexdigest()
for rel in ['script.md','editorial-approval.json','voice/params.json','voice/sents.json']:
 p=EP/'voice/opening-mini'/rel;m[os.path.relpath(p,EP)]=hashlib.sha256(p.read_bytes()).hexdigest()
(EP/'source-sha256.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f'{len(m)} actual opening-revision inputs frozen.')
