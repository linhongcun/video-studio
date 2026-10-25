"""Render only the added methods section and reuse the original encoded pictures.

The original MP4 is decoded/re-encoded at the exact frame boundary, not copied
as a compressed stream. Narration comes from the verified PCM insertion; the
shared mixer then lays one continuous music track across the whole result.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
OUT = D / 'remotion/out'
OUT.mkdir(parents=True, exist_ok=True)


def run(args, **kwargs):
    subprocess.run([str(a) for a in args], check=True, **kwargs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


run([sys.executable, D / 'freeze.py', '--verify'])
sb = json.loads((D / 'storyboard.json').read_text())
baseline = json.loads((D / 'revisions/methods-before/baseline.json').read_text())
added = [shot for scene in sb['scenes'] for shot in scene['shots'] if shot['id'] in ['16', '17']]
assert [s['id'] for s in added] == ['16', '17']
start = baseline['insertFrame']
count = sum(s['durationInFrames'] for s in added)
total = sb['meta']['durationInFrames']
assert added[0]['from'] == start and total == baseline['totalFrames'] + count
old = D / 'revisions/methods-before/video.mp4'
assert sha(old) == baseline['files']['video.mp4']
clip = OUT / 'methods-insert.mp4'
render = ['npx', 'remotion', 'render', 'src/index.ts', 'Main', str(clip),
          f'--frames={start}-{start + count - 1}', '--muted', '--codec=h264',
          '--crf=18', '--concurrency=2', '--browser-executable=/usr/bin/chromium',
          '--bundle-cache=false']
run(render, cwd=D / 'remotion')
streams = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(clip)]))['streams']
v = next(s for s in streams if s['codec_type'] == 'video')
assert (v['width'], v['height'], v['r_frame_rate'], int(v['nb_frames'])) == (1920, 1080, '30/1', count)
filters = (
    f'[0:v]trim=end_frame={start},settb=1/30,setpts=PTS-STARTPTS[a];'
    f'[1:v]trim=end_frame={count},settb=1/30,setpts=PTS-STARTPTS[b];'
    f"[2:v]trim=start_frame={start}:end_frame={baseline['totalFrames']},settb=1/30,setpts=PTS-STARTPTS[c];"
    '[a][b][c]concat=n=3:v=1:a=0,fps=30[v]'
)
voice_video = OUT / 'voice.mp4'
splice = ['ffmpeg', '-y', '-v', 'warning', '-threads', '2', '-i', old,
          '-threads', '2', '-i', clip, '-threads', '2', '-i', old,
          '-i', D / 'voice.wav', '-filter_complex_threads', '1', '-filter_complex', filters,
          '-map', '[v]', '-map', '3:a:0', '-c:v', 'libx264', '-preset', 'veryfast',
          '-crf', '20', '-pix_fmt', 'yuv420p', '-threads', '2', '-r', '30',
          '-video_track_timescale', '90000', '-frames:v', str(total),
          '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', str(total / 30), voice_video]
run(splice)
run([sys.executable, ROOT / 'episodes/_shared/music/mix_bgm.py',
     '--in', voice_video, '--bgm', ROOT / 'episodes/_shared/music/Wallpaper.mp3',
     '--mode', 'constant', '--below', '12', '--out', D / 'video.mp4',
     '--report', D / 'mix-report.json'])
run([sys.executable, D / 'freeze.py', '--verify'])
report = dict(insertFrame=start, addedFrames=count, originalFrames=baseline['totalFrames'],
              finalFrames=total, originalVideoSha256=sha(old),
              insertedVideoSha256=sha(clip), finalVideoSha256=sha(D / 'video.mp4'),
              renderCommand=render, spliceCommand=[str(a) for a in splice],
              scope='Only two new shots rendered. Original pictures decoded/re-encoded; not lossless stream copy. Original narration PCM preserved before final continuous music mix.')
(D / 'methods-splice-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
