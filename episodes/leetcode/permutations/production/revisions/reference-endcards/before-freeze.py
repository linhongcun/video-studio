from pathlib import Path
import json,hashlib,subprocess,sys,os
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1]
if '--verify' in sys.argv:
 m=json.loads((EP/'source-sha256.json').read_text())
 for rel,expected in m.items():assert hashlib.sha256((EP/rel).read_bytes()).hexdigest()==expected,rel
 print(f'{len(m)} frozen inputs unchanged.');raise SystemExit(0)
subprocess.run([sys.executable,str(ROOT/'episodes-codex/_shared/freeze_sentence_episode.py'),str(EP)],check=True)
m=json.loads((EP/'source-sha256.json').read_text())
extra=[EP/n for n in ['solution.py','solution.json','prepare_code_endcard.py','freeze.py','remotion/scripts/qa.mjs','remotion/scripts/covers.mjs']]
extra += [p for p in (EP/'research').rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md']]
extra += [ROOT/'docs/leetcode-batch-next/prepare_audio.py',ROOT/'docs/leetcode-batch-next/approved-scripts.json']
for p in extra:m[os.path.relpath(p,EP)]=hashlib.sha256(p.read_bytes()).hexdigest()
(EP/'source-sha256.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f'{len(m)} actual production inputs frozen.')
