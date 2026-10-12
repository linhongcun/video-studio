#!/usr/bin/env python3
"""给 Remotion 渲染出的成片（人声+音效）混入曲库 BGM，并做闪避与响度归一。

用法：python3 mix_bgm.py --in voice.mp4 --bgm track.mp3 --out video.mp4 [--offset 0] [--below 20] [--lift 6] [--lufs -16]
- BGM 电平按“人声说话时的 RMS”定标：说话时 BGM 比人声低 --below dB（默认 20）
- 闪避：检测到人声时压低，停顿处上抬 --lift dB（默认 6；攻击 80ms / 释放 600ms）
- BGM 1s 淡入、成片末尾 2s 淡出；短于成片时循环（2s 交叉淡化）
- 最后 ffmpeg loudnorm 两遍处理到 --lufs（TP -1.5），视频流直接拷贝
"""
import argparse, json, subprocess, tempfile, os, re
import numpy as np

SR = 48000


def load(path, offset=0.0):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(offset), '-i', path, '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def save(path, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_s24le', path], input=x.astype('<f8').tobytes(), check=True)


def loudness(path):
    log = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[0-9.]+) LUFS', log)[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True); ap.add_argument('--bgm', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--offset', type=float, default=0.0); ap.add_argument('--below', type=float, default=20.0)
    ap.add_argument('--lift', type=float, default=6.0); ap.add_argument('--lufs', type=float, default=-16.0)
    ap.add_argument('--wav', help='另存混音 wav'); ap.add_argument('--report', help='写 JSON 测量结果')
    a = ap.parse_args()
    v = load(a.inp); n = len(v)
    b = load(a.bgm, a.offset)
    if len(b) < n:  # 循环 + 2s 交叉淡化
        xf = 2 * SR; out = b.copy()
        while len(out) < n:
            r = np.linspace(0, 1, xf)[:, None]
            out = np.concatenate([out[:-xf], out[-xf:] * (1 - r) + b[:xf] * r, b[xf:]])
        b = out
    b = b[:n]
    # 人声包络（20ms 帧）
    hop = SR // 50
    fr = v[: n // hop * hop].mean(1).reshape(-1, hop)
    rms_db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    active = rms_db > -42
    # 保持 250ms，填补字间空隙
    hold = 12; act = active.copy()
    for i in np.nonzero(active)[0]: act[i:i + hold] = True
    voice_db = 20 * np.log10(np.sqrt((fr[act] ** 2).mean()) + 1e-9)
    bf = b[: n // hop * hop].mean(1).reshape(-1, hop)
    bgm_db = 20 * np.log10(np.sqrt((bf ** 2).mean()) + 1e-9)
    base = voice_db - a.below - bgm_db  # 说话时 BGM 增益（dB）
    target = np.where(act, base, base + a.lift)
    # 平滑：下压 80ms，上抬 600ms
    g = np.empty_like(target); cur = target[0]
    ka, kr = 1 - np.exp(-1 / (0.08 * 50)), 1 - np.exp(-1 / (0.6 * 50))
    for i, t in enumerate(target):
        cur += (t - cur) * (ka if t < cur else kr); g[i] = cur
    gain = 10 ** (np.interp(np.arange(n) / hop, np.arange(len(g)), g) / 20)
    fade = np.ones(n); fade[:SR] = np.linspace(0, 1, SR); fade[-2 * SR:] *= np.linspace(1, 0, 2 * SR)
    bm = b * (gain * fade)[:, None]
    mix = v + bm
    with tempfile.TemporaryDirectory() as td:
        pv, pb, pm = (os.path.join(td, x) for x in ('v.wav', 'b.wav', 'm.wav'))
        save(pv, v); save(pb, bm); save(pm, mix)
        # 说话段的电平差（RMS）
        bmf = bm[: n // hop * hop].mean(1).reshape(-1, hop)
        diff_speech = voice_db - 20 * np.log10(np.sqrt((bmf[act] ** 2).mean()) + 1e-9)
        diff_pause = (voice_db - 20 * np.log10(np.sqrt((bmf[~act] ** 2).mean()) + 1e-9)) if (~act).any() else None
        Lv, Lb = loudness(pv), loudness(pb)
        # loudnorm 两遍
        log = subprocess.run(['ffmpeg', '-hide_banner', '-i', pm, '-af', f'loudnorm=I={a.lufs}:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
        m = json.loads(log[log.rindex('{'):log.rindex('}') + 1])
        ln = f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
        fin = os.path.join(td, 'f.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pm, '-af', ln + ',aresample=48000', '-c:a', 'pcm_s16le', fin], check=True)
        if a.wav: subprocess.run(['cp', fin, a.wav], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.inp, '-i', fin, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', a.out], check=True)
        rep = {'out': a.out, 'bgm': a.bgm, 'final_LUFS': loudness(a.out), 'voice_LUFS_premix': Lv, 'bgm_LUFS_premix': Lb,
               'voice_minus_bgm_LUFS': round(Lv - Lb, 1), 'voice_minus_bgm_rms_speech_dB': round(diff_speech, 1),
               'voice_minus_bgm_rms_pause_dB': round(diff_pause, 1) if diff_pause is not None else None, 'duck_depth_dB': a.lift}
    print(json.dumps(rep, ensure_ascii=False))
    if a.report: json.dump(rep, open(a.report, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
