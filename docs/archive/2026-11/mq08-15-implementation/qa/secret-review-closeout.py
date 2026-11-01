#!/usr/bin/env python3
"""Run the existing review unchanged, redirecting only its fixed report output."""
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone
import hashlib
import json
import runpy

A = Path(__file__).resolve().parent.parent
original = A / 'qa/secret-review.json'
target = A / 'qa/secret-review-final-closeout.json'
assert not target.exists()
before = original.read_bytes()
mtime = original.stat().st_mtime_ns
write_text = Path.write_text
writes = []


def redirect(path, content, *args, **kwargs):
    assert path.resolve() == original, 'Only the known report output may be redirected'
    writes.append(str(path))
    return write_text(target, content, *args, **kwargs)


with patch.object(Path, 'write_text', redirect):
    runpy.run_path(str(A / 'secret-review.py'), run_name='__main__')
assert len(writes) == 1
assert original.read_bytes() == before and original.stat().st_mtime_ns == mtime
report = json.loads(target.read_text())
assert report['passed'] and len(report['approvedPublicSourceMatches']) == 48
assert report['unresolved'] == [] and report['canonicalRuleSetUnchanged']
meta = {'atUTC': datetime.now(timezone.utc).isoformat(),
        'scope': 'Exact existing checker and classifications; only output path redirected, no historical report/source/rule modified.',
        'originalReportSHA256': hashlib.sha256(before).hexdigest(),
        'freshReportSHA256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'originalReportBytesAndMtimePreserved': True}
write_text(A / 'qa/secret-review-closeout-output.json', json.dumps(meta, indent=2) + '\n')
