"""Audit selected depth-revision takes through the shared load/cut helpers.

This records waveform and input identity only; no ASR or human listening.
Run from the repository root with the project's Python environment.
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
D = V.parent
ROOT = D.parents[1]
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import load, cut

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
S = json.loads((V / 'sents.json').read_text())
P = json.loads((V / 'picks.json').read_text())
B = json.loads((V / 'depth-generation-baseline.json').read_text())
G = json.loads((V / 'revisions/depth-generation-before-visual-correction.json').read_text())
assert B['generationScriptSha256'] == G['scriptSha256']
assert B['sentencesSha256'] == G['sentencesSha256']
assert B['paramsSha256'] == G['paramsSha256']
assert sha(D / 'script.md') == B['productionScriptSha256']
# Generation identity stays immutable; only the production visual text changed.
sections = re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)', (D/'script.md').read_text(), re.S)
narrations = []
for number, slug, body in sections:
    narration = re.search(r'^旁白：(.*)$', body, re.M)[1]
    expected = ''.join(row['text'] for row in S if row['shot'] == f'{int(number):02d}-{slug}')
    assert narration == expected, ('Production narration differs from generated TTS input', number, slug)
    narrations.append(narration)
assert hashlib.sha256('\n'.join(narrations).encode()).hexdigest() == B['narrationSha256']
assert sha(V / 'sents.json') == B['sentencesSha256']
assert sha(V / 'params.json') == B['paramsSha256']
old = json.loads((V / 'revisions/depth-baseline.json').read_text())
for row in old['selected']:
    stem = f"{row['id']}-{row['take']}"
    assert sha(V / 'takes' / (stem + '.wav')) == row['wavSha256']
    assert sha(V / 'takes' / (stem + '.txt.json')) == row['ttsSha256']
rows, failures = [], []
for sentence in S:
    stem = f"{sentence['id']}-{P[sentence['id']]}"
    audio = V / 'takes' / (stem + '.wav')
    raw = V / 'takes' / (stem + '.raw.wav')
    sidecar = V / 'takes' / (stem + '.txt.json')
    warnings = []
    try:
        text_match = json.loads(sidecar.read_text()) == sentence['tts']
        if not text_match:
            warnings.append('model input differs from current prepared sentence')
        clipped, tail = cut(load(str(audio)))
        peaks = np.abs(clipped[:len(clipped)//480*480]).reshape(-1,480).max(1)
        run = longest = 0
        for active in peaks > .005:
            run = 0 if active else run+1
            longest = max(longest, run)
        if tail < .12:
            warnings.append('isolated throwaway tail under 0.12 seconds')
        if longest >= 50:
            warnings.append('internal low-signal run at least 0.50 seconds')
        with wave.open(str(audio)) as handle:
            fmt = [handle.getframerate(), handle.getnchannels(), handle.getsampwidth()]
            pcm = handle.readframes(handle.getnframes())
        converted = subprocess.run(['ffmpeg','-v','error','-i',str(raw),'-ar','48000','-ac','1','-f','s16le','-'], capture_output=True, check=True).stdout
        exact = pcm == converted
        if fmt != [48000,1,2] or not exact:
            warnings.append('audio format or raw-to-48k PCM mismatch')
        row = dict(id=sentence['id'], take=P[sentence['id']], textMatch=text_match,
                   seconds=len(clipped)/48000, isolatedTailSeconds=float(tail),
                   maxInnerSilenceSeconds=longest/100, format=fmt,
                   rawTo48kPCMExact=exact, wavSha256=sha(audio),
                   rawSha256=sha(raw), ttsSha256=sha(sidecar), warnings=warnings)
    except Exception as error:
        warnings.append(f'{type(error).__name__}: {str(error)[:160]}')
        row = dict(id=sentence['id'], take=P[sentence['id']], warnings=warnings)
    if warnings:
        failures.append(dict(id=sentence['id'], warnings=warnings))
    rows.append(row)
report = dict(executor='/root/voice_timing',
              scope='Current prepared text identity, raw PCM conversion, canonical shared-cut waveform checks, and preservation of 24 historical selected takes. No ASR or listening.',
              generationScriptSha256=B['generationScriptSha256'],
              productionScriptSha256=B['productionScriptSha256'],
              narrationSha256=B['narrationSha256'], narrationUnchangedFromGeneration=True,
              sentencesSha256=B['sentencesSha256'],
              commonSha256=sha(ROOT/'episodes/_shared/voice/common.py'),
              historicalTakesPreserved=len(old['selected']), expectedSentences=len(S),
              completeSentences=sum('seconds' in row for row in rows),
              failures=failures, rows=rows)
(V / 'depth-take-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({key:report[key] for key in ['expectedSentences','completeSentences','historicalTakesPreserved','failures']},ensure_ascii=False))
if failures:
    raise SystemExit(1)
