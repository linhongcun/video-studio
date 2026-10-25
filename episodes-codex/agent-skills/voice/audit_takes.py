#!/usr/bin/env python3
"""Signal/provenance review using shared cut/load; does not recognize speech."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import wave

import numpy as np

V = Path(__file__).resolve().parent
ROOT = V.parents[2]
SHARED = ROOT / 'episodes/_shared/voice'
sys.path.insert(0, str(SHARED))
from common import cut, load

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sents = json.loads((V/'sents.json').read_text())
picks = json.loads((V/'picks.json').read_text()) if (V/'picks.json').exists() else {}
rows = []
for sent in sents:
    take = picks.get(sent['id'], 'a')
    path = V/'takes'/f"{sent['id']}-{take}.wav"
    item = {'id':sent['id'], 'take':take, 'warnings':[], 'errors':[]}
    if not path.is_file():
        item['errors'].append('missing selected take');rows.append(item);continue
    text_path = path.with_suffix('.txt.json')
    raw_path = path.with_suffix('.raw.wav')
    expected = sent['tts']
    item['ttsTextMatchesPrepared'] = json.loads(text_path.read_text()) == expected
    if not item['ttsTextMatchesPrepared']:item['errors'].append('TTS text differs; declare substitution before selection')
    with wave.open(str(path)) as w:
        item.update(sampleRate=w.getframerate(), channels=w.getnchannels(), sampleWidth=w.getsampwidth(), sourceSeconds=w.getnframes()/w.getframerate())
    if (item['sampleRate'],item['channels'],item['sampleWidth']) != (48000,1,2):item['errors'].append('unexpected converted PCM format')
    try:
        converted = load(str(path)); trimmed, tail = cut(converted)
        item.update(sha256=sha(path),rawSha256=sha(raw_path),cutSeconds=len(trimmed)/48000,throwawayTailSeconds=round(float(tail),4))
        blocks=np.abs(trimmed[:len(trimmed)//480*480]).reshape(-1,480).max(1)
        flags=blocks<=0.005;best=run=0
        for flag in flags:
            run=run+1 if flag else 0;best=max(best,run)
        item['maxLowLevelGapSeconds'] = best/100
        # This is an episode review trigger, not a shared speech/tail guarantee.
        if tail < 0.22:item['warnings'].append('short throwaway tail; compare another take')
        if best >= 50:item['warnings'].append('low-level gap >=0.5s; compare natural pacing')
        if len(trimmed)<4800:item['errors'].append('empty or very short shared-cut result')
    except Exception as e:item['errors'].append('shared-cut failed: '+type(e).__name__)
    rows.append(item)
# Raw take levels vary. Keep their review triggers, then resolve only gap
# triggers against the same selected take in the actual normalized build.
build_path = V/'build.json'
if build_path.exists():
    build = json.loads(build_path.read_text())
    normalized = {r['id']:r for r in build['sentences']}
    for item in rows:
        result = normalized.get(item['id'])
        item['rawSignalTriggers'] = item['warnings'][:]
        if result and result['take'] == item['take']:
            item['normalizedGapSeconds'] = result['maxInnerSilenceS']
            item['normalizedBuildAudioSha256'] = build['summary']['sha']
            if result['maxInnerSilenceS'] < 0.5:
                item['warnings'] = [w for w in item['warnings'] if not w.startswith('low-level gap')]
report={'method':'Shared common.load/cut plus PCM envelope and prepared-text checks; raw-level triggers remain recorded and gap verdicts use the same selected take at actual shared-build level. Not ASR or phonetic listening.', 'asrAvailable':importlib.util.find_spec('faster_whisper') is not None, 'sharedCommonSha256':sha(SHARED/'common.py'), 'sentences':len(sents),'takes':rows,'errors':sum(len(x['errors']) for x in rows),'warnings':sum(len(x['warnings']) for x in rows)}
(V/'qa-take-signals.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sentences':len(rows),'errors':report['errors'],'warnings':report['warnings'],'flagged':[{'id':x['id'],'take':x['take'],'warnings':x['warnings'],'errors':x['errors']} for x in rows if x['warnings'] or x['errors']]},ensure_ascii=False))
raise SystemExit(1 if report['errors'] else 0)
