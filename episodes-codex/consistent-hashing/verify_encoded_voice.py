#!/usr/bin/env python3
"""Audit EA01's encoded voice through the retained, pinned read-only checker.

This wrapper does not build or reassemble audio. It redirects only the checker
module's EPISODE/ROOT, and annotates the newly produced QA report with the real
executor and implementation provenance. The existing waveform/lag/two-source
algorithms and pass criteria are not copied or changed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

EPISODE = Path(__file__).resolve().parent
ROOT = EPISODE.parents[1]
SOURCE = ROOT / 'episodes-codex/egg-drop/verify_encoded_voice.py'
SOURCE_SHA256 = '055846dda7e983d569c0360dc36f74ff6a99e086ca2de3efec1daea5a0ff5f6b'
REPORT = EPISODE / 'qa-encoded-voice-content.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executor', default='Codex (EA01 read-only audio checker)',
                        help='Actual operator or agent running this audit')
    args = parser.parse_args()
    assert SOURCE.is_file(), f'Retained read-only checker is missing: {SOURCE}'
    implementation_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert implementation_hash == SOURCE_SHA256, 'Pinned audio checker changed; review before reuse'
    spec = importlib.util.spec_from_file_location('ea01_pinned_audio_checker', SOURCE)
    assert spec is not None and spec.loader is not None
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    checker.EPISODE = EPISODE
    checker.ROOT = ROOT
    before = REPORT.read_bytes() if REPORT.is_file() else None
    try:
        checker.main()
    finally:
        # A failed precondition must not relabel a stale result from an old run.
        if REPORT.is_file() and REPORT.read_bytes() != before:
            result = json.loads(REPORT.read_text())
            result['executor'] = args.executor
            result['invocationEntry'] = str(Path(__file__).resolve().relative_to(ROOT))
            result['reusedImplementation'] = {
                'path': str(SOURCE.relative_to(ROOT)),
                'sha256': implementation_hash,
                'episodeGlobalRedirected': True,
                'numericAlgorithmsAndCriteriaUnchanged': True,
            }
            result['wrapperScope'] = (
                'Numerical whole-track and per-sentence AAC/source coverage; '
                'constant-mode known-BGM reconstruction only. No ASR, numerical '
                'pronunciation recognition, semantic listening or human review.'
            )
            REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
