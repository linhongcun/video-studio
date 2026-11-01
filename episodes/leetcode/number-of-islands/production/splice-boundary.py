"""Render only changed shot06, then assemble verified old pictures with new voice."""
from pathlib import Path
import hashlib, json, subprocess, sys

EP = Path(__file__).resolve().parent
plan = json.loads((EP / 'splice-plan.json').read_text())
subprocess.run([sys.executable, str(EP / 'freeze.py'), '--verify'], check=True)
old = EP / plan['oldVideo']
assert hashlib.sha256(old.read_bytes()).hexdigest() == plan['oldVideoSHA256']
clip = EP / 'remotion/out/boundary-shot06.mp4'
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(clip)]))
v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
assert (v['width'], v['height'], v['r_frame_rate'], int(v['nb_frames'])) == (1920, 1080, '30/1', plan['newShotFrames'])
out = EP / 'remotion/out/voice.mp4'
filters = (
    f"[0:v]trim=end_frame={plan['prefixFrames']},settb=1/30,setpts=PTS-STARTPTS[a];"
    f"[1:v]trim=end_frame={plan['newShotFrames']},settb=1/30,setpts=PTS-STARTPTS[b];"
    f"[2:v]trim=start_frame={plan['oldSuffixFrom']}:end_frame={plan['oldTotalFrames']},settb=1/30,setpts=PTS-STARTPTS[c];"
    '[a][b][c]concat=n=3:v=1:a=0,fps=30[v]'
)
cmd = ['ffmpeg', '-y', '-v', 'warning', '-threads', '2', '-i', str(old),
       '-threads', '2', '-i', str(clip), '-threads', '2', '-i', str(old),
       '-i', str(EP / 'voice.wav'), '-filter_complex_threads', '1', '-filter_complex', filters,
       '-map', '[v]', '-map', '3:a:0', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
       '-pix_fmt', 'yuv420p', '-threads', '2', '-r', '30', '-video_track_timescale', '90000',
       '-frames:v', str(plan['newTotalFrames']), '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
       '-t', str(plan['newTotalFrames'] / 30), str(out)]
subprocess.run(cmd, check=True)
report = {'oldVideoSHA256': plan['oldVideoSHA256'],
          'newShot06SHA256': hashlib.sha256(clip.read_bytes()).hexdigest(),
          'newWholeVoiceSHA256': hashlib.sha256((EP / 'voice.wav').read_bytes()).hexdigest(),
          'outputVoiceVideoSHA256': hashlib.sha256(out.read_bytes()).hexdigest(),
          'plan': plan, 'command': cmd,
          'scope': 'Pictures outside06 reuse old encoded pictures via FFmpeg decoding/re-encoding; new whole narration replaces old audio. Not lossless stream copy.'}
(EP / 'splice-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
subprocess.run([sys.executable, str(EP / 'freeze.py'), '--verify'], check=True)
print(json.dumps({k: report[k] for k in ['newShot06SHA256', 'outputVoiceVideoSHA256']}, indent=2))
