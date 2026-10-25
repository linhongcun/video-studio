#!/usr/bin/env python3
"""Check source requests and shared cut boundaries, without speech recognition."""
from pathlib import Path
import hashlib, json, subprocess, sys
import numpy as np

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[1]
sys.path.insert(0, str(ROOT/'episodes/_shared/voice'))
from common import load, cut

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def audit():
    sentences = json.loads((D/'voice/sents.json').read_text())
    picks = json.loads((D/'voice/picks.json').read_text()) if (D/'voice/picks.json').exists() else {}
    jobs = {}
    for path in (D/'voice').glob('jobs*.json'):
        for item in json.loads(path.read_text()):
            jobs[(item[0], item[1])] = item[2]
    rows, failures, warnings = [], [], []
    for sentence in sentences:
        take = picks.get(sentence['id'],'a')
        stem = D/'voice/takes'/f"{sentence['id']}-{take}"
        wav = stem.with_suffix('.wav')
        raw = stem.with_suffix('.raw.wav')
        request = stem.with_suffix('.txt.json')
        for path in (wav, raw, request):
            assert path.is_file(), path
        sent_text = jobs.get((sentence['id'],take)) or sentence['tts']
        request_matches = json.loads(request.read_text()) == sent_text
        samples = load(str(wav))
        trimmed, tail = cut(samples)
        activity = np.abs(trimmed[:len(trimmed)//480*480]).reshape(-1,480).max(1) > .005
        longest = current = 0
        for active in activity:
            current = 0 if active else current+1
            longest = max(longest,current)
        expected_pcm = subprocess.run(['ffmpeg','-v','error','-i',str(raw),'-ar','48000','-ac','1','-f','s16le','-'],check=True,capture_output=True).stdout
        actual_pcm = subprocess.run(['ffmpeg','-v','error','-i',str(wav),'-ar','48000','-ac','1','-f','s16le','-'],check=True,capture_output=True).stdout
        conversion_matches = expected_pcm == actual_pcm
        row = dict(id=sentence['id'],take=take,scriptText=sentence['text'],requestMatchesExpected=request_matches,
                   pcmConversionMatches=conversion_matches,rawSHA256=sha(raw),takeSHA256=sha(wav),
                   rawDurationSeconds=len(samples)/48000,cutDurationSeconds=len(trimmed)/48000,
                   trailingDiscardedSegmentSeconds=tail,maxLowLevelIntervalSeconds=longest/100)
        rows.append(row)
        if not request_matches: failures.append(sentence['id']+': request mismatch')
        if not conversion_matches: failures.append(sentence['id']+': PCM conversion mismatch')
        if tail < .20: warnings.append(sentence['id']+': discarded segment shorter than .20s')
        if longest >= 50: warnings.append(sentence['id']+': low-level interval at least .50s')
    report=dict(status='passed' if not failures and not warnings else 'needs-review',scope='Selected request text, PCM conversion, and shared cut signal boundaries only; not ASR or semantic listening.',
                scriptSHA256=sha(D/'script.md'),sentences=len(rows),failures=failures,warnings=warnings,rows=rows,
                ASRPerformed=False,semanticListeningPerformed=False,fullHumanListeningPerformed=False)
    (D/'qa-voice-takes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','sentences','failures','warnings']},ensure_ascii=False))
    return report

if __name__ == '__main__':
    result=audit()
    raise SystemExit(bool(result['failures'] or result['warnings']))
