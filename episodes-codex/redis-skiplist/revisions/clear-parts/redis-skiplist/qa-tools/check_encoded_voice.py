#!/usr/bin/env python3
"""Read-only encoded sound QA for the Redis skiplist episode.

Run only after final freeze/default render, with the exact authorized manifest
and final MP4 SHA-256 passed explicitly. This imports the retained numerical
checker unchanged, redirects only its episode/repository globals, and writes
only new-episode QA reports. It neither recognizes speech nor listens.
"""
from __future__ import annotations

import argparse
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
from zoneinfo import ZoneInfo

import numpy as np

D = Path(__file__).resolve().parents[1]
ROOT = next(p for p in D.parents if (p / '.git').exists() and (p / 'AGENTS.md').is_file())
MANIFEST = D / 'source-sha256.json'
BODY_CHECKER = ROOT / 'episodes-codex/_shared/check_encoded_episode.py'
BODY_CHECKER_SHA256 = '183b01c300269dc2b5ad82ff7893552916405882556a6daf2f87c4dcd9d2db7a'
NUMERICAL_CHECKER = ROOT / 'episodes-codex/egg-drop/verify_encoded_voice.py'
NUMERICAL_CHECKER_SHA256 = '0ca5ba05a0a0e7c8bbad4abd512a0b83d1667e69b6061af94822591841e1eac5'
REPORT = D / 'qa-encoded-voice-content.json'
BODY = D / 'remotion/out/body.mp4'
FINAL = D / 'video.mp4'
PREMIX = D / 'remotion/out/voice.mp4'
SR = 48000


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, obj):
    assert path.resolve().is_relative_to(D), 'QA outputs must stay in this revision'
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def full_digest(value):
    if not re.fullmatch(r'[0-9a-f]{64}', value):
        raise argparse.ArgumentTypeError('Use the complete lowercase 64-digit SHA-256')
    return value


def frozen_snapshot(expected_manifest_sha):
    assert sha(MANIFEST) == expected_manifest_sha, 'Authorized new manifest SHA mismatch'
    expected = read(MANIFEST)
    assert isinstance(expected, dict) and expected
    required_local = ['storyboard.json', 'words.json', 'episode-config.json', 'voice.wav',
        'voice/build.json', 'voice/sents.json', 'voice/input-provenance.json']
    assert all(relative in expected for relative in required_local), 'Required source/timing input is not frozen'
    actual = {}
    for relative, digest in expected.items():
        path = (D / relative).resolve()
        assert path.is_relative_to(ROOT), ('Frozen input outside repository', relative)
        assert path.is_file(), ('Frozen input missing', relative)
        actual[relative] = sha(path)
        assert actual[relative] == digest, ('Frozen input changed', relative)
    return actual


def expected_shape():
    sb = read(D / 'storyboard.json')
    words = read(D / 'words.json')
    config = read(D / 'episode-config.json')
    build = read(D / 'voice/build.json')
    shots = [sh for sc in sb['scenes'] for sh in sc['shots']]
    assert config['slug'] == 'redis-skiplist' and sb['meta']['episode'] == 40
    assert sb['meta']['fps'] == 30
    assert (sb['meta']['width'], sb['meta']['height']) == (1920, 1080)
    assert not sb['meta'].get('pendingAudio') and not sb['meta'].get('provisionalTiming')
    body_frames = sb['meta']['durationInFrames']
    assert isinstance(body_frames, int) and body_frames > 0
    assert body_frames == words['durationFrames'] == sum(sh['durationInFrames'] for sh in shots)
    assert len(shots) == config['shotCount'] == len(words['shots'])
    sentences = len(build['sentences'])
    assert sentences == 2 * config['shotCount'] == len(read(D / 'voice/sents.json'))
    assert words['audioSha256'] == sha(D / 'voice.wav')
    return body_frames, sentences, len(shots)


