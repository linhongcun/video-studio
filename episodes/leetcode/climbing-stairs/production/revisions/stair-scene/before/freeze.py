"""Freeze with the shared implementation, then include this episode's display/QA inputs."""
from pathlib import Path
import hashlib,json,subprocess,sys
EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
if '--verify' in sys.argv:
    m=json.loads((EP/'source-sha256.json').read_text())
    for rel,expected in m.items():
        assert hashlib.sha256((EP/rel).read_bytes()).hexdigest()==expected,rel
    print(f'{len(m)} frozen inputs unchanged.')
    raise SystemExit(0)
subprocess.run([sys.executable,str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
f=EP/'source-sha256.json'
m=json.loads(f.read_text())
for name in ['solution.py','solution.json','prepare_code_endcard.py','freeze.py','research/verify_algorithm.py','remotion/scripts/qa.mjs','remotion/scripts/covers.mjs']:
    m[name]=hashlib.sha256((EP/name).read_bytes()).hexdigest()
f.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f'{len(m)} total frozen inputs including executable/display source.')
