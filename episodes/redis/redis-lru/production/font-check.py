#!/usr/bin/env python3
"""Pin actual system font bytes used by this episode; verify never rewrites."""
from pathlib import Path
import subprocess,json,hashlib,sys
D=Path(__file__).resolve().parent
requests=['Noto Sans CJK SC:style=Regular','Noto Sans CJK SC:style=Bold','Noto Sans Mono:style=Regular','Noto Sans Mono:style=Bold','DejaVu Sans:style=Book','DejaVu Sans:style=Bold']
rows=[]
for request in requests:
    raw=subprocess.check_output(['fc-match','-f','%{file}\n%{family}\n%{style}\n',request],text=True).splitlines()
    path=Path(raw[0]);assert path.is_file(),request
    rows.append(dict(request=request,path=str(path),family=raw[1],style=raw[2],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
record={'fontconfigResolved':True,'fonts':rows,'scope':'Actual font file hashes; not a visual text legibility claim.'}
file=D/'font-environment.json'
if '--verify' in sys.argv:assert json.loads(file.read_text())==record,'Current font environment differs'
else:assert not file.exists(),'Preserve prior font identity';file.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'passed':True,'fonts':len(rows),'readOnly':'--verify' in sys.argv}))