def body_gate(manifest, manifest_sha, body_frames):
    assert sha(BODY_CHECKER) == BODY_CHECKER_SHA256
    with tempfile.TemporaryDirectory(prefix='skiplist-body-gate-') as temp:
        stage_root = Path(temp) / 'repo'
        # Keep the complete episode location, so every ../ manifest path
        # resolves within the same disposable repository-shaped view.
        stage = stage_root / D.relative_to(ROOT)
        stage.mkdir(parents=True)
        for relative in manifest:
            target = stage / relative
            assert target.resolve().is_relative_to(stage_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            assert not target.exists(), ('Duplicate staged destination', relative)
            target.symlink_to((D / relative).resolve())
        for name, source in [('source-sha256.json', MANIFEST), ('video.mp4', BODY),
                             ('mix-report.json', D / 'remotion/out/mix-report.json')]:
            target = stage / name
            assert not target.exists(), ('Unexpected staged output collision', name)
            target.symlink_to(source.resolve())
        run = subprocess.run([sys.executable, str(BODY_CHECKER), str(stage)],
                             check=True, capture_output=True, text=True)
        result = read(stage / 'render-result.json')
        assert result['frames'] == body_frames and result['sha256'] == sha(BODY)
        result.update(scope='Actual body only; unchanged canonical checker in a disposable repository-shaped symlink view.',
            actualBody='remotion/out/body.mp4', canonicalChecker=str(BODY_CHECKER.relative_to(ROOT)),
            canonicalCheckerSHA256=BODY_CHECKER_SHA256, frozenInputsChecked=len(manifest),
            sourceManifestSHA256=manifest_sha, realPublicationMetadataRewritten=False,
            stageInputs='Same frozen files; body mapped to temporary video.mp4. No source/media generated.')
        save(D / 'qa-encoded-body-gate.json', result)
        (D / 'qa-encoded-body-gate.log').write_text(run.stdout + run.stderr)
        return result


def audio_pcm_digest(path):
    command = ['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-vn',
               '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    h = hashlib.sha256()
    count = 0
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        while block := process.stdout.read(1024 * 1024):
            h.update(block)
            count += len(block)
        error = process.stderr.read()
        assert process.wait() == 0, error.decode(errors='replace')
    assert count % 8 == 0
    return {'sha256': h.hexdigest(), 'decodedStereoSamples': count // 8,
            'bytes': count, 'command': command}


def audio_packets(path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_packets',
               '-show_data_hash', 'sha256', '-show_entries',
               'packet=pts_time,dts_time,duration_time,size,data_hash', '-of', 'json', str(path)]
    rows = json.loads(subprocess.check_output(command))['packets']
    assert rows and all('data_hash' in row for row in rows)
    return rows


def loudness(path):
    command = ['ffmpeg', '-nostdin', '-hide_banner', '-i', str(path), '-vn',
               '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-']
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    measured = json.loads(re.findall(r'\{\s*"input_i".*?\}', result.stderr, re.S)[-1])
    return {'integratedLUFS': float(measured['input_i']),
            'truePeakDBTP': float(measured['input_tp']), 'command': command}


def longest_low_level(signal):
    frame_size = 480
    assert len(signal) >= frame_size
    bins = np.abs(signal[:len(signal) // frame_size * frame_size]).reshape(-1, frame_size).max(1) > .005
    longest = run = 0
    for active in bins:
        run = 0 if active else run + 1
        longest = max(longest, run)
    return longest / 100


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-media-sha256', required=True, type=full_digest)
    parser.add_argument('--expected-manifest-sha256', required=True, type=full_digest)
    args = parser.parse_args()
    # No reports or checks are claimed until the exact final artifact is present.
    before = frozen_snapshot(args.expected_manifest_sha256)
    assert sha(FINAL) == args.expected_media_sha256, 'Authorized actual MP4 SHA mismatch'
    body_frames, sentence_count, shot_count = expected_shape()
    rendered = read(D / 'render-result.json')
    appendix = read(D / 'reference-appendix.json')
    receipt = read(D / 'reference-appendix-media-check.json')
    final_frames = rendered['frames']
    assert rendered['sha256'] == appendix['outputSHA256'] == receipt['outputSHA256'] == args.expected_media_sha256
    assert rendered['bodyFrames'] == appendix['bodyFrames'] == receipt['bodyFrames'] == body_frames
    assert final_frames == appendix['finalVideoFrames'] == receipt['finalFrames']
    assert final_frames > body_frames and receipt['appendedFrames'] == final_frames - body_frames
    assert receipt['passed'] is True
    assert appendix['presentation'] == read(D / 'references.json')['presentation'] == 'title-author'
    assert appendix['layout']['quotesRendered'] is False and appendix['layout']['maxItemsPerPage'] == 4
    for path in [BODY, PREMIX, D / 'remotion/out/mix-report.json']:
        assert path.is_file(), ('Actual completed media required', str(path))
    assert sha(BODY) == appendix['inputs']['bodySHA256']
    publication_before = {name: sha(D / name) for name in ['render-result.json',
        'reference-appendix.json', 'reference-appendix-media-check.json']}
    media_before = {str(path.relative_to(D)): sha(path) for path in [BODY, FINAL, PREMIX]}
    report = {'status': 'in-progress', 'passed': False,
        'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
        'checkedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'executor': '/root/skip_media_qa',
        'scope': 'Actual final/body AAC, selected-source voice WAV, premix and known constant BGM; numerical provenance/signal checks only.',
        'productionManifestSHA256': args.expected_manifest_sha256,
        'authorizedFinalSHA256': args.expected_media_sha256,
        'qaEntry': str(Path(__file__).resolve().relative_to(ROOT)), 'qaEntrySHA256': sha(Path(__file__)),
        'ASRPerformed': False, 'semanticListeningPerformed': False, 'fullHumanListeningPerformed': False,
        'limitations': ['AAC is lossy; measured offsets, coverage, padding and correlations are reported.',
            'Source/waveform consistency cannot determine spoken words or pronunciation.',
            'Known-BGM regression is not blind voice isolation or whole-film listening.',
            'Actual visual review and browser/native VTT behavior are separate checks.']}
    save(REPORT, report)
    try:
        source = read(D / 'qa-voice.json')
        takes = read(D / 'qa-voice-takes.json')
        provenance = read(D / 'voice/input-provenance.json')
        assert source['status'] == 'passed'
        assert takes['status'] in ['passed', 'needs-review']
        assert provenance['voiceQAReportSHA256'] == sha(D / 'qa-voice.json')
        assert source['sourceAuditSHA256'] == sha(D / 'qa-voice-takes.json')
        assert source['scriptSHA256'] == provenance['scriptSHA256']
        # Preserve the actual approved TTS script identity. A later nonspoken
        # reference/prolog update may change the full file SHA; independently
        # require every current narration sentence to equal the frozen requests.
        narration_lines = re.findall(r'^旁白：(.*)$', (D / 'script.md').read_text(), re.M)
        current_narration = [sentence.strip() for line in narration_lines
                             for sentence in re.findall(r'[^。？！]+[。？！]?', line) if sentence.strip()]
        request_narration = [row['text'] for row in read(D / 'voice/sents.json')]
        assert current_narration == request_narration and len(current_narration) == sentence_count
        report['scriptBinding'] = {'approvedTtsScriptSHA256': source['scriptSHA256'],
            'currentDeliveryScriptSHA256': sha(D / 'script.md'),
            'currentNarrationSentencesEqualFrozenRequests': True,
            'sentenceCount': len(current_narration),
            'scope': 'Exact text equality, not ASR or spoken-word listening.'}
        assert source['voiceSHA256'] == provenance['currentVoiceSHA256'] == sha(D / 'voice.wav')
        assert source['frames'] == body_frames
        assert source['sentences'] == takes['sentences'] == provenance['sentences'] == sentence_count
        assert source['shots'] == provenance['shots'] == shot_count
        assert not takes['failures']
        # Preserve explicitly reviewed source-pause flags. This is narrow source
        # provenance handling; the retained encoded correlation/delay/drift/gain
        # criteria below are unchanged and all remain mandatory.
        warnings = takes.get('warnings', [])
        pause_review = None
        pause_ids = set()
        if warnings:
            pause_path = D / source['sourcePauseReview']['path']
            assert pause_path.resolve().is_relative_to(D)
            pause_sha = sha(pause_path)
            assert pause_sha == source['sourcePauseReview']['sha256'] == provenance['pauseReviewSHA256']
            pause_review = read(pause_path)
            assert pause_review['sourceAuditSHA256'] == sha(D / 'qa-voice-takes.json')
            assert warnings == source['retainedSourceSignalFlags']
            assert pause_review['status'] == 'source-intervals-verified-awaiting-track-replay'
            assert source['sharedBuilderReplay']['status'] == 'passed'
            assert source['sharedBuilderReplay']['voiceSHA256'] == sha(D / 'voice.wav')
            pause_ids = set(pause_review['sourceFlagIds'])
            assert set(warnings) == {f'{key}: low-level interval at least .50s' for key in pause_ids}
            assert {row['id'] for row in pause_review['rows']} == pause_ids
            for row in pause_review['rows']:
                assert row['trimmedInteriorEqualsOriginalTake'] is True and row['flagIntervalEqualsOriginalTake'] is True
                assert sha(D / 'voice/takes' / f"{row['id']}-{row['take']}.wav") == row['takeSHA256']
            assert set(source['measurements']['innerDropouts']).issubset(pause_ids)
        else:
            assert takes['status'] == 'passed'
        report['retainedSourceSignalFlags'] = {
            'sourceTakeScreeningStatus': takes['status'], 'warnings': warnings,
            'sourceTrackFlags': source['measurements'].get('innerDropouts', []),
            'review': None if pause_review is None else {
                'path': str(pause_path.relative_to(D)), 'sha256': pause_sha,
                'status': pause_review['status'], 'scope': pause_review['scope'],
                'trackReplayStatus': source['sharedBuilderReplay']['status'],
                'reviewedSourceFlagIds': sorted(pause_ids)},
            'note': 'Source pause screening flags remain recorded; no spoken-word or naturalness judgment is claimed.'}

        report['bodyGate'] = body_gate(before, args.expected_manifest_sha256, body_frames)
        assert sha(NUMERICAL_CHECKER) == NUMERICAL_CHECKER_SHA256
        spec = importlib.util.spec_from_file_location('skiplist_pinned_encoded_audio', NUMERICAL_CHECKER)
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        checker.EPISODE, checker.ROOT = D, ROOT
        numerical_path = D / 'qa-encoded-voice-content.numerical.json'
        checker.main(numerical_path)
        numerical = read(numerical_path)
        numerical['executor'] = '/root/skip_media_qa'
        numerical['invocationEntry'] = str(Path(__file__).resolve().relative_to(ROOT))
        numerical['reusedImplementation'] = {'path': str(NUMERICAL_CHECKER.relative_to(ROOT)),
            'sha256': NUMERICAL_CHECKER_SHA256, 'episodeGlobalRedirected': True,
            'numericAlgorithmsAndCriteriaUnchanged': True}
        save(numerical_path, numerical)
        assert numerical['passed'] is True
        assert numerical['mixedSHA256'] == args.expected_media_sha256
        assert numerical['unmixedComparison']['sentenceCount'] == sentence_count
        assert numerical['mixedVersusPremix']['sentenceCount'] == sentence_count
        body_packets, final_packets = audio_packets(BODY), audio_packets(FINAL)
        assert body_packets == final_packets, 'Actual AAC packet payload or PTS/DTS/duration changed'
        body_pcm, final_pcm = audio_pcm_digest(BODY), audio_pcm_digest(FINAL)
        assert body_pcm['sha256'] == final_pcm['sha256']
        assert body_pcm['decodedStereoSamples'] == final_pcm['decodedStereoSamples']
        body_level, final_level = loudness(BODY), loudness(FINAL)
        for label, level in [('body', body_level), ('final', final_level)]:
            assert abs(level['integratedLUFS'] + 16) <= .3, (label, level)
            assert level['truePeakDBTP'] <= -2.0, (label, level)
        with wave.open(str(D / 'voice.wav')) as wav:
            assert (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) == (SR, 1, 2)
            reference = np.frombuffer(wav.readframes(wav.getnframes()), '<i2').astype(np.float32) / 32768
        premix, _ = checker.decode(PREMIX)
        quiet_rows = []
        for sentence in read(D / 'voice/build.json')['sentences']:
            a, b = sentence['startSample'], sentence['endSample']
            source_gap = longest_low_level(reference[a:b])
            decoded_gap = longest_low_level(premix[a:b])
            reviewed_pause = sentence['id'] in pause_ids
            if reviewed_pause:
                # Source pause already approved as source-preserved, rather than
                # an encoded interruption. Measurements use 10ms bins; allow at
                # most two bin boundaries while all correlation/drift checks
                # above still apply to every sample range.
                assert decoded_gap <= source_gap + .0200001, (sentence['id'], 'Encoded pause exceeds reviewed source', source_gap, decoded_gap)
            else:
                assert decoded_gap < .5, (sentence['id'], 'New encoded premix low-level gap', decoded_gap)
            quiet_rows.append({'id': sentence['id'], 'sourceMaximumLowLevelSeconds': source_gap,
                'premixMaximumLowLevelSeconds': decoded_gap, 'reviewedSourceFlag': reviewed_pause,
                'maximumEncodedExtraLowLevelSeconds': .02 if reviewed_pause else None,
                'lowLevelBinSeconds': .01})
        assert before == frozen_snapshot(args.expected_manifest_sha256)
        assert publication_before == {name: sha(D / name) for name in publication_before}
        assert media_before == {relative: sha(D / relative) for relative in media_before}
        assert sha(FINAL) == args.expected_media_sha256
        report.update(status='passed', passed=True, bodySHA256=sha(BODY), finalSHA256=sha(FINAL),
            bodyFrames=body_frames, finalFrames=final_frames, sentences=sentence_count, shots=shot_count,
            numericalReport={'path': numerical_path.name, 'sha256': sha(numerical_path), 'result': numerical},
            sourceProvenance={'voiceSHA256': source['voiceSHA256'],
                'sourceReportSHA256': sha(D / 'qa-voice.json'),
                'selectedTakesReportSHA256': sha(D / 'qa-voice-takes.json'),
                'inputProvenanceSHA256': sha(D / 'voice/input-provenance.json'),
                'selectedRawConversionAndSharedCutPassed': True,
                'assembledSharedBuilderReplayPassed': source['sharedBuilderReplay']['status'] == 'passed',
                'sourceMeasurements': source['measurements']},
            bodyFinalAAC={'equal': True, 'packetCount': len(final_packets),
                'packetRowsSHA256': hashlib.sha256(json.dumps(final_packets, sort_keys=True).encode()).hexdigest(),
                'fieldsCompared': ['pts_time', 'dts_time', 'duration_time', 'size', 'data_hash']},
            bodyFinalDecodedAudio={'equal': True, 'body': body_pcm, 'final': final_pcm},
            actualLoudness={'body': body_level, 'final': final_level}, encodedPremixQuietWindows=quiet_rows,
            frozenInputsChecked=len(before), frozenInputsUnchanged=True, mediaUnchanged=True,
            productionPublicationMetadataUnchanged=True)
        save(REPORT, report)
        print(json.dumps({'status': report['status'], 'sentences': sentence_count,
            'bodyFrames': body_frames, 'finalFrames': final_frames,
            'bodyFinalPCMEqual': True, 'bodyFinalAACEqual': True, 'loudness': final_level}, ensure_ascii=False))
    except BaseException as error:
        report.update(status='failed', passed=False, error=repr(error))
        save(REPORT, report)
        raise


if __name__ == '__main__':
    main()
