#!/usr/bin/env python3
"""Read production audio without mutation; write this archive's bounded QA evidence."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import resample_poly

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = next(p for p in OUT.parents if (p / 'AGENTS.md').is_file())
SLUG = OUT.name
EP = ROOT / f'episodes/puzzles/{SLUG}/production/revisions/logic-20261111/{SLUG}'
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
import common  # noqa: E402; actual shared implementation, never copied


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_wav(path):
    with wave.open(str(path), 'rb') as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        sr = w.getframerate()
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').copy()
    return sr, pcm


def longest_run(values):
    n = best = 0
    for v in values:
        n = n + 1 if v else 0
        best = max(n, best)
    return best


def metrics(sr, pcm):
    x = pcm.astype(np.float64) / 32768
    win = max(1, sr // 100)
    bins = np.abs(x[:len(x) // win * win]).reshape(-1, win).max(axis=1)
    active = np.flatnonzero(np.abs(x) > .005)
    peak = float(np.abs(x).max())
    true_peak = float(np.abs(resample_poly(x, 4, 1)).max())
    return {
        'sampleRate': sr, 'channels': 1, 'bitsPerSample': 16,
        'samples': len(pcm), 'seconds': len(pcm) / sr,
        'finite': bool(np.isfinite(x).all()),
        'allSilent': not bool(np.any(pcm)), 'peakAbs': peak,
        'clippedSamples': int((np.abs(pcm.astype(np.int32)) >= 32767).sum()),
        'rmsDbfs': float(20 * np.log10(np.sqrt(np.mean(x * x)) + 1e-30)),
        'truePeakDbtp4x': float(20 * np.log10(true_peak + 1e-30)),
        'maxLowPeakRunSecondsAt0p005': longest_run(bins <= .005) / 100,
        'leadingUnder0p005Seconds': int(active[0]) / sr if len(active) else len(x) / sr,
        'trailingUnder0p005Seconds': (len(x) - int(active[-1]) - 1) / sr if len(active) else len(x) / sr,
        'firstSample': int(pcm[0]), 'lastSample': int(pcm[-1]),
        'head10msPeak': float(np.abs(x[:win]).max()),
        'tail10msPeak': float(np.abs(x[-win:]).max()),
        'maxSampleJumpFirstAndLast10ms': float(max(np.abs(np.diff(x[:win])).max(), np.abs(np.diff(x[-win:])).max())),
    }


provenance = json.loads((EP / 'input-provenance.json').read_text())
source_relative = provenance.get('source', provenance.get('baselineProduction'))
source = ROOT / source_relative
reuse = provenance['voiceReuse']
changed = reuse['replaceSentenceIds']
sents = {s['id']: s for s in json.loads((EP / 'voice/sents.json').read_text())}
baseline_sents = {s['id']: s for s in json.loads((source / 'voice/sents.json').read_text())}
picks = json.loads((EP / 'voice/picks.json').read_text())
baseline_picks = json.loads((source / 'voice/picks.json').read_text())
script = (EP / 'script.md').read_text()
script_sents = []
for text in re.findall(r'^旁白：(.*)$', script, re.M):
    script_sents.extend(re.findall(r'[^。？！]+[。？！]?', text))
script_matches_prepared = script_sents == [s['text'] for s in sents.values()]
jobs_path = EP / 'voice/jobs-logic.json'
jobs = json.loads(jobs_path.read_text()) if jobs_path.exists() else None
jobs_match = jobs is not None and sorted(j[0] for j in jobs) == sorted(changed) and all(j[1] == picks[j[0]] and (j[2] or sents[j[0]]['tts']) == sents[j[0]]['tts'] for j in jobs)

report = {
    'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'episode': SLUG, 'production': str(EP.relative_to(ROOT)),
    'baselineCommit': provenance['baselineCommit'],
    'baselineProduction': source_relative,
    'scope': 'New selected takes: text metadata, signal, raw-to-48k conversion and actual shared tail cut. If assembled: exact new sentence-to-track PCM. Retained selected takes: text/pick/file SHA identity only.',
    'scriptSHA256': sha(EP / 'script.md'),
    'inputProvenanceSHA256': sha(EP / 'input-provenance.json'),
    'sharedCutImplementation': 'episodes/_shared/voice/common.py:cut',
    'sharedCutImplementationSHA256': sha(ROOT / 'episodes/_shared/voice/common.py'),
    'scriptSentencesMatchPreparedText': script_matches_prepared,
    'jobsSHA256': sha(jobs_path) if jobs_path.exists() else None,
    'jobsExactlyMatchChangedSelectedTts': jobs_match,
    'asrRequestedThisRun': False, 'semanticListeningPerformed': False,
    'wordAlignmentPerformed': False,
    'recognitionLimitation': 'No recognition request made in this 2026-11-11 QA. Prior 2026-11-07 pirate-gold evidence retained two HTTP400 Unsupported model mimo-v2.5 responses and one HTTP400 Unsupported model mimo-v2-omni response. They are historical service limitations, not requests for these clips. No successful transcript or semantic listening is claimed.',
    'historicalRecognitionEvidence': 'episodes/puzzles/pirate-gold/production/revisions/motivation-20261107/pirate-gold/qa/audio-asr-04-responses.json',
    'newTakeChecks': [], 'retainedTakeChecks': [],
}

build_path = EP / 'voice/build.json'
track_path = EP / 'voice.wav'
assembled = build_path.exists() and track_path.exists()
build = json.loads(build_path.read_text()) if assembled else None
rows = {r['id']: r for r in build['sentences']} if assembled else {}
track_sr, track_pcm = read_wav(track_path) if assembled else (None, None)
if assembled:
    report['assembly'] = {
        'wholeAudioSHA256': sha(track_path),
        'buildSHA256': sha(build_path),
        'buildSummarySHA256Matches': sha(track_path) == build['summary']['sha'],
        'trackSampleRate': track_sr, 'trackSamples': len(track_pcm),
        'trackSampleCountMatchesBuild': len(track_pcm) == build['summary']['samples'],
        'buildReportedLufs': build['summary']['track_lufs'],
        'buildReportedInnerDropouts': build['summary']['inner_dropouts'],
    }

for sid in changed:
    label = picks[sid]
    take = EP / f'voice/takes/{sid}-{label}.wav'
    raw = take.with_suffix('.raw.wav')
    text_path = take.with_suffix('.txt.json')
    take_text = json.loads(text_path.read_text())
    sr, pcm = read_wav(take)
    raw_sr, raw_pcm = read_wav(raw)
    resampled = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(raw), '-ar', '48000', '-ac', '1', '-f', 's16le', '-'], capture_output=True, check=True).stdout
    converted_matches = np.array_equal(pcm, np.frombuffer(resampled, dtype='<i2'))
    cut, tail = common.cut(common.load(str(take)))
    cut_trimmed = cut[:np.flatnonzero(np.abs(cut) > 1e-4)[-1] + 1]
    item = {
        'sentence': sid, 'selectedTake': label,
        'expectedText': sents[sid]['text'],
        'ttsTextMetadata': take_text,
        'metadataMatchesPreparedTts': take_text == sents[sid]['tts'],
        'ttsMetadataIsScriptPlusDiscardTail': take_text == sents[sid]['text'] + '好。',
        'hashes': {str(p.relative_to(EP)): sha(p) for p in [take, raw, text_path]},
        'rawSignal': metrics(raw_sr, raw_pcm), 'convertedTakeSignal': metrics(sr, pcm),
        'rawTo48kPcmConversionMatchesExactly': bool(converted_matches),
        'sharedCutRetainedSamplesBeforeFinalTrim': len(cut),
        'sharedCutRetainedSamplesAfterFinalTrim': len(cut_trimmed),
        'discardedStandaloneTailSeconds': float(tail),
        'discardedStandaloneTailDurationAtLeast0p15s': bool(tail >= .15),
        'discardedTailContentSemanticallyVerified': False,
        'actualRecognitionText': None, 'pronunciationVerified': False,
        'semanticDifferenceFromScript': 'Not assessable: no transcript or semantic listening.',
    }
    item['newTakeSignalAndMetadataPass'] = all([
        item['metadataMatchesPreparedTts'], item['ttsMetadataIsScriptPlusDiscardTail'],
        sr == 48000, raw_sr == 24000, converted_matches,
        item['discardedStandaloneTailDurationAtLeast0p15s'],
        not item['rawSignal']['allSilent'], not item['convertedTakeSignal']['allSilent'],
        item['rawSignal']['clippedSamples'] == 0, item['convertedTakeSignal']['clippedSamples'] == 0,
    ])
    if assembled:
        row = rows[sid]
        sentence = EP / f'voice/sentences/{sid}.wav'
        sentence_sr, sentence_pcm = read_wav(sentence)
        signal = metrics(sentence_sr, sentence_pcm)
        checks = {
            'inputSentenceSHA256': sha(sentence), 'signal': signal,
            'startSample': row['startSample'], 'endSample': row['endSample'],
            'sampleCountMatchesBuild': len(sentence_pcm) == row['endSample'] - row['startSample'],
            'sharedCutLengthMatchesSentence': len(sentence_pcm) == len(cut_trimmed),
            'sentencePcmEqualsWholeTrackSlice': bool(np.array_equal(sentence_pcm, track_pcm[row['startSample']:row['endSample']])),
            'metadataMatchesBuild': row['text'] == sents[sid]['text'] and row['tts'] == take_text and row['take'] == label,
            'tailSecondsMatchesBuildRounded': bool(round(tail, 2) == row['tailCut']),
        }
        checks['pass'] = all([checks['sampleCountMatchesBuild'], checks['sharedCutLengthMatchesSentence'], checks['sentencePcmEqualsWholeTrackSlice'], checks['metadataMatchesBuild'], checks['tailSecondsMatchesBuildRounded'], sentence_sr == 48000, signal['clippedSamples'] == 0, signal['finite'], not signal['allSilent'], signal['maxLowPeakRunSecondsAt0p005'] < .5])
        item['assemblyCheck'] = checks
    report['newTakeChecks'].append(item)

for sid, baseline in reuse['reusedSentences'].items():
    record = {
        'sentence': sid, 'take': picks[sid],
        'selectedTakeMatchesBaseline': picks[sid] == baseline_picks[sid] == baseline['take'],
        'preparedTextAndTtsUnchanged': all(sents[sid][k] == baseline_sents[sid][k] == baseline[k] for k in ['text', 'tts']),
        'files': [],
    }
    for rel, expected in baseline['files'].items():
        original_hash, new_hash = sha(source / rel), sha(EP / rel)
        record['files'].append({'relative': rel, 'provenanceSHA256': expected, 'originalSHA256': original_hash, 'revisionSHA256': new_hash, 'matches': expected == original_hash == new_hash})
    record['pass'] = record['selectedTakeMatchesBaseline'] and record['preparedTextAndTtsUnchanged'] and all(f['matches'] for f in record['files'])
    report['retainedTakeChecks'].append(record)

report['summary'] = {
    'newTakeCount': len(report['newTakeChecks']),
    'newTakesSignalAndMetadataPass': script_matches_prepared and jobs_match and all(r['newTakeSignalAndMetadataPass'] for r in report['newTakeChecks']),
    'retainedTakeCount': len(report['retainedTakeChecks']),
    'retainedFileCount': sum(len(r['files']) for r in report['retainedTakeChecks']),
    'retainedTakeIdentityPass': all(r['pass'] for r in report['retainedTakeChecks']),
    'assembledAudioPresent': assembled,
    'newSentencesAssemblyPass': (all(r['assemblyCheck']['pass'] for r in report['newTakeChecks']) and report['assembly']['buildSummarySHA256Matches'] and report['assembly']['trackSampleCountMatchesBuild']) if assembled else None,
    'semanticVerdict': 'Unverified; no new ASR or semantic listening performed.',
}
(OUT / 'audio-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report['summary'], ensure_ascii=False, indent=2))
