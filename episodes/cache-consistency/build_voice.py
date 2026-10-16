"""Insert v9 chapter-card silences and pad the voice track to the storyboard."""
import argparse
import hashlib
import json
from pathlib import Path
import wave

HERE = Path(__file__).resolve().parent
NARRATION = Path('/workspace/share/ep22-v9/narration.wav')
TIMELINE = Path('/workspace/share/ep22-v9/timeline.json')
SHA_PREFIX = '0e3138f7'


def read_narration():
    digest = hashlib.sha256(NARRATION.read_bytes()).hexdigest()
    assert digest.startswith(SHA_PREFIX), f'Unexpected narration SHA256: {digest}'
    with wave.open(str(NARRATION), 'rb') as source:
        params = source.getparams()
        assert params.comptype == 'NONE' and params.sampwidth == 2, params
        pcm = source.readframes(params.nframes)
    return params, pcm, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tail_frames', type=float, nargs='?', help='Optional tail in video frames; default: compute from storyboard')
    args = parser.parse_args()
    storyboard = json.loads((HERE / 'storyboard.json').read_text())
    fps = storyboard['meta']['fps']
    shots = [shot for scene in storyboard['scenes'] for shot in scene['shots']]
    total = storyboard['meta']['durationInFrames']
    assert total == sum(shot['durationInFrames'] for shot in shots)
    params, pcm, digest = read_narration()
    sr = params.framerate
    stride = params.nchannels * params.sampwidth
    timeline = json.loads(TIMELINE.read_text())
    assert timeline['sample_rate'] == sr
    sentences = timeline['sentences']
    by_id = {sentence['id']: (i, sentence) for i, sentence in enumerate(sentences)}
    assert len(by_id) == len(sentences), 'Duplicate sentence IDs'
    assert abs(timeline['duration'] - params.nframes / sr) * fps <= 1
    holds = []
    for shot in shots:
        if not shot.get('chapterCard'):
            continue
        card = shot['chapterCard']
        sid = card['insertBeforeSentence']
        index, sentence = by_id[sid]
        # The source timeline uses start/end seconds, not startSec/endSec.
        insertion = sentence['start'] - 0.1
        assert index == 0 or sentences[index - 1]['end'] <= insertion, sid
        position = round(insertion * sr)
        assert 0 <= position < params.nframes, sid
        assert not holds or position >= holds[-1]['orig_sample'], sid
        frames = card['holdFrames']
        assert frames == shot['durationInFrames'], shot['id']
        samples = round(frames * sr / fps)
        holds.append(dict(shot=shot['id'], before=sid, orig_sec=position / sr,
                          orig_sample=position, frames=frames, samples=samples))
        print(f"{shot['id']}: insert {frames} frames before {sid} at {position / sr:.3f}s")
    target_samples = round(total * sr / fps)
    hold_samples = sum(hold['samples'] for hold in holds)
    remaining = target_samples - params.nframes - hold_samples
    tail_samples = remaining if args.tail_frames is None else round(args.tail_frames * sr / fps)
    assert tail_samples >= 0, 'Narration and holds exceed storyboard, or tail is negative'
    output_samples = params.nframes + hold_samples + tail_samples
    assert abs(output_samples - target_samples) * fps / sr <= 1, 'Explicit tail does not match storyboard (±1 frame)'
    print(f'Tail: {tail_samples * fps / sr:.6f} frames ({tail_samples} samples, {tail_samples / sr:.6f}s)')
    output = HERE / 'remotion/public/audio/voice.wav'
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), 'wb') as voice:
        voice.setparams(params._replace(nframes=output_samples))
        previous = 0
        inserted = 0
        for hold in holds:
            position = hold['orig_sample']
            voice.writeframesraw(pcm[previous * stride:position * stride])
            hold['output_sample'] = position + inserted
            voice.writeframesraw(bytes(hold['samples'] * stride))
            previous = position
            inserted += hold['samples']
        voice.writeframesraw(pcm[previous * stride:])
        voice.writeframesraw(bytes(tail_samples * stride))
    holds.append(dict(shot=shots[-1]['id'], before='end', frames=tail_samples * fps / sr,
                      samples=tail_samples, output_sample=params.nframes + hold_samples,
                      narration_samples=params.nframes, narration_sha256=digest,
                      sample_rate=sr, fps=fps))
    (HERE / 'holds_applied.json').write_text(json.dumps(holds, ensure_ascii=False, indent=2) + '\n')
    print(f'Voice: {output_samples * fps / sr:.6f} frames; storyboard: {total} frames')


if __name__ == '__main__':
    main()
