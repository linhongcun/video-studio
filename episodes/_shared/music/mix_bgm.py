#!/usr/bin/env python3
"""给 Remotion 渲染出的成片（人声+音效）混入曲库 BGM，并做闪避与响度归一。

用法：python3 mix_bgm.py --in voice.mp4 --bgm track.mp3 --out video.mp4 [--offset 0] [--below 11] [--bridge 2.5] [--lufs -16]
- BGM 电平按“人声说话时的 RMS”定标：说话时 BGM 比人声低 --below dB（默认 11）
- 桥段：≥ --min-pause 秒（默认 0.5）的停顿（镜头/章节末约 1.2s 的停顿）里 BGM 升到比人声低 --bridge dB（默认 2.5），
  字间小空隙不抬（避免抽吸）；人声恢复前 --lookahead 秒（默认 0.3）先压下；两级一阶平滑（压低约 150ms、上抬约 220ms 的 S 形过渡）
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
    ap.add_argument('--offset', type=float, default=0.0); ap.add_argument('--below', type=float, default=11.0)
    ap.add_argument('--bridge', type=float, default=2.5); ap.add_argument('--min-pause', type=float, default=0.5)
    ap.add_argument('--lookahead', type=float, default=0.15); ap.add_argument('--lufs', type=float, default=-16.0)
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
    # 桥段 = 足够长的停顿；提前 lookahead 结束，让 BGM 在人声回来前压下
    # 桥段检测用更短的保持（100ms），否则 1.2s 的停顿会被吃掉一半
    act2 = active.copy()
    for i in np.nonzero(active)[0]: act2[i:i + 5] = True
    bridge = np.zeros_like(act); la = int(a.lookahead * 50); i = 0
    while i < len(act2):
        if not act2[i]:
            j = i
            while j < len(act2) and not act2[j]: j += 1
            if (j - i) / 50 >= a.min_pause: bridge[i:max(i, j - la if j < len(act2) else j)] = True
            i = j
        else: i += 1
    base = voice_db - a.below - bgm_db
    target = np.where(bridge, voice_db - a.bridge - bgm_db, base)
    g = target.copy()
    ka, kr = 1 - np.exp(-1 / (0.06 * 50)), 1 - np.exp(-1 / (0.09 * 50))  # 两级串联后约 150ms / 220ms 的平滑 S 形
    for _ in range(2):  # 两级一阶平滑 ≈ 平滑 S 形过渡
        cur = g[0]; h = np.empty_like(g)
        for k, t in enumerate(g):
            cur += (t - cur) * (ka if t < cur else kr); h[k] = cur
        g = h
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
        # 桥段电平：取每个桥段中间 60% 的 RMS（避开过渡），相对人声说话电平
        core = bridge.copy()
        for k in range(len(bridge)):
            if bridge[k] and (not bridge[max(0, k - 8)] or not bridge[min(len(bridge) - 1, k + 8)]): core[k] = False
        core &= np.arange(len(core)) > 75  # 跳过 1s 淡入
        diff_pause = (voice_db - 20 * np.log10(np.sqrt((bmf[core] ** 2).mean()) + 1e-9)) if core.any() else None
        segs = []; k = 0
        while k < len(bridge):
            if bridge[k]:
                j = k
                while j < len(bridge) and bridge[j]: j += 1
                segs.append((round(k / 50, 2), round(j / 50, 2))); k = j
            else: k += 1
        Lv, Lb = loudness(pv), loudness(pb)
        # loudnorm 两遍
        log = subprocess.run(['ffmpeg', '-hide_banner', '-i', pm, '-af', f'loudnorm=I={a.lufs}:TP=-2.0:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
        m = json.loads(log[log.rindex('{'):log.rindex('}') + 1])
        ln = f"loudnorm=I={a.lufs}:TP=-2.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
        fin = os.path.join(td, 'f.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pm, '-af', ln + ',aresample=48000,alimiter=limit=0.79:attack=2:release=50:level=false', '-c:a', 'pcm_s16le', fin], check=True)
        if a.wav: subprocess.run(['cp', fin, a.wav], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.inp, '-i', fin, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', a.out], check=True)
        tp = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', a.out, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
        tpk = float(re.findall(r'Peak:\s+(-?[0-9.]+) dBFS', tp)[-1])
        rep = {'out': a.out, 'bgm': a.bgm, 'final_LUFS': loudness(a.out), 'voice_LUFS_premix': Lv, 'bgm_LUFS_premix': Lb,
               'voice_minus_bgm_LUFS': round(Lv - Lb, 1), 'voice_minus_bgm_rms_speech_dB': round(diff_speech, 1),
               'voice_minus_bgm_bridge_dB': round(diff_pause, 1) if diff_pause is not None else None,
               'duck_depth_dB': round(a.below - a.bridge, 1), 'bridges_s': segs, 'true_peak_dBTP': tpk}
    print(json.dumps(rep, ensure_ascii=False))
    if a.report: json.dump(rep, open(a.report, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
