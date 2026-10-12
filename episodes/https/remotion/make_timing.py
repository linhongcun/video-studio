"""不重新合成，按 public/audio/*.wav 实测时长重算 src/timing.json（与 ../../tts_timing.py 同一公式）：
镜头时长 = 配音帧 + 段停顿（每段 60 帧均摊到各镜头，至少 10 帧）+ ../extra_hold.json 的额外停顿；保留已有的 sentences 等字段。"""
import json, subprocess, os
here = os.path.dirname(os.path.abspath(__file__))
sb = json.load(open(os.path.join(here, '..', 'storyboard.json')))
hp = os.path.join(here, '..', 'extra_hold.json')
HOLD = {k: v for k, v in (json.load(open(hp)) if os.path.exists(hp) else {}).items() if not k.startswith('_')}
tp = os.path.join(here, 'src', 'timing.json'); old = json.load(open(tp)) if os.path.exists(tp) else {}
FPS = 30; PAUSE = 60
out = {}
for s in sb['scenes']:
    n = len(s['shots'])
    for sh in s['shots']:
        i = sh['id']
        sec = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(here, 'public', 'audio', f'{i}.wav')]))
        af = round(sec * FPS); dur = af + max(10, round(PAUSE / n)) + HOLD.get(i, 0)
        out[i] = {**old.get(i, {}), 'audioSec': round(sec, 3), 'audioFrames': af, 'duration': dur, 'origDuration': sh['durationInFrames'], 'scale': round(dur / sh['durationInFrames'], 4)}
        out[i].pop('extraHold', None)
        if i in HOLD: out[i]['extraHold'] = HOLD[i]
json.dump(out, open(tp, 'w'), indent=1, ensure_ascii=False)
tot = sum(v['duration'] for v in out.values())
print('total frames', tot, f'{tot / FPS:.2f}s', 'scale!=1:', {k: v['scale'] for k, v in out.items() if v['scale'] != 1})
