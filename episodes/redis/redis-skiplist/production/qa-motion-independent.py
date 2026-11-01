#!/usr/bin/env python3
"""Audit actual continuous QA clips and sampled actor phase witnesses.

No production scene/model algorithm import. Visual viewing remains a separate
record and cannot be inferred from this script's numerical result.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, subprocess
from PIL import Image, ImageChops, ImageStat

D = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    samples_path = D / 'remotion/out/preflight-final/samples.json'
    samples = json.loads(samples_path.read_text())
    plan = json.loads((D / 'qa-preflight-plan.json').read_text())
    dom = json.loads((D / 'qa-dom-independent.json').read_text())
    model = json.loads((D / 'model.json').read_text())
    assert samples['status'] == 'completed' and dom['status'] == 'passed'
    assert dom['samplesSHA256'] == sha(samples_path)
    assert samples['planSHA256'] == sha(D / 'qa-preflight-plan.json')
    audits = {a['frame']: a for a in samples['audits']}
    full_images = {s['frame']: s for s in samples['samples']}
    checks = Counter(); failures = []; rows = []
    def test(value, name, detail=None):
        checks[name] += 1
        if not value: failures.append({'check': name, 'detail': detail})
    for e in plan['events']:
        typ, op = e['visualType'], e['operation']
        moving = e['label'] not in ['linear-stop', 'reject70', 'reject60']
        if typ == 'linear':
            event = model['linearSearch']['events'][op if e['sentence'] == 0 else 5]
            actor = ('advance', event['current'], event['candidate'], 0)
        elif typ == 'upper': actor = ('advance', 'head', 'n40', 1)
        elif typ == 'descend': actor = ('descend', 'n40', 'n40', 1)
        elif typ == 'locate': actor = ('advance', 'n40', 'n50', 0)
        else:
            w = model['insertion']['pointerWrites'][op + (2 if typ == 'splice-upper' else 0)]
            actor = ('write', w['owner'], w['newTarget'], w['level'])
        observations = []
        for phase in ['0', '0.18', '0.45', '0.72', '1']:
            frame = e['predictedPhases'][phase]; a = audits[frame]
            circles = [(m, g) for m in a['motions'] for g in m['geometry'] if g['tag'] == 'circle']
            expected_dot = moving and phase in ['0.18', '0.45']
            test(len(circles) == int(expected_dot), 'actual-dot-witness-at-declared-stage', (frame, e['label'], phase))
            if expected_dot and circles:
                m, point = circles[0]
                test((m['kind'], m['from'], m['to'], m['level']) == actor, 'actual-dot-has-correct-route-owner', frame)
                if phase == '0.45':
                    test(.45 <= m['progress'] <= .56, 'actual-mid-motion-is-between-endpoints', (frame, m['progress']))
            observations.append({'phase': phase, 'frame': frame, 'actualCircleCount': len(circles)})
        rows.append({**e, 'expectsMotion': moving, 'actualWitnesses': observations})
    clip_rows = []
    for clip in samples['clips']:
        test(sha(clip['file']) == clip['sha256'], 'actual-clip-identity', clip['name'])
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', clip['file']]))
        videos = [s for s in probe['streams'] if s['codec_type'] == 'video']
        test(len(videos) == 1 and not any(s['codec_type'] == 'audio' for s in probe['streams']), 'actual-clip-is-single-video-and-silent', clip['name'])
        v = videos[0]; expected = clip['range'][1] - clip['range'][0] + 1
        test(int(v['nb_frames']) == expected, 'all-critical-clip-frames-encoded', clip['name'])
        test((v['width'], v['height'], v['r_frame_rate']) == (960, 540, '30/1'), 'actual-clip-format', clip['name'])
        decoded = []
        for p in clip['decodedReviewFrames']:
            test(sha(p['file']) == p['sha256'], 'actual-decoded-image-identity', p['globalFrame'])
            test(p['subtitleBandForegroundPixels'] == 0, 'encoded-clip-subtitle-band-is-clear', p['globalFrame'])
            test(p['globalFrame'] in full_images, 'decoded-stage-has-independent-still-witness', p['globalFrame'])
            if p['globalFrame'] not in full_images: continue
            actual = Image.open(p['file']).convert('RGB')
            reference = Image.open(full_images[p['globalFrame']]['file']).convert('RGB').resize((960, 540), Image.Resampling.LANCZOS)
            # Compare the actual graph area (all ports, shafts and bypass curves).
            # Text at 0.5 render scale rasterizes differently from a downsampled
            # full PNG; title/result text is inspected visually, not pixel-equal.
            # The original 3-unit threshold remains for this defined graph ROI.
            mae = sum(ImageStat.Stat(ImageChops.difference(actual.crop((35, 155, 890, 390)), reference.crop((35, 155, 890, 390)))).mean) / 3
            test(mae < 3, 'encoded-diagram-agrees-with-same-frame-real-still', (p['globalFrame'], mae))
            decoded.append({'globalFrame': p['globalFrame'], 'sha256': p['sha256'], 'diagramROIAt960x540': [35,155,890,390], 'diagramPixelMeanAbsoluteDifference': mae})
        clip_rows.append({'name': clip['name'], 'sha256': clip['sha256'], 'range': clip['range'], 'actualFrames': int(v['nb_frames']), 'actualDurationSeconds': float(probe['format']['duration']), 'decodedStages': decoded})
    out = {'status': 'numerically-passed-awaiting-recorded-visual-review' if not failures else 'failed', 'checkedAtUTC': datetime.now(timezone.utc).isoformat(), 'scope': 'Actual encoded silent no-subtitle critical clips, actual decoded stage PNGs, and fifteen DOM actor phase witnesses.', 'checkerSHA256': sha(__file__), 'samplesSHA256': sha(samples_path), 'domReportSHA256': sha(D / 'qa-dom-independent.json'), 'assertionsExecuted': sum(checks.values()), 'assertionsByCategory': dict(checks), 'operationCount': len(rows), 'movingOperations': sum(r['expectsMotion'] for r in rows), 'blockedOperations': sum(not r['expectsMotion'] for r in rows), 'operations': rows, 'clips': clip_rows, 'failures': failures, 'limitations': ['Numerical checks do not prove a human watched the clips or understood the voice.', 'The two clips cover only the critical search/insertion interval; no final encoded film conclusion.']}
    (D / 'qa-motion-independent.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': out['status'], 'operations': len(rows), 'assertions': sum(checks.values()), 'failures': len(failures)}))
    if failures: raise SystemExit(1)
if __name__ == '__main__': main()
