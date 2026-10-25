#!/usr/bin/env python3
"""Audit exact-text reused takes and changed sentences for the UI/Java revision.

Uses the canonical load/cut helpers; it does not synthesize, recognize speech or
copy an onset/normalization algorithm. Old take bytes must remain unchanged.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'episodes/_shared/voice'))
from common import cut, load


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert len(sys.argv) == 2, 'Usage: audit_sentence_reuse.py EPDIR'
D = Path(sys.argv[1]).resolve()
V = D/'voice'
baseline = json.loads((V/'flow-generation-baseline.json').read_text())
provenance = json.loads((V/'flow-reuse-provenance.json').read_text())
for path, key in [(D/'script.md','scriptSHA256'), (D/'plan.json','planSHA256'),
                  (D/'episode-config.json','episodeConfigSHA256'), (V/'sents.json','sentencesSHA256')]:
    assert sha(path) == baseline[key], ('Frozen TTS input changed', path)
for relative, expected in provenance['oldTakeFiles'].items():
    assert sha(D/relative) == expected, ('Historical take changed', relative)
planned = {row['id']: row for row in provenance['rows']}
rows, failures, flags, picks = [], [], [], {}
sentences = json.loads((V/'sents.json').read_text())
for sentence in sentences:
    plan = planned[sentence['id']]
    assert plan['text'] == sentence['text']
    if plan['status'] == 'reused-exact-text':
        for item in plan['files']:
            assert sha(D/item['source']) == item['sha256'] == sha(D/item['target']), item
        sidecars = [V/'takes'/(sentence['id']+'-'+plan['selectedTake']+'.txt.json')]
    else:
        sidecars = sorted((V/'takes').glob(sentence['id']+'-flow*.txt.json'))
    candidates = []
    for sidecar in sidecars:
        stem = sidecar.name.removesuffix('.txt.json')
        take = stem.removeprefix(sentence['id']+'-')
        audio, raw = V/'takes'/(stem+'.wav'), V/'takes'/(stem+'.raw.wav')
        warnings = []
        try:
            matches = json.loads(sidecar.read_text()) == sentence['tts']
            if not matches:
                warnings.append('model input text differs from frozen narration')
            clipped, tail = cut(load(str(audio)))
            peak_windows = np.abs(clipped[:len(clipped)//480*480]).reshape(-1,480).max(1)
            run = longest = 0
            for active in peak_windows > .005:
                run = 0 if active else run+1
                longest = max(longest,run)
            cps = len(re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]','',sentence['text']))/(len(clipped)/48000)
            if tail < .12:
                warnings.append('isolated throwaway tail shorter than 0.12 seconds')
            if longest >= 50:
                warnings.append('at least 0.50 seconds internal low signal')
            if not 2.3 <= cps <= 8:
                warnings.append('unusual characters per second; requires review')
            with wave.open(str(audio)) as handle:
                fmt = [handle.getframerate(),handle.getnchannels(),handle.getsampwidth()]
                pcm = handle.readframes(handle.getnframes())
            converted = subprocess.run(['ffmpeg','-v','error','-i',str(raw),'-ar','48000','-ac','1','-f','s16le','-'],capture_output=True,check=True).stdout
            exact = pcm == converted
            if fmt != [48000,1,2] or not exact:
                warnings.append('format or raw-to-48k PCM mismatch')
            candidates.append({'take':take,'textMatch':matches,'format':fmt,
                'rawTo48kPCMExact':exact,'audioSHA256':sha(audio),'rawSHA256':sha(raw),
                'mainSeconds':len(clipped)/48000,'isolatedTailSeconds':float(tail),
                'maxInnerSilenceSeconds':longest/100,'charactersPerSecond':cps,
                'trimmedFloat32SHA256':hashlib.sha256(clipped.astype('<f4').tobytes()).hexdigest(),
                'warnings':warnings})
        except Exception as error:
            candidates.append({'take':take,'warnings':['signal audit failed: '+type(error).__name__+': '+str(error)[:180]]})
    def hard(item):
        return [warning for warning in item['warnings'] if warning != 'at least 0.50 seconds internal low signal']
    candidates.sort(key=lambda item:(len(hard(item)),len(item['warnings']),item.get('maxInnerSilenceSeconds',99) if item['warnings'] else 0,item['take']!=plan['selectedTake'],item['take']))
    if not candidates:
        failures.append({'id':sentence['id'],'warnings':['no completed take']})
        continue
    selected = candidates[0]
    picks[sentence['id']] = selected['take']
    if hard(selected):
        failures.append({'id':sentence['id'],'warnings':hard(selected)})
    if selected['warnings'] and not hard(selected):
        flags.append({'id':sentence['id'],'take':selected['take'],'maxInnerSilenceSeconds':selected['maxInnerSilenceSeconds'],
                      'note':'Retained pause-review signal flag; not recognized speech or proof of a missing/incorrect word.'})
    rows.append({'id':sentence['id'],'status':plan['status'],'selectedTake':selected['take'],'candidates':candidates})
report = {
    'checkedAtUTC':datetime.now(timezone.utc).isoformat(), 'executor':'/root/observer_voice',
    'scope':'Frozen narration input and exact-text reuse provenance, raw conversion and shared-cut waveform checks. No speech recognition or listening.',
    'scriptSHA256':baseline['scriptSHA256'],'sentencesSHA256':baseline['sentencesSHA256'],
    'expectedSentences':len(sentences),'completeSentences':len(rows),
    'newSentences':sum(row['status']=='new-tts' for row in rows),
    'reusedSentences':sum(row['status']=='reused-exact-text' for row in rows),
    'oldTakeFilesChecked':len(provenance['oldTakeFiles']),'oldTakeFilesUnchanged':True,
    'commonSHA256':sha(ROOT/'episodes/_shared/voice/common.py'),
    'candidateCount':sum(len(row['candidates']) for row in rows),
    'thresholds':{'innerLowSignalWarningSeconds':.50,'minimumIsolatedTailSeconds':.12,'peakWindowSeconds':.01},
    'failures':failures,'signalReviewFlags':flags,'rows':rows,
}
(V/'flow-candidate-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if not failures:
    (V/'picks.json').write_text(json.dumps(picks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({key:report[key] for key in ['expectedSentences','completeSentences','newSentences','reusedSentences','oldTakeFilesChecked','oldTakeFilesUnchanged','failures','signalReviewFlags']},ensure_ascii=False))
if failures:
    raise SystemExit(1)
