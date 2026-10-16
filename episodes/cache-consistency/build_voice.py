"""Place v9 sentence audio at storyboard voice offsets, preserving all holds."""
import hashlib
import json
from pathlib import Path
import wave

HERE = Path(__file__).resolve().parent
SOURCE = Path('/workspace/share/ep22-v9')
NARRATION = SOURCE / 'narration.wav'
TIMELINE = SOURCE / 'timeline.json'
SHA_PREFIX = '0e3138f7'
SAMPLE_RATE = 48000
SAMPLE_WIDTH = 2
SENTENCE_COUNT = 50


def read_sentence(sid):
    path = SOURCE / 'sentences' / f'{sid}.wav'
    with wave.open(str(path), 'rb') as source:
        params = source.getparams()
        if (params.framerate != SAMPLE_RATE or params.nchannels != 1
                or params.sampwidth != SAMPLE_WIDTH or params.comptype != 'NONE'):
            raise SystemExit(f'{path}: expected 48 kHz mono s16 PCM, got {params}')
        pcm = source.readframes(params.nframes)
    if len(pcm) != params.nframes * SAMPLE_WIDTH:
        raise SystemExit(f'{path}: truncated audio data')
    # Drop trailing digital silence (exact zero samples) so padding in the
    # sentence file is not counted as speech for overlap/end checks.
    end = len(pcm)
    while end >= SAMPLE_WIDTH and pcm[end - SAMPLE_WIDTH:end] == bytes(SAMPLE_WIDTH):
        end -= SAMPLE_WIDTH
    return pcm[:end]


def main():
    storyboard = json.loads((HERE / 'storyboard.json').read_text())
    fps = storyboard['meta']['fps']
    total = storyboard['meta']['durationInFrames']
    shots = [shot for scene in storyboard['scenes'] for shot in scene['shots']]
    assert total == sum(shot['durationInFrames'] for shot in shots), (
        'Storyboard duration does not equal the sum of shot durations'
    )

    digest = hashlib.sha256(NARRATION.read_bytes()).hexdigest()
    if not digest.startswith(SHA_PREFIX):
        raise SystemExit(f'Unexpected narration SHA256: {digest}')
    timeline = json.loads(TIMELINE.read_text())
    timeline_ids = [sentence['id'] for sentence in timeline['sentences']]
    if len(timeline_ids) != SENTENCE_COUNT or len(set(timeline_ids)) != SENTENCE_COUNT:
        raise SystemExit(f'Timeline must contain exactly {SENTENCE_COUNT} unique sentence IDs')

    placements = {}
    for shot in shots:
        offsets = {}
        for subtitle in shot.get('subtitles', []):
            if 'src' not in subtitle:
                continue
            sid = subtitle['src']
            offset = subtitle['voiceFrom']
            offsets[sid] = min(offsets.get(sid, offset), offset)
        for sid, offset in offsets.items():
            if sid in placements:
                raise SystemExit(
                    f"Sentence {sid} appears in two shots: "
                    f"{placements[sid]['shot']} and {shot['id']}"
                )
            placements[sid] = dict(id=sid, shot=shot['id'], startFrame=shot['from'] + offset)

    if len(placements) != SENTENCE_COUNT or set(placements) != set(timeline_ids):
        missing = sorted(set(timeline_ids) - set(placements))
        extra = sorted(set(placements) - set(timeline_ids))
        raise SystemExit(
            f'Storyboard must match all {SENTENCE_COUNT} timeline sentences; '
            f'found {len(placements)}, missing={missing}, extra={extra}'
        )

    target_samples = round(total * SAMPLE_RATE / fps)
    holds = sorted(placements.values(), key=lambda item: item['startFrame'])
    clips = []
    for entry in holds:
        pcm = read_sentence(entry['id'])
        samples = len(pcm) // SAMPLE_WIDTH
        entry['startSample'] = round(entry['startFrame'] * SAMPLE_RATE / fps)
        entry['endSample'] = entry['startSample'] + samples
        entry['durFrames'] = samples * fps / SAMPLE_RATE
        if entry['startSample'] < 0 or entry['endSample'] > target_samples:
            raise SystemExit(
                f"Sentence {entry['id']} spans samples {entry['startSample']}.."
                f"{entry['endSample']}, outside output 0..{target_samples}"
            )
        clips.append(pcm)

    for current, following in zip(holds, holds[1:]):
        if current['endSample'] > following['startSample']:
            raise SystemExit(
                f"Sentence {current['id']} ends at sample {current['endSample']} "
                f"and overlaps {following['id']} starting at {following['startSample']}"
            )

    audio = bytearray(target_samples * SAMPLE_WIDTH)
    for entry, pcm in zip(holds, clips):
        audio[entry['startSample'] * SAMPLE_WIDTH:entry['endSample'] * SAMPLE_WIDTH] = pcm
    output = HERE / 'remotion/public/audio/voice.wav'
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), 'wb') as voice:
        voice.setnchannels(1)
        voice.setsampwidth(SAMPLE_WIDTH)
        voice.setframerate(SAMPLE_RATE)
        voice.writeframes(audio)
    (HERE / 'holds_applied.json').write_text(
        json.dumps(holds, ensure_ascii=False, indent=2) + '\n'
    )
    print(f'Placed {len(holds)} sentences; narration SHA256 verified ({SHA_PREFIX}).')
    print(f'Voice: {total} frames at {fps} fps, {target_samples} samples '
          f'({target_samples / SAMPLE_RATE:.3f}s): {output}')


if __name__ == '__main__':
    main()
