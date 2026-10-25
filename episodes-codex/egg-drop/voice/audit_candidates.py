#!/usr/bin/env python3
"""Read-only candidate/input QA using shared load/cut; never generates audio."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys
import wave

import numpy as np

VOICE = Path(__file__).resolve().parent
EPISODE = VOICE.parent
ROOT = EPISODE.parents[1]
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import load, cut


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sents = {s['id']: s for s in json.loads((VOICE / 'sents.json').read_text())}
    picks = json.loads((VOICE / 'picks.json').read_text())
    requests = {}
    for path in sorted(VOICE.glob('jobs_*.json')):
        for row in json.loads(path.read_text()):
            sid, take, text = row[:3]
            request = dict(text=text or sents[sid]['tts'], style=row[3] if len(row) > 3 else None)
            key = (sid, take)
            assert key not in requests or requests[key]['text'] == request['text'], key
            requests[key] = dict(request, jobsFile=path.name, jobsSHA256=sha(path))
    rows = []
    failures = []
    for path in sorted((VOICE / 'takes').glob('*.raw.wav')):
        basename = path.name.removesuffix('.raw.wav')
        sid, take = basename.rsplit('-', 1)
        target = path.with_name(basename + '.wav')
        sidecar = path.with_name(basename + '.txt.json')
        request = requests.get((sid, take), dict(text=sents[sid]['tts'], style=None, jobsFile=None))
        actual = json.loads(sidecar.read_text())
        with wave.open(str(target)) as audio:
            fmt = [audio.getframerate(), audio.getnchannels(), audio.getsampwidth()]
            pcm = audio.readframes(audio.getnframes())
        raw_pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ar', '48000',
                                  '-ac', '1', '-c:a', 'pcm_s16le', '-f', 's16le', '-'],
                                 capture_output=True, check=True).stdout
        y, tail = cut(load(str(target)))
        frames = np.max(np.abs(y[:len(y)//480*480].reshape(-1, 480)), axis=1)
        quiet = np.flatnonzero(np.diff(np.r_[False, frames <= .005, False]))
        longest = int(np.max(quiet[1::2]-quiet[::2])) if len(quiet) else 0
        seconds = len(y)/48000
        row = dict(id=sid, take=take, selected=picks.get(sid, 'a') == take,
                   actualTTSInput=actual, expectedRequest=request,
                   selectedInputExact=actual == request['text'],
                   originalTextUnchanged=actual == sents[sid]['tts'], format=fmt,
                   rawTo48kPCMExact=raw_pcm == pcm, rawSHA256=sha(path), sha256=sha(target),
                   speechSeconds=round(seconds, 5), tailSeconds=round(tail, 5),
                   maxInnerSilenceS=longest/100,
                   charactersPerSecond=round(len(re.findall(r'[\u4e00-\u9fff]', sents[sid]['text']))/seconds, 4),
                   reviewFlags=[])
        if longest >= 50:
            row['reviewFlags'].append('Low-signal interval >=0.50s; inspect envelope/consider same-text candidate, not a semantic verdict.')
        if tail < .15:
            row['reviewFlags'].append('Short throwaway tail; possible automatic cut risk.')
        if not row['selectedInputExact'] or not row['rawTo48kPCMExact'] or fmt != [48000, 1, 2]:
            failures.append(basename)
        rows.append(row)
    chosen = {(r['id'], r['take']) for r in rows if r['selected']}
    assert chosen == {(sid, picks.get(sid, 'a')) for sid in sents}, 'A selected candidate is missing'
    result = dict(checkedAtUTC=datetime.now(timezone.utc).isoformat(),
                  method='Shared common.load/cut, actual request and exact raw-to-48k PCM checks; not ASR or listening.',
                  scriptSHA256AtCheck=sha(EPISODE/'script.md'),
                  scriptSHA256AtTTS=json.loads((VOICE/'input-provenance.json').read_text())['scriptSHA256'],
                  sentenceCount=len(sents), candidateCount=len(rows), failures=failures,
                  selectedReviewFlags=[r['id'] for r in rows if r['selected'] and r['reviewFlags']], candidates=rows)
    (VOICE/'qa-candidates.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'candidates'}, ensure_ascii=False))
    for row in rows:
        print(row['id'], row['take'], row['speechSeconds'], row['tailSeconds'], row['maxInnerSilenceS'], row['charactersPerSecond'], row['reviewFlags'])
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
