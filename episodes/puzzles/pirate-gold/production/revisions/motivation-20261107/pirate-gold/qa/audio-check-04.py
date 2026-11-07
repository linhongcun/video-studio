#!/usr/bin/env python3
"""Read-only two-sentence signal/PCM/cut QA; writes only qa/audio-* evidence."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import sys
import wave

import numpy as np

EP = Path(__file__).resolve().parent.parent
ROOT = next(p for p in EP.parents if (p / 'AGENTS.md').is_file())
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
import common  # noqa: E402; use the actual shared cut implementation


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_wav(path):
    with wave.open(str(path), 'rb') as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        sr, n = w.getframerate(), w.getnframes()
        pcm = np.frombuffer(w.readframes(n), dtype='<i2').copy()
    return sr, pcm


def longest_run(values):
    current = longest = 0
    for v in values:
        current = current + 1 if v else 0
        longest = max(current, longest)
    return longest


build = json.loads((EP / 'voice/build.json').read_text())
recognition = json.loads((EP / 'qa/audio-asr-04-responses.json').read_text())
requests = {r['sentence']: r for r in recognition['requests']}
track_sr, track = read_wav(EP / 'voice.wav')
picks = json.loads((EP / 'voice/picks.json').read_text())
script = (EP / 'script.md').read_text()
script04 = re.search(r'### 04 backwards\n旁白：(.*?)\n画面：', script).group(1)
script_sentences = re.findall(r'[^。？！]+[。？！]', script04)
assert len(script_sentences) == 2
sents = {r['id']: r for r in json.loads((EP / 'voice/sents.json').read_text())}
report = {
    'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': '04-backwards-{1,2} only; signal, exact PCM placement, shared cut and external recognition attempt. Other 26 sentences are outside this check.',
    'scriptSHA256': sha(EP / 'script.md'),
    'wholeAudioSHA256': sha(EP / 'voice.wav'),
    'recognitionEvidence': 'qa/audio-asr-04-responses.json',
    'sharedCutImplementation': 'episodes/_shared/voice/common.py:cut',
    'sharedCutImplementationSHA256': sha(ROOT / 'episodes/_shared/voice/common.py'),
    'semanticListeningPerformed': False,
    'interiorWordAlignmentPerformed': False,
    'sentences': [],
}
for row in build['sentences']:
    sid = row['id']
    if sid not in ['04-backwards-1', '04-backwards-2']:
        continue
    assert picks[sid] == row['take'] == 'motivation'
    script_text = script_sentences[int(sid.rsplit('-', 1)[1]) - 1]
    take_text = json.loads((EP / f'voice/takes/{sid}-motivation.txt.json').read_text())
    path = EP / f'voice/sentences/{sid}.wav'
    take = EP / f'voice/takes/{sid}-motivation.wav'
    sr, pcm = read_wav(path)
    assert sr == track_sr == 48000
    x = pcm.astype(np.float64) / 32768
    take_x = common.load(str(take))
    cut, discarded_tail = common.cut(take_x)
    nz = np.flatnonzero(np.abs(cut) > 1e-4)
    cut_trimmed = cut[:nz[-1] + 1]
    bins = np.abs(x[:len(x) // 480 * 480]).reshape(-1, 480).max(axis=1)
    active = np.flatnonzero(np.abs(x) > 0.005)
    response = requests[sid]
    attempts = [response] + [r for r in recognition.get('fallbackRequests', []) if r['sentence'] == sid]
    contents = [c.get('content') for c in response.get('choices', []) if c.get('content')]
    text = '\n'.join(contents) if contents else None
    item = {
        'id': sid, 'take': 'motivation', 'expectedText': row['text'],
        'buildAndPreparedTextMatchScript': row['text'] == sents[sid]['text'] == script_text,
        'takeTtsMetadataMatchesScriptWithDiscardTail': take_text == row['tts'] == sents[sid]['tts'] == script_text + '好。',
        'actualRecognition': text,
        'textDifference': 'Not assessable: no successful recognition text returned.' if text is None else 'See recognition comparison.',
        'recognitionHTTPStatus': response.get('httpStatus'),
        'recognitionAttempts': [{'model': r.get('modelRequested', recognition['model']), 'httpStatus': r.get('httpStatus'), 'errorBody': r.get('errorBody')} for r in attempts],
        'recognitionInputSHA256Matches': sha(path) == response['inputSHA256'],
        'hashes': {str(p.relative_to(EP)): sha(p) for p in [path, take, take.with_suffix('.raw.wav'), take.with_suffix('.txt.json')]},
        'sampleRate': sr, 'channels': 1, 'bitsPerSample': 16,
        'samples': len(pcm), 'durationSeconds': len(pcm) / sr,
        'trackStartSample': row['startSample'], 'trackEndSample': row['endSample'],
        'sampleCountMatchesBuild': len(pcm) == row['endSample'] - row['startSample'],
        'pcmMatchesWholeAudioExactly': bool(np.array_equal(pcm, track[row['startSample']:row['endSample']])),
        'finite': bool(np.isfinite(x).all()),
        'peakAbs': float(np.abs(x).max()),
        'clippedSamples': int((np.abs(pcm.astype(np.int32)) >= 32767).sum()),
        'rmsDbfs': float(20 * np.log10(np.sqrt(np.mean(x * x)))),
        'maxLowPeakRunSecondsAt0p005': longest_run(bins <= 0.005) / 100,
        'leadingUnder0p005Seconds': int(active[0]) / sr,
        'trailingUnder0p005Seconds': (len(x) - int(active[-1]) - 1) / sr,
        'firstSample': int(pcm[0]), 'lastSample': int(pcm[-1]),
        'head10msPeak': float(np.abs(x[:480]).max()),
        'tail10msPeak': float(np.abs(x[-480:]).max()),
        'maxSampleJumpInFirstAndLast10ms': float(max(np.abs(np.diff(x[:480])).max(), np.abs(np.diff(x[-480:])).max())),
        'sharedCutRetainedSamplesBeforeFinalTrim': len(cut),
        'sharedCutRetainedSamplesAfterFinalTrim': len(cut_trimmed),
        'sharedCutLengthMatchesAssembledSentence': len(cut_trimmed) == len(pcm),
        'discardedStandaloneTailSeconds': float(discarded_tail),
        'buildReportedTailSeconds': row['tailCut'],
        'tailContentSemanticallyVerified': False,
        'limitations': 'Signal checks establish that the clips are not all-silent, have no full-scale clipped samples, have no >=0.5s low-peak runs and have exact placement; they do not prove pronunciation, final syllable completeness or whether the discarded tail said 好.',
    }
    item['signalAndPlacementPass'] = all([item['buildAndPreparedTextMatchScript'], item['takeTtsMetadataMatchesScriptWithDiscardTail'], item['recognitionInputSHA256Matches'], item['sampleCountMatchesBuild'], item['pcmMatchesWholeAudioExactly'], item['finite'], item['clippedSamples'] == 0, item['sharedCutLengthMatchesAssembledSentence'], item['maxLowPeakRunSecondsAt0p005'] < 0.5])
    report['sentences'].append(item)
report['signalAndPlacementPass'] = all(s['signalAndPlacementPass'] for s in report['sentences'])
report['semanticVerdict'] = 'Unverified: documented MiMo audio input requests returned HTTP 400 Unsupported model mimo-v2.5 for both clips; the single authorized fallback on clip 1 returned Unsupported model mimo-v2-omni, so fallback clip 2 was not requested. No transcription or semantic listening result.'
out = EP / 'qa/audio-check-04.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
