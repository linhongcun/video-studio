#!/usr/bin/env python3
"""Verify frozen production assets and their optional site/build copies.

This checks file identity, measured media metadata and frozen caption/chapter
boundaries. It does not assess teaching quality or claim speech recognition.
Run after each episode's motion review and final encoded-media checks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import wave
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['http-request', 'https', 'dns', 'cookie-session', 'cdn',
         'load-balancing', 'browser-cache', 'server-cache', 'cache-consistency',
         'message-queue', 'rate-limit', 'idempotency', 'circuit-breaker', 'degradation']


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text())


def clean(text):
    return re.sub(r'\s+', '', text)


def stamp(frame, fps):
    ms = round(frame / fps * 1000)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}'


def verify(slug, integrated, built):
    ep = SLUGS.index(slug) + 1
    d = ROOT / 'episodes-codex' / slug
    required = ['script.md', 'article.mdx', 'research.md', 'pronunciation.md',
                'visual-direction.md', 'knoll-props.md', 'storyboard.json',
                'words.json', 'voice.wav', 'source-sha256.json', 'render-result.json',
                'qa-final.md', 'qa-motion.md', 'video.mp4', 'covers.json',
                'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']
    for name in required:
        assert (d / name).is_file() and (d / name).stat().st_size, f'{slug}: missing {name}'
    manifest = read(d / 'source-sha256.json')
    for name, expected in manifest.items():
        p = (d / name).resolve()
        assert p.is_relative_to(ROOT), f'{slug}: input outside repository: {name}'
        assert digest(p) == expected, f'{slug}: frozen input changed: {name}'
    for name in ['script.md', 'article.mdx', 'research.md', 'pronunciation.md',
                 'storyboard.json', 'words.json', 'voice.wav', 'covers.json',
                 'remotion/src/Main.tsx', 'remotion/public/audio/voice.wav']:
        assert name in manifest, f'{slug}: input omitted from freeze: {name}'
    sb, words = read(d / 'storyboard.json'), read(d / 'words.json')
    meta = sb['meta']
    fps, frames = meta['fps'], meta['durationInFrames']
    assert fps == 30 and frames > 0
    assert not meta.get('pendingAudio') and not meta.get('provisionalTiming')
    assert words['durationFrames'] == frames
    assert words['scriptSha256'] == digest(d / 'script.md')
    assert words['audioSha256'] == digest(d / 'voice.wav')
    assert digest(d / 'remotion/public/audio/voice.wav') == words['audioSha256']
    assert not (d / 'remotion/public/audio/voice.wav').is_symlink(), f'{slug}: public audio must be a real file'
    for name in ['voice.wav', 'words.json']:
        assert digest(d / name)[:8] in meta['timingSource'], f'{slug}: timing source {name}'
    with wave.open(str(d / 'voice.wav')) as w:
        assert w.getframerate() == 48000 and w.getnframes() == frames * 1600
    shots = [sh for scene in sb['scenes'] for sh in scene['shots']]
    at, subtitles, chapters = 0, [], []
    for scene in sb['scenes']:
        assert scene['from'] == at, f'{slug}: chapter start {scene["id"]}'
        chapters.append({'id': scene.get('chapterId', scene['id']), 'frame': at})
        for sh in scene['shots']:
            n = sh['durationInFrames']
            assert sh['from'] == at and n > 0, f'{slug}: shot continuity {sh["id"]}'
            rows = sh.get('subtitles', [])
            assert rows and clean(''.join(x['text'] for x in rows)) == clean(sh['narration']), f'{slug}: caption/narration {sh["id"]}'
            last = -1
            for sub in rows:
                a, b = sub['from'], sub['to']
                assert isinstance(a, int) and isinstance(b, int) and last < a <= b < n, f'{slug}: subtitle timing {sh["id"]}'
                last = b
                subtitles.append(f'{stamp(at + a, fps)} --> {stamp(at + b + 1, fps)}\n{sub["text"]}')
            at += n
    assert at == frames, f'{slug}: duration sum'
    render = read(d / 'render-result.json')
    sha = digest(d / 'video.mp4')
    assert render.get('sha256', render.get('videoSha256')) == sha and render['frames'] == frames
    assert sha in (d / 'qa-final.md').read_text(), f'{slug}: final QA must identify the actual encoded file'
    mix = read(d / 'mix-report.json') if (d / 'mix-report.json').exists() else render.get('mix', render.get('mixReport', {}))
    loudness = render.get('finalLUFS', mix.get('final_LUFS'))
    peak = render.get('truePeakDBTP', mix.get('true_peak_dBTP'))
    assert loudness is not None and peak is not None
    assert abs(loudness + 16) <= .3 and peak <= -2
    probe = read_probe(d / 'video.mp4')
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    a = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    assert (v['width'], v['height'], v['r_frame_rate'], int(v['nb_frames'])) == (1920, 1080, '30/1', frames)
    assert v['codec_name'] == 'h264' and a['codec_name'] == 'aac' and int(a['sample_rate']) == 48000
    assert abs(float(probe['format']['duration']) - frames / fps) < .1
    files = {name: digest(d / name) for name in required if name.endswith(('.mp4', '.jpg', '.json'))}
    if integrated:
        site = ROOT / 'episodes' / slug
        sm = read(site / 'meta.json')
        assert sm['ep'] == ep and not sm.get('draft') and not sm.get('legacy')
        assert sm['finalVideoFrames'] == frames and sm['sourcePath'] == f'episodes-codex/{slug}/remotion'
        for name in ['video.mp4', 'storyboard.json', 'words.json', 'script.md',
                     'research.md', 'pronunciation.md', 'covers.json',
                     'cover-16x9.jpg', 'cover-4x3.jpg', 'cover-3x4.jpg']:
            assert digest(d / name) == digest(site / name), f'{slug}: site copy {name}'
        spec = importlib.util.spec_from_file_location('integrate_batch', ROOT / 'episodes-codex/integrate-batch.py')
        integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(integration)
        assert (site / 'article.mdx').read_text() == integration.article_for_site(slug), f'{slug}: article navigation derivative'
        for name in ['chapters.txt', 'timing.json', 'remotion/src/timing.json']:
            assert not (site / name).exists(), f'{slug}: stale override {name}'
        if built:
            out = ROOT / 'site/dist/episodes' / slug
            assert digest(out / sm['video']) == sha
            assert digest(out / sm['poster']) == digest(site / sm['poster'])
            vtt = (out / 'captions.vtt').read_text()
            expected = 'WEBVTT\n\n' + '\n\n'.join(subtitles) + '\n'
            assert vtt == expected, f'{slug}: built VTT differs from frozen boundaries'
            html = (out / 'index.html').read_text()
            assert sm['title'] in html and 'sourcePath' not in html
    return {'ep': ep, 'slug': slug, 'frames': frames, 'seconds': round(frames / fps, 3),
            'sha256': sha, 'frozenInputs': len(manifest), 'shots': len(shots),
            'subtitleCues': len(subtitles), 'chapters': chapters, 'files': files,
            'productionPassed': True, 'sitePassed': integrated, 'buildPassed': built}


def read_probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                              '-show_format', '-of', 'json', str(path)]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slugs', nargs='+', choices=SLUGS, default=SLUGS)
    parser.add_argument('--integrated', action='store_true')
    parser.add_argument('--built', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    assert not args.built or args.integrated, '--built requires --integrated'
    report = [verify(s, args.integrated, args.built) for s in args.slugs]
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    for row in report:
        print(f'EP{row["ep"]:02d} {row["slug"]}: {row["frames"]} frames, {row["frozenInputs"]} frozen inputs, SHA {row["sha256"][:8]} PASS')


if __name__ == '__main__':
    main()
