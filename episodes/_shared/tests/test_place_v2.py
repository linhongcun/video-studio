#!/usr/bin/env python3
"""Synthetic selftest plus the EP.14 whole-track regression. Does not write into the episode."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'episodes' / '_shared'))
import place_v2

EXPECTED = '9e70470c096c4198f679eceb5323b0cd9f90323784e7dad284dc43c47265468b'


def regression():
    src = ROOT / 'episodes/degradation/remotion/public/audio/voice.wav'
    sb = ROOT / 'episodes/degradation/storyboard.json'
    if not src.exists() or not sb.exists():
        print('skip degradation place regression, missing voice.wav or storyboard.json')
        return
    before = hashlib.sha256(src.read_bytes()).hexdigest()
    td = Path(tempfile.mkdtemp(prefix='place-reg-'))
    copied = td / 'v.wav'
    report = td / 'r.json'
    r = subprocess.run(
        [sys.executable, str(ROOT / 'episodes/_shared/place_v2.py'),
         '--dir', str(ROOT / 'episodes/degradation'), '--mode', 'whole',
         '--src', str(src), '--copy-to', str(copied), '--report', str(report)],
        cwd=ROOT, check=False)
    assert r.returncode == 0, r.returncode
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before
    assert hashlib.sha256(copied.read_bytes()).hexdigest() == EXPECTED
    assert not copied.is_symlink()
    rep = json.loads(report.read_text())
    assert rep['maxOffsetFrames'] == 0.48, rep
    assert rep['violations'] == []
    assert rep['sha'] == EXPECTED
    assert rep['frames'] == 5152 and rep['samples'] == 8243200
    print('degradation whole-track copy matches', EXPECTED[:16])


def main():
    place_v2.selftest()
    regression()
    print('test_place_v2 ok')


if __name__ == '__main__':
    main()
