#!/usr/bin/env python3
"""Independent final-MP4 metrics and actual-frame extraction, not visual approval.

Run after the final default rendering entry has produced video.mp4 and receipts.
This QA tool never writes production sources, freezes, audio or render receipts.
The output remains awaiting visual review until its actual images are viewed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

D = Path(__file__).resolve().parent
ROOT = D.parents[1]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def run(args: list[str]) -> bytes:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}): '
                           + result.stderr.decode(errors='replace')[-3000:])
    return result.stdout


def probe(args: list[str]):
    return json.loads(run(['ffprobe', '-v', 'error', *args, '-of', 'json']))


def packet_rows(path: Path):
    result = probe(['-select_streams', 'a:0', '-show_packets',
                    '-show_data_hash', 'sha256', '-show_entries',
                    'packet=pts_time,dts_time,duration_time,size,data_hash',
                    str(path)])['packets']
    assert result and all('data_hash' in row for row in result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--video', type=Path, default=D / 'video.mp4')
    ap.add_argument('--plan', type=Path, default=D / 'qa-video-independent-plan.json')
    ap.add_argument('--output', type=Path, default=D / 'qa-video-independent-evidence')
    args = ap.parse_args()
    video = args.video.resolve()
    plan = read(args.plan)
    expected = plan['expected']
    for relative, digest in plan['inputSHA256'].items():
        assert sha(D / relative) == digest, f'Plan production input moved: {relative}'
    manifest_path = D / 'source-sha256.json'
    manifest = read(manifest_path)
    assert manifest
    for relative, digest in manifest.items():
        path = (D / relative).resolve()
        assert path.is_relative_to(ROOT) and sha(path) == digest, relative

    render = read(D / 'render-result.json')
    appendix = read(D / 'reference-appendix.json')
    receipt = read(D / 'reference-appendix-media-check.json')
    references = read(D / 'references.json')
    media_sha = sha(video)
    assert render['sha256'] == appendix['outputSHA256'] == receipt['outputSHA256'] == media_sha
    assert render['frames'] == appendix['finalVideoFrames'] == receipt['finalFrames'] == expected['finalFrames']
    assert appendix['bodyFrames'] == receipt['bodyFrames'] == expected['bodyFrames']
    assert receipt['appendedFrames'] == expected['referenceFrames']
    assert receipt['passed'] is True
    assert appendix['inputs']['referencesSHA256'] == sha(D / 'references.json')
    assert appendix['presentation'] == references['presentation'] == 'original-title-quote'
    assert appendix['sourceTitles'] == [dict(id=s['id'], title=s['title']) for s in references['sources']]
    for s in references['sources']:
        if s.get('quotation'):
            q = next(q for q in appendix['quotations'] if q['id'] == s['id'])
            assert q['text'] == s['quotation']['text'] and q['locator'] == s['quotation']['locator']

    stream_probe = probe(['-show_streams', '-show_format', str(video)])
    vs = next(s for s in stream_probe['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in stream_probe['streams'] if s['codec_type'] == 'audio')
    assert vs['codec_name'] == 'h264' and audio['codec_name'] == 'aac'
    assert (vs['width'], vs['height']) == (expected['width'], expected['height'])
    assert vs['r_frame_rate'] == vs['avg_frame_rate'] == expected['fps']
    assert int(audio['sample_rate']) == 48000

    frame_probe = probe(['-select_streams', 'v:0', '-show_frames', '-show_entries',
                         'frame=best_effort_timestamp_time,duration_time,pkt_duration_time',
                         str(video)])['frames']
    assert len(frame_probe) == expected['finalFrames']
    pts = [Decimal(row['best_effort_timestamp_time']) for row in frame_probe]
    assert pts[0] == 0 and all(b > a for a, b in zip(pts, pts[1:]))
    errors = [abs(t - Decimal(i) / Decimal(30)) for i, t in enumerate(pts)]
    assert max(errors) <= Decimal('0.000001'), max(errors)
    durations = [Decimal(row.get('duration_time', row.get('pkt_duration_time', '0')))
                 for row in frame_probe]
    assert all(abs(d - Decimal(1) / Decimal(30)) <= Decimal('0.000001') for d in durations)

    decode = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror',
                             '-err_detect', 'explode', '-i', str(video),
                             '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert decode.returncode == 0 and not decode.stderr, decode.stderr.decode(errors='replace')

    body = Path(appendix['body'])
    assert body.is_file() and sha(body) == appendix['inputs']['bodySHA256']
    body_packets = packet_rows(body)
    final_packets = packet_rows(video)
    assert body_packets == final_packets, 'Actual final AAC packets or timing changed'
    packet_digest = hashlib.sha256(json.dumps(final_packets, sort_keys=True).encode()).hexdigest()

    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    selection = '+'.join(f'eq(n\\,{row["frame"]})' for row in plan['frames'])
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(video), '-an',
         '-vf', 'select=' + selection, '-fps_mode', 'passthrough',
         str(out / 'decoded-%03d.png')])
    extracted = sorted(out.glob('decoded-*.png'))
    assert len(extracted) == len(plan['frames'])
    images = []
    for file, row in zip(extracted, plan['frames']):
        target = out / f'frame-{row["frame"]:06d}.png'
        file.replace(target)
        images.append({**row, 'ptsSeconds': str(pts[row['frame']]),
                       'file': str(target.relative_to(D)), 'sha256': sha(target),
                       'actuallyViewed': False})
    pts_file = out / 'actual-video-pts.json'
    pts_file.write_text(json.dumps([str(t) for t in pts]) + '\n')
    assert sha(video) == media_sha, 'Final media changed during review'
    report = {
        'status': 'technical-checks-passed-awaiting-image-review',
        'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
        'checkedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'reviewer': 'bloom_final_media', 'scope': __doc__,
        'media': {'file': str(video.relative_to(ROOT)), 'sha256': media_sha,
                  'bytes': video.stat().st_size, 'width': vs['width'], 'height': vs['height'],
                  'fps': vs['avg_frame_rate'], 'frames': len(pts),
                  'seconds': str(Decimal(len(pts)) / Decimal(30)),
                  'videoCodec': vs['codec_name'], 'audioCodec': audio['codec_name'],
                  'audioSampleRate': int(audio['sample_rate'])},
        'productionInputs': {'manifestSHA256': sha(manifest_path),
                             'frozenInputsVerified': len(manifest),
                             'planSHA256': sha(args.plan),
                             'validatorSHA256': sha(Path(__file__))},
        'fullDecode': {'returnCode': decode.returncode, 'stderrBytes': len(decode.stderr)},
        'timeline': {'frames': len(pts), 'firstPTS': str(pts[0]), 'lastPTS': str(pts[-1]),
                     'maximumExpectedPTSErrorSeconds': str(max(errors)),
                     'allDurationsOneFrame': True,
                     'actualPTSFile': str(pts_file.relative_to(D)), 'actualPTSSHA256': sha(pts_file)},
        'actualAACRetention': {'bodySHA256': sha(body), 'bodyMatchesReceipt': True,
                               'packetCount': len(final_packets),
                               'allPacketPayloadsAndTimingEqual': True,
                               'packetRowsSHA256': packet_digest,
                               'note': 'Original AAC packet endpoint retained; no claim of new zero PCM packets in the visual appendix.'},
        'referenceIdentity': {'sourceTitles': appendix['sourceTitles'],
                              'quotationsBoundToCurrentReferences': True,
                              'appendixFrom': expected['bodyFrames'],
                              'appendixFrames': expected['referenceFrames']},
        'actualEncodedImages': images,
        'limitations': ['The images still require actual visual inspection.',
                        'No ASR, semantic audio listening, full human listening or real-time full-film watching is performed by this tool.',
                        'Browser playback and native VTT boundaries are separate website checks.'],
    }
    (D / 'qa-video-independent-data.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'mediaSHA256': media_sha,
                      'frames': len(pts), 'actualImages': len(images),
                      'AACPackets': len(final_packets)}))


if __name__ == '__main__':
    main()
