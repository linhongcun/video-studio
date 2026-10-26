#!/usr/bin/env python3
"""Read-only EP39 body/final sound QA after default render has completed.

No TTS, assembly, source re-freeze, mixing or render is performed. The canonical
body checker runs unchanged in a temporary symlink view so its render-result
output cannot overwrite the real reference-appended publication metadata.
Waveform/known-music analysis reuses a pinned retained checker without changing
its numerical algorithms or criteria. New results are QA outputs only.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import wave

import numpy as np

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[1]
MANIFEST = D / 'source-sha256.json'
MANIFEST_SHA256 = 'f7f978e13b703c7cc57e9182615e1448f8dc8c9269424c0394ff4ae81a0ff7f9'
BODY_CHECKER = ROOT / 'episodes-codex/_shared/check_encoded_episode.py'
BODY_CHECKER_SHA256 = '183b01c300269dc2b5ad82ff7893552916405882556a6daf2f87c4dcd9d2db7a'
NUMERICAL_CHECKER = ROOT / 'episodes-codex/egg-drop/verify_encoded_voice.py'
NUMERICAL_CHECKER_SHA256 = '0ca5ba05a0a0e7c8bbad4abd512a0b83d1667e69b6061af94822591841e1eac5'
REPORT = D / 'qa-encoded-voice-content.json'
BODY = D / 'remotion/out/body.mp4'
FINAL = D / 'video.mp4'
PREMIX = D / 'remotion/out/voice.mp4'
SR = 48000
BODY_FRAMES = 5741
FINAL_FRAMES = 5891


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def frozen_snapshot():
    assert sha(MANIFEST) == MANIFEST_SHA256, 'The authorized150-input manifest changed'
    expected = json.loads(MANIFEST.read_text())
    assert len(expected) == 150
    actual = {relative: sha(D / relative) for relative in expected}
    assert actual == expected, 'A frozen production input changed'
    return actual


def body_gate(manifest):
    assert sha(BODY_CHECKER) == BODY_CHECKER_SHA256
    with tempfile.TemporaryDirectory(prefix='bloom-body-gate-') as temp:
        stage_root = Path(temp) / 'repo'
        stage = stage_root / 'episodes-codex/bloom-filter'
        stage.mkdir(parents=True)
        for relative in manifest:
            target = stage / relative
            assert target.resolve().is_relative_to(stage_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to((D / relative).resolve())
        for name, source in [('source-sha256.json', MANIFEST),
                             ('video.mp4', BODY),
                             ('mix-report.json', D / 'remotion/out/mix-report.json')]:
            target = stage / name
            assert not target.exists(), f'Unexpected staged output/input collision: {name}'
            target.symlink_to(source.resolve())
        run = subprocess.run([sys.executable, str(BODY_CHECKER), str(stage)],
                             check=True, capture_output=True, text=True)
        result = json.loads((stage / 'render-result.json').read_text())
        assert result['frames'] == BODY_FRAMES and result['sha256'] == sha(BODY)
        result.update(scope='Actual body only; canonical checker unchanged in isolated symlink view.',
            actualBody='remotion/out/body.mp4', canonicalChecker=str(BODY_CHECKER.relative_to(ROOT)),
            canonicalCheckerSHA256=BODY_CHECKER_SHA256, frozenInputsChecked=len(manifest),
            sourceManifestSHA256=MANIFEST_SHA256, realPublicationMetadataRewritten=False,
            stageInputs='The same actual frozen files; body mapped to temporary video.mp4. No media or source produced.')
        save(D / 'qa-encoded-body-gate.json', result)
        (D / 'qa-encoded-body-gate.log').write_text(run.stdout + run.stderr)
        return result


def audio_pcm_digest(path):
    command = ['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-vn',
               '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    h = hashlib.sha256()
    count = 0
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        while block := process.stdout.read(1024 * 1024):
            h.update(block)
            count += len(block)
        error = process.stderr.read()
        code = process.wait()
        assert code == 0, error.decode(errors='replace')
    assert count % 8 == 0
    return {'sha256': h.hexdigest(), 'decodedStereoSamples': count // 8,
            'bytes': count, 'command': command}


def loudness(path):
    command = ['ffmpeg', '-hide_banner', '-i', str(path), '-vn',
               '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-']
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    measured = json.loads(re.findall(r'\{\s*"input_i".*?\}', result.stderr, re.S)[-1])
    return {'integratedLUFS': float(measured['input_i']),
            'truePeakDBTP': float(measured['input_tp']), 'command': command}


def longest_low_level(signal):
    frame_size = 480
    bins = np.abs(signal[:len(signal) // frame_size * frame_size]).reshape(-1, frame_size).max(1) > .005
    longest = run = 0
    for active in bins:
        run = 0 if active else run + 1
        longest = max(longest, run)
    return longest / 100


def main():
    report = {'status': 'in-progress', 'passed': False,
              'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
              'executor': '/root/engineering_next_pipeline',
              'scope': 'Actual body/final AAC, real selected-source voice WAV, premix, and known constant BGM. Numerical provenance and signal checks only.',
              'sourceCommit': '606dd8990cd69c31df1aeba2da9ec660eb468f61',
              'productionManifestSHA256': MANIFEST_SHA256,
              'qaEntry': str(Path(__file__).resolve().relative_to(ROOT)),
              'qaEntrySHA256': sha(Path(__file__).resolve()),
              'ASRPerformed': False, 'semanticListeningPerformed': False,
              'fullHumanListeningPerformed': False,
              'limitations': ['AAC is lossy; actual offsets, coverage, padding and correlations are reported.',
                  'Source/waveform consistency does not identify spoken words or numerical pronunciation.',
                  'Known-BGM regression is not blind voice isolation or whole-film listening.',
                  'Reference append packet/PTS preservation is separately checked by final-media QA.']}
    save(REPORT, report)
    try:
        before = frozen_snapshot()
        for path in [BODY, FINAL, PREMIX, D / 'render-result.json', D / 'remotion/out/mix-report.json']:
            assert path.is_file(), f'Actual completed media required: {path}'
        rendered = json.loads((D / 'render-result.json').read_text())
        assert rendered['frames'] == FINAL_FRAMES and rendered['bodyFrames'] == BODY_FRAMES
        assert rendered['sha256'] == sha(FINAL)
        source = json.loads((D / 'qa-voice.json').read_text())
        takes = json.loads((D / 'qa-voice-takes.json').read_text())
        provenance = json.loads((D / 'voice/input-provenance.json').read_text())
        assert source['status'] == takes['status'] == 'passed'
        assert provenance['finalVoiceAuditSHA256'] == sha(D / 'qa-voice.json')
        assert provenance['finalSelectedAuditSHA256'] == sha(D / 'qa-voice-takes.json')
        assert source['voiceSHA256'] == provenance['audioSHA256'] == sha(D / 'voice.wav')
        assert source['frames'] == BODY_FRAMES and source['sentences'] == takes['sentences'] == 26
        assert not takes['failures'] and not takes['warnings']
        publication_before = sha(D / 'render-result.json')
        report['bodyGate'] = body_gate(before)
        assert sha(D / 'render-result.json') == publication_before
        assert sha(NUMERICAL_CHECKER) == NUMERICAL_CHECKER_SHA256
        spec = importlib.util.spec_from_file_location('bloom_pinned_encoded_audio', NUMERICAL_CHECKER)
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        checker.EPISODE, checker.ROOT = D, ROOT
        numerical_path = D / 'qa-encoded-voice-content.numerical.json'
        checker.main(numerical_path)
        numerical = json.loads(numerical_path.read_text())
        numerical['executor'] = '/root/engineering_next_pipeline'
        numerical['invocationEntry'] = str(Path(__file__).resolve().relative_to(ROOT))
        numerical['reusedImplementation'] = {'path': str(NUMERICAL_CHECKER.relative_to(ROOT)),
            'sha256': NUMERICAL_CHECKER_SHA256, 'episodeGlobalRedirected': True,
            'numericAlgorithmsAndCriteriaUnchanged': True}
        save(numerical_path, numerical)
        assert numerical['passed'] is True
        assert numerical['unmixedComparison']['sentenceCount'] == 26
        assert numerical['mixedVersusPremix']['sentenceCount'] == 26
        body_pcm, final_pcm = audio_pcm_digest(BODY), audio_pcm_digest(FINAL)
        assert body_pcm['sha256'] == final_pcm['sha256']
        assert body_pcm['decodedStereoSamples'] == final_pcm['decodedStereoSamples']
        body_level, final_level = loudness(BODY), loudness(FINAL)
        for label, level in [('body', body_level), ('final', final_level)]:
            assert abs(level['integratedLUFS'] + 16) <= .3, (label, level)
            assert level['truePeakDBTP'] <= -2.0, (label, level)
        with wave.open(str(D / 'voice.wav')) as wav:
            reference = np.frombuffer(wav.readframes(wav.getnframes()), '<i2').astype(np.float32) / 32768
        premix, _ = checker.decode(PREMIX)
        build = json.loads((D / 'voice/build.json').read_text())
        quiet_rows = []
        for sentence in build['sentences']:
            a, b = sentence['startSample'], sentence['endSample']
            source_gap = longest_low_level(reference[a:b])
            decoded_gap = longest_low_level(premix[a:b])
            assert decoded_gap < .5, (sentence['id'], 'Encoded premix low-level gap', decoded_gap)
            quiet_rows.append({'id': sentence['id'], 'sourceMaximumLowLevelSeconds': source_gap,
                               'premixMaximumLowLevelSeconds': decoded_gap})
        after = frozen_snapshot()
        assert before == after
        assert sha(D / 'render-result.json') == publication_before
        report.update(status='passed', passed=True, bodySHA256=sha(BODY), finalSHA256=sha(FINAL),
            bodyFrames=BODY_FRAMES, finalFrames=FINAL_FRAMES, sentences=26,
            numericalReport={'path': numerical_path.name, 'sha256': sha(numerical_path),
                             'result': numerical},
            sourceProvenance={'voiceSHA256': source['voiceSHA256'],
                'sourceReportSHA256': sha(D / 'qa-voice.json'),
                'selectedTakesReportSHA256': sha(D / 'qa-voice-takes.json'),
                'selectedRawConversionAndSharedCutPassed': True,
                'assembledSharedBuilderReplayPassed': source['sharedBuilderReplay']['status'] == 'passed',
                'sourceMeasurements': source['measurements']},
            bodyFinalDecodedAudio={'equal': True, 'body': body_pcm, 'final': final_pcm},
            actualLoudness={'body': body_level, 'final': final_level},
            encodedPremixQuietWindows=quiet_rows,
            frozenInputsChecked=len(before), frozenInputsUnchanged=True,
            productionPublicationMetadataUnchanged=True)
        save(REPORT, report)
        print(json.dumps({'status': report['status'], 'sentences': 26,
                          'bodyFrames': BODY_FRAMES, 'finalFrames': FINAL_FRAMES,
                          'bodyFinalPCMEqual': True, 'loudness': final_level}, ensure_ascii=False))
    except BaseException as error:
        report.update(status='failed', passed=False, error=repr(error))
        save(REPORT, report)
        raise


if __name__ == '__main__':
    main()
