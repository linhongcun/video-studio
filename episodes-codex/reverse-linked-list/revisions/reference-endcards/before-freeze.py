"""Freeze this approach revision; --preflight excludes not-yet-produced splice inputs."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
manifest=EP/'source-sha256.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if '--verify' in sys.argv:
 m=json.loads(manifest.read_text())
 for rel,expected in m.items():
  p=(EP/rel).resolve();assert p.is_file() and sha(p)==expected,rel
 print(f'{len(m)} frozen inputs unchanged.')
 raise SystemExit(0)
subprocess.run([sys.executable,str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
m=json.loads(manifest.read_text())
extra=[EP/n for n in ['solution.py','solution.json','prepare_code_endcard.py','freeze.py','remotion/scripts/qa.mjs','remotion/scripts/covers.mjs','revisions/approach-first/baseline.json','revisions/approach-first/baseline-identity.json','revisions/approach-first/voice-reuse.json','revisions/approach-first/algorithm-preservation.json']]
extra += [ROOT/'docs/leetcode-derivation-20261025/prepare_voice_revision.py',ROOT/'episodes-codex/_shared/remix_approach.py']
if '--preflight' not in sys.argv:
 plan=json.loads((EP/'approach-remix-plan.json').read_text())
 assert all(clip['sha256'] for clip in plan['clips']),'Render all changed clips before the final splice freeze'
 assert (EP/plan['visualReview']).is_file(),'Independent visual-reuse review required'
 extra += [(EP/name).resolve() for name in plan['freezeRequirements']['files']]
for p in extra:
 assert p.is_file(),p
 m[os.path.relpath(p,EP)]=sha(p)
manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
if '--preflight' in sys.argv:
 shutil.copy2(manifest,EP/'revisions/approach-first/preflight-source-sha256.json')
 print(f'{len(m)} preflight inputs; final freeze must add actual splice clips/plan/review.')
else:print(f'{len(m)} complete frozen inputs including actual splice dependencies.')
