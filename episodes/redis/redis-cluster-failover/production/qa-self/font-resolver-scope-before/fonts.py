#!/usr/bin/env python3
"""Record exact resolved production fonts; --verify only reads, never repairs."""
from pathlib import Path
import argparse,hashlib,json,subprocess
D=Path(__file__).resolve().parent;P=D/'font-environment.json'
queries=['Noto Sans CJK SC:style=Regular','Noto Sans CJK SC:style=Bold','Noto Sans Mono:style=Regular','Noto Sans Mono CJK SC:style=Bold','DejaVu Sans:style=Bold']
def actual():
    rows=[]
    for q in queries:
        path=Path(subprocess.check_output(['fc-match','-f','%{file}',q],text=True).strip())
        rows.append(dict(query=q,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
    return dict(kind='actual fontconfig resolution; system font bytes are not vendored',fonts=rows)
p=argparse.ArgumentParser(__doc__);p.add_argument('--verify',action='store_true');a=p.parse_args();v=actual()
if a.verify:assert v==json.loads(P.read_text()),'Actual font bytes/resolution changed'
else:
    assert not P.exists(),'Preserve prior font ledger'
    P.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(passed=True,fonts=len(v['fonts']),readOnly=a.verify)))
