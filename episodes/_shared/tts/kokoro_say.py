"""Kokoro-82M v1.0（sherpa-onnx）逐句合成一段旁白 → wav。
按 。？！ 分句，每句单独合成、去首尾静音，句间留 --gap 秒；--segments 输出每句起点/时长（JSON）。
用法：kokoro_say.py --text "..." --out x.wav [--sid 50] [--speed 1.15] [--gap 0.12] [--segments x.json]"""
import argparse, json, os, re
import numpy as np, soundfile as sf, sherpa_onnx
ap = argparse.ArgumentParser(); ap.add_argument('--text', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--sid', type=int, default=50)  # 50 = zm_yunxi
ap.add_argument('--speed', type=float, default=1.15); ap.add_argument('--gap', type=float, default=0.12); ap.add_argument('--segments')
a = ap.parse_args()
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'kokoro-multi-lang-v1_0') + '/'
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
        model=d + 'model.onnx', voices=d + 'voices.bin', tokens=d + 'tokens.txt', data_dir=d + 'espeak-ng-data', dict_dir=d + 'dict',
        lexicon=d + 'lexicon-us-en.txt,' + d + 'lexicon-zh.txt'), num_threads=4),
    rule_fsts=d + 'phone-zh.fst,' + d + 'date-zh.fst,' + d + 'number-zh.fst'))
sents = [s for s in re.findall(r'[^。？！]+[。？！]?', a.text) if s.strip()]
parts, segs, t, sr = [], [], 0.0, 24000
for s in sents:
    g = tts.generate(s, sid=a.sid, speed=a.speed); sr = g.sample_rate; x = np.asarray(g.samples, dtype=np.float32)
    nz = np.where(np.abs(x) > 0.01)[0]
    if len(nz): x = x[max(0, nz[0] - int(.03 * sr)):nz[-1] + int(.08 * sr)]
    segs.append({'text': s, 'start': round(t, 3), 'dur': round(len(x) / sr, 3)}); t += len(x) / sr + a.gap
    parts += [x, np.zeros(int(a.gap * sr), np.float32)]
sf.write(a.out, np.concatenate(parts[:-1]), sr)
if a.segments: json.dump(segs, open(a.segments, 'w'), ensure_ascii=False, indent=1)
