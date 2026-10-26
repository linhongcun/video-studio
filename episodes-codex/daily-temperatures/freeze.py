"""Freeze this revision's actual shared-voice and bounded-render dependencies."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if '--verify' in sys.argv:
    m=read(EP/'source-sha256.json')
    for rel,expected in m.items():assert sha(EP/rel)==expected,rel
    print(f'{len(m)} frozen inputs unchanged.');raise SystemExit(0)
subprocess.run([sys.executable,str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
m=read(EP/'source-sha256.json')
paths=[EP/n for n in ['solution.py','solution.json','prepare_code_endcard.py','freeze.py','render_derive.py','derive-render-changes.json','voice/derive-provenance.json','voice/derive-phase-alignment.json','revisions/derive-before/baseline.json','revisions/derive-before/body-recovery.json','references.json','reference-appendix-plan.json','remotion/scripts/qa.mjs','remotion/scripts/covers.mjs']]
paths += [p for p in (EP/'research').rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md']]
paths += [ROOT/'docs/daily-derive'/n for n in ['prepare_audio.py','editorial-approval.json']]
paths += [ROOT/'episodes-codex/_shared'/n for n in ['remix_approach.py','render_with_references.py','append_references.py','append_references_original.py','append_references_bibliography.py','requirements-reference-appendix.txt']]
paths += [ROOT/'site/scripts/check-references.mjs']
for source in read(EP/'references.json')['sources']:
    paths += [ROOT/source['verification']['evidence'],ROOT/source['titleEvidence']['evidence']]
    if 'quotation' in source:paths.append(ROOT/source['quotation']['evidence'])
for row in read(EP/'voice/derive-provenance.json')['rows']:
    for item in row['files']:
        paths += [EP/item[k] for k in ['source','target']]
paths += [EP/'voice/derive-mini'/n for n in ['script.md','editorial-approval.json','voice/params.json','voice/sents.json']]
plan=EP/'derive-remix-plan.json'
if plan.is_file():
    data=read(plan);paths += [plan]+[EP/n for n in data['inputSHA256']]
    review=EP/data['visualReview']
    if review.is_file():paths.append(review)
for path in paths:m[os.path.relpath(path,EP)]=sha(path)
(EP/'source-sha256.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f'{len(m)} actual revision inputs frozen.')
