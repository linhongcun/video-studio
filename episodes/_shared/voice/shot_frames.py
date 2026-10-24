#!/usr/bin/env python3
"""../words.json -> voice/shot_frames.json, the per-shot frame table.

EP.14 has no saved script for this file. This derivation reproduces EP.14's
voice/shot_frames.json byte for byte (sha256 f8f03b6c): indent=1, no trailing newline.

  python3 episodes/_shared/voice/shot_frames.py --dir EPDIR
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common


def derive(W):
    return dict(fps=W['fps'], audio=W['audio'], audioSha256=W['audioSha256'], durationFrames=W['durationFrames'],
                shots=[dict(shot=q['id'], startFrame=q['startFrame'], endFrame=q['endFrame'], durationFrames=q['durationFrames'],
                            sec=round(q['durationFrames']/W['fps'], 2), speechStartFrame=q['speechStartFrame'],
                            speechEndFrame=q['speechEndFrame'], onsetFrame=q['onsetFrame']) for q in W['shots']])


if __name__ == '__main__':
    a, P = common.setup(__doc__)
    W = json.load(open('../words.json', encoding='utf-8'))
    open('shot_frames.json', 'w', encoding='utf-8').write(json.dumps(derive(W), ensure_ascii=False, indent=1))
    print(len(W['shots']), 'shots', W['durationFrames'], 'frames')
