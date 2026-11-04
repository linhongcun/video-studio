#!/usr/bin/env python3
"""Audit actual P06 selected voice with shared algorithms; writes only new QA files.

No TTS, ASR, production replacement, word timing inference or semantic audition.
The retained scratch rebuild runs the current unmodified shared build script.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import wave

import numpy as np

D = Path(__file__).resolve().parents[1]
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file())
Q = D / 'qa'
sys.path.insert(0, str(ROOT / 'episodes/_shared/voice'))
import common
sys.path.insert(0, str(ROOT / 'episodes/_shared'))
from onset_rule import Rule


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def wav(p):
    with wave.open(str(p)) as source:
        fmt = dict(channels=source.getnchannels(), sampleWidth=source.getsampwidth(),
                   sampleRate=source.getframerate(), sampleCount=source.getnframes())
        pcm = source.readframes(source.getnframes())
    return fmt, pcm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='independent-voice-v1')
    args = parser.parse_args()
    assert re.fullmatch(r'independent-voice-[A-Za-z0-9_-]+', args.name)
    target = Q / (args.name + '.json')
    scratch = Q / (args.name + '-scratch')
    assert not target.exists() and not scratch.exists(), 'Preserve earlier evidence; use a new --name.'
    required = ['script.md', 'words.json', 'storyboard.json', 'voice.wav',
                'remotion/public/audio/voice.wav', 'voice/sents.json', 'voice/params.json',
                'voice/picks.json', 'voice/build.json']
    assert all((D / n).is_file() for n in required), 'Wait for actual finalized assembly and public WAV.'
    report = dict(executor='Codex independent P06 selected-voice signal QA',
                  startedAtUTC=datetime.now(timezone.utc).isoformat(), status='running',
                  checks={}, notPerformed=['TTS generation', 'production mutation', 'ASR',
                                           'interior word alignment', 'full semantic listening',
                                           'phonetic or pronunciation judgement'],
                  limitations=['Exact request text and signal identity do not prove the spoken words or tones.',
                               'Detected tail lengths are shared cut measurements, not phoneme identification.',
                               'Sentence onsets are measured; interior character envelopes are not word timestamps.'])

    def save():
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    save()
    try:
        sents = read(D / 'voice/sents.json')
        picks = read(D / 'voice/picks.json')
        build = read(D / 'voice/build.json')
        words = read(D / 'words.json')
        board = read(D / 'storyboard.json')
        script = (D / 'script.md').read_text()
        sections = re.findall(r'### (\d+) ([\w-]+)\n(.*?)(?=\n### |\Z)', script, re.S)
        original = []
        for n, slug, body in sections:
            text = re.search(r'^旁白：(.*)$', body, re.M)[1]
            parts = re.findall(r'.+?[。？！]', text)
            assert len(parts) == 2, (n, parts)
            for i, part in enumerate(parts, 1):
                original.append(dict(id=f'{int(n):02d}-{slug}-{i}', shot=f'{int(n):02d}-{slug}', text=part))
        assert len(sections) == 15 and len(original) == len(sents) == len(build['sentences']) == 30
        assert [r['id'] for r in original] == [r['id'] for r in sents] == [r['id'] for r in build['sentences']]
        assert len({r['id'] for r in original}) == 30
        names = list(required)
        for expected, submitted, row in zip(original, sents, build['sentences']):
            assert expected['text'] == submitted['text'] == row['text']
            assert expected['shot'] == submitted['shot'] == row['shot']
            assert submitted['tts'] == submitted['text'] + '好。' == row['tts']
            take = picks.get(submitted['id'], 'a')
            assert row['take'] == take
            stem = f"voice/takes/{submitted['id']}-{take}"
            names += [stem + '.wav', stem + '.raw.wav', stem + '.txt.json',
                      f"voice/sentences/{submitted['id']}.wav"]
            assert read(D / (stem + '.txt.json')) == submitted['tts']
        before = {n: sha(D / n) for n in sorted(set(names))}
        shared = [ROOT / 'episodes/_shared/voice/build.py', ROOT / 'episodes/_shared/voice/common.py',
                  ROOT / 'episodes/_shared/onset_rule.py']
        shared_before = {str(p.relative_to(ROOT)): sha(p) for p in shared}
        report['inputSHA256'] = before
        report['sharedToolSHA256'] = shared_before
        report['checks']['scriptAndSubmittedTTS'] = dict(pass_=True, shots=15, sentences=30,
              allExactScriptSentences=True, allSelectedRequestTextExact=True, ttsSuffix='好。', picks=picks)
        selected = []
        for source, row in zip(sents, build['sentences']):
            take = picks.get(source['id'], 'a')
            path = D / f"voice/takes/{source['id']}-{take}.wav"
            x = common.load(str(path))
            assert len(x) > 0 and np.isfinite(x).all()
            clipped, tail = common.cut(x)
            active = np.flatnonzero(np.abs(clipped) > 1e-4)
            assert len(active)
            trimmed = clipped[:active[-1] + 1]
            assert len(trimmed) == row['endSample'] - row['startSample']
            assert round(tail, 2) == row['tailCut']
            assert tail >= .25, f"Selected tail duration requires review: {source['id']} {tail}"
            selected.append(dict(id=source['id'], take=take, sourceSamples48k=len(x),
                  selectedTakeSHA256=sha(path), canonicalCutAppendedTailSeconds=float(tail),
                  postFadeTrimSamples=len(trimmed), buildStartSample=row['startSample'],
                  buildEndSample=row['endSample'], sampleCountExact=True))
        report['checks']['canonicalCutRecalculation'] = dict(pass_=True, sentences=selected,
              definition='common.cut returns time after the selected final >=150ms gap; this is detected appended-tail duration, not narration removed.')
        save()

        vd = scratch / 'voice'
        (vd / 'takes').mkdir(parents=True)
        for name in ['sents.json', 'params.json', 'picks.json']:
            shutil.copyfile(D / 'voice' / name, vd / name)
        for source in sents:
            name = f"{source['id']}-{picks.get(source['id'], 'a')}.wav"
            shutil.copyfile(D / 'voice/takes' / name, vd / 'takes' / name)
        result = subprocess.run([sys.executable, str(ROOT / 'episodes/_shared/voice/build.py'),
                                 '--dir', str(scratch)], capture_output=True)
        (Q / (args.name + '-shared-build.log')).write_bytes(result.stdout + result.stderr)
        assert result.returncode == 0, 'Scratch shared rebuild failed; retained log and scratch have details.'
        assert sha(scratch / 'voice.wav') == sha(D / 'voice.wav')
        rebuilt = read(vd / 'build.json')
        assert rebuilt == build, 'Canonical build JSON differs.'
        rebuilt_sentences = []
        for source in sents:
            rel = f"sentences/{source['id']}.wav"
            assert sha(vd / rel) == sha(D / 'voice' / rel)
            rebuilt_sentences.append(dict(id=source['id'], pcmWavSHA256=sha(vd / rel), byteIdentical=True))
        report['checks']['canonicalRebuild'] = dict(pass_=True,
              command='python3 episodes/_shared/voice/build.py --dir <new QA scratch of exact current parameters, picks and selected takes>',
              sharedAlgorithmCopied=False, voiceSHA256=sha(D / 'voice.wav'), wholeWavByteIdentical=True,
              buildJSONExactlyEqual=True, scratchPath=str(scratch.relative_to(D)), sentences=rebuilt_sentences)

        fmt, pcm = wav(D / 'voice.wav')
        assert fmt['channels'] == 1 and fmt['sampleWidth'] == 2 and fmt['sampleRate'] == 48000
        assert fmt['sampleCount'] == words['durationFrames'] * 1600 == build['summary']['samples']
        assert build['summary']['frames'] == words['durationFrames'] and build['summary']['sha'] == sha(D / 'voice.wav')
        rows = build['sentences']
        assert all(isinstance(r['startSample'], int) and isinstance(r['endSample'], int)
                   and 0 <= r['startSample'] < r['endSample'] <= fmt['sampleCount'] for r in rows)
        assert all(a['endSample'] <= b['startSample'] for a, b in zip(rows, rows[1:]))
        for row in rows:
            part_fmt, part = wav(D / f"voice/sentences/{row['id']}.wav")
            assert part_fmt['channels'] == 1 and part_fmt['sampleWidth'] == 2 and part_fmt['sampleRate'] == 48000
            assert part_fmt['sampleCount'] == row['endSample'] - row['startSample']
            assert part == pcm[row['startSample'] * 2:row['endSample'] * 2]
        samples = np.frombuffer(pcm, '<i2')
        gaps = [(0, rows[0]['startSample'])] + [(a['endSample'], b['startSample']) for a, b in zip(rows, rows[1:])] + [(rows[-1]['endSample'], len(samples))]
        assert all(0 <= a <= b <= len(samples) for a, b in gaps)
        assert all(np.max(np.abs(samples[a:b].astype(np.int32)), initial=0) == 0 for a, b in gaps)
        public = D / 'remotion/public/audio/voice.wav'
        assert public.is_file() and not public.is_symlink() and public.read_bytes() == (D / 'voice.wav').read_bytes()
        assert words['audioSha256'] == sha(D / 'voice.wav') and words['scriptSha256'] == sha(D / 'script.md')
        assert words['asrModel'] == 'none' and words['wordAlignment'] is False
        report['checks']['pcmPlacement'] = dict(pass_=True, format=fmt,
              all30SentencePCMByteSlicesExact=True, publicWavIsEntityAndWholeBytesEqual=True,
              bodyFrames=words['durationFrames'], silentGapPCMZero=True, silentIntervals=len(gaps),
              wordAlignment=False, asrModel='none')

        shots = [s for scene in board['scenes'] for s in scene['shots']]
        assert len(shots) == len(words['shots']) == 15
        assert all(len(s['sentences']) == 2 for s in words['shots'])
        assert [s['id'] for sh in words['shots'] for s in sh['sentences']] == [s['id'] for s in sents]
        assert sum(s['durationInFrames'] for s in shots) == words['durationFrames']
        rule = Rule(samples.astype(float) / 32767, 48000)
        onsets = []
        for shot, ws in zip(shots, words['shots']):
            assert shot['from'] == ws['startFrame'] and shot['durationInFrames'] == ws['durationFrames']
            assert len(shot['voice']) == len(shot['subtitles']) == 2
            for index, sentence in enumerate(ws['sentences']):
                assert sentence['text'] == next(r['text'] for r in original if r['id'] == sentence['id'])
                assert shot['voice'][index]['id'] == sentence['id']
                assert shot['subtitles'][index]['text'] == sentence['text']
                assert abs(shot['from'] + shot['voice'][index]['localStart'] - sentence['startFrame']) < 1e-6
                assert abs(shot['from'] + shot['voice'][index]['localEnd'] - sentence['endFrame']) < 1e-6
                actual = rule.onset(sentence['startFrame'], min(sentence['endFrame'], sentence['startFrame'] + 30))
                assert actual['source'] == 'pause' and abs(actual['onset'] - sentence['onsetFrame']) < 1e-9
                cue = shot['from'] + shot['cueFrames']['sentences'][index]
                assert -6 <= cue - actual['onset'] <= 2
                assert sentence.get('asr') == '' and sentence.get('asrCoverage') is None
                assert all(c.get('timingUnit') == 'sentence envelope' for c in sentence['chars'])
                onsets.append(dict(id=sentence['id'], storedOnsetFrame=sentence['onsetFrame'],
                      recomputedOnsetFrame=actual['onset'], cueAbsoluteFrame=cue,
                      cueMinusOnsetFrames=cue - actual['onset'], source=actual['source'], kind=actual['kind'], equal=True))
        assert len(onsets) == 30
        report['checks']['sentenceOnsetsAndAssembly'] = dict(pass_=True, sharedRuleUsed=True, rows=onsets,
              all30NarrationSubtitlesAndVoiceIntervalsMatch=True,
              scope='Sentence starts and envelope consistency only; no interior word alignment or speech recognition.')
        assert {n: sha(D / n) for n in before} == before
        assert {str(p.relative_to(ROOT)): sha(p) for p in shared} == shared_before
        report.update(productionInputsUnchanged=True, sharedToolsUnchanged=True,
                      checkedAtUTC=datetime.now(timezone.utc).isoformat(), status='passed', passed=True,
                      voiceSHA256=sha(D / 'voice.wav'), bodyFrames=words['durationFrames'])
        save()
        print(json.dumps(dict(passed=True, voiceSHA256=sha(D / 'voice.wav'),
              bodyFrames=words['durationFrames'], sentences=30, report=str(target.relative_to(ROOT)))))
    except Exception as error:
        report.update(status='failed', passed=False, errorType=type(error).__name__, error=str(error),
                      failedAtUTC=datetime.now(timezone.utc).isoformat())
        save()
        raise


if __name__ == '__main__':
    main()
