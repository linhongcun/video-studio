#!/usr/bin/env python3
"""Generate solution.json directly from solution.py so display and executable source match verbatim."""
import hashlib
import json
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
src = EP / 'solution.py'
text = src.read_text()
lines = text.splitlines()
out = {
    'source': 'solution.py',
    'sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
    'lineCount': len(lines),
    'lines': lines,
}
(EP / 'solution.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(f'Wrote solution.json ({len(lines)} lines, sha256={out["sha256"][:12]})')
