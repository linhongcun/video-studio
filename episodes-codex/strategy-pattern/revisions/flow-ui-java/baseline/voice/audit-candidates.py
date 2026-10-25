"""Inspect candidate signal and source provenance; not speech recognition.

The trim being evaluated is always the repository common.cut implementation.
This tool does not replace trimming, onset, or track assembly algorithms.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import wave

import numpy as np

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import cut, load

sents = json.loads((D / 'sents.json').read_text())
rows = []
picks = {}
failures = []

for sentence in sents:
    candidates = []
    for sidecar in sorted((D / 'takes').glob(sentence['id'] + '-*.txt.json')):
        stem = sidecar.name.removesuffix('.txt.json')
        audio = D / 'takes' / (stem + '.wav')
        raw = D / 'takes' / (stem + '.raw.wav')
        variant = stem.removeprefix(sentence['id'] + '-')
        warnings = []
        value = json.loads(sidecar.read_text())
        text_matches = value == sentence['tts']
        if not text_matches:
            warnings.append('model text differs from expected text')
        try:
            samples = load(str(audio))
            trimmed, isolated_tail = cut(samples)
            rate = len(re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', sentence['text'])) / (len(trimmed) / 48000)
            frame_peaks = np.abs(trimmed[:len(trimmed)//480*480]).reshape(-1, 480).max(axis=1)
            run = longest = 0
            for active in frame_peaks > 0.005:
                run = 0 if active else run + 1
                longest = max(longest, run)
            if isolated_tail < 0.12:
                warnings.append('isolated throwaway tail shorter than 0.12s')
            if longest >= 50:
                warnings.append('at least 0.50s internal low signal')
            if not 2.8 <= rate <= 8.0:
                warnings.append('unusual characters per second; requires review')
            with wave.open(str(audio)) as handle:
                fmt = [handle.getframerate(), handle.getnchannels(), handle.getsampwidth()]
                pcm = handle.readframes(handle.getnframes())
            raw_pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(raw), '-ar', '48000', '-ac', '1', '-f', 's16le', '-'], capture_output=True, check=True).stdout
            exact_raw_conversion = raw_pcm == pcm
            if fmt != [48000, 1, 2] or not exact_raw_conversion:
                warnings.append('format or raw conversion mismatch')
            candidate = dict(id=sentence['id'], take=variant,
                textMatch=text_matches, format=fmt,
                rawTo48kPCMExact=exact_raw_conversion,
                rawSHA256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                audioSHA256=hashlib.sha256(audio.read_bytes()).hexdigest(),
                mainSeconds=round(len(trimmed)/48000, 4),
                isolatedTailSeconds=round(float(isolated_tail), 4),
                maxInnerSilenceSeconds=longest/100,
                charactersPerSecond=round(rate, 3), warnings=warnings)
            candidates.append(candidate)
        except Exception as error:
            candidates.append(dict(id=sentence['id'], take=variant,
                warnings=['signal audit failed: ' + type(error).__name__ + ': ' + str(error)[:160]]))
    if not candidates:
        failures.append(sentence['id'] + ': no completed candidates')
        continue
    candidates.sort(key=lambda x: (len(x['warnings']), x['take'] != 'a', x['take']))
    selected = candidates[0]
    picks[sentence['id']] = selected['take']
    if selected['warnings']:
        failures.append(sentence['id'] + ': ' + '; '.join(selected['warnings']))
    rows.append(dict(id=sentence['id'], selectedTake=selected['take'], candidates=candidates))

audit = dict(scope='Signal and provenance inspection only; no transcript recognition or pronunciation verdict.',
             expectedSentences=len(sents), completeSentences=len(rows),
             candidateCount=sum(len(x['candidates']) for x in rows),
             failures=failures, rows=rows)
(D / 'candidate-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
(D / 'picks.json').write_text(json.dumps(picks, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: audit[k] for k in ['expectedSentences','completeSentences','candidateCount','failures']}, ensure_ascii=False))
if failures:
    sys.exit(1)
