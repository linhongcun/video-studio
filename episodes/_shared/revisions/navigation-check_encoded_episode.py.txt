"""Check the actual encoded local viewing copy; record measured results."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

assert len(sys.argv) == 2, 'Usage: check_encoded_episode.py EPDIR'
D = Path(sys.argv[1]).resolve()
sb = json.loads((D/'storyboard.json').read_text())
meta = sb['meta']
manifest = json.loads((D/'source-sha256.json').read_text())
for rel, expected in manifest.items():
    assert hashlib.sha256((D/rel).read_bytes()).hexdigest() == expected, rel
probe = json.loads(subprocess.check_output([
    'ffprobe','-v','error','-show_streams','-show_format','-of','json',str(D/'video.mp4')]))
video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
assert (video['width'],video['height']) == (meta['width'],meta['height'])
assert video['r_frame_rate'] == '30/1'
assert int(video['nb_frames']) == meta['durationInFrames']
assert abs(float(probe['format']['duration'])-meta['durationInFrames']/meta['fps']) < .1
assert audio['codec_name'] == 'aac' and int(audio['sample_rate']) == 48000
mix = json.loads((D/'mix-report.json').read_text())
assert abs(mix['final_LUFS']+16) <= .3
assert mix['true_peak_dBTP'] <= -2.0
subprocess.run(['ffmpeg','-v','error','-i',str(D/'video.mp4'),'-f','null','-'],check=True)
digest = hashlib.sha256((D/'video.mp4').read_bytes()).hexdigest()
report = dict(visualRevision=meta.get('visualRevision',1),width=video['width'],height=video['height'],fps=video['r_frame_rate'],
              frames=int(video['nb_frames']),seconds=float(probe['format']['duration']),
              audio=audio['codec_name'],audioSampleRate=int(audio['sample_rate']),
              finalLUFS=mix['final_LUFS'],truePeakDBTP=mix['true_peak_dBTP'],
              bytes=(D/'video.mp4').stat().st_size,sha256=digest,
              checks='Source hashes, format, frames, audio, loudness and full decode passed.')
(D/'render-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
