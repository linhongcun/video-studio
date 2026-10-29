#!/usr/bin/env python3
"""Bind already-extracted final PNGs to actual movies; create QA contact sheets."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json

ROOT=next(parent for parent in Path(__file__).resolve().parents if (parent/'.git').exists())
OUT=ROOT/'work/peak-video-style/independent'
ARCHIVE=ROOT/'docs/archive/2026-10/peak-video-style'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows={}
for slug in ('rate-limit','idempotency','circuit-breaker','degradation'):
    revision=ROOT/f'episodes-codex/{slug}/revisions/peak-style'
    result=read(revision/'render-result.json')
    receipt=read(revision/'reference-appendix.json')
    media=read(revision/'reference-appendix-media-check.json')
    color=read(revision/'color-encoding-check.json')
    extraction=read(ARCHIVE/f'final/{slug}/final-media-check.json')
    movie=revision/'video.mp4'
    movie_sha=sha(movie)
    assert movie_sha==result['sha256']==receipt['outputSHA256']==media['outputSHA256']==extraction['sha256']
    assert sha(revision/'source-sha256.json')==result['newProductionManifestSHA256']
    assert media['passed'] and all(media[k] for k in ('bodyDecodedFramesAndTimestampsEqual','outputVideoTimelineContinuous','audioPacketsAndTimingEqual'))
    assert color['passed'] and color['allOriginalPublishedPresentationTimesEqual']
    samples=extraction['samples']
    for s in samples:assert sha(ROOT/s['file'])==s['sha256']
    for start in range(0,len(samples),6):
        batch=samples[start:start+6]
        sheet=Image.new('RGB',(1920,584*((len(batch)+1)//2)),'#1d1d1d');draw=ImageDraw.Draw(sheet)
        for j,s in enumerate(batch):
            p=ROOT/s['file'];im=Image.open(p).convert('RGB');im.thumbnail((960,540))
            x=(j%2)*960;y=(j//2)*584
            sheet.paste(im,(x,y+38));draw.text((x+15,y+10),f'{slug}: final frame {s["frame"]} / {s["frame"]/30:.3f}s',fill='white')
        sheet.save(OUT/f'final-{slug}-{start//6+1}.jpg',quality=95)
    figure_frame=extraction['article']['figureFrame']
    figure_sample=next(s for s in samples if s['frame']==figure_frame)
    rows[slug]={'status':'media-provenance-pass-awaiting-visual-review','videoSHA256':movie_sha,'manifestSHA256':result['newProductionManifestSHA256'],
        'frames':result['frames'],'bodyFrames':result['bodyFrames'],'referenceFrames':result['frames']-result['bodyFrames'],
        'samples':samples,'figureSeconds':extraction['article']['figureSeconds'],'figureFrame':figure_frame,'figureSample':figure_sample,
        'completeBaselineAudioReusedEvidence':result['baselineAudioPreserved'],
        'referenceAppendixCheckSHA256':sha(revision/'reference-appendix-media-check.json'),
        'colorEncodingCheckSHA256':sha(revision/'color-encoding-check.json'),
        'sampledBackgroundRGB':list(Image.open(ROOT/figure_sample['file']).convert('RGB').getpixel((40,300)))}
report={'schemaVersion':1,'status':'media-provenance-pass-awaiting-visual-review','scope':'Complete SHA binding of actual movies, existing complete producer audio/append/PTS checks and already-extracted PNGs. No redundant full decode or new listening is claimed. Contact sheets still require actual image viewing.','sampleCount':sum(len(v['samples']) for v in rows.values()),'episodes':rows}
(OUT/'final-media-bindings.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':report['status'],'sampleCount':report['sampleCount'],'episodes':{k:{'frames':v['frames'],'samples':len(v['samples']),'figureFrame':v['figureFrame']} for k,v in rows.items()}},indent=2))
