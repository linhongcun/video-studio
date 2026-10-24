#!/usr/bin/env python3
"""Synthetic skeleton selftest plus historical EP.14 v0.45.0 knoll-props."""
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from degradation_fixture import historical_degradation

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'episodes' / '_shared'))
import make_knoll_props as K

EXPECTED = '2a5e56ee22d3e2ba4d9e237950d6299dd8efe8bab8c07c1d4e02c3a8ef7d7bd1'


def regression():
    ep = historical_degradation()
    sb = ep / 'storyboard.json'
    cv = ep / 'covers.json'
    example = ROOT / 'docs/examples/knoll-props.degradation.md'
    spec = ROOT / 'docs/examples/knoll_props_spec.degradation.py'
    if not sb.exists() or not cv.exists() or not example.exists():
        print('skip degradation knoll-props regression, missing storyboard, covers, or example')
        return
    body = ''.join(example.read_text(encoding='utf-8').splitlines(keepends=True)[8:]).encode()
    out = Path(tempfile.mkdtemp(prefix='knoll-reg-')) / 'kp.md'
    r = subprocess.run(
        [sys.executable, str(ROOT / 'episodes/_shared/make_knoll_props.py'),
         '--dir', str(ep), '--spec', str(spec), '--out', str(out)],
        cwd=ROOT, check=False, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout
    assert 'knoll-props ok 6265993b' in r.stdout, r.stdout
    got = out.read_bytes()
    assert got == body, hashlib.sha256(got).hexdigest()
    assert hashlib.sha256(got).hexdigest() == EXPECTED
    print(r.stdout.strip())
    print('degradation knoll-props matches tail -n +9')


def main():
    K.selftest()
    regression()
    print('test_make_knoll_props ok')


if __name__ == '__main__':
    main()
