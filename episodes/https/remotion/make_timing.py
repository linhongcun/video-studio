"""按配音实测时长生成 src/timing.json：镜头时长 = 配音帧数 + 段落停顿（每段 2 秒平均分到各镜头），并记录相对原分镜的缩放系数。"""
import json, subprocess, os
here = os.path.dirname(os.path.abspath(__file__))
sb = json.load(open(os.path.join(here, '..', 'storyboard.json')))
FPS = 30; PAUSE = 60; MIN_TAIL = 10
out = {}
for s in sb['scenes']:
    n = len(s['shots'])
    for sh in s['shots']:
        wav = os.path.join(here, 'public', 'audio', f"{sh['id']}.wav")
        sec = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav]))
        af = round(sec * FPS)
        dur = af + max(MIN_TAIL, round(PAUSE / n))
        out[sh['id']] = {'audioSec': round(sec, 3), 'audioFrames': af, 'duration': dur, 'origDuration': sh['durationInFrames'], 'scale': round(dur / sh['durationInFrames'], 4)}
json.dump(out, open(os.path.join(here, 'src', 'timing.json'), 'w'), indent=1)
tot = sum(v['duration'] for v in out.values())
print('total frames', tot, f'{tot / FPS:.2f}s')
