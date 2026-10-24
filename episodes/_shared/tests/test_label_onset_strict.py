#!/usr/bin/env python3
"""Synthetic selftest plus historical EP.14 v0.45.0 label-onset regression."""
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from degradation_fixture import historical_degradation

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'episodes' / '_shared'))
import label_onset_strict as L

GOLDEN = ROOT / 'episodes' / '_shared' / 'tests' / 'golden' / 'degradation.label-onset-strict.txt'
EXPECTED = 'aaf507b3200a7bd4c80e7389d3710aa3d352ff974e0c41cb05104f9471f27344'


def regression():
    ep = historical_degradation()
    need = [
        ep / 'storyboard.json',
        ep / 'words.json',
        ep / 'remotion/public/audio/voice.wav',
    ]
    missing = [p for p in need if not p.exists()]
    if missing:
        print('skip degradation label regression, missing:', ', '.join(str(p.relative_to(ROOT)) for p in missing))
        return
    out = Path(tempfile.mkdtemp(prefix='label-reg-')) / 'x.txt'
    r = subprocess.run(
        [sys.executable, str(ROOT / 'episodes/_shared/label_onset_strict.py'),
         '--dir', str(ep), '--out', str(out)],
        cwd=ROOT, check=False)
    assert r.returncode == 0, r.returncode
    got = out.read_bytes()
    exp = GOLDEN.read_bytes()
    assert got == exp, hashlib.sha256(got).hexdigest()
    assert hashlib.sha256(got).hexdigest() == EXPECTED
    assert len(got) == 11026
    print('degradation label-onset-strict.txt matches golden')


def main():
    L.selftest()
    regression()
    print('test_label_onset_strict ok')


if __name__ == '__main__':
    main()
