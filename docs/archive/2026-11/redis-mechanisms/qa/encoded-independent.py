#!/usr/bin/env python3
"""Retain exact integer-frame PNGs while independently decoding complete final media."""
from pathlib import Path
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('production', type=Path)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--spec', type=Path)
    a = ap.parse_args()
    render_lock = open('/tmp/video-studio-render.lock', 'a')
    fcntl.flock(render_lock, fcntl.LOCK_EX)
    d, out = a.production.resolve(), a.out_dir.resolve()
    assert out.is_relative_to(HERE) and out != HERE and not out.exists(), 'Preserve raw attempts; choose a fresh QA child'
    out.mkdir(parents=True)
    report = {'kind': 'independent-actual-final-media-review', 'production': str(d),
              'reviewerScriptSHA256': sha(__file__), 'createdAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'machinePass': False, 'visualReviewed': False, 'inputSHA256': {}, 'samples': [],
              'scope': 'Technical decode/identity checks and exact sampled PNGs. Actual image/continuous motion review is separate. No ASR/full semantic listening or learner-outcome claim.'}

    def save():
        (out / 'encoded-media-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    save()
    try:
        sys.path.insert(0, str(ROOT / 'episodes/_shared'))
        from episode_paths import episode_slug, production_directory
        assert d.is_relative_to(production_directory(episode_slug(d), root=ROOT))
        names = ['source-sha256.json', 'voice.wav', 'storyboard.json', 'remotion/src/Main.tsx',
                 'references.json', 'reference-appendix.json', 'render-result.json', 'video.mp4']
        if (d / 'article-figure-plan.json').is_file():
            names.append('article-figure-plan.json')
        report['inputSHA256'] = {str(d / name): sha(d / name) for name in names}
        if a.spec:
            report['inputSHA256'][str(a.spec.resolve())] = sha(a.spec)
        pipeline_file = ROOT / 'episodes/_shared/render_with_references.py'
        report['inputSHA256'][str(pipeline_file)] = sha(pipeline_file)
        spec = importlib.util.spec_from_file_location('readonly_current_reference_pipeline', pipeline_file)
        pipeline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pipeline)
        pipeline.verify_freeze(d)
        report['actualFrozenInputsVerified'] = len(read(d / 'source-sha256.json'))
        board, receipt, render, refs = [read(d / name) for name in
            ['storyboard.json', 'reference-appendix.json', 'render-result.json', 'references.json']]
        shots = [shot for scene in board['scenes'] for shot in scene['shots']]
        body, total = receipt['bodyFrames'], receipt['finalVideoFrames']
        assert body == board['meta']['durationInFrames'] == sum(shot['durationInFrames'] for shot in shots)
        assert total == render['frames'] and sha(d / 'video.mp4') == receipt['outputSHA256'] == render['sha256']
        bibliography = [{'id': source['id'], 'title': source['title'],
                         'credit': source.get('author') or source['organization']} for source in refs['sources']]
        assert receipt['bibliography'] == bibliography
        assert total == body + 150 * math.ceil(len(bibliography) / 4)
        report.update(bodyFrames=body, finalFrames=total, bibliography=bibliography)
        frames = {}

        def add(frame, label):
            assert type(frame) is int and 0 <= frame < total, 'Exact valid integer n required'
            frames.setdefault(frame, []).append(label)

        for shot in shots:
            add(shot['from'], f"shot{shot['id']} first")
            add(shot['from'] + shot['durationInFrames'] // 2, f"shot{shot['id']} midpoint")
            add(shot['from'] + shot['durationInFrames'] - 1, f"shot{shot['id']} final")
        for frame in [0, body - 1, body, total - 1]:
            add(frame, 'body/reference boundary')
        for page in range(math.ceil(len(bibliography) / 4)):
            for local in [0, 75, 149]:
                add(body + page * 150 + local, f'reference page{page + 1} first/mid/last')
        if (d / 'article-figure-plan.json').is_file():
            for figure in read(d / 'article-figure-plan.json')['figures']:
                assert abs(figure['seconds'] - figure['frame'] / 30) < 1e-9
                label = figure.get('caption') or figure.get('state') or figure.get('modelState') or figure['file']
                add(figure['frame'], 'article: ' + label)
        if a.spec:
            for sample in read(a.spec)['samples']:
                add(sample['frame'], sample.get('label', ','.join(sample.get('reasons', []))))
        probe_command = ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(d / 'video.mp4')]
        probe = json.loads(subprocess.check_output(probe_command))
        video = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        audio = next(stream for stream in probe['streams'] if stream['codec_type'] == 'audio')
        assert (video['width'], video['height'], video['r_frame_rate'], int(video['nb_frames'])) == (1920, 1080, '30/1', total)
        assert audio['codec_name'] == 'aac' and int(audio['sample_rate']) == 48000
        expected = {'codec_name': 'h264', 'pix_fmt': 'yuv420p', 'color_space': 'bt709',
                    'color_range': 'tv', 'color_transfer': 'bt709', 'color_primaries': 'bt709'}
        assert all(video.get(key) == value for key, value in expected.items())
        report.update(format={key: video.get(key) for key in [*expected, 'width', 'height', 'r_frame_rate', 'nb_frames']},
                      audio={key: audio.get(key) for key in ['codec_name', 'sample_rate', 'channels', 'duration']})

        def balanced(parts):
            if len(parts) == 1:
                return parts[0]
            mid = len(parts) // 2
            return '(' + balanced(parts[:mid]) + '+' + balanced(parts[mid:]) + ')'

        selection = balanced([f'eq(n,{frame})' for frame in sorted(frames)])
        raw_dir = out / 'raw'
        raw_dir.mkdir()
        command = ['ffmpeg', '-v', 'error', '-xerror', '-err_detect', 'explode', '-threads', '3',
                   '-filter_threads', '1', '-i', str(d / 'video.mp4'), '-map', '0:v:0',
                   '-vf', f"select='{selection}'", '-fps_mode', 'vfr', str(raw_dir / 'raw-%03d.png'),
                   '-map', '0:a:0', '-f', 'null', '/dev/null']
        result = subprocess.run(command, capture_output=True, text=True)
        (out / 'complete-decode.stderr.txt').write_text(result.stderr)
        report['completeVideoAndAudioDecode'] = {'command': command, 'exit': result.returncode,
                                                'stderr': result.stderr, 'selection': 'Exact decoder integer n, no approximate -ss seek'}
        save()
        assert result.returncode == 0 and not result.stderr
        raw = sorted(raw_dir.glob('raw-*.png'))
        assert len(raw) == len(frames)
        report['samples'] = [{'frame': frame, 'reasons': labels, 'file': str(file), 'sha256': sha(file)}
                             for (frame, labels), file in zip(sorted(frames.items()), raw)]
        loudness_command = ['ffmpeg', '-hide_banner', '-nostats', '-i', str(d / 'video.mp4'),
                            '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']
        measured = subprocess.run(loudness_command, capture_output=True, text=True)
        (out / 'actual-final-aac-ebur128.txt').write_text(measured.stderr)
        assert measured.returncode == 0
        integrated = re.findall(r'I:\s+(-?[0-9.]+) LUFS', measured.stderr)
        peaks = re.findall(r'Peak:\s+(-?[0-9.]+) dBFS', measured.stderr)
        assert integrated and peaks, 'Missing independently measured AAC loudness/true-peak summary'
        loudness, true_peak = float(integrated[-1]), float(peaks[-1])
        report['actualFinalAudioMeasurement'] = {'command': loudness_command, 'integratedLUFS': loudness,
            'truePeakDbTP': true_peak, 'method': 'Fresh complete AAC decode through FFmpeg ebur128 peak=true; summary precision0.1dB'}
        assert abs(loudness + 16) <= .3 and true_peak <= -2.0, 'Actual final AAC misses loudness/true-peak requirement'
        pipeline.verify_freeze(d)
        report['machinePass'] = True
        report['status'] = 'technical-pass-await-independent-image-review'
    except Exception as exc:
        report.update(status='failed-preserved-raw-attempt', failure={'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()})
    finally:
        changed = [file for file, value in report['inputSHA256'].items() if not Path(file).is_file() or sha(file) != value]
        report['sourceInputsUnchanged'] = not changed
        if changed:
            report.update(machinePass=False, changedInputs=changed)
        save()
    print(json.dumps({'machinePass': report['machinePass'], 'samples': len(report['samples']), 'report': str(out / 'encoded-media-review.json')}))
    return 0 if report['machinePass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
