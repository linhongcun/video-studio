"""Audit only the six replacement sentences and preserve all original takes.

Uses the repository's common.load/common.cut; does not build or splice audio.
Signal and input-text checks do not recognize pronunciation or speech content.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import wave

import numpy as np

V = Path(__file__).resolve().parent
ROOT = V.parents[2]
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import cut, load

jobs = json.loads((V / 'chapter-bridge-jobs.json').read_text())
expected = {}
for sid, take, text, *_ in jobs:
    assert take in ['c', 'd']
    expected.setdefault(sid, {})[take] = text
assert len(expected) == 6
baseline = json.loads((V / 'chapter-bridge-input-baseline.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
preserved = {name: sha(V/name) == value for name, value in baseline['existingABTakeFiles'].items()}
assert all(preserved.values()), 'An original a/b take changed'

rows = []
picks = {}
failures = []
for sid, variants in expected.items():
    candidates = []
    for take, model_text in variants.items():
        stem = V / 'takes' / f'{sid}-{take}'
        audio = stem.with_suffix('.wav')
        raw = stem.with_suffix('.raw.wav')
        sidecar = stem.with_suffix('.txt.json')
        warnings = []
        try:
            text_matches = json.loads(sidecar.read_text()) == model_text
            if not text_matches:
                warnings.append('model input text mismatch')
            samples = load(str(audio))
            trimmed, isolated_tail = cut(samples)
            peaks = np.abs(trimmed[:len(trimmed)//480*480]).reshape(-1,480).max(axis=1)
            run = longest = 0
            for active in peaks > 0.005:
                run = 0 if active else run + 1
                longest = max(longest, run)
            narration = model_text.removesuffix('好。')
            cps = len(re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', narration)) / (len(trimmed)/48000)
            if isolated_tail < 0.12:
                warnings.append('isolated throwaway tail shorter than 0.12 seconds')
            if longest >= 50:
                warnings.append('at least 0.50 seconds internal low signal')
            if not 2.3 <= cps <= 8.0:
                warnings.append('unusual characters per second; requires review')
            with wave.open(str(audio)) as handle:
                fmt = [handle.getframerate(),handle.getnchannels(),handle.getsampwidth()]
                pcm = handle.readframes(handle.getnframes())
            converted = subprocess.run(['ffmpeg','-v','error','-i',str(raw),'-ar','48000','-ac','1','-f','s16le','-'],capture_output=True,check=True).stdout
            raw_exact = converted == pcm
            if fmt != [48000,1,2] or not raw_exact:
                warnings.append('PCM format or raw conversion mismatch')
            candidates.append(dict(id=sid,take=take,text=narration,textMatch=text_matches,
                format=fmt,rawTo48kPCMExact=raw_exact,rawSHA256=sha(raw),audioSHA256=sha(audio),
                trimmedFloat32SHA256=hashlib.sha256(trimmed.astype('<f4').tobytes()).hexdigest(),
                trimmedSamples=len(trimmed),mainSeconds=round(len(trimmed)/48000,5),
                isolatedTailSeconds=round(float(isolated_tail),5),maxInnerSilenceSeconds=longest/100,
                charactersPerSecond=round(cps,3),warnings=warnings))
        except Exception as error:
            candidates.append(dict(id=sid,take=take,warnings=['audit failed: '+type(error).__name__+': '+str(error)[:180]]))
    candidates.sort(key=lambda x:(len(x['warnings']),x['take'] != 'c',x['take']))
    selected = candidates[0]
    picks[sid] = selected['take']
    if selected['warnings']:
        failures.append(dict(id=sid,warnings=selected['warnings']))
    rows.append(dict(id=sid,selectedTake=selected['take'],candidates=candidates))

report=dict(scope='Only six replacement sentence candidates; shared common.cut signal and source provenance audit. No track build/splice, ASR, pronunciation verdict, or full human listening.',
    checked_on='2026-10-24（北京时间）',sentences=len(expected),candidateCount=len(jobs),
    originalABFilesChecked=len(preserved),originalABFilesUnchanged=all(preserved.values()),
    jobsSHA256=sha(V/'chapter-bridge-jobs.json'),
    commonImplementationSHA256=sha(ROOT/'episodes/_shared/voice/common.py'),
    signalThresholds=dict(windowSeconds=.01,activePeakThreshold=.005,internalLowSignalWarningSeconds=.50,isolatedTailMinimumSeconds=.12),
    failures=failures,rows=rows)
(V/'chapter-bridge-picks.json').write_text(json.dumps(picks,ensure_ascii=False,indent=2)+'\n')
(V/'chapter-bridge-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['sentences','candidateCount','originalABFilesChecked','originalABFilesUnchanged','failures']},ensure_ascii=False))
if failures:
    sys.exit(1)
