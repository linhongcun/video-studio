import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'solution.py'
data={'language':'python','source':'solution.py','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'lines':source.read_text().splitlines()}
(root/'solution.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(f'Built {len(data["lines"])} exact source lines.')
