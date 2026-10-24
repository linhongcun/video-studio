"""Pinned historical inputs for the EP.14 v0.45.0 regression tests.

Live episodes/degradation is free to evolve. These bytes come from the named
Git revision and are checked before running the existing golden assertions.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / 'episodes/_shared/tests/fixtures/degradation-v0.45.0'
REVISION = 'c1da2a1eef696d8bd08c9b078d7b833d75308498'


def historical_degradation():
    manifest = json.loads((FIXTURE / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['sourceRevision'] == REVISION, 'historical fixture revision changed'
    for name, expected in manifest['files'].items():
        path = FIXTURE / name
        assert path.is_file() and not path.is_symlink(), f'missing physical fixture: {name}'
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, f'historical fixture changed: {name}'
    return FIXTURE
