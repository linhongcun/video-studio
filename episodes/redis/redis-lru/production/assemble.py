#!/usr/bin/env python3
"""Use current shared sentence/onset assembly, then select immutable Redis style."""
from pathlib import Path
import hashlib,json,subprocess,sys
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file() and (p/'site/package.json').is_file())
subprocess.run([sys.executable,str(ROOT/'episodes/_shared/assemble_sentence_episode.py'),str(D)],check=True)
path=D/'storyboard.json';original=path.read_bytes();board=json.loads(original)
style=json.loads((ROOT/'episodes/_shared/redis-video/style-v1.json').read_text())
board['meta']['palette']={'bg':style['palette']['background'],'text':style['palette']['text']}
board['meta']['styleContract']='episodes/_shared/redis-video/style-v1.json'
for scene in board['scenes']:
    for shot in scene['shots']:shot['timing']['holdReason']='Natural sentence pauses and planned action holds; no universal shot minimum.'
path.write_text(json.dumps(board,ensure_ascii=False,indent=2)+'\n')
(D/'storyboard-metadata-adaptation.json').write_text(json.dumps({'sharedAssemblySHA256':hashlib.sha256(original).hexdigest(),'adaptedSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'changedFields':['meta.palette','meta.styleContract','shots[].timing.holdReason'],'timingOrNarrationChanged':False},ensure_ascii=False,indent=2)+'\n')
