"""Builds the synthetic tiny episode: copies fixtures/tiny into DIR and writes voice.wav + words.json there.
voice.wav = 4 s, 48 kHz mono 16-bit: silence, then each narration char is a 5-frame 150 Hz tone with 3 frames of silence
between chars (so onset_rule.py finds a pause before every char). No real voice/video anywhere."""
import hashlib, json, shutil, sys, wave
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
FPS, SR = 30, 48000; SPF = SR // FPS
SHOTS = [('01-open', 0, 60, [('s01', '你好世界。', 10)]), ('02-bye', 60, 120, [('s02', '再见朋友。', 70)])]
CH_LEN, CH_GAP, ASR_SLACK = 5, 3, 0.5


def make(dst):
    dst = Path(dst); shutil.copytree(HERE / 'fixtures' / 'tiny', dst, dirs_exist_ok=True)
    total = SHOTS[-1][2]; x = np.zeros(total * SPF); t = np.arange(len(x)) / SR
    shots = []
    for sid, a, b, sents in SHOTS:
        S = []
        for sent_id, text, f0 in sents:
            chars = []; f = f0
            for ch in text:
                if ch in '，。':
                    continue
                sl = slice(f * SPF, (f + CH_LEN) * SPF); x[sl] = 0.1 * np.sin(2 * np.pi * 150 * t[sl])
                chars.append({'ch': ch, 'startFrame': f + ASR_SLACK, 'endFrame': float(f + CH_LEN)}); f += CH_LEN + CH_GAP
            S.append({'id': sent_id, 'text': text, 'startFrame': chars[0]['startFrame'], 'endFrame': chars[-1]['endFrame'], 'chars': chars})
        shots.append({'id': sid, 'startFrame': a, 'endFrame': b, 'sentences': S})
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    with wave.open(str(dst / 'voice.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)
    words = {'fps': FPS, 'durationFrames': total,
             'scriptSha256': hashlib.sha256((dst / 'script.md').read_bytes()).hexdigest(),
             'audioSha256': hashlib.sha256((dst / 'voice.wav').read_bytes()).hexdigest(), 'shots': shots}
    (dst / 'words.json').write_text(json.dumps(words, ensure_ascii=False, indent=1) + '\n')
    return dst


if __name__ == '__main__':
    print(make(sys.argv[1]))
