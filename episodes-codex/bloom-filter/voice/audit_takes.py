#!/usr/bin/env python3
"""Audit selected TTS request provenance and shared cut signal boundaries.

This reuses the unique shared load/cut implementation. It does not recognize
speech or establish pronunciation/semantic correctness.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import numpy as np

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[1]
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import load, cut


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    sentences = json.loads((D / 'voice/sents.json').read_text())
    picks = json.loads((D / 'voice/picks.json').read_text())
    overrides = {}
    for path in sorted((D / 'voice').glob('jobs*.json')):
        for row in json.loads(path.read_text()):
            overrides[(row[0], row[1])] = row[2]
    rows, failures, warnings = [], [], []
    for sentence in sentences:
        take = picks.get(sentence['id'], 'a')
        stem = D / 'voice/takes' / f"{sentence['id']}-{take}"
        paths = {kind: Path(str(stem) + suffix) for kind, suffix in
                 [('wav', '.wav'), ('raw', '.raw.wav'), ('request', '.txt.json')]}
        missing = [str(path.relative_to(D)) for path in paths.values() if not path.is_file()]
        if missing:
            failures.append(sentence['id'] + ': missing ' + ', '.join(missing))
            continue
        expected = overrides.get((sentence['id'], take)) or sentence['tts']
        request_matches = json.loads(paths['request'].read_text()) == expected
        source = load(str(paths['wav']))
        try:
            trimmed, discarded = cut(source)
        except (IndexError, ValueError) as error:
            failures.append(sentence['id'] + ': shared cut failed: ' + str(error))
            continue
        activity = np.abs(trimmed[:len(trimmed) // 480 * 480]).reshape(-1, 480).max(1) > .005
        current = longest = 0
        for active in activity:
            current = 0 if active else current + 1
            longest = max(longest, current)
        pcm = lambda path: subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path),
            '-ar', '48000', '-ac', '1', '-f', 's16le', '-'], check=True, capture_output=True).stdout
        conversion_matches = pcm(paths['raw']) == pcm(paths['wav'])
        row = {'id': sentence['id'], 'take': take, 'scriptText': sentence['text'],
               'requestMatchesExpected': request_matches, 'pcmConversionMatches': conversion_matches,
               'rawSHA256': sha(paths['raw']), 'takeSHA256': sha(paths['wav']),
               'requestSHA256': sha(paths['request']), 'rawDurationSeconds': len(source) / 48000,
               'cutDurationSeconds': len(trimmed) / 48000, 'cutSamples': len(trimmed),
               'trailingDiscardedSegmentSeconds': discarded,
               'maxLowLevelIntervalSeconds': longest / 100,
               'peakBeforeNormalization': float(np.max(np.abs(trimmed)))}
        rows.append(row)
        if not request_matches:
            failures.append(sentence['id'] + ': request mismatch')
        if not conversion_matches:
            failures.append(sentence['id'] + ': PCM conversion mismatch')
        if discarded < .20:
            warnings.append(sentence['id'] + ': discarded tail shorter than .20s')
        if longest >= 50:
            warnings.append(sentence['id'] + ': low-level interval at least .50s')
    report = {'status': 'passed' if not failures and not warnings else 'needs-review',
              'scope': 'Selected TTS request text, exact PCM conversion, and shared cut signal boundaries; not ASR or semantic listening.',
              'scriptSHA256': sha(D / 'script.md'), 'sentences': len(rows),
              'failures': failures, 'warnings': warnings, 'rows': rows,
              'ASRPerformed': False, 'semanticListeningPerformed': False,
              'fullHumanListeningPerformed': False}
    (D / 'qa-voice-takes.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['status', 'sentences', 'failures', 'warnings']}, ensure_ascii=False))
    return report


if __name__ == '__main__':
    result = audit()
    raise SystemExit(bool(result['failures'] or result['warnings']))
