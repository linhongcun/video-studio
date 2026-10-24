"""Render only a revised opener, then reuse the approved body with frame-exact cuts.

This does not build or place narration. Its audio input is the shared voice build.
Plan first, freeze the inputs, then repeat the command with --run.
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


def shots(sb):
    return [sh for scene in sb['scenes'] for sh in scene['shots']]


def probe(path):
    data = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))
    return next(s for s in data['streams'] if s['codec_type'] == 'video')


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('episode', type=Path)
ap.add_argument('--baseline', type=Path, help='Directory containing the old storyboard.json/video.mp4')
ap.add_argument('--intro', type=Path, help='Rendered revised first two shots, starting at frame zero')
ap.add_argument('--out', type=Path, help='Video with new voice, before shared BGM mixing')
ap.add_argument('--plan', type=Path, help='Deterministic input/range/command manifest')
ap.add_argument('--run', action='store_true', help='Actually encode; otherwise only write the plan')
a = ap.parse_args()
D = a.episode.resolve()
B = (a.baseline or D/'remotion/out/problem-first-baseline').resolve()
intro = (a.intro or D/'remotion/out/problem-first-intro.mp4').resolve()
output = (a.out or D/'remotion/out/voice-remix.mp4').resolve()
plan_path = (a.plan or D/'opener-remix-plan.json').resolve()
old_sb_path, new_sb_path = B/'storyboard.json', D/'storyboard.json'
old_movie, voice = B/'video.mp4', D/'voice.wav'
assert output not in [old_movie, intro, voice], 'Never overwrite an input'
old, new = load(old_sb_path), load(new_sb_path)
old_shots, new_shots = shots(old), shots(new)
assert len(old_shots) == len(new_shots) >= 3, 'This revision replaces exactly the first two shots'
assert old['meta']['fps'] == new['meta']['fps'] == 30
assert (old['meta']['width'], old['meta']['height']) == (new['meta']['width'], new['meta']['height'])
old_card, new_card = old['meta']['unvoicedEndCard'], new['meta']['unvoicedEndCard']
assert old_card['kind'] == new_card['kind'] == 'full-python-solution'
assert old_card['durationInFrames'] == new_card['durationInFrames'] == 150
for field in ['codeSourceSha256', 'displaySourceSha256']:
    assert old_card[field] == new_card[field], 'Changed code card needs a fresh render'
prefix = new_shots[2]['from']
assert prefix == sum(sh['durationInFrames'] for sh in new_shots[:2])
total = new['meta']['durationInFrames']
assert new_card['from'] + 150 == total
with wave.open(str(voice)) as audio:
    assert (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) == (48000, 1, 2)
    assert audio.getnframes() == total * 1600
v = probe(intro)
assert int(v['nb_frames']) == prefix, ('Wrong intro frame count', v['nb_frames'], prefix)
assert v['r_frame_rate'] == '30/1'
assert (v['width'], v['height']) == (new['meta']['width'], new['meta']['height'])
v = probe(old_movie)
assert int(v['nb_frames']) == old['meta']['durationInFrames']
assert v['r_frame_rate'] == '30/1'

segments = []
for old_sh, new_sh in zip(old_shots[2:], new_shots[2:]):
    assert old_sh['id'] == new_sh['id'] and old_sh['visualType'] == new_sh['visualType']
    assert old_sh['narration'] == new_sh['narration'], 'Changed body narration requires explicit review'
    old_len = old_sh.get('codeCardFrom', old_sh['durationInFrames'])
    new_len = new_sh.get('codeCardFrom', new_sh['durationInFrames'])
    delta = new_len - old_len
    assert abs(delta) <= 1, (old_sh['id'], 'Body changed by more than one frame; render it', delta)
    if delta < 0:
        speech_end = max(v['localEnd'] for v in old_sh['voice'])
        assert speech_end < new_len - 1, 'Do not remove a frame containing narration'
    segments.append(dict(shot=old_sh['id'], sourceFrom=old_sh['from'],
                         sourceFrames=old_len, targetFrom=new_sh['from'], targetFrames=new_len,
                         tailFrameAdjustment=delta))
assert prefix + sum(s['targetFrames'] for s in segments) == new_card['from']
segments.append(dict(shot='full-python-card', sourceFrom=old_card['from'], sourceFrames=150,
                     targetFrom=new_card['from'], targetFrames=150, tailFrameAdjustment=0))

# Every old branch only emits its own interval; concat sees exact frame counts.
count = len(segments)
labels = ''.join(f'[old{i}]' for i in range(count))
graph = [f'[0:v]split={count}{labels}',
         f'[1:v]trim=end_frame={prefix},setpts=N/(30*TB),setsar=1[intro]']
for i, s in enumerate(segments):
    start, length, wanted = s['sourceFrom'], s['sourceFrames'], s['targetFrames']
    graph.append(f'[old{i}]trim=start_frame={start}:end_frame={start+length},'
                 f'setpts=N/(30*TB),tpad=stop_mode=clone:stop=1,'
                 f'trim=end_frame={wanted},setpts=N/(30*TB),setsar=1[s{i}]')
graph.append('[intro]' + ''.join(f'[s{i}]' for i in range(count)) +
             f'concat=n={count+1}:v=1:a=0,setpts=N/(30*TB)[video]')
command = ['ffmpeg', '-y', '-v', 'error', '-i', str(old_movie), '-i', str(intro), '-i', str(voice),
           '-filter_complex_threads', '1', '-filter_complex', ';'.join(graph),
           '-map', '[video]', '-map', '2:a:0', '-frames:v', str(total), '-r', '30',
           '-fps_mode', 'cfr', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
           '-threads', '2', '-pix_fmt', 'yuv420p', '-video_track_timescale', '30000',
           '-c:a', 'aac', '-b:a', '192k', '-t', f'{total/30:.10f}',
           '-movflags', '+faststart', str(output)]
inputs = [old_sb_path, old_movie, new_sb_path, intro, voice, Path(__file__).resolve()]
manifest = dict(method='New first-two-shot render + approved body frame ranges; no audio-generation logic.',
                inputs={str(p): sha(p) for p in inputs}, introFrames=prefix, fps=30,
                frames=total, segments=segments, command=command,
                limitations='Body may gain/drop at most one final hold frame per shot; verify actual handoffs and samples. No ASR/listening claim.')
plan_path.parent.mkdir(parents=True, exist_ok=True)
plan_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(f'Plan: {plan_path}; intro={prefix}, body/card={total-prefix}, total={total}')
if a.run:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True)
    actual = probe(output)
    assert int(actual['nb_frames']) == total and actual['r_frame_rate'] == '30/1'
    frames = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'frame=best_effort_timestamp_time', '-of', 'json', str(output)]))['frames']
    assert len(frames) == total
    assert all(abs(float(f['best_effort_timestamp_time'])-i/30) < 2e-6 for i, f in enumerate(frames))
    assert all(sha(Path(p)) == h for p, h in manifest['inputs'].items()), 'Input changed during encoding'
    result = dict(status='passed', frames=total, lastPTS=(total-1)/30,
                  output=str(output), sha256=sha(output), planSha256=sha(plan_path),
                  checks='Encoded frame count, continuous display PTS, and frozen remix input hashes passed.')
    (D/'opener-remix-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))
