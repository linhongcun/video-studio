"""Read-only numeric provenance for pre-mix and mixed AAC, including Java tail.

Accept another episode path as its sole argument to use the same comparison.
Does not synthesize, mix, recognize speech, listen or mutate frozen inputs.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import correlate, correlation_lags


D = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
ROOT = D.parents[1]
OUT = D/'qa-encoded-voice-content.json'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
manifest = json.loads((D/'source-sha256.json').read_text())
before = {name: sha(D/name) for name in manifest}
assert before == manifest, 'Frozen inputs changed before check'
sb = json.loads((D/'storyboard.json').read_text())
build = json.loads((D/'voice/build.json').read_text())
card = sb['meta']['javaEndCard']
assert card['kind'] == 'java-design-pattern' and card['durationInFrames'] == 150
with wave.open(str(D/'voice.wav')) as handle:
    assert (handle.getframerate(), handle.getnchannels(), handle.getsampwidth()) == (48000, 1, 2)
    reference = np.frombuffer(handle.readframes(handle.getnframes()), '<i2').astype(float)/32768
assert len(reference) == sb['meta']['durationInFrames']*1600
commands = []


def decode(path):
    command = ['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','48000','-f','f32le','-']
    commands.append(command)
    return np.frombuffer(subprocess.run(command, capture_output=True, check=True).stdout, '<f4').astype(float)


def offset_for(decoded):
    n = min(1440000, len(reference), len(decoded))
    values = correlate(decoded[:n], reference[:n], mode='full', method='fft')
    lags = correlation_lags(n, n, 'full')
    selection = np.abs(lags) <= 4800
    return int(lags[selection][np.argmax(values[selection])])


def metrics(a, b):
    n = len(a)
    am, bm = float(a.mean()), float(b.mean())
    aa, bb, ab = float(np.dot(a,a)), float(np.dot(b,b)), float(np.dot(a,b))
    gain = ab/aa
    return {
        'samples': n,
        'correlation': float((ab-n*am*bm)/np.sqrt((aa-n*am*am)*(bb-n*bm*bm))),
        'fittedGain': gain,
        'fittedGainDB': float(20*np.log10(abs(gain))),
        'residualRMSE': float(np.sqrt(max(0,(bb-2*gain*ab+gain*gain*aa)/n))),
    }


def compare(path):
    decoded = decode(path)
    offset = offset_for(decoded)
    a, b = max(0,-offset), max(0,offset)
    n = min(len(reference)-a, len(decoded)-b)
    rows = []
    for row in build['sentences']:
        start, end = row['startSample'], row['endSample']
        assert start+offset >= 0 and end+offset <= len(decoded)
        rows.append({'id':row['id'], **metrics(reference[start:end],decoded[start+offset:end+offset])})
    return decoded, {
        'file': str(path.relative_to(D)), 'sha256': sha(path),
        'referenceSamples': len(reference), 'decodedSamples': len(decoded),
        'sampleOffset': offset, 'offsetMilliseconds': offset/48, 'offsetFrames': offset/1600,
        'offsetConvention': 'decoded[t + sampleOffset] corresponds to frozen voice.wav[t]',
        'lagProbeSamples': min(1440000,len(reference),len(decoded)), 'lagSearchSamples': [-4800,4800],
        'referenceCompareFrom': a, 'decodedCompareFrom': b, 'commonAlignedSamples': n,
        'uncomparedReferenceSamples': len(reference)-n, 'uncomparedDecodedSamples': len(decoded)-n,
        'uncomparedReferenceAllZero': not bool(np.any(reference[:a])) and not bool(np.any(reference[a+n:])),
        'whole': metrics(reference[a:a+n],decoded[b:b+n]),
        'sentenceCount': len(rows), 'minimumSentenceCorrelation': min(row['correlation'] for row in rows),
        'sentences': rows,
    }


premix, premix_report = compare(D/'remotion/out/voice.mp4')
mixed, mixed_report = compare(D/'video.mp4')
music_path = ROOT/'episodes/_shared/music/Wallpaper.mp3'
music = decode(music_path)
start = card['from']*1600
end = (card['from']+card['durationInFrames'])*1600
assert not np.any(reference[start:end])
uo, mo = premix_report['sampleOffset'], mixed_report['sampleOffset']
premix_tail, mixed_tail = premix[start+uo:end+uo], mixed[start+mo:end+mo]
# Compare Wallpaper during an unfaded part of the card. This source exceeds
# episode duration, so the shared mixer's looping branch is not applicable.
ws, we = start+4800, end-100800
assert len(music) >= we
background = metrics(music[ws:we],mixed[ws+mo:we+mo])
criteria = {
    'unmixedMinimumWholeCorrelation': .99, 'unmixedMinimumSentenceCorrelation': .98,
    'unmixedMaximumAbsoluteSampleOffset': 0,
    'mixedMinimumWholeCorrelation': .95, 'mixedMinimumSentenceCorrelation': .90,
    'mixedMaximumAbsoluteOffsetSamples': 800,
    'javaCardWallpaperWindowMinimumCorrelation': .99,
    'unmixedJavaCardMaximumAbsPCM': .0001,
}
passed = (
    premix_report['whole']['correlation'] >= .99
    and premix_report['minimumSentenceCorrelation'] >= .98 and uo == 0
    and premix_report['uncomparedReferenceSamples'] == 0
    and mixed_report['whole']['correlation'] >= .95
    and mixed_report['minimumSentenceCorrelation'] >= .90 and abs(mo) <= 800
    and background['correlation'] >= .99 and float(np.abs(premix_tail).max()) < .0001
)
rms_db = lambda data: float(20*np.log10(np.sqrt(np.mean(data**2))+1e-20))
report = {
    'revision': 'adapter-pattern-first-release', 'episode': D.name,
    'checkedAtUTC': datetime.now(timezone.utc).isoformat(), 'executor': '/root/observer_voice',
    'comparisonScript': 'check-encoded-voice.py',
    'comparisonScriptSHA256': sha(Path(__file__).resolve()),
    'scope': f'Read-only actual pre-mix AAC and final mixed AAC comparison with frozen WAV: complete aligned tracks and all {len(build["sentences"])} sentence windows, plus Java-card zero-voice/Wallpaper-only region. No ASR, pronunciation or listening.',
    'reference': 'voice.wav', 'referenceSHA256': sha(D/'voice.wav'),
    'sampleRate': 48000, 'referenceFrames': sb['meta']['durationInFrames'],
    'unmixedAAC': premix_report, 'finalMixedAAC': mixed_report,
    'javaCard': {
        'fromFrame': card['from'], 'frames': 150, 'referenceSamples': end-start,
        'referenceVoiceAllZero': True,
        'unmixedDecodedSamplesCompared': len(premix_tail),
        'finalMixedDecodedSamplesCompared': len(mixed_tail),
        'finalMixedMissingTrailingReferenceSamples': (end-start)-len(mixed_tail),
        'unmixedDecodedAbsPeak': float(np.abs(premix_tail).max()),
        'finalMixedRMSDBFS': rms_db(mixed_tail),
        'finalMixedFirstHalfSecondRMSDBFS': rms_db(mixed_tail[:24000]),
        'finalMixedLastHalfSecondRMSDBFS': rms_db(mixed_tail[-24000:]),
        'backgroundSource': '../../episodes/_shared/music/Wallpaper.mp3',
        'backgroundSHA256': sha(music_path),
        'unfadedBackgroundCompareFromReferenceSample': ws,
        'unfadedBackgroundCompareToReferenceSample': we,
        'wallpaperOnlyWindow': background,
        'explanation': 'Frozen voice is digital silence throughout the Java card. Final audio intentionally retains Wallpaper at the shared constant mix level, with its final two-second fade. It is therefore not expected to equal the silent voice WAV.',
    },
    'actualMixReport': json.loads((D/'remotion/out/mix-report.json').read_text()),
    'decodeCommands': commands, 'criteria': criteria,
    'frozenInputsChecked': len(manifest),
    'frozenInputsUnchanged': before == {name:sha(D/name) for name in manifest},
    'passed': bool(passed),
    'limitations': [
        'AAC is lossy; numeric content provenance does not establish recognized words or correct pronunciation.',
        'Final mixed signal intentionally differs because of Wallpaper and shared loudness/limiter processing. Its offset is measured independently from pre-mix provenance.',
        'No full listening, ASR, source separation or audience understanding assessment was performed.',
    ],
}
assert report['frozenInputsUnchanged'], 'Frozen inputs changed during check'
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({
    'unmixed': {key:premix_report[key] for key in ['sampleOffset','whole','minimumSentenceCorrelation']},
    'mixed': {key:mixed_report[key] for key in ['sampleOffset','whole','minimumSentenceCorrelation']},
    'javaWallpaperCorrelation': background['correlation'],
    'unmixedCardPeak': report['javaCard']['unmixedDecodedAbsPeak'],
    'frozenInputsChecked': len(manifest), 'frozenInputsUnchanged': report['frozenInputsUnchanged'],
    'passed': report['passed'],
},ensure_ascii=False))
if not passed:
    raise SystemExit(1)
