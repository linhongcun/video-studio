#!/usr/bin/env python3
"""Sample the final encoded MP4 without changing production inputs.

python3 scripts/check_encoded_visual.py --preflight qa/preflight/qa-report.json
The report intentionally awaits actual visual review; numeric image difference
is evidence of correspondence, not an automatic visual/content pass.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

EP = Path(__file__).resolve().parent.parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def local(path: str, base=EP) -> Path:
    p = Path(path)
    return p if p.is_absolute() else base / p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--video', default='video.mp4')
    ap.add_argument('--preflight', default='qa/preflight/qa-report.json')
    ap.add_argument('--out', default='qa/encoded-visual')
    ap.add_argument('--supplement', help='Passed repaired-frame report;its samples replace primary samples by global frame')
    ap.add_argument('--closure', help='Visual QA closure report documenting bounded reuse and repaired sample applicability')
    ap.add_argument('--frames', help='Additional comma-separated global frame indices')
    args = ap.parse_args()
    video, preflight, out = local(args.video), local(args.preflight), local(args.out)
    if not video.is_file():
        ap.error(f'Final encoded video does not exist: {video}')
    if not preflight.is_file():
        ap.error(f'Final preflight report does not exist: {preflight}')
    report_before = sha(preflight)
    qa = read(preflight)
    provenance = [dict(role='primary', file=str(preflight), sha256=report_before,
                       originalStatus=qa.get('status'), sampleCount=len(qa.get('samples', [])))]
    for sample in qa.get('samples', []):
        sample['_report'] = str(preflight)
    report_inputs = {preflight: report_before}
    if args.supplement:
        supplement = local(args.supplement)
        if not supplement.is_file() or not args.closure:
            ap.error('--supplement requires existing supplemental and --closure reports')
        repaired = read(supplement)
        if repaired.get('status') != 'passed':
            ap.error('Repaired-frame supplemental QA must have passed')
        closure_file = local(args.closure)
        if not closure_file.is_file():
            ap.error('Visual QA closure report does not exist')
        closure = read(closure_file) if closure_file.suffix == '.json' else None
        report_inputs[supplement], report_inputs[closure_file] = sha(supplement), sha(closure_file)
        provenance += [dict(role='repaired-supplement', file=str(supplement), sha256=sha(supplement),
                            originalStatus=repaired.get('status'), sampleCount=len(repaired.get('samples', []))),
                       dict(role='bounded-reuse-closure', file=str(closure_file), sha256=sha(closure_file),
                            reportedStatus=closure.get('status') if closure else 'See exact closure document')]
        merged = {item['frame']: item for item in qa.get('samples', [])}
        overridden = []
        for item in repaired.get('samples', []):
            if item['frame'] in merged:
                overridden.append(item['frame'])
            item['_report'] = str(supplement)
            merged[item['frame']] = item
        qa['samples'] = [merged[frame] for frame in sorted(merged)]
        windows = {(w['eventId'], w['globalStart'], w['globalEnd']): w
                   for w in qa.get('motionWindows', []) + repaired.get('motionWindows', [])}
        qa['motionWindows'] = list(windows.values())
        provenance.append(dict(role='merge-method', overwrittenFrames=overridden,
                               scope='Repaired samples replace same-frame primary PNGs;original primary failure is retained,not reclassified as passed;bounded reuse relies on visual QA closure'))
    elif qa.get('status') != 'passed':
        ap.error('Failed primary requires --supplement and --closure;its original failure cannot be silently reclassified')
    sb = read(EP / 'storyboard.json')
    receipt = read(EP / 'reference-appendix.json')
    video_sha = sha(video)
    if receipt.get('outputSHA256') != video_sha:
        ap.error('Final MP4 does not match reference-appendix receipt SHA')
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=width,height,nb_frames,r_frame_rate,color_space,color_range,color_transfer,color_primaries:format=duration',
        '-of', 'json', str(video)], text=True))
    stream = probe['streams'][0]
    total = int(stream['nb_frames'])
    if total != receipt['finalVideoFrames']:
        ap.error(f'Frame count differs: actual {total}, receipt {receipt["finalVideoFrames"]}')
    space = stream.get('color_space')
    matrix = {'bt709': 'bt709', 'bt470bg': 'bt601', 'smpte170m': 'bt601'}.get(space)
    if matrix is None:
        ap.error(f'No declared matrix mapping for actual MP4 color_space={space!r};inspect before decoding')
    color_range = {'pc': 'pc', 'tv': 'tv'}.get(stream.get('color_range'))
    if color_range is None:
        ap.error(f'No explicit color_range in actual MP4: {stream.get("color_range")!r};inspect before decoding')
    frame_probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
        '-show_entries', 'frame=best_effort_timestamp_time,color_space,color_range,color_transfer,color_primaries',
        '-of', 'json', str(video)], text=True))['frames']
    if len(frame_probe) != total:
        ap.error(f'Actual decoded frame records {len(frame_probe)} differ from nb_frames {total}')
    color_fields = ('color_space', 'color_range', 'color_transfer', 'color_primaries')
    def color_set(start, stop):
        return [dict(zip(color_fields, value)) for value in sorted({
            tuple(f.get(key, 'unspecified') for key in color_fields)
            for f in frame_probe[start:stop]})]
    appendix_start = receipt['appendix']['from']
    body_color, reference_color = color_set(0, appendix_start), color_set(appendix_start, total)
    color_consistency = dict(bodyFrames=appendix_start, referenceFrames=total-appendix_start,
                             decodedFrameRecords=len(frame_probe), bodyValues=body_color,
                             referenceValues=reference_color, sameParameters=body_color == reference_color)
    if not color_consistency['sameParameters']:
        ap.error('Actual decoded body/reference frame color parameters differ;inspect before sampling')
    shots = [s for scene in sb['scenes'] for s in scene['shots']]
    tags: dict[int, list[str]] = {}

    def add(frame, tag):
        fr = max(0, min(total - 1, int(frame)))
        if tag not in tags.setdefault(fr, []):
            tags[fr].append(tag)

    for shot in shots:
        body_end = shot['from'] + shot.get('codeCardFrom', shot['durationInFrames'])
        add((shot['from'] + body_end - 1) // 2, f'shot-{shot["id"]}-middle')
    for sample in qa.get('samples', []):
        add(sample['frame'], f'preflight-shot-{sample.get("shot", "?")}')
    motion_windows = []
    for window in qa.get('motionWindows', []):
        if window['kind'] not in ('append', 'swap-up', 'swap-down', 'replace-root', 'remove-root'):
            continue
        start, end = window['globalStart'], window['globalEnd']
        motion_windows.append(window)
        for name, fr in [('before', math.floor(start) - 1), ('middle', round((start + end) / 2)), ('after', math.ceil(end) + 1)]:
            add(fr, f'{window["kind"]}-event-{window["eventId"]}-{name}')
    python = sb['meta']['unvoicedEndCard']
    refs = receipt['appendix']
    for name, card in [('python', python), ('references', refs)]:
        start, duration = card['from'], card['durationInFrames']
        add(start - 1, f'{name}-previous-frame')
        for label, fr in [('first', start), ('middle', start + duration // 2), ('last', start + duration - 1)]:
            add(fr, f'{name}-{label}')
    if args.frames:
        for frame in args.frames.split(','):
            add(int(frame), 'extra')
    frames = sorted(tags)
    out.mkdir(parents=True, exist_ok=True)
    png_dir = out / 'frames'
    png_dir.mkdir(exist_ok=True)
    # Select actual decoded global frame numbers. No keyframe seek approximation.
    def balanced_sum(values):
        if len(values) == 1:
            return values[0]
        middle = len(values) // 2
        return '(' + balanced_sum(values[:middle]) + '+' + balanced_sum(values[middle:]) + ')'
    selector = balanced_sum([f'eq(n\\,{frame})' for frame in frames])
    vf = f'select={selector},scale=in_color_matrix={matrix}:out_color_matrix={matrix}:in_range={color_range}:out_range=pc,format=rgb24'
    command = ['ffmpeg', '-v', 'error', '-y', '-threads', '2', '-i', str(video),
               '-an', '-vf', vf, '-fps_mode', 'passthrough',
               '-start_number', '0', str(png_dir / 'selected-%06d.png')]
    subprocess.run(command, check=True)
    source_map = {s['frame']: s for s in qa.get('samples', [])}
    comparisons = []
    records = []
    for index, frame in enumerate(frames):
        src = png_dir / f'selected-{index:06d}.png'
        if not src.is_file():
            raise RuntimeError(f'No actual encoded PNG for selected frame {frame}')
        target = png_dir / f'frame-{frame:06d}.png'
        src.replace(target)
        shot = next((s for s in shots if s['from'] <= frame < s['from'] + s['durationInFrames']), None)
        record = dict(frame=frame, tags=tags[frame], file=str(target), sha256=sha(target),
                      shot=shot['id'] if shot else None)
        records.append(record)
        source = source_map.get(frame)
        if source:
            source_path = Path(source['file'])
            if not source_path.is_file():
                source_path = Path(source['_report']).parent / source_path.name
            if not source_path.is_file():
                record['preflightComparison'] = dict(status='missing-source-PNG', path=str(source_path))
                continue
            if sha(source_path) != source['sha256']:
                raise RuntimeError(f'Preflight PNG bytes differ at frame {frame}')
            actual = Image.open(target).convert('RGB')
            expected = Image.open(source_path).convert('RGB')
            actual = actual.resize(expected.size, Image.Resampling.LANCZOS)
            delta = np.asarray(actual, dtype=np.float32) - np.asarray(expected, dtype=np.float32)
            item = dict(frame=frame, source=str(source_path), sourceSHA256=sha(source_path),
                        sourceReport=source['_report'],
                        comparisonSize=list(expected.size), MAE=float(np.abs(delta).mean()),
                        RMSE=float(np.sqrt(np.square(delta).mean())),
                        sourceHideSubtitles=qa.get('inputProps', {}).get('hideSubtitles', False),
                        caveat='Lossy RGB decode using actual declared MP4 matrix/range,resized to preflight PNG size;metrics are evidence only,not a content or visibility pass')
            comparisons.append(item)
            record['preflightComparison'] = item
    groups = dict(
        shot_middles=[r for r in records if any('shot-' in t and t.endswith('-middle') for t in r['tags'])],
        motion=[r for r in records if any(t.startswith(('append-', 'swap-', 'replace-', 'remove-')) for t in r['tags'])],
        cards=[r for r in records if any(t.startswith(('python-', 'references-')) for t in r['tags'])],
    )
    font_file = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    font = ImageFont.truetype(str(font_file), 20) if font_file.is_file() else ImageFont.load_default()
    sheets = []
    for group_name, group in groups.items():
        for start in range(0, len(group), 8):
            batch = group[start:start + 8]
            sheet = Image.new('RGB', (1920, math.ceil(len(batch) / 2) * 574), '#111827')
            draw = ImageDraw.Draw(sheet)
            for i, r in enumerate(batch):
                x, y = (i % 2) * 960, (i // 2) * 574
                pic = Image.open(r['file']).convert('RGB').resize((960, 540), Image.Resampling.LANCZOS)
                sheet.paste(pic, (x, y + 34))
                label = f'frame {r["frame"]} | ' + ', '.join(r['tags'])
                draw.text((x + 8, y + 5), label[:108], fill='white', font=font)
            dest = out / f'{group_name}-{start // 8 + 1:02d}.jpg'
            sheet.save(dest, quality=94)
            sheets.append(dict(group=group_name, file=str(dest), frames=[r['frame'] for r in batch], sha256=sha(dest)))
    if sha(video) != video_sha or any(sha(path) != value for path, value in report_inputs.items()):
        raise RuntimeError('MP4 or a source/closure report changed during encoded sampling')
    numeric = dict(comparisonCount=len(comparisons),
                   meanMAE=sum(x['MAE'] for x in comparisons) / max(1, len(comparisons)),
                   maximumMAE=max((x['MAE'] for x in comparisons), default=None),
                   maximumRMSE=max((x['RMSE'] for x in comparisons), default=None))
    report = dict(schemaVersion=1, status='sampled-awaiting-actual-visual-review',
                  checkedAt=dt.datetime.now(dt.timezone.utc).isoformat(), executor='Codex research/encoded-review agent',
                  video=str(video), videoSHA256=video_sha, videoBytes=video.stat().st_size,
                  preflight=str(preflight), preflightSHA256=report_before,
                  preflightProvenance=provenance,
                  preflightInputProps=qa.get('inputProps'), probe=probe,
                  sourceReferencesSHA256=receipt['inputs']['referencesSHA256'],
                  decodeColor=dict(actualColorSpace=space, mappedMatrix=matrix, actualRange=color_range, outputRange='pc', filter=vf),
                  frameColorConsistency=color_consistency,
                  method='Decoded global select(n) frames;explicit actual-MP4 matrix/range to RGB;no production inputs changed',
                  sampledFrameCount=len(records), motionWindowCount=len(motion_windows),
                  motionWindows=motion_windows, frames=records, contactSheets=sheets,
                  imageDifference=numeric,
                  limitations=['Still triplets and contact sheets do not establish all-frame motion or full human listening',
                               'No threshold can substitute for actual visual examination',
                               'Source PNG and final decode may have expected lossy/color/resampling differences'])
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(videoSHA256=video_sha, sampledFrameCount=len(records), motionWindowCount=len(motion_windows),
                          contactSheets=len(sheets), imageDifference=numeric, report=str(out / 'report.json')), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
