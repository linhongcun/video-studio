# EP.18：从整轨 narration.wav（/workspace/share/ep18，sha bf69aeea…）按 timing.json 每镜首句 src → timeline.json 绝对起点，切出 remotion/public/audio/<shot>.wav
# 镜头本地第 0 帧 = 该镜首句起点；长度 = 首句起点 → 末句止（不重采样、不改响度）
import json, sys, subprocess
NAR = sys.argv[1] if len(sys.argv) > 1 else '/workspace/share/ep18/narration.wav'
TL = sys.argv[2] if len(sys.argv) > 2 else '/workspace/share/ep18/timeline.json'
tl = {s['id']: s for s in json.load(open(TL))['sentences']}
tm = json.load(open('timing.json'))
for shot, t in tm.items():
    ss = t['sentences']; a = tl[ss[0]['src']]['start']; b = tl[ss[-1]['src']]['end']
    for s in ss:  # 校验镜内相对起点一致
        assert abs((tl[s['src']]['start'] - a) - s['start']) < 0.02, (shot, s)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', NAR, '-ss', f'{a:.4f}', '-t', f'{b - a:.4f}', '-c:a', 'pcm_s16le', f'remotion/public/audio/{shot}.wav'], check=True)
    print(shot, f'{a:.3f}-{b:.3f}', f'{(b-a)*30:.1f}f / audioFrames {t["audioFrames"]} / dur {t["duration"]}')
