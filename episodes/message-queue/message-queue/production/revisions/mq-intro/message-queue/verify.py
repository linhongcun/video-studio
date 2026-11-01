#!/usr/bin/env python3
"""Validate body timing and final appendix ranges without rewriting production receipts."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())


def read(path):
    return json.loads(path.read_text())


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                             '-show_format', '-of', 'json', str(path)]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final', action='store_true')
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / 'episodes-codex/_shared/check_sentence_episode.py'), str(D)], check=True)
    if not args.final:
        return
    subprocess.run([sys.executable, str(D / 'freeze.py'), '--verify'], check=True)
    result = read(D / 'render-result.json')
    receipt = read(D / 'reference-appendix.json')
    body = probe(D / 'remotion/out/body.mp4')
    final = probe(D / 'video.mp4')
    body_video = next(s for s in body['streams'] if s['codec_type'] == 'video')
    final_video = next(s for s in final['streams'] if s['codec_type'] == 'video')
    final_audio = next(s for s in final['streams'] if s['codec_type'] == 'audio')
    frames = read(D / 'words.json')['durationFrames']
    assert int(body_video['nb_frames']) == frames == receipt['bodyFrames']
    assert int(final_video['nb_frames']) == receipt['finalVideoFrames'] == result['frames']
    assert result['publicationMetadata']['referenceAppendix']['from'] == frames
    assert (final_video['width'], final_video['height'], final_video['r_frame_rate']) == (1920, 1080, '30/1')
    assert final_video['codec_name'] == 'h264' and final_audio['codec_name'] == 'aac'
    assert int(final_audio['sample_rate']) == 48000
    digest = hashlib.sha256((D / 'video.mp4').read_bytes()).hexdigest()
    assert digest == receipt['outputSHA256'] == result['sha256']
    mix = read(D / 'remotion/out/mix-report.json')
    assert abs(mix['final_LUFS'] + 16) <= .3 and mix['true_peak_dBTP'] <= -2.0
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(D / 'video.mp4'), '-f', 'null', '-'], check=True)
    report = {'passed': True, 'bodyFrames': frames, 'finalFrames': receipt['finalVideoFrames'],
              'sha256': digest, 'finalLUFS': mix['final_LUFS'], 'truePeakDBTP': mix['true_peak_dBTP'],
              'fullDecode': True, 'note': 'Media and timing checks; source meaning, visual and listening review remain separate.'}
    (D / 'qa-encoded-media.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
