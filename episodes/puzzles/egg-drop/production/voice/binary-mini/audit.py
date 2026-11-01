#!/usr/bin/env python3
"""Inspect only this revision's actual candidates through shared load/cut."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys
import wave
import numpy as np

D = Path(__file__).resolve().parents[2]
V = Path(__file__).resolve().parent / 'voice'
sys.path.insert(0, str(D.parents[1] / 'episodes/_shared/voice'))
from common import load, cut

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stamp = lambda p: datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()
sents = {r['id']: r for r in json.loads((V/'sents.json').read_text())}
picks = json.loads((V/'picks.json').read_text())
jobs = {}
for path in sorted(V.glob('jobs_*.json')):
    for row in json.loads(path.read_text()):
        sid, take, text = row[:3]
        jobs[(sid, take)] = dict(jobsFile=path.name, jobsSHA256=sha(path),
                                jobsPreparedFileMtimeUTC=stamp(path),
                                text=text or sents[sid]['tts'], style=row[3] if len(row)>3 else None)
rows = []
for path in sorted((V/'takes').glob('*.raw.wav')):
    stem = path.name.removesuffix('.raw.wav')
    sid, take = stem.rsplit('-', 1)
    target = path.with_name(stem+'.wav')
    actual = json.loads(path.with_name(stem+'.txt.json').read_text())
    assert actual == jobs[(sid,take)]['text'] == sents[sid]['tts']
    with wave.open(str(target)) as audio:
        assert (audio.getframerate(),audio.getnchannels(),audio.getsampwidth()) == (48000,1,2)
        converted = audio.readframes(audio.getnframes())
    raw = subprocess.run(['ffmpeg','-v','error','-i',str(path),'-ar','48000','-ac','1',
                          '-c:a','pcm_s16le','-f','s16le','-'], capture_output=True, check=True).stdout
    assert raw == converted
    y, tail = cut(load(str(target)))
    levels = np.max(np.abs(y[:len(y)//480*480].reshape(-1,480)),axis=1)
    edges = np.flatnonzero(np.diff(np.r_[False,levels<=.005,False]))
    longest = int(np.max(edges[1::2]-edges[::2])) if len(edges) else 0
    rows.append(dict(id=sid,take=take,selected=picks[sid]==take,actualTTSInput=actual,
                     expectedRequest=jobs[(sid,take)],inputExact=True,rawTo48kPCMExact=True,
                     rawSHA256=sha(path),wavSHA256=sha(target),rawCompletedFileMtimeUTC=stamp(path),
                     speechSeconds=len(y)/48000,tailSeconds=float(tail),maxInnerSilenceS=longest/100,
                     charactersPerSecond=len(re.findall(r'[\u4e00-\u9fff]',sents[sid]['text']))/(len(y)/48000),
                     rawReview=bool(longest>=50 or tail<.15)))
build = json.loads((V/'build.json').read_text())
assert len([r for r in rows if r['selected']]) == 4
report = dict(checkedAtUTC=datetime.now(timezone.utc).isoformat(),
              scope='Only four revised sentences and their actual candidates; no ASR or semantic listening.',
              timestampDefinition='Actual jobs/raw file mtimes, not claimed network acceptance timestamps.',
              candidates=rows, rawWarningCount=sum(r['rawReview'] for r in rows),
              selectedRawReviewIDs=[r['id'] for r in rows if r['selected'] and r['rawReview']],
              selectedProcessedInnerDropouts=build['summary']['inner_dropouts'],
              finalProcessedEnvelopeAccepted=not build['summary']['inner_dropouts'],
              processedMaximumInnerSilenceS=max(r['maxInnerSilenceS'] for r in build['sentences']),
              ASRPerformed=False,semanticListeningPerformed=False)
(V/'qa-candidates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='candidates'},ensure_ascii=False))
assert report['finalProcessedEnvelopeAccepted']
