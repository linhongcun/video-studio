#!/usr/bin/env python3
"""Invoke the current shared actual-media audit; no copied media-check algorithm."""
import argparse,datetime,hashlib,json,pathlib,subprocess,sys
Q=pathlib.Path(__file__).resolve().parent;D=Q.parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file())
H=ROOT/'docs/archive/2026-10/mq-source-depth-remake/qa/final-independent.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true',required=True,help='Only after root announces final media ready.');a=p.parse_args()
spec=json.loads((Q/'sample-spec.json').read_text())
for name,expected in spec['sourceIdentity'].items():
 assert sha(D/name)==expected, f'Prepared frozen identity changed: {name}'
manifest=json.loads((D/'source-sha256.json').read_text())
for name,expected in manifest.items():assert sha((D/name).resolve())==expected, f'Frozen input changed: {name}'
for name in ['video.mp4','render-result.json','reference-appendix.json']:assert (D/name).is_file(), f'Actual final output missing: {name}'
assert not (Q/'encoded-independent.json').exists(), 'Preserve existing actual audit; do not overwrite it.'
command=[sys.executable,str(H),str(D),'--spec',str(Q/'sample-spec.json'),'--out-dir','qa-final-independent']
inv={'startedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sharedHelper':str(H.relative_to(ROOT)),'sharedHelperSHA256':sha(H),'thinEntrySHA256':sha(pathlib.Path(__file__)),'command':command,'preFrozenInputs':len(manifest),'preFrozenManifestSHA256':sha(D/'source-sha256.json'),'status':'running'}
(Q/'invocation.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n')
r=subprocess.run(command,cwd=ROOT);inv['exit']=r.returncode;inv['finishedAtUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();inv['status']='machine-failed'if r.returncode else'machine-completed-awaiting-actual-visual-review'
if r.returncode==0:
 for name,expected in manifest.items():assert sha((D/name).resolve())==expected, f'Frozen input changed during audit: {name}'
 report=json.loads((Q/'encoded-independent.json').read_text());assert all(report['format'].get(k)==v for k,v in {'pix_fmt':'yuv420p','color_space':'bt709','color_transfer':'bt709','color_primaries':'bt709','color_range':'tv'}.items()), 'Final five color fields differ'
 inv['postFrozenInputsUnchanged']=True;inv['videoSHA256']=report['videoSHA256'];inv['visualReviewed']=False
(Q/'invocation.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n')
sys.exit(r.returncode)
