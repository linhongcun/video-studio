#!/usr/bin/env python3
"""Locate source clipping flags relative to the unchanged shared cut waveform."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

import numpy as np

D = Path(__file__).resolve().parents[1]
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
import common

evidence = D / 'qa/voice-independent.json'
report = json.loads(evidence.read_text())
rows = []
for flag in report['flags']:
    assert flag['flags'] == ['selected source contains clipped samples'], 'Additional source flags need separate review'
    record = next(r for r in report['sentences'] if r['id'] == flag['id'])
    source = D / 'voice/takes' / f"{record['id']}-{record['take']}.wav"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == record['takeSHA256']
    raw = common.load(str(source))
    cut, tail = common.cut(raw)
    # Match an unchanged interior sample sequence to locate the shared cut in
    # its original waveform; do not reproduce or replace common.cut's rule.
    anchor = cut[1000:1256]
    offsets = [int(i-1000) for i in np.flatnonzero(raw == anchor[0])
               if i >= 1000 and np.array_equal(raw[i:i+256], anchor)]
    assert len(offsets) == 1
    start = offsets[0]
    clipped = np.flatnonzero(np.abs(raw) >= .9999)
    assert len(clipped) == record['sourceClippedSamples']
    points = [{'sourceSample': int(i), 'seconds': float(i/48000),
               'amplitude': float(raw[i]), 'insideSharedCut': bool(start <= i < start+len(cut)),
               'neighborSamples': raw[max(0,i-4):i+5].tolist()} for i in clipped]
    assert not any(point['insideSharedCut'] for point in points), 'Clipping enters selected narration: review it before accepting'
    rows.append({'id': record['id'], 'sourceSHA256': record['takeSHA256'],
                 'sharedCutStartSample': start, 'sharedCutEndExclusive': start+len(cut),
                 'sharedCutSamples': len(cut), 'clippedPoints': points,
                 'resolution': 'All flagged source samples lie after the shared selected sentence cut, in the removed throwaway tail. They do not enter the emitted sentence or whole-track PCM.'})
assert report['selectedSentencePCMMatchesWholeTrack'] and report['publicVoiceCopyByteIdentical']
diagnosis = {'checkedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'status': 'resolved-source-tail-only', 'originalSignalFlagsPreserved': True,
             'sourceReportSHA256': hashlib.sha256(evidence.read_bytes()).hexdigest(),
             'voiceSHA256': report['voiceSHA256'], 'diagnoses': rows,
             'thresholdsChanged': False, 'sourcesRegenerated': False,
             'limitations': 'This locates waveform samples and shared cut boundaries. It is not ASR or semantic listening, and does not establish spoken pronunciation accuracy.'}
(D / 'qa/voice-signal-diagnosis.json').write_text(json.dumps(diagnosis,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':diagnosis['status'],'diagnosedSources':len(rows),'narrationClippingFromFlaggedSourcePoints':False},ensure_ascii=False))
