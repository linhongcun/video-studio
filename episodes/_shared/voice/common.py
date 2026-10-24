"""Shared setup and audio helpers for the voice step (EP.14 degradation numerics).

Every script takes --dir EPDIR and runs inside EPDIR/voice, so the relative
paths (sents.json, takes/, ../voice.wav, ../words.json) match the scripts
that produced EP.14. Optional EPDIR/voice/params.json overrides DEFAULTS;
the defaults are the EP.14 values, so EP.14 needs no params.json.
"""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent          # episodes/_shared/voice
SHARED = HERE.parent                            # episodes/_shared
ROOT = HERE.parents[2]                          # repo root

DEFAULTS = {
    'fps': 30, 'sr': 48000,
    # prep: TTS-only substitutions [[from, to], ...] applied to every sentence (EP.14: none)
    'subst': [],
    # build: pauses in seconds; minShotFrames=None turns the minimum-shot-length rule off
    'lead': 0.30, 'gapIn': 0.35, 'gapShot': 0.70, 'tail': 0.60,
    'minShotFrames': 225, 'extraAfter': {},
    'sentenceLufs': -21.0, 'trackLufs': -16.0, 'tpCeilingDb': -1.4, 'tpStopDb': -1.2,
    'tts': {'script': 'episodes/_shared/tts/mimo_say.py', 'threads': 4},
    'asr': {'model': 'medium', 'device': 'cpu', 'computeType': 'float32', 'threads': 8,
            'beam': 5, 'language': 'zh', 'initialPrompt': '以下是普通话的句子。'},
}


def load_params(voice_dir='.'):
    p = json.loads(json.dumps(DEFAULTS))
    f = Path(voice_dir) / 'params.json'
    if f.exists():
        for k, v in json.loads(f.read_text(encoding='utf-8')).items():
            if isinstance(v, dict) and isinstance(p.get(k), dict) and k != 'extraAfter':
                p[k].update(v)
            else:
                p[k] = v
    return p


def setup(doc, add_args=None, argv=None):
    """Parse --dir, chdir to EPDIR/voice, return (args, params)."""
    ap = argparse.ArgumentParser(description=doc)
    ap.add_argument('--dir', required=True, help='episode dir (holds script.md and voice/)')
    if add_args:
        add_args(ap)
    a = ap.parse_args(argv)
    vd = Path(a.dir).resolve() / 'voice'
    vd.mkdir(parents=True, exist_ok=True)
    os.chdir(vd)
    return a, load_params('.')


SR = 48000


def load(f):
    """Any audio file -> float32 mono 48 kHz via ffmpeg (EP.14 build.py `load`)."""
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ar', '48000', '-ac', '1', '-f', 'f32le', '-'],
                                        capture_output=True).stdout, np.float32).copy()


def lufs(a):
    """Integrated loudness via ffmpeg ebur128 (EP.14 build.py `lufs`)."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', 'ebur128', '-f', 'null', '-'],
                       input=a.astype(np.float32).tobytes(), capture_output=True).stderr.decode()
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])


def cut(x):
    """Drop the trailing "好。" take tail: cut at the last >=150 ms gap (EP.14 build.py `cut`, verbatim)."""
    fr = np.abs(x[:len(x)//480*480]).reshape(-1, 480).max(1) > 0.01; sp = np.where(fr)[0]; gaps = []; i = sp[0]
    while i < sp[-1]:
        if not fr[i]:
            j = i
            while not fr[j]: j += 1
            if j-i >= 15: gaps.append((i, j))
            i = j
        else: i += 1
    g = gaps[-1]; tail = len(x)/SR-g[1]*.01
    y = x[max(0, sp[0]*480-int(.03*SR)):min(int((g[0]*.01+.20)*SR), g[1]*480)].copy(); r = int(.02*SR); y[-r:] *= np.linspace(1, 0, r); r = int(.01*SR); y[:r] *= np.linspace(0, 1, r)
    return y, tail


def whisper(params):
    from faster_whisper import WhisperModel
    q = params['asr']
    return WhisperModel(q['model'], device=q['device'], compute_type=q['computeType'], cpu_threads=q['threads'])
