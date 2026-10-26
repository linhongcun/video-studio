#!/usr/bin/env python3
"""Verify selected sources -> assembled voice-only WAV, before music/encoding.

The replay executes the actual shared builder rather than copying its audio
algorithm. It establishes provenance and timing, not semantic listening.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import wave
import numpy as np

D = Path(__file__).resolve().parents[1]
ROOT = next(parent for parent in D.parents
            if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
SR = 48000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pcm(path):
    with wave.open(str(path)) as wav:
        assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (1, 2, SR)
        return wav.readframes(wav.getnframes())


def main():
    config = json.loads((D / 'episode-config.json').read_text())
    expected_sentences = 2 * config['shotCount']
    selected = json.loads((D / 'qa-voice-takes.json').read_text())
    assert selected['status'] in {'passed', 'needs-review'} and selected['sentences'] == expected_sentences
    assert not selected['failures']
    pause_review = json.loads((D / 'voice/pause-review.json').read_text())
    assert pause_review['sourceAuditSHA256'] == sha(D / 'qa-voice-takes.json')
    source_flags = {warning.split(':', 1)[0] for warning in selected['warnings']}
    assert all(warning.endswith('low-level interval at least .50s') for warning in selected['warnings'])
    assert source_flags == set(pause_review['sourceFlagIds'])
    assert all(row['trimmedInteriorEqualsOriginalTake'] and row['flagIntervalEqualsOriginalTake'] for row in pause_review['rows'])
    build = json.loads((D / 'voice/build.json').read_text())
    sents = json.loads((D / 'voice/sents.json').read_text())
    picks = json.loads((D / 'voice/picks.json').read_text())
    samples = pcm(D / 'voice.wav')
    assert len(samples) // 2 == build['summary']['samples']
    assert build['summary']['samples'] * 30 == build['summary']['frames'] * SR
    assert sha(D / 'voice.wav') == sha(D / 'remotion/public/audio/voice.wav')
    assert len(build['sentences']) == len(sents) == expected_sentences
    previous_end = 0
    rows = []
    for request, row in zip(sents, build['sentences']):
        assert request['id'] == row['id'] and request['text'] == row['text']
        assert row['take'] == picks.get(row['id'], 'a')
        start, end = row['startSample'], row['endSample']
        assert start >= previous_end and end > start
        window = samples[start * 2:end * 2]
        sentence_pcm = pcm(D / 'voice/sentences' / (row['id'] + '.wav'))
        assert window == sentence_pcm
        rows.append({'id': row['id'], 'take': row['take'], 'startSample': start,
                     'endSample': end, 'startFrame': row['startFrame'],
                     'endFrame': row['endFrame'], 'lufs': row['lufs'],
                     'maxInnerSilenceS': row['maxInnerSilenceS'],
                     'trackWindowEqualsSentencePCM': True})
        previous_end = end
    with tempfile.TemporaryDirectory(prefix='bloom-voice-replay-') as temp:
        replica = Path(temp)
        replica_voice = replica / 'voice'
        (replica_voice / 'takes').mkdir(parents=True)
        for name in ['params.json', 'picks.json', 'sents.json']:
            shutil.copyfile(D / 'voice' / name, replica_voice / name)
        for row in sents:
            filename = row['id'] + '-' + picks.get(row['id'], 'a') + '.wav'
            shutil.copyfile(D / 'voice/takes' / filename, replica_voice / 'takes' / filename)
        replay = subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/voice/build.py'),
                                 '--dir', str(replica)], check=True, capture_output=True, text=True)
        (D / 'voice/replay-build.log').write_text(replay.stdout + replay.stderr)
        replay_sha = sha(replica / 'voice.wav')
        assert replay_sha == sha(D / 'voice.wav'), 'Shared selected-source replay changed the output bytes'
    analysis = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(D / 'voice.wav'),
        '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'],
        check=True, capture_output=True, text=True)
    measured = json.loads(re.findall(r'\{\s*"input_i".*?\}', analysis.stderr, re.S)[-1])
    level, peak = float(measured['input_i']), float(measured['input_tp'])
    assert abs(level + 16) <= .5, ('voice-only loudness', level)
    assert peak <= -1.95, ('voice-only true peak', peak)
    assert set(build['summary']['inner_dropouts']) <= source_flags, 'Unreviewed low-energy flag in assembled track'
    signal = np.frombuffer(samples, dtype='<i2')
    assert np.max(np.abs(signal.astype(np.int32))) < 32767
    tail = signal[previous_end:]
    assert len(tail) and not np.any(tail), 'The configured voice tail must be zero PCM'
    report = {'status': 'passed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
              'scope': 'Selected raw/take requests and conversion, shared cuts, and assembled voice-only WAV before music. No final mixed or encoded audio checked here.',
              'scriptSHA256': sha(D / 'script.md'), 'voiceSHA256': sha(D / 'voice.wav'),
              'publicVoiceSHA256': sha(D / 'remotion/public/audio/voice.wav'),
              'sourceAuditSHA256': sha(D / 'qa-voice-takes.json'), 'sentences': len(rows),
              'sourceSignalScreeningStatus': selected['status'],
              'retainedSourceSignalFlags': selected['warnings'],
              'sourcePauseReview': {'path': 'voice/pause-review.json', 'sha256': sha(D / 'voice/pause-review.json'), 'scope': pause_review['scope']},
              'shots': len({row['shot'] for row in sents}),
              'frames': build['summary']['frames'], 'seconds': build['summary']['seconds'],
              'sampleRate': SR, 'samples': len(samples) // 2,
              'sharedBuilderReplay': {'status': 'passed', 'voiceSHA256': replay_sha,
                  'builderSHA256': sha(ROOT / 'episodes/_shared/voice/build.py'),
                  'algorithmCopied': False, 'noNewTTS': True},
              'measurements': {'integratedLUFS': level, 'truePeakDBTP': peak,
                  'samplePeak': float(np.max(np.abs(signal.astype(np.int32)))) / 32768,
                  'maxNeighbourLUFSDifference': build['summary']['max_neighbour_lufs_diff'],
                  'maxJoinSampleJump': build['summary']['max_join_sample_jump'],
                  'innerDropouts': build['summary']['inner_dropouts'],
                  'innerDropoutsFieldMeaning': 'Shared legacy field for >=.50s low-level intervals, not speech-recognition evidence of missing words. These flagged source intervals were preserved and reviewed numerically.',
                  'silentTailSeconds': len(tail) / SR},
              'rows': rows, 'ASRPerformed': False, 'semanticListeningPerformed': False,
              'fullHumanListeningPerformed': False,
              'limitations': 'Waveform/source checks do not prove exact spoken wording, pronunciation or full-film listening. Source-level low-energy flags are retained, not erased or declared semantically correct.'}
    (D / 'qa-voice.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['status', 'frames', 'seconds', 'voiceSHA256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
