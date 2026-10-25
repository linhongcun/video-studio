#!/usr/bin/env python3
"""Read-only final-video audit for EA01.

Checks every decoded presentation timestamp, decodes the complete MP4, extracts
actual encoded PNGs, and compares representative frames to the frozen Remotion
source. Numeric checks do not recognize speech or judge teaching quality.
Actual image inspection is recorded separately in qa-video-independent.*.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess


D = Path(__file__).resolve().parent
ROOT = D.parents[1]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def run(command, **kwargs):
    return subprocess.run(command, check=True, text=True, capture_output=True, **kwargs)


def frozen_snapshot():
    manifest_path = D / 'source-sha256.json'
    assert manifest_path.is_file(), 'Final audit requires the production freeze manifest'
    expected = json.loads(manifest_path.read_text())
    actual = {relative: sha(D / relative) for relative in expected}
    assert actual == expected, 'Frozen production input has changed'
    return actual


def frame_plan(shots):
    """Use actual shot durations, including intermediate and completed states."""
    fractions = {
        '01': [0, .52, .97],
        '02': [.18, .56, .97],
        '03': [.12, .57, .97],
        '04': [.18, .62, .97],
        '05': [.12, .55, .97],
        '06': [.14, .54, .97],
        '07': [.10, .32, .57, .97],
        '08': [.12, .39, .63, .97],
        '09': [.12, .30, .56, .97],
        '10': [.08, .26, .50, .68, .97],
        '11': [.04, .23, .49, .97],
        '12': [.14, .47, .70, .97],
        '13': [.06, .29, .53, .76, .97],
        '14': [.04, .36, .48, .63, .97],
    }
    rows = []
    for shot in shots:
        sid = str(shot['id']).zfill(2)
        for fraction in fractions[sid]:
            local = min(shot['durationInFrames'] - 1,
                        round(shot['durationInFrames'] * fraction))
            rows.append({'shot': sid, 'visualType': shot['visualType'],
                         'frame': shot['from'] + local, 'local': local,
                         'fraction': fraction})
    return sorted({row['frame']: row for row in rows}.values(), key=lambda x: x['frame'])


REFERENCE_JS = r'''
import {bundle} from '@remotion/bundler';
import {openBrowser,renderStill,selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import webpack from 'webpack';
const cfg=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));
const inputProps={hideSubtitles:false,auditLayout:false};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,
 webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,
 '@storyboard':path.resolve('../storyboard.json'),'@covers':path.resolve('../covers.json')},
 modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),
 new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browserExecutable='/usr/bin/chromium';
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const selected=await selectComposition({serveUrl,id:'Main',browserExecutable,
  puppeteerInstance:browser,inputProps});
 const composition={...selected,props:{...selected.props,...inputProps}};
 for(const item of cfg){
  await renderStill({composition,serveUrl,frame:item.frame,output:item.referenceFile,
   browserExecutable,puppeteerInstance:browser,inputProps,imageFormat:'png',scale:1});
 }
}finally{await browser.close({silent:true});}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--media', type=Path, default=D / 'video.mp4')
    parser.add_argument('--out', type=Path, default=D / 'remotion/out/final-independent')
    parser.add_argument('--skip-source-comparison', action='store_true')
    args = parser.parse_args()
    media = args.media.resolve()
    assert media.is_file(), 'The actual final MP4 does not exist; no audit was run'
    before = frozen_snapshot()
    media_before = sha(media)
    sb = json.loads((D / 'storyboard.json').read_text())
    assert not sb['meta'].get('provisionalTiming') and not sb['meta'].get('pendingAudio')
    shots = [s for scene in sb['scenes'] for s in scene['shots']]
    duration_frames = sb['meta']['durationInFrames']
    fps = sb['meta']['fps']
    assert fps == 30
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                            '-of', 'json', str(media)]).stdout)
    videos = [s for s in probe['streams'] if s['codec_type'] == 'video']
    audios = [s for s in probe['streams'] if s['codec_type'] == 'audio']
    assert len(videos) == len(audios) == 1
    video, audio = videos[0], audios[0]
    assert (video['width'], video['height']) == (1920, 1080)
    assert video['codec_name'] == 'h264' and video['r_frame_rate'] == '30/1'
    assert audio['codec_name'] == 'aac' and int(audio['sample_rate']) == 48000
    if video.get('nb_frames'):
        assert int(video['nb_frames']) == duration_frames
    frame_info = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                 '-show_frames', '-show_entries',
                                 'frame=best_effort_timestamp_time', '-of', 'json',
                                 str(media)]).stdout)['frames']
    timestamps = [float(frame['best_effort_timestamp_time']) for frame in frame_info]
    assert len(timestamps) == duration_frames, (len(timestamps), duration_frames)
    deviations = [abs(timestamp - i / fps) for i, timestamp in enumerate(timestamps)]
    assert max(deviations) < 0.00001
    assert all(b > a for a, b in zip(timestamps, timestamps[1:]))
    assert abs(float(probe['format']['duration']) - duration_frames / fps) < .1
    run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(media), '-f', 'null', '-'])

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows = frame_plan(shots)
    selection = '+'.join(f'eq(n\\,{row["frame"]})' for row in rows)
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(media), '-vf', f'select={selection}',
         '-fps_mode', 'vfr', str(out / 'encoded-%03d.png')])
    for index, row in enumerate(rows, 1):
        original = out / f'encoded-{index:03d}.png'
        image = out / f'{row["shot"]}-global{row["frame"]:05d}-local{row["local"]:03d}.png'
        original.replace(image)
        row['file'] = str(image)
        row['sha256'] = sha(image)

    comparisons = []
    if not args.skip_source_comparison:
        # One completed representative for each shot. Actual visual review also
        # inspects intermediate encoded frames, independent of this numeric test.
        references = [max((r for r in rows if r['shot'] == str(s['id']).zfill(2)),
                          key=lambda x: x['frame']).copy() for s in shots]
        for row in references:
            row['referenceFile'] = str(out / f'source-global{row["frame"]:05d}.png')
        config = out / 'source-reference-plan.json'
        config.write_text(json.dumps(references, ensure_ascii=False, indent=2) + '\n')
        run(['node', '--input-type=module', '-e', REFERENCE_JS, str(config)],
            cwd=D / 'remotion')
        for row in references:
            result = run(['ffmpeg', '-v', 'info', '-i', row['file'], '-i', row['referenceFile'],
                          '-lavfi', 'ssim', '-f', 'null', '-'])
            found = re.findall(r'All:([0-9.]+)', result.stderr)
            assert found, result.stderr[-1000:]
            ssim = float(found[-1])
            assert ssim >= .97, (row['frame'], ssim)
            comparisons.append({'shot': row['shot'], 'frame': row['frame'],
                                'ssim': ssim, 'encodedFile': row['file'],
                                'encodedSHA256': row['sha256'],
                                'sourceFile': row['referenceFile'],
                                'sourceSHA256': sha(Path(row['referenceFile']))})

    assert frozen_snapshot() == before
    assert sha(media) == media_before, 'Final MP4 changed during the audit'
    report = {
        'status': 'computer-checks-passed-awaiting-independent-visual-review',
        'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
        'reviewer': 'hash_final_media',
        'media': {'file': str(media), 'sha256': media_before, 'bytes': media.stat().st_size,
                  'width': video['width'], 'height': video['height'], 'fps': fps,
                  'frames': len(timestamps), 'seconds': float(probe['format']['duration']),
                  'audioCodec': audio['codec_name'], 'audioSampleRate': int(audio['sample_rate'])},
        'pts': {'checkedEveryFrame': True, 'strictlyIncreasing': True,
                'maximumDeviationFromFrameIndexSeconds': max(deviations)},
        'fullDecodePassed': True, 'extractedEncodedFrames': rows,
        'frozenSameFrameComparisons': comparisons,
        'productionInputCount': len(before),
        'freezeManifestSHA256': sha(D / 'source-sha256.json'),
        'voiceSemanticListeningPerformed': False, 'ASRPerformed': False,
        'fullHumanViewingPerformed': False,
        'limitations': [
            'Timestamp continuity and source similarity cannot prove teaching quality.',
            'Extracted PNGs need actual independent inspection before visual acceptance.',
            'This checker does not identify words or listen to pronunciation.',
        ],
    }
    destination = D / 'qa-video-metrics.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'frames': len(timestamps),
                      'extractedFrames': len(rows), 'sourceComparisons': len(comparisons),
                      'minimumSSIM': min((c['ssim'] for c in comparisons), default=None),
                      'report': str(destination)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
