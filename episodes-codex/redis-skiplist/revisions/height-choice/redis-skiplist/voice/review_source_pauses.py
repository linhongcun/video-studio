#!/usr/bin/env python3
"""Locate flagged low-energy intervals in the original selected source samples.

This is a numerical source/crop review, not listening or word recognition.
It does not change takes, cuts, pauses, normalization or shared implementations.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import numpy as np
from scipy.signal import correlate

D = Path(__file__).resolve().parents[1]
ROOT = next(parent for parent in D.parents
            if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
from common import load, cut


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    audit = json.loads((D / 'qa-voice-takes.json').read_text())
    assert not audit['failures']
    flag_ids = {warning.split(':', 1)[0] for warning in audit['warnings']}
    assert all(warning.endswith('low-level interval at least .50s') for warning in audit['warnings'])
    rows = []
    for row in audit['rows']:
        if row['id'] not in flag_ids:
            continue
        path = D / 'voice/takes' / (row['id'] + '-' + row['take'] + '.wav')
        raw = load(str(path))
        trimmed, tail = cut(raw)
        lag = int(np.argmax(correlate(raw, trimmed, mode='valid', method='fft')))
        # Only the shared cut's first10ms/last20ms fade is excluded. Every
        # remaining selected sample must be exactly from the original take.
        assert np.array_equal(raw[lag+480:lag+len(trimmed)-960], trimmed[480:-960])
        active = np.abs(trimmed[:len(trimmed)//480*480]).reshape(-1,480).max(1) > .005
        best = (0,0); start = None
        for index, value in enumerate(np.r_[active, True]):
            if not value and start is None:
                start = index
            elif value and start is not None:
                if index-start > best[1]-best[0]: best = (start,index)
                start = None
        a,b = best[0]*480,best[1]*480
        assert a >= 480 and b <= len(trimmed)-960
        assert np.array_equal(raw[lag+a:lag+b], trimmed[a:b])
        rows.append({'id':row['id'],'take':row['take'],'takeSHA256':sha(path),
            'longestLowEnergySeconds':(b-a)/48000,'intervalInCutSamples':[a,b],
            'intervalInOriginalTakeSamples':[lag+a,lag+b],
            'cropOffsetSamples':lag,'trimmedInteriorEqualsOriginalTake':True,
            'flagIntervalEqualsOriginalTake':True,'discardedTailSeconds':tail})
    assert {row['id'] for row in rows} == flag_ids
    report={'status':'source-intervals-verified-awaiting-track-replay',
        'checkedAtUTC':datetime.now(timezone.utc).isoformat(),
        'scope':'Source-level low-energy flags retained as pacing, not gaps introduced by cutting or assembly. No claim that words or naturalness were listened to.',
        'sourceAuditSHA256':sha(D/'qa-voice-takes.json'),'sourceFlagIds':sorted(flag_ids),
        'decision':'Retain selected sources; no further TTS solely to eliminate a low-energy threshold flag. Whole-track replay and coverage remain required.',
        'rows':rows,'ASRPerformed':False,'semanticListeningPerformed':False,
        'fullHumanListeningPerformed':False}
    (D/'voice/pause-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'reviewedFlags':len(rows),'sourceFlags':sorted(flag_ids)}))


if __name__=='__main__': main()
