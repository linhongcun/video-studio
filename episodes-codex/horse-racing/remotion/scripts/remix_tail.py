"""Frame-exact approved-prefix reuse plus a separately rendered new ending.

This only composes video and muxes the already checked shared voice.wav. It does
not generate, trim or place TTS. By default the prefix is extracted from the
published Git tag, so the command is reproducible outside the original machine.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import wave


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def video(path):
    data = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams',
        '-of', 'json', str(path)]))
    return data['streams'][0]


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--episode', type=Path, default=Path(__file__).resolve().parents[2])
ap.add_argument('--old-video', type=Path, help='Optional existing copy of the published v0.55.0 video')
ap.add_argument('--tag', default='v0.55.0')
ap.add_argument('--tail', type=Path)
ap.add_argument('--out', type=Path)
ap.add_argument('--run', action='store_true', help='Encode after writing the input/range plan')
args = ap.parse_args()
D = args.episode.resolve()
repo = D.parents[1]
outdir = D/'remotion/out'
outdir.mkdir(parents=True, exist_ok=True)
old_video = args.old_video.resolve() if args.old_video else outdir/'ending-baseline-v0.55.0.mp4'
if not old_video.exists():
    assert args.old_video is None, 'Requested old-video does not exist'
    with old_video.open('wb') as output:
        subprocess.run(['git', 'show', f'{args.tag}:episodes/horse-racing/video.mp4'],
                       cwd=repo, stdout=output, check=True)
tail = (args.tail or outdir/'self-contained-ending.mp4').resolve()
output = (args.out or outdir/'voice-revised-ending.mp4').resolve()
voice = D/'voice.wav'
baseline = D/'revisions/self-contained-ending/before/storyboard.json'
current = D/'storyboard.json'
old, new = load(baseline), load(current)
old_shots = [sh for sc in old['scenes'] for sh in sc['shots']]
new_shots = [sh for sc in new['scenes'] for sh in sc['shots']]
for a, b in zip(old_shots[:17], new_shots[:17]):
    for field in ('id', 'from', 'durationInFrames', 'visualType', 'narration', 'subtitles', 'voice', 'cueFrames'):
        assert a[field] == b[field], f'Prefix field changed: {a["id"]}/{field}'
prefix = sum(sh['durationInFrames'] for sh in old_shots[:17])
total = new['meta']['durationInFrames']
assert prefix == new_shots[17]['from'] == 5875
assert old['meta']['fps'] == new['meta']['fps'] == 30
assert output not in (old_video, tail, voice), 'Never overwrite a remix input'
expected_old = load(D/'revisions/self-contained-ending/before-media-sha256.json')['video.mp4']
assert sha(old_video) == expected_old, 'Old video is not the published baseline'
before, ending = video(old_video), video(tail)
assert int(before['nb_frames']) == old['meta']['durationInFrames']
assert int(ending['nb_frames']) == total-prefix
assert before['r_frame_rate'] == ending['r_frame_rate'] == '30/1'
assert (before['width'], before['height']) == (ending['width'], ending['height']) == (1920, 1080)
assert before['pix_fmt'] == ending['pix_fmt'], 'Color format mismatch requires explicit handling'
with wave.open(str(voice)) as wav:
    assert (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) == (48000, 1, 2)
    assert wav.getnframes() == total*1600
pix = before['pix_fmt']
graph = (f'[0:v]trim=end_frame={prefix},setpts=N/(30*TB),setsar=1,format={pix}[prefix];'
         f'[1:v]trim=end_frame={total-prefix},setpts=N/(30*TB),setsar=1,format={pix}[ending];'
         '[prefix][ending]concat=n=2:v=1:a=0,setpts=N/(30*TB)[video]')
command = ['ffmpeg', '-y', '-v', 'error', '-i', str(old_video), '-i', str(tail), '-i', str(voice),
           '-filter_complex_threads', '1', '-filter_complex', graph,
           '-map', '[video]', '-map', '2:a:0', '-frames:v', str(total), '-r', '30',
           '-fps_mode', 'cfr', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
           '-threads', '2', '-pix_fmt', pix, '-video_track_timescale', '90000',
           '-c:a', 'aac', '-b:a', '192k', '-t', f'{total/30:.10f}',
           '-movflags', '+faststart']
if before.get('color_range') in ('pc', 'tv'):
    command += ['-color_range', before['color_range']]
if before.get('color_space') not in (None, 'unknown'):
    command += ['-colorspace', before['color_space']]
command += [str(output)]
inputs = [old_video, tail, voice, baseline, current, Path(__file__).resolve()]
manifest = {'method': 'Display-frame trim of approved prefix + new-tail concat; fast video re-encode and mux of checked full new voice.wav.',
            'baselineTag': args.tag, 'inputs': {str(p): sha(p) for p in inputs},
            'prefixFrames': prefix, 'tailFrames': total-prefix, 'totalFrames': total,
            'command': command, 'output': str(output),
            'limitations': 'Prefix visual sources, timing, captions and PCM remain unchanged. Re-encoding introduces measured codec differences; this is not lossless packet reuse. Old/tail audio are discarded.'}
plan_path = outdir/'ending-remix-plan.json'
plan_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(f'Plan: old prefix={prefix}, new ending={total-prefix}, total={total} frames')
if args.run:
    subprocess.run(['python3', str(D/'freeze.py'), '--verify'], check=True)
    subprocess.run(command, check=True)
    subprocess.run(['python3', str(D/'freeze.py'), '--verify'], check=True)
    actual = video(output)
    assert int(actual['nb_frames']) == total and actual['r_frame_rate'] == '30/1'
    display = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'frame=best_effort_timestamp_time', '-of', 'json', str(output)]))['frames']
    assert len(display) == total
    assert all(abs(float(frame['best_effort_timestamp_time'])-i/30) < 2e-6
               for i, frame in enumerate(display)), 'Non-continuous display timestamps'
    assert all(sha(Path(p)) == value for p, value in manifest['inputs'].items())
    (outdir/'ending-remix-result.json').write_text(json.dumps({
        'status': 'passed', 'frames': total, 'prefixFrames': prefix,
        'lastPTS': (total-1)/30, 'output': str(output), 'sha256': sha(output),
        'planSHA256': sha(plan_path)}, ensure_ascii=False, indent=2)+'\n')
    print(f'Frame-exact ending remix passed: {sha(output)}')
