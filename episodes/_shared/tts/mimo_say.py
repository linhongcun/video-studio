"""Xiaomi MiMo TTS（mimo-v2.5-tts，预置音色 冰糖）逐句合成一段旁白 → wav。
按 。？！ 分句，每句单独请求、去首尾静音，句间留 --gap 秒；--segments 输出每句起点/时长（JSON）。
密钥从环境变量 MIMO_API_KEY 读取，或从 --env 文件（默认 /workspace/video-studio/.mimo.env（工作区根目录，已被 .gitignore 忽略））读取；不写入仓库。
用法：mimo_say.py --text "..." --out x.wav [--voice 冰糖] [--gap 0.28] [--segments x.json]"""
import argparse, base64, io, json, os, re, time, urllib.request
import numpy as np, soundfile as sf
STYLE = '轻松自然的科普博主语气，语速适中偏快，吐字清晰。'
ap = argparse.ArgumentParser(); ap.add_argument('--text', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--voice', default='冰糖'); ap.add_argument('--style', default=STYLE); ap.add_argument('--gap', type=float, default=0.28)
ap.add_argument('--segments'); ap.add_argument('--env', default='/workspace/video-studio/.mimo.env')
a = ap.parse_args()
key = os.environ.get('MIMO_API_KEY')
if not key and os.path.exists(a.env):
    for l in open(a.env):
        if l.strip().startswith('MIMO_API_KEY='): key = l.split('=', 1)[1].strip().strip('"\'')
assert key, 'MIMO_API_KEY missing'
def synth(s):
    body = json.dumps({'model': 'mimo-v2.5-tts', 'messages': [{'role': 'user', 'content': a.style}, {'role': 'assistant', 'content': s}],
                       'audio': {'format': 'wav', 'voice': a.voice}}).encode()
    for i in range(5):
        try:
            req = urllib.request.Request('https://api.xiaomimimo.com/v1/chat/completions', body, {'api-key': key, 'Content-Type': 'application/json'})
            d = json.load(urllib.request.urlopen(req, timeout=120))
            x, sr = sf.read(io.BytesIO(base64.b64decode(d['choices'][0]['message']['audio']['data'])), dtype='float32')
            if x.ndim > 1: x = x.mean(1)
            if len(x) / sr >= len(s) / 14: return x, sr
            print('short audio, retry', s)
        except Exception as e: print('retry', i, type(e).__name__, getattr(e, 'code', ''))
        time.sleep(2 + 3 * i)
    raise SystemExit('MiMo TTS failed: ' + s)
sents = [s for s in re.findall(r'[^。？！]+[。？！]?', a.text) if s.strip()]
parts, segs, t, sr = [], [], 0.0, 24000
for s in sents:
    x, sr = synth(s); nz = np.where(np.abs(x) > 0.01)[0]
    if len(nz): x = x[max(0, nz[0] - int(.03 * sr)):nz[-1] + int(.12 * sr)]
    segs.append({'text': s, 'start': round(t, 3), 'dur': round(len(x) / sr, 3)}); t += len(x) / sr + a.gap
    parts += [x, np.zeros(int(a.gap * sr), np.float32)]
sf.write(a.out, np.concatenate(parts[:-1]), sr)
if a.segments: json.dump(segs, open(a.segments, 'w'), ensure_ascii=False, indent=1)
