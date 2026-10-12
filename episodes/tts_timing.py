"""配音 + 时间轴：edge-tts 逐镜头生成 → 去尾部静音 → ffprobe 实测 → 写 remotion/src/timing.json。
用法：python3 episodes/tts_timing.py <episode_dir> --rate=+44% --pause=<每段停顿帧> [--skip=sceneId,...]
镜头时长 = 配音帧 + 段停顿均摊（≥10 帧）；scale = 新时长/分镜原时长，Main.tsx 按 scale 等比压缩动画与字幕相对帧（动画同步变快，不只是砍停留）。
--skip 的段落沿用已有音频与 timing（标记 pending），用于等待新分镜。"""
import json, subprocess, re, os, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('ep'); ap.add_argument('--rate', default='+44%'); ap.add_argument('--pause', type=int, default=60)
ap.add_argument('--skip', default=''); ap.add_argument('--voice', default='zh-CN-YunxiNeural'); a = ap.parse_args()
ep = os.path.abspath(a.ep); sb = json.load(open(f'{ep}/storyboard.json')); FPS = sb['meta'].get('fps', 30)
tpath = f'{ep}/remotion/src/timing.json'; old = json.load(open(tpath)) if os.path.exists(tpath) else {}
skip = set(filter(None, a.skip.split(','))); out = {}; tmp = '/tmp/tts_' + os.path.basename(ep); os.makedirs(tmp, exist_ok=True)
probe = lambda f: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
for s in sb['scenes']:
    n = len(s['shots'])
    for sh in s['shots']:
        i = sh['id']; wav = f'{ep}/remotion/public/audio/{i}.wav'
        if s.get('chapterId', s['id']) in skip or s['id'] in skip:
            out[i] = {**old[i], 'pending': True}; continue
        mp3 = f'{tmp}/{i}.mp3'
        for attempt in range(3):
            r = subprocess.run(['python3', '-m', 'edge_tts', '-v', a.voice, f'--rate={a.rate}', '-t', sh['narration'], '--write-media', mp3], capture_output=True, text=True)
            if r.returncode == 0: break
        else: sys.exit(f'TTS ERROR {i}: {r.stderr[-800:]}')
        log = subprocess.run(['ffmpeg', '-hide_banner', '-i', mp3, '-af', 'silencedetect=n=-40dB:d=0.2', '-f', 'null', '-'], capture_output=True, text=True).stderr
        st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', log)]; full = probe(mp3)
        end = (st[-1] if st and st[-1] > full - 1.2 else full) + 0.15
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mp3, '-t', f'{end:.3f}', '-ar', '48000', wav], check=True)
        sec = probe(wav); af = round(sec * FPS); dur = af + max(10, round(a.pause / n))
        out[i] = {'audioSec': round(sec, 3), 'audioFrames': af, 'duration': dur, 'origDuration': sh['durationInFrames'],
                  'scale': round(dur / sh['durationInFrames'], 4), 'rate': a.rate, 'oldAudioSec': old.get(i, {}).get('audioSec')}
json.dump(out, open(tpath, 'w'), indent=1, ensure_ascii=False)
tot = sum(v['duration'] for v in out.values()); print('total', tot, f'{tot / FPS:.2f}s')
