#!/usr/bin/env python3
"""Read-only independent QA of this revision's completed, frozen final MP4.

--prepare-plan writes only this QA plan after actual timing and key-state frame
selection are final. It does not freeze production inputs or render media.
The default check requires the producer's complete expected media/manifest SHA.
This height-choice revision samples its new one-level counterexample, explicit
reset, preselected two-level allocation, retained handoff/search/pointer writes
and actual reference appendix. Timing comes from the new final storyboard.
Technical success is never visual or semantic audio approval.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

D = Path(__file__).resolve().parent
ROOT = next(p for p in D.parents
            if (p / 'AGENTS.md').is_file() and (p / 'site/package.json').is_file())
PLAN = D / 'qa-video-independent-plan.json'
MANIFEST = D / 'source-sha256.json'
CORE = ['script.md', 'storyboard.json', 'words.json', 'model.json',
        'height-options.json', 'references.json', 'remotion/src/Main.tsx',
        'voice.wav', 'voice/input-provenance.json', 'voice/reused-source-baseline.json',
        'qa-voice.json', 'qa-voice-takes.json']


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def save(path: Path, obj):
    assert path.resolve().is_relative_to(D), 'QA output must stay in this new episode'
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def run(args: list[str]) -> bytes:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}): '
                           + result.stderr.decode(errors='replace')[-3000:])
    return result.stdout


def probe(args: list[str]):
    return json.loads(run(['ffprobe', '-v', 'error', *args, '-of', 'json']))


def valid_sha(value: str) -> str:
    if not re.fullmatch('[0-9a-f]{64}', value):
        raise argparse.ArgumentTypeError('A complete lowercase SHA-256 is required')
    return value


def frozen_snapshot(expected_sha: str):
    assert sha(MANIFEST) == expected_sha, 'Authorized new manifest identity differs'
    manifest = read(MANIFEST)
    assert manifest and all(p in manifest for p in CORE), 'Core production input missing from freeze'
    for helper in ['append_references_bibliography.py', 'append_references_original.py', 'append_references.py', 'render_with_references.py']:
        source = ROOT / 'episodes-codex/_shared' / helper
        relative = os.path.relpath(source, D)
        assert relative in manifest and manifest[relative] == sha(source), f'Actual bibliography dependency not frozen: {helper}'
    for relative, digest in manifest.items():
        path = (D / relative).resolve()
        assert path.is_relative_to(ROOT), relative
        assert path.is_file() and sha(path) == digest, f'Frozen production input changed: {relative}'
    return manifest


def storyboard():
    sb = read(D / 'storyboard.json')
    meta = sb['meta']
    assert meta['episode'] == 40 and read(D / 'episode-config.json')['slug'] == 'redis-skiplist'
    assert not any(meta.get(k) for k in ('draft', 'provisionalTiming', 'pendingAudio'))
    assert (meta['width'], meta['height'], meta['fps']) == (1920, 1080, 30)
    shots = [s for scene in sb['scenes'] for s in scene['shots']]
    assert len(shots) == read(D / 'episode-config.json')['shotCount']
    cursor = 0
    for shot in shots:
        assert shot['from'] == cursor and shot['durationInFrames'] > 0
        cursor += shot['durationInFrames']
    assert cursor == meta['durationInFrames'], 'This QA currently expects the body to be the timed shots'
    words = read(D / 'words.json')
    assert words['durationFrames'] == cursor and words['audioSha256'] == sha(D / 'voice.wav')
    source = read(D / 'qa-voice.json')
    assert source['status'] == 'passed' and source['voiceSHA256'] == sha(D / 'voice.wav')
    assert source['frames'] == cursor and source['scriptSHA256'] == sha(D / 'script.md')
    reused = read(D / 'voice/reused-source-baseline.json')
    assert sha(D / 'voice.wav') != reused['originalVoiceSHA256'], 'Old all-20 audio is not this revision final voice'
    return sb, shots


def prepare_plan(args):
    manifest = frozen_snapshot(args.expected_manifest_sha256)
    sb, shots = storyboard()
    old = read(args.plan)
    for relative, digest in old['observedPlanningInputs'].items():
        assert sha(D / relative) == digest, f'Planning source changed; re-audit keyframes before freezing QA plan: {relative}'
    lookup = {str(s['id']).zfill(2): s for s in shots}
    keys = old['keyframes']
    assert keys, 'Actual Main/storyboard key-state pairs must be selected before finalizing this plan'
    groups = {}
    frames = {}

    def add(frame, purpose, **context):
        assert 0 <= frame < sb['meta']['durationInFrames']
        if frame not in frames:
            frames[frame] = {'frame': frame, 'purposes': [], **context}
        frames[frame]['purposes'].append(purpose)

    add(0, 'Actual first body frame')
    if old.get('includeShotRepresentatives', False):
        for shot_id, shot in lookup.items():
            local = min(shot['durationInFrames'] - 1,
                        int(shot['durationInFrames'] * Decimal('0.72')))
            add(shot['from'] + local, 'Representative encoded shot state', shot=shot_id, local=local)
    for row in keys:
        shot_id = str(row['shot']).zfill(2)
        local = row['local']
        assert isinstance(local, int) and 0 <= local < lookup[shot_id]['durationInFrames']
        global_frame = lookup[shot_id]['from'] + local
        groups.setdefault(row['group'], set()).add(global_frame)
        add(global_frame, row['purpose'],
            shot=shot_id, local=local, keyStateGroup=row['group'])
    assert all(len(groups.get(g, [])) >= 2 for g in old['requiredKeyStateGroups']), groups
    assert len(frames) == old['plannedBodyImageCount'], 'Review the bounded frame plan before freezing it'
    covered = {str(s['id']).zfill(2) for s in shots
               if any(s['from'] <= f < s['from'] + s['durationInFrames'] for f in frames)}
    assert covered == set(lookup), 'Every shot needs at least one actual selected state'
    old.update(status='ready-for-final-media-awaiting-producer-render-notification',
               preparedAtUTC=datetime.now(timezone.utc).isoformat(),
               productionManifestSHA256=sha(MANIFEST),
               frozenInputCount=len(manifest),
               inputSHA256={p: sha(D / p) for p in CORE},
               expected={'bodyFrames': sb['meta']['durationInFrames'], 'width': 1920,
                         'height': 1080, 'fps': '30/1', 'shotCount': len(shots),
                         'finalFrames': 'derived-from-matching-actual-render-and-appendix-receipts',
                         'referenceFrames': 'derived-from-actual-appendix-pages'},
               frames=[frames[n] for n in sorted(frames)],
               referenceSelection='For every actual page: first, middle, last; plus last body frame')
    save(args.plan, old)
    print(json.dumps({'status': old['status'], 'bodyFrames': sb['meta']['durationInFrames'],
                      'plannedBodyImages': len(frames), 'frozenInputCount': len(manifest)}))


def packet_rows(path: Path):
    rows = probe(['-select_streams', 'a:0', '-show_packets', '-show_data_hash', 'sha256',
                  '-show_entries', 'packet=pts_time,dts_time,duration_time,size,data_hash',
                  str(path)])['packets']
    assert rows and all('data_hash' in row for row in rows)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prepare-plan', action='store_true')
    ap.add_argument('--expected-manifest-sha256', type=valid_sha, required=True)
    ap.add_argument('--expected-media-sha256', type=valid_sha)
    ap.add_argument('--plan', type=Path, default=PLAN)
    args = ap.parse_args()
    args.plan = args.plan.resolve()
    assert args.plan.is_relative_to(D), 'Plan must stay in the new episode'
    if args.prepare_plan:
        prepare_plan(args)
        return
    assert args.expected_media_sha256, 'Completed final render notification and full media SHA required'
    video = D / 'video.mp4'
    media_sha = sha(video)
    assert media_sha == args.expected_media_sha256, 'Final actual media differs from producer identity'
    manifest = frozen_snapshot(args.expected_manifest_sha256)
    plan = read(args.plan)
    assert plan['status'] == 'ready-for-final-media-awaiting-producer-render-notification'
    assert plan['productionManifestSHA256'] == args.expected_manifest_sha256
    for relative, digest in plan['inputSHA256'].items():
        assert sha(D / relative) == digest, f'Plan input moved: {relative}'
    sb, shots = storyboard()
    expected = plan['expected']
    body_frames = sb['meta']['durationInFrames']
    assert body_frames == expected['bodyFrames'] and len(shots) == expected['shotCount']
    render = read(D / 'render-result.json')
    appendix = read(D / 'reference-appendix.json')
    receipt = read(D / 'reference-appendix-media-check.json')
    references = read(D / 'references.json')
    assert render['sha256'] == appendix['outputSHA256'] == receipt['outputSHA256'] == media_sha
    final_frames = render['frames']
    reference_frames = appendix['appendix']['durationInFrames']
    assert final_frames == render['finalVideoFrames'] == appendix['finalVideoFrames'] == receipt['finalFrames']
    assert body_frames == render['bodyFrames'] == appendix['bodyFrames'] == receipt['bodyFrames']
    assert reference_frames == receipt['appendedFrames'] == final_frames - body_frames
    assert appendix['appendix']['from'] == body_frames and receipt['passed'] is True
    assert appendix['inputs']['referencesSHA256'] == sha(D / 'references.json')
    assert appendix['presentation'] == references['presentation'] == 'title-author'
    layout = appendix['layout']
    assert layout == {'kind': 'title-author-single-column', 'maxItemsPerPage': 4,
                      'renderedFields': ['title', 'credit'], 'quotesRendered': False}
    bibliography = [dict(id=s['id'], title=s['title'], credit=s['author'] if 'author' in s else s['organization'])
                    for s in references['sources']]
    assert all(isinstance(row['credit'], str) and row['credit'].strip() for row in bibliography)
    assert appendix['bibliography'] == bibliography
    expected_pages = (len(bibliography) + layout['maxItemsPerPage'] - 1) // layout['maxItemsPerPage']
    assert len(appendix['appendix']['pages']) == expected_pages
    assert appendix['appendix']['framesPerPage'] == sb['meta']['fps'] * 5
    assert reference_frames == expected_pages * appendix['appendix']['framesPerPage']
    assert appendix['sourceTitles'] == [dict(id=s['id'], title=s['title']) for s in references['sources']]
    dependencies = appendix['dependencies']
    for file_key, sha_key in [('oldEngine', 'oldEngineSHA256'), ('originalRenderer', 'originalRendererSHA256')]:
        source = (ROOT / dependencies[file_key]).resolve()
        assert source.is_relative_to(ROOT) and sha(source) == dependencies[sha_key]
    assert appendix['inputs']['generatorSHA256'] == sha(ROOT / 'episodes-codex/_shared/append_references_bibliography.py')
    # Quotations remain research identities only; the new card intentionally
    # draws no quotation/version/date/pause hint.
    for source in references['sources']:
        if source.get('quotation'):
            q = next(q for q in appendix['quotations'] if q['id'] == source['id'])
            assert all(q[k] == source['quotation'][k] for k in ('text', 'locator', 'evidence'))
    body = Path(appendix['body']).resolve()
    assert body == (D / 'remotion/out/body.mp4').resolve(), 'Old or other episode body prohibited'
    assert Path(appendix['output']).resolve() == video.resolve()
    assert Path(appendix['references']).resolve() == (D / 'references.json').resolve()
    assert sha(body) == appendix['inputs']['bodySHA256'] == receipt['bodySHA256']

    stream_probe = probe(['-show_streams', '-show_format', str(video)])
    vs = next(s for s in stream_probe['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in stream_probe['streams'] if s['codec_type'] == 'audio')
    assert vs['codec_name'] == 'h264' and audio['codec_name'] == 'aac'
    assert (vs['width'], vs['height']) == (expected['width'], expected['height'])
    assert vs['r_frame_rate'] == vs['avg_frame_rate'] == expected['fps']
    assert int(audio['sample_rate']) == 48000
    fps_fraction = Fraction(expected['fps'])
    fps = Decimal(fps_fraction.numerator) / Decimal(fps_fraction.denominator)
    frame_probe = probe(['-select_streams', 'v:0', '-show_frames', '-show_entries',
                         'frame=best_effort_timestamp_time,duration_time,pkt_duration_time',
                         str(video)])['frames']
    assert len(frame_probe) == final_frames
    pts = [Decimal(row['best_effort_timestamp_time']) for row in frame_probe]
    assert pts[0] == 0 and all(b > a for a, b in zip(pts, pts[1:]))
    errors = [abs(t - Decimal(i) / fps) for i, t in enumerate(pts)]
    assert max(errors) <= Decimal('0.000001'), max(errors)
    durations = [Decimal(row.get('duration_time', row.get('pkt_duration_time', '0')))
                 for row in frame_probe]
    assert all(abs(d - 1 / fps) <= Decimal('0.000001') for d in durations)
    decode = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror',
                             '-err_detect', 'explode', '-i', str(video),
                             '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert decode.returncode == 0 and not decode.stderr, decode.stderr.decode(errors='replace')
    body_packets, final_packets = packet_rows(body), packet_rows(video)
    assert body_packets == final_packets, 'Final AAC payload/PTS/DTS/duration/size differs from body'
    packet_digest = hashlib.sha256(json.dumps(final_packets, sort_keys=True).encode()).hexdigest()

    selected = {row['frame']: row for row in plan['frames']}
    selected.setdefault(body_frames - 1, {'frame': body_frames - 1, 'purposes': ['Last actual body frame / caption boundary']})
    page_frames = appendix['appendix']['framesPerPage']
    assert page_frames * len(appendix['appendix']['pages']) == reference_frames
    for page in range(len(appendix['appendix']['pages'])):
        start = body_frames + page * page_frames
        for delta, purpose in ((0, 'first'), (page_frames // 2, 'middle'), (page_frames - 1, 'last')):
            frame = start + delta
            selected[frame] = {'frame': frame, 'purposes': [f'Actual reference page {page+1} {purpose} frame; original title/credit only and caption boundary'], 'referencePage': page + 1}
    frames = [selected[n] for n in sorted(selected)]
    out = D / 'qa-video-independent-evidence' / media_sha
    out.mkdir(parents=True, exist_ok=True)
    assert not list(out.glob('decoded-*.png')), 'Incomplete extraction exists; inspect QA evidence before rerun'
    selection = '+'.join(f'eq(n\\,{row["frame"]})' for row in frames)
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(video), '-an',
         '-vf', 'select=' + selection, '-fps_mode', 'passthrough', str(out / 'decoded-%03d.png')])
    extracted = sorted(out.glob('decoded-*.png'))
    assert len(extracted) == len(frames)
    images = []
    for file, row in zip(extracted, frames):
        target = out / f'frame-{row["frame"]:06d}.png'
        file.replace(target)
        images.append({**row, 'ptsSeconds': str(pts[row['frame']]),
                       'file': str(target.relative_to(D)), 'sha256': sha(target),
                       'actuallyViewed': False})
    pts_file = out / 'actual-video-pts.json'
    save(pts_file, [str(t) for t in pts])
    assert sha(video) == media_sha and frozen_snapshot(args.expected_manifest_sha256) == manifest
    baseline_comparisons = []
    for row in plan['previousEncodedArtifacts']:
        previous = (ROOT / row['previousPath']).resolve()
        current = (D / row['currentPath']).resolve()
        assert previous.is_relative_to(ROOT) and current.is_relative_to(D)
        assert sha(previous) == row['previousSHA256'], 'Protected previous media identity moved'
        baseline_comparisons.append({**row, 'currentSHA256': sha(current),
            'byteIdentical': sha(current) == row['previousSHA256'],
            'scope': 'Artifact byte comparison only; generation/reuse method must come from production provenance.'})
    production_provenance = D / 'voice/input-provenance.json'
    assert production_provenance.is_file(), 'Fresh current-voice provenance is required'
    report = {
        'status': 'technical-checks-passed-awaiting-actual-image-review', 'passed': False,
        'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
        'checkedAtBeijing': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'reviewer': 'skip_media_qa', 'scope': __doc__,
        'media': {'file': str(video.relative_to(ROOT)), 'sha256': media_sha,
                  'bytes': video.stat().st_size, 'width': vs['width'], 'height': vs['height'],
                  'fps': vs['avg_frame_rate'], 'frames': len(pts), 'bodyFrames': body_frames,
                  'referenceFrames': reference_frames, 'seconds': str(Decimal(len(pts)) / fps),
                  'videoCodec': vs['codec_name'], 'audioCodec': audio['codec_name'],
                  'audioSampleRate': int(audio['sample_rate'])},
        'productionInputs': {'manifestSHA256': sha(MANIFEST), 'frozenInputsVerified': len(manifest),
                             'planSHA256': sha(args.plan), 'validatorSHA256': sha(Path(__file__))},
        'fullDecode': {'returnCode': decode.returncode, 'stderrBytes': len(decode.stderr)},
        'timeline': {'frames': len(pts), 'firstPTS': str(pts[0]), 'lastPTS': str(pts[-1]),
                     'maximumExpectedPTSErrorSeconds': str(max(errors)), 'allDurationsOneFrame': True,
                     'actualPTSFile': str(pts_file.relative_to(D)), 'actualPTSSHA256': sha(pts_file)},
        'actualAACRetention': {'bodySHA256': sha(body), 'packetCount': len(final_packets),
                               'allPacketPayloadsAndTimingEqual': True, 'packetRowsSHA256': packet_digest,
                               'note': 'Retains the original body AAC endpoint; no new zero PCM packet claim.'},
        'referenceIdentity': {'sourceTitles': appendix['sourceTitles'],
                              'presentation': appendix['presentation'], 'layout': layout,
                              'bibliography': bibliography, 'researchQuotationsBoundToCurrentReferences': True,
                              'quotesRendered': False, 'maximumItemsPerPage': layout['maxItemsPerPage'],
                              'appendixFrom': body_frames, 'appendixFrames': reference_frames},
        'actualEncodedImages': images,
        'previousEncodedArtifactComparison': baseline_comparisons,
        'currentVoiceProvenance': {'path': str(production_provenance.relative_to(D)),
                                  'sha256': sha(production_provenance),
                                  'freshSourceAudits': {p: sha(D / p) for p in ['qa-voice.json', 'qa-voice-takes.json']},
                                  'rawSourceReuseLedger': {'path': 'voice/reused-source-baseline.json',
                                                          'sha256': sha(D / 'voice/reused-source-baseline.json')},
                                  'note': '17 raw/48k/request sources reused and 3 selected takes newly generated. Current full-track audit and encoded numerical checks are fresh; old full-WAV/normalized-PCM identity is not assumed.'},
        'limitations': ['Every extracted image still requires actual visual inspection.',
                        'No ASR, semantic audio listening, full human listening or real-time full-film watching is performed.',
                        'Loudness, delay, drift and source waveform checks are separate numerical audio QA.',
                        'Browser playback and native VTT boundaries are separate website checks.']}
    save(D / 'qa-video-independent-data.json', report)
    print(json.dumps({'status': report['status'], 'mediaSHA256': media_sha, 'frames': len(pts),
                      'actualImages': len(images), 'AACPackets': len(final_packets)}))


if __name__ == '__main__':
    main()
