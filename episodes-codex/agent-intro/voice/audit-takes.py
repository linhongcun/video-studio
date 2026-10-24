"""Audit selected PCM, sent/job text, raw conversion and shared-cut envelopes.

Signal warnings do not establish pronunciation accuracy. No ASR is performed.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import wave

import numpy as np

VD = Path(__file__).resolve().parent
ROOT = VD.parents[2]
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import cut, load


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


sents = json.loads((VD / 'sents.json').read_text())
picks = json.loads((VD / 'picks.json').read_text()) if (VD / 'picks.json').exists() else {}
overrides = {}
for path in sorted(VD.glob('jobs*.json')):
    for row in json.loads(path.read_text()):
        if row[2]:
            overrides[(row[0], row[1])] = row[2]
records, warnings, failures = [], [], []
for sentence in sents:
    sid, take = sentence['id'], picks.get(sentence['id'], 'a')
    base = VD / 'takes' / f'{sid}-{take}'
    wav, raw, txt = Path(str(base) + '.wav'), Path(str(base) + '.raw.wav'), Path(str(base) + '.txt.json')
    assert wav.exists() and raw.exists() and txt.exists(), sid
    sent_to_model = json.loads(txt.read_text())
    expected = overrides.get((sid, take), sentence['tts'])
    if sent_to_model != expected:
        failures.append(dict(id=sid, reason='TTS sent/job text differs'))
    with wave.open(str(wav)) as stream:
        fmt = dict(sampleRate=stream.getframerate(), channels=stream.getnchannels(),
                   bits=stream.getsampwidth() * 8, compression=stream.getcomptype())
        pcm = stream.readframes(stream.getnframes())
    if fmt != dict(sampleRate=48000, channels=1, bits=16, compression='NONE'):
        failures.append(dict(id=sid, reason='Unexpected PCM format', actual=fmt))
    converted = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(raw), '-ar', '48000', '-ac', '1', '-f', 's16le', '-'],
                               check=True, capture_output=True).stdout
    if converted != pcm:
        failures.append(dict(id=sid, reason='Original raw to PCM conversion mismatch'))
    y, tail = cut(load(str(wav)))
    active = np.where(np.abs(y) > 1e-4)[0]
    assert len(active), sid
    y = y[:active[-1] + 1]
    envelopes = np.abs(y[:len(y) // 480 * 480]).reshape(-1, 480).max(axis=1) > 0.005
    run, longest = 0, 0
    for item in envelopes:
        run = 0 if item else run + 1
        longest = max(longest, run)
    record = dict(id=sid, take=take, sha256=sha(wav), format=fmt,
                  rawTo48kConversionExact=converted == pcm, textMatches=sent_to_model == expected,
                  mainSeconds=len(y) / 48000, tailAfterLastGapSeconds=tail,
                  maxInnerSilenceSeconds=longest / 100, peak=float(np.abs(y).max()),
                  ttsJobOverride=(sid, take) in overrides)
    records.append(record)
    if tail < 0.22 or tail > 1.25 or longest >= 50:
        warnings.append(dict(id=sid, take=take, tailAfterLastGapSeconds=tail,
                             maxInnerSilenceSeconds=longest / 100,
                             note='Signal risk requiring candidate review; not a pronunciation finding.'))
report = dict(scope='Selected-take text, PCM, raw-conversion and shared-cut signal audit; no ASR or human listening.',
              expected=len(sents), complete=len(records), failures=failures, warnings=warnings, records=records)
(VD / 'selected-take-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(expected=len(sents), complete=len(records), failures=failures, warnings=warnings), ensure_ascii=False))
if failures:
    raise SystemExit(1)
