"""Audit language-independent idea takes without touching older recordings or assembling a track.

Signal thresholds and input text provenance are independent of understanding
speech. The repository's common.load/common.cut provide all audio trimming.
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
ROOT = V.parents[2]
sys.path.insert(0, str(ROOT/'episodes/_shared/voice'))
from common import cut, load

sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
baseline = json.loads((V/'idea-generation-baseline.json').read_text())
assert sha(D/'script.md') == baseline['scriptSHA256'], 'Production script changed after TTS freeze'
legacy = baseline['oldTakeFiles']
changed = [name for name, expected in legacy.items() if sha(V/name) != expected]
assert not changed, changed
sentences = json.loads((V/'sents.json').read_text())
assert len(sentences) == 22
rows = []
picks = {}
failures = []
signal_review_flags = []
for sentence in sentences:
    candidates = []
    for sidecar in sorted((V/'takes').glob(sentence['id']+'-idea*.txt.json')):
        stem = sidecar.name.removesuffix('.txt.json')
        variant = stem.removeprefix(sentence['id']+'-')
        audio = V/'takes'/(stem+'.wav')
        raw = V/'takes'/(stem+'.raw.wav')
        warnings = []
        try:
            text_matches = json.loads(sidecar.read_text()) == sentence['tts']
            if not text_matches:
                warnings.append('model input text differs from frozen narration')
            trimmed, tail = cut(load(str(audio)))
            peaks = np.abs(trimmed[:len(trimmed)//480*480]).reshape(-1,480).max(axis=1)
            run = longest = 0
            for active in peaks > .005:
                run = 0 if active else run+1
                longest = max(longest,run)
            cps = len(re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', sentence['text'])) / (len(trimmed)/48000)
            if tail < .12:
                warnings.append('isolated throwaway tail shorter than 0.12 seconds')
            if longest >= 50:
                warnings.append('at least 0.50 seconds internal low signal')
            if not 2.3 <= cps <= 8.0:
                warnings.append('unusual characters per second; requires review')
            with wave.open(str(audio)) as handle:
                fmt = [handle.getframerate(),handle.getnchannels(),handle.getsampwidth()]
                pcm = handle.readframes(handle.getnframes())
            converted = subprocess.run(['ffmpeg','-v','error','-i',str(raw),'-ar','48000','-ac','1','-f','s16le','-'],capture_output=True,check=True).stdout
            raw_exact = pcm == converted
            if fmt != [48000,1,2] or not raw_exact:
                warnings.append('format or raw-to-48k PCM mismatch')
            candidates.append(dict(id=sentence['id'],take=variant,textMatch=text_matches,
                format=fmt,rawTo48kPCMExact=raw_exact,rawSHA256=sha(raw),audioSHA256=sha(audio),
                trimmedSamples=len(trimmed),trimmedFloat32SHA256=hashlib.sha256(trimmed.astype('<f4').tobytes()).hexdigest(),
                mainSeconds=round(len(trimmed)/48000,5),isolatedTailSeconds=round(float(tail),5),
                maxInnerSilenceSeconds=longest/100,charactersPerSecond=round(cps,3),warnings=warnings))
        except Exception as error:
            candidates.append(dict(id=sentence['id'],take=variant,warnings=['signal audit failed: '+type(error).__name__+': '+str(error)[:180]]))
    if not candidates:
        failures.append(dict(id=sentence['id'],warnings=['no completed idea take']))
        continue
    def hard_warnings(item):
        return [w for w in item['warnings'] if w != 'at least 0.50 seconds internal low signal']
    candidates.sort(key=lambda x:(len(hard_warnings(x)),len(x['warnings']),x.get('maxInnerSilenceSeconds',99) if x['warnings'] else 0,x['take']!='idea',x['take']))
    selected = candidates[0]
    picks[sentence['id']] = selected['take']
    if hard_warnings(selected):
        failures.append(dict(id=sentence['id'],warnings=hard_warnings(selected)))
    if 'at least 0.50 seconds internal low signal' in selected['warnings']:
        signal_review_flags.append(dict(id=sentence['id'],take=selected['take'],
            maxInnerSilenceSeconds=selected['maxInnerSilenceSeconds'],
            note='Retained for natural-pause review as authorized by root; this signal threshold cannot establish a word error or speech understanding.'))
    rows.append(dict(id=sentence['id'],selectedTake=selected['take'],candidates=candidates))

report=dict(checked_on='2026-10-25（北京时间）',
    scope='Frozen input text, PCM conversion and shared common.cut signal checks only. No whole-track build/assembly, ASR, speech understanding, pronunciation verdict, or human listening.',
    expectedSentences=len(sentences),completeSentences=len(rows),candidateCount=sum(len(x['candidates']) for x in rows),
    scriptSHA256=sha(D/'script.md'),narrationSHA256=baseline['narrationSHA256'],
    oldTakeFilesChecked=len(legacy),oldTakeFilesUnchanged=not changed,
    commonImplementationSHA256=sha(ROOT/'episodes/_shared/voice/common.py'),
    thresholds=dict(windowSeconds=.01,activePeakThreshold=.005,innerLowSignalWarningSeconds=.50,minimumIsolatedTailSeconds=.12),
    failures=failures,signalReviewFlags=signal_review_flags,rows=rows)
(V/'idea-candidate-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if not failures:
    (V/'picks.json').write_text(json.dumps(picks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({key:report[key] for key in ['expectedSentences','completeSentences','candidateCount','oldTakeFilesChecked','oldTakeFilesUnchanged','failures','signalReviewFlags']},ensure_ascii=False))
if failures:
    sys.exit(1)
