#!/usr/bin/env python3
"""Append a silent Java design-pattern card to an already checked voiced body.

The original sentence checker remains unchanged and is run against the actual
saved body in a temporary directory. Java is never relabeled as a Python card.
Only explicit duration/hash fields and the Java-card declaration may differ.
This helper does no synthesis, onset detection, trimming or normalization.

  python append_java_endcard.py append EPDIR --frames 150
  python append_java_endcard.py verify EPDIR
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / 'episodes-codex/_shared/check_sentence_episode.py'
PLACE = ROOT / 'episodes/_shared/place_v2.py'
ONSET = ROOT / 'episodes/_shared/label_onset_strict.py'
BODY_DEFAULT = 'revisions/flow-ui-java/voiced-body'
REQUIRED_BODY = (
    'voice.wav', 'words.json', 'storyboard.json', 'script.md', 'plan.json',
    'episode-config.json', 'captions.srt', 'voice/build.json',
    'voice/params.json', 'voice/sents.json', 'voice/picks.json',
    'voice/shot_frames.json',
)
OPTIONAL_BODY = (
    'covers.json', 'voice/cues.json', 'voice/cue_tests.json',
    'voice/place_v2.json', 'qa-timing.json', 'label-onset-strict.txt',
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def read_pcm(path: Path) -> tuple[tuple[int, int, int], bytes]:
    with wave.open(str(path), 'rb') as handle:
        fmt = (handle.getframerate(), handle.getnchannels(), handle.getsampwidth())
        pcm = handle.readframes(handle.getnframes())
    assert fmt == (48000, 1, 2), (path, fmt)
    return fmt, pcm


def write_pcm(path: Path, pcm: bytes) -> None:
    with wave.open(str(path), 'wb') as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(48000)
        handle.writeframes(pcm)


def flat_shots(storyboard: dict) -> list[dict]:
    return [shot for scene in storyboard['scenes'] for shot in scene['shots']]


def run_checked(command: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, (
        'Shared check failed', command[1], result.returncode,
        result.stdout[-6000:], result.stderr[-3000:],
    )
    return result


def body_path(directory: Path, specified: str | None) -> Path:
    path = Path(specified or BODY_DEFAULT)
    return path.resolve() if path.is_absolute() else (directory/path).resolve()


def save_body(directory: Path, body: Path) -> dict:
    assert not body.exists(), ('Body snapshot already exists; never overwrite it', body)
    # This is the genuine pre-card production state, with its real public WAV.
    run_checked([sys.executable, str(CHECKER), str(directory)])
    files = list(REQUIRED_BODY)
    files += [name for name in OPTIONAL_BODY if (directory/name).is_file()]
    for name in files:
        assert (directory/name).is_file(), ('Missing voiced-body input', name)
    sb = read_json(directory/'storyboard.json')
    assert sb['meta']['fps'] == 30
    assert 'javaEndCard' not in sb['meta'] and 'unvoicedEndCard' not in sb['meta']
    for name in files:
        source = directory/name
        target = body/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    manifest = {
        'createdAtUTC': datetime.now(timezone.utc).isoformat(),
        'bodyFrames': sb['meta']['durationInFrames'],
        'fps': 30,
        'format': {'sampleRate': 48000, 'channels': 1, 'sampleWidth': 2},
        'files': {name: sha(body/name) for name in sorted(files)},
        'originalSentenceChecker': {
            'path': 'episodes-codex/_shared/check_sentence_episode.py',
            'sha256': sha(CHECKER),
        },
        'publicAudioReconstruction': 'Byte-copy this saved voice.wav into the temporary body/public path.',
        'scope': 'Immutable genuine voiced-body inputs checked before adding any Java card. No final state is relabeled for the original checker.',
    }
    write_json(body/'body-manifest.json', manifest)
    return manifest


def load_body(body: Path) -> dict:
    manifest = read_json(body/'body-manifest.json')
    for name, expected in manifest['files'].items():
        path = (body/name).resolve()
        assert path.is_relative_to(body), ('Unsafe saved body path', name)
        assert sha(path) == expected, ('Immutable body changed', name)
    assert sha(CHECKER) == manifest['originalSentenceChecker']['sha256'], 'Original checker changed'
    return manifest


def expected_final(body: Path, manifest: dict, frames: int, audio_sha: str):
    body_frames = manifest['bodyFrames']
    total = body_frames + frames
    words = copy.deepcopy(read_json(body/'words.json'))
    words['durationFrames'] = total
    words['audioSha256'] = audio_sha
    words['scriptSha256'] = sha(body/'script.md')
    words['shots'][-1]['endFrame'] += frames
    words['shots'][-1]['durationFrames'] += frames
    # All sentence envelopes and the speech endpoint are deliberately unchanged.
    words_bytes = (json.dumps(words, ensure_ascii=False, indent=2) + '\n').encode()
    words_sha = hashlib.sha256(words_bytes).hexdigest()
    source = f"voice.wav {audio_sha[:8]} + words.json {words_sha[:8]} + script.md {words['scriptSha256'][:8]}"
    sb = copy.deepcopy(read_json(body/'storyboard.json'))
    sb['meta']['durationInFrames'] = total
    sb['meta']['finalVideoFrames'] = total
    sb['meta']['timingSource'] = source
    sb['meta']['javaEndCard'] = {
        'kind': 'java-design-pattern', 'from': body_frames,
        'durationInFrames': frames,
    }
    sb['scenes'][-1]['durationInFrames'] += frames
    shots = flat_shots(sb)
    shots[-1]['durationInFrames'] += frames
    shots[-1]['javaCardFrom'] = body_frames - shots[-1]['from']
    for shot in shots:
        shot['timing']['source'] = source
    shot_frames = copy.deepcopy(read_json(body/'voice/shot_frames.json'))
    shot_frames['durationFrames'] = total
    shot_frames['audioSha256'] = audio_sha
    shot_frames['shots'][-1]['endFrame'] += frames
    shot_frames['shots'][-1]['durationFrames'] += frames
    return words, sb, shot_frames


def verify(directory: Path, body: Path, report_path: Path) -> dict:
    manifest = load_body(body)
    sb = read_json(directory/'storyboard.json')
    card = sb['meta']['javaEndCard']
    assert card['kind'] == 'java-design-pattern'
    assert 'unvoicedEndCard' not in sb['meta'], 'Java cannot impersonate a Python end card'
    frames = card['durationInFrames']
    assert isinstance(frames, int) and not isinstance(frames, bool) and frames > 0
    assert card['from'] == manifest['bodyFrames']
    for name in manifest['files']:
        if name in {
            'voice.wav', 'words.json', 'storyboard.json', 'voice/shot_frames.json',
            'voice/place_v2.json', 'qa-timing.json', 'label-onset-strict.txt',
        }:
            continue
        assert (directory/name).read_bytes() == (body/name).read_bytes(), ('Body input changed after snapshot', name)
    _, body_pcm = read_pcm(body/'voice.wav')
    _, final_pcm = read_pcm(directory/'voice.wav')
    assert len(body_pcm) == manifest['bodyFrames'] * 1600 * 2
    assert len(final_pcm) == (manifest['bodyFrames']+frames) * 1600 * 2
    assert final_pcm[:len(body_pcm)] == body_pcm, 'Voiced PCM prefix changed'
    assert not any(final_pcm[len(body_pcm):]), 'Java-card voice tail is not true digital silence'
    public = directory/'remotion/public/audio/voice.wav'
    assert not public.is_symlink(), 'Public WAV must be a real file'
    assert public.read_bytes() == (directory/'voice.wav').read_bytes()
    expected_words, expected_sb, expected_shot_frames = expected_final(body, manifest, frames, sha(directory/'voice.wav'))
    assert read_json(directory/'words.json') == expected_words, 'Unexpected words/timing/narration change'
    assert sb == expected_sb, 'Unexpected storyboard/caption/voice-row change'
    assert read_json(directory/'voice/shot_frames.json') == expected_shot_frames, 'Unexpected shot-frame derivative'
    assert (directory/'captions.srt').read_bytes() == (body/'captions.srt').read_bytes()
    assert all(shot['from'] + sub['to'] < card['from']
               for shot in flat_shots(sb) for sub in shot['subtitles']), 'Subtitle extends into Java card'
    assert max(voice['wavEnd'] for shot in flat_shots(sb) for voice in shot['voice']) <= card['from']
    # The old checker sees only the unmodified, genuine body snapshot.
    with tempfile.TemporaryDirectory(prefix='java-body-check-') as temporary:
        temp = Path(temporary)
        for name in manifest['files']:
            target = temp/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(body/name, target)
        body_public = temp/'remotion/public/audio/voice.wav'
        body_public.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(temp/'voice.wav', body_public)
        checked = run_checked([sys.executable, str(CHECKER), str(temp)])
        original_report = json.loads(checked.stdout)
        placement = run_checked([
            sys.executable, str(PLACE), '--dir', str(directory), '--mode', 'whole',
            '--no-copy', '--report', str(temp/'final-placement.json'),
        ])
        onset = run_checked([
            sys.executable, str(ONSET), '--dir', str(directory),
            '--out', str(temp/'final-onsets.txt'),
        ])
        placement_report = read_json(temp/'final-placement.json')
        onset_report = (temp/'final-onsets.txt').read_text()
    # Check again after subprocesses; validation must not mutate its saved body.
    assert load_body(body) == manifest
    report = {
        'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
        'scope': 'Real voiced body checked by unchanged original checker; final state checked as a narrow Java-tail derivative. No ASR or listening.',
        'bodyPath': str(body.relative_to(directory)) if body.is_relative_to(directory) else str(body),
        'bodyManifestSHA256': sha(body/'body-manifest.json'),
        'originalCheckerSHA256': sha(CHECKER),
        'originalBodyCheckerReport': original_report,
        'bodyFrames': manifest['bodyFrames'], 'javaCardFrames': frames,
        'finalFrames': manifest['bodyFrames']+frames,
        'cardKind': card['kind'], 'javaCardFrom': card['from'],
        'bodyAudioSHA256': sha(body/'voice.wav'),
        'finalAudioSHA256': sha(directory/'voice.wav'),
        'finalWordsSHA256': sha(directory/'words.json'),
        'finalStoryboardSHA256': sha(directory/'storyboard.json'),
        'prefixSamplesCompared': len(body_pcm)//2, 'prefixPCMExact': True,
        'silentTailSamples': frames*1600, 'silentTailAllZero': True,
        'originalCaptionsAndSentenceTimingsUnchanged': True,
        'onlyDeclaredDurationAndHashFieldsChanged': True,
        'bodyInputsAndManifestUnchanged': True,
        'finalWholePlacement': placement_report,
        'finalStrictOnsetReport': onset_report,
        'passed': True,
    }
    write_json(report_path, report)
    return report


def append(directory: Path, body: Path, frames: int, report_path: Path) -> dict:
    assert frames > 0
    current = read_json(directory/'storyboard.json')
    if 'javaEndCard' in current['meta']:
        assert current['meta']['javaEndCard']['durationInFrames'] == frames
        return verify(directory, body, report_path)  # Idempotent; never append twice.
    manifest = save_body(directory, body)
    _, pcm = read_pcm(body/'voice.wav')
    assert len(pcm) == manifest['bodyFrames']*1600*2
    write_pcm(directory/'voice.wav', pcm + bytes(frames*1600*2))
    words, sb, shot_frames = expected_final(body, manifest, frames, sha(directory/'voice.wav'))
    write_json(directory/'words.json', words)
    write_json(directory/'storyboard.json', sb)
    write_json(directory/'voice/shot_frames.json', shot_frames)
    # The canonical whole-track helper performs the real-file copy and checks
    # exact layout; no placement logic is reimplemented here.
    run_checked([sys.executable, str(PLACE), '--dir', str(directory), '--mode', 'whole'])
    run_checked([sys.executable, str(ONSET), '--dir', str(directory)])
    return verify(directory, body, report_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['append', 'verify'])
    parser.add_argument('directory', type=Path)
    parser.add_argument('--frames', type=int, default=150)
    parser.add_argument('--body-dir', help='Episode-relative or absolute immutable body snapshot path')
    parser.add_argument('--report', type=Path, help='Validation report; default EPDIR/qa-java-endcard.json')
    args = parser.parse_args()
    directory = args.directory.resolve()
    body = body_path(directory, args.body_dir)
    report_path = args.report.resolve() if args.report else directory/'qa-java-endcard.json'
    report = (append(directory, body, args.frames, report_path) if args.action == 'append'
              else verify(directory, body, report_path))
    print(json.dumps({key: report[key] for key in [
        'bodyFrames', 'javaCardFrames', 'finalFrames', 'prefixPCMExact',
        'silentTailAllZero', 'originalCaptionsAndSentenceTimingsUnchanged', 'passed',
    ]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
