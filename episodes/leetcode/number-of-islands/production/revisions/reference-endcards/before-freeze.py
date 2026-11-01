from pathlib import Path
import hashlib,json,subprocess,sys
EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
if '--verify' in sys.argv:
    manifest=json.loads((EP/'source-sha256.json').read_text())
    for rel,expected in manifest.items():
        assert hashlib.sha256((EP/rel).read_bytes()).hexdigest()==expected,rel
    print(f'{len(manifest)} frozen inputs unchanged.')
    raise SystemExit(0)
subprocess.run([sys.executable,str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
p=EP/'source-sha256.json';manifest=json.loads(p.read_text())
for name in ['solution.py','solution.json','prepare_code_endcard.py','freeze.py','research/verify_algorithm.py','research/generate_demo_trace.py','research/demo-trace.json','research/source-access.json','research/algorithm-verification.json','research/TRACE.md','remotion/scripts/qa.mjs','remotion/scripts/covers.mjs','voice/jobs-boundary.json','voice/boundary-padding.json','splice-boundary.py','splice-plan.json','reuse-proof.json','revisions/boundary-before/video.mp4','revisions/boundary-before/storyboard.json','revisions/boundary-before/baseline.json']:
    manifest[name]=hashlib.sha256((EP/name).read_bytes()).hexdigest()
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'{len(manifest)} total production inputs frozen.')
