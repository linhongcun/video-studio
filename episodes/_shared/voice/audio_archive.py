#!/usr/bin/env python3
"""Lossless FLAC archival and Remotion audio staging helper for new episodes.

Keeps existing frozen voice scripts byte-identical while enabling new episodes to:
  1. Archive master narration `voice.wav` losslessly as `voice.flac` (~36% size,
     bit-identical 16-bit PCM verified on encode and decode).
  2. Stage `remotion/public/audio/voice.wav` right before rendering (via hardlink
     or lossless FLAC decode) so duplicate WAV copies never need to be committed.

Commands:
  python3 episodes/_shared/voice/audio_archive.py encode EPDIR/voice.wav
  python3 episodes/_shared/voice/audio_archive.py decode EPDIR/voice.flac
  python3 episodes/_shared/voice/audio_archive.py prepare-remotion EPDIR
  python3 episodes/_shared/voice/audio_archive.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def wav_pcm_fingerprint(path: Path) -> dict:
    with wave.open(str(path), 'rb') as wf:
        params = wf.getparams()
        h = hashlib.sha256()
        while True:
            frames = wf.readframes(65536)
            if not frames:
                break
            h.update(frames)
    return {
        'channels': params.nchannels,
        'sampwidth': params.sampwidth,
        'framerate': params.framerate,
        'nframes': params.nframes,
        'pcmSha256': h.hexdigest(),
    }


def ensure_ffmpeg() -> str:
    binary = shutil.which('ffmpeg')
    if not binary:
        raise RuntimeError('ffmpeg is required for lossless FLAC audio archival')
    return binary


def encode_wav_to_flac(wav_path: Path, flac_path: Path | None = None, *, write_meta: bool = True) -> dict:
    wav_path = wav_path.resolve()
    if not wav_path.is_file():
        raise FileNotFoundError(f'Missing source WAV: {wav_path}')
    flac_path = (flac_path or wav_path.with_suffix('.flac')).resolve()
    ffmpeg = ensure_ffmpeg()

    orig_wav_sha = sha256_file(wav_path)
    orig_pcm = wav_pcm_fingerprint(wav_path)
    if orig_pcm['sampwidth'] != 2:
        raise ValueError(f'Expected 16-bit PCM WAV, got sampwidth={orig_pcm["sampwidth"]}')

    flac_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, '-y', '-v', 'error', '-i', str(wav_path), '-c:a', 'flac', '-compression_level', '8', str(flac_path)],
        check=True,
    )

    # Round-trip decode verification to guarantee bit-exact PCM equivalence.
    with tempfile.TemporaryDirectory() as tmp:
        roundtrip = Path(tmp) / 'roundtrip.wav'
        decode_flac_to_wav(flac_path, roundtrip, verify_pcm_sha=orig_pcm['pcmSha256'])

    wav_bytes = wav_path.stat().st_size
    flac_bytes = flac_path.stat().st_size
    meta = {
        'schemaVersion': 1,
        'codec': 'flac',
        'compressionLevel': 8,
        'sourceWavBytes': wav_bytes,
        'sourceWavSha256': orig_wav_sha,
        'flacBytes': flac_bytes,
        'flacSha256': sha256_file(flac_path),
        'ratio': round(flac_bytes / wav_bytes, 4) if wav_bytes else 1.0,
        **orig_pcm,
    }
    if write_meta:
        meta_path = flac_path.with_name(flac_path.name + '.json')
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return meta


def decode_flac_to_wav(flac_path: Path, wav_path: Path | None = None, *, verify_pcm_sha: str | None = None) -> dict:
    flac_path = flac_path.resolve()
    if not flac_path.is_file():
        raise FileNotFoundError(f'Missing source FLAC: {flac_path}')
    wav_path = (wav_path or flac_path.with_suffix('.wav')).resolve()
    ffmpeg = ensure_ffmpeg()

    expected_pcm = verify_pcm_sha
    meta_path = flac_path.with_name(flac_path.name + '.json')
    if expected_pcm is None and meta_path.is_file():
        expected_pcm = json.loads(meta_path.read_text(encoding='utf-8')).get('pcmSha256')

    wav_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, '-y', '-v', 'error', '-i', str(flac_path), '-c:a', 'pcm_s16le', str(wav_path)],
        check=True,
    )
    decoded = wav_pcm_fingerprint(wav_path)
    if expected_pcm and decoded['pcmSha256'] != expected_pcm:
        raise ValueError(f'Decoded PCM SHA mismatch: expected {expected_pcm}, got {decoded["pcmSha256"]}')
    return {'wavPath': str(wav_path), 'wavSha256': sha256_file(wav_path), **decoded}


def link_or_copy(src: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    try:
        os.link(src, dest)
        return 'hardlink'
    except OSError:
        shutil.copy2(src, dest)
        return 'copy'


def prepare_remotion_audio(ep_dir: Path, *, dest_rel: str = 'remotion/public/audio/voice.wav') -> dict:
    """Ensure EPDIR/remotion/public/audio/voice.wav exists as a real file before rendering."""
    ep_dir = ep_dir.resolve()
    dest = ep_dir / dest_rel
    master_wav = ep_dir / 'voice.wav'
    master_flac = ep_dir / 'voice.flac'

    if master_wav.is_file():
        if dest.is_file() and not dest.is_symlink() and dest.stat().st_ino == master_wav.stat().st_ino:
            method = 'already-hardlinked'
        elif dest.is_file() and not dest.is_symlink() and sha256_file(dest) == sha256_file(master_wav):
            method = 'already-synced'
        else:
            method = link_or_copy(master_wav, dest)
        return {'source': str(master_wav), 'dest': str(dest), 'method': method, 'sha256': sha256_file(dest)}

    if master_flac.is_file():
        decoded = decode_flac_to_wav(master_flac, dest)
        return {'source': str(master_flac), 'dest': str(dest), 'method': 'decoded-flac', 'sha256': decoded['wavSha256'], 'pcmSha256': decoded['pcmSha256']}

    if dest.is_file() and not dest.is_symlink():
        return {'source': str(dest), 'dest': str(dest), 'method': 'existing-public-wav', 'sha256': sha256_file(dest)}

    raise FileNotFoundError(f'No master voice.wav or voice.flac found under {ep_dir}')


def selftest() -> int:
    import math
    import struct

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        wav_path = root / 'voice.wav'
        sr = 48000
        samples = [int(12000 * math.sin(2 * math.pi * 440 * i / sr)) for i in range(sr // 2)]
        with wave.open(str(wav_path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(struct.pack('<' + 'h' * len(samples), *samples))

        meta = encode_wav_to_flac(wav_path)
        assert meta['ratio'] < 0.8, f'Expected FLAC compression, got ratio={meta["ratio"]}'

        # Stage from WAV via hardlink
        res_wav = prepare_remotion_audio(root)
        assert (root / 'remotion/public/audio/voice.wav').is_file()
        assert res_wav['method'] in ('hardlink', 'copy')

        # Remove WAV and stage from FLAC via lossless decode
        wav_path.unlink()
        (root / 'remotion/public/audio/voice.wav').unlink()
        res_flac = prepare_remotion_audio(root)
        assert res_flac['method'] == 'decoded-flac'
        assert res_flac['pcmSha256'] == meta['pcmSha256']
        print('audio_archive selftest True')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selftest', action='store_true', help='Run offline round-trip FLAC verification test')
    sub = parser.add_subparsers(dest='command')

    p_enc = sub.add_parser('encode', help='Losslessly encode WAV to FLAC with PCM SHA-256 verification')
    p_enc.add_argument('wav', type=Path)
    p_enc.add_argument('--out', type=Path, default=None)
    p_enc.add_argument('--no-meta', action='store_true')

    p_dec = sub.add_parser('decode', help='Decode FLAC back to 16-bit PCM WAV with SHA-256 verification')
    p_dec.add_argument('flac', type=Path)
    p_dec.add_argument('--out', type=Path, default=None)

    p_prep = sub.add_parser('prepare-remotion', help='Stage EPDIR/remotion/public/audio/voice.wav from voice.wav or voice.flac')
    p_prep.add_argument('ep_dir', type=Path)
    p_prep.add_argument('--dest', default='remotion/public/audio/voice.wav')

    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.command == 'encode':
        print(json.dumps(encode_wav_to_flac(args.wav, args.out, write_meta=not args.no_meta), ensure_ascii=False, indent=2))
        return 0
    if args.command == 'decode':
        print(json.dumps(decode_flac_to_wav(args.flac, args.out), ensure_ascii=False, indent=2))
        return 0
    if args.command == 'prepare-remotion':
        print(json.dumps(prepare_remotion_audio(args.ep_dir, dest_rel=args.dest), ensure_ascii=False, indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
