#!/usr/bin/env python3
"""Compare preserved and corrected Figure JPEG interiors to exact final PNGs."""
from pathlib import Path
from PIL import Image
import numpy as np
import hashlib,json
ROOT=next(parent for parent in Path(__file__).resolve().parents if (parent/'.git').exists())
OUT=ROOT/'work/peak-video-style/independent'
ARCHIVE=ROOT/'docs/archive/2026-10/peak-video-style'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
bindings=read(OUT/'final-media-bindings.json')
correction=read(ARCHIVE/'figure-export-correction.json')
rows={}
for slug,item in bindings['episodes'].items():
    png=ROOT/item['figureSample']['file']
    old=ARCHIVE/f'independent/before-jpeg-color-correction/figure-{slug}.jpg'
    current=ROOT/f'episodes/{slug}/article/01.jpg'
    record=next(x for x in correction['reports'] if x['slug']==slug)
    assert sha(png)==record['referencePNGSHA256']
    assert sha(old)==record['beforeSHA256']
    assert sha(current)==record['correctedSHA256']
    a=np.asarray(Image.open(png).convert('RGB')).astype(int)
    b=np.asarray(Image.open(old).convert('RGB')).astype(int)
    c=np.asarray(Image.open(current).convert('RGB')).astype(int)
    # Erode by one pixel so JPEG ringing/antialiased letter edges do not become
    # a substitute for the actual flat cyan palette interiors.
    mask=(a[:,:,0]>85)&(a[:,:,0]<115)&(a[:,:,1]>210)&(a[:,:,1]<240)&(a[:,:,2]>210)&(a[:,:,2]<240)
    interior=mask.copy()
    for dy in (-1,0,1):
        for dx in (-1,0,1):interior &= np.roll(np.roll(mask,dy,axis=0),dx,axis=1)
    old_delta=np.median((b-a)[interior],axis=0)
    corrected_delta=np.median((c-a)[interior],axis=0)
    old_mae=float(np.abs(b-a).mean());corrected_mae=float(np.abs(c-a).mean())
    assert interior.sum()>7000 and np.abs(corrected_delta).max()<=1 and corrected_mae<old_mae
    rows[slug]={'status':'pass','flatCyanInteriorPixels':int(interior.sum()),'formalPNGSHA256':sha(png),'beforeJPEGSHA256':sha(old),'correctedJPEGSHA256':sha(current),
        'formalPNGMedianRGB':np.median(a[interior],axis=0).tolist(),
        'beforeJPEGMedianRGB':np.median(b[interior],axis=0).tolist(),
        'correctedJPEGMedianRGB':np.median(c[interior],axis=0).tolist(),
        'beforeMedianJPEGMinusPNG':old_delta.tolist(),'correctedMedianJPEGMinusPNG':corrected_delta.tolist(),
        'beforeWholeImageMeanAbsoluteRGBError':old_mae,'correctedWholeImageMeanAbsoluteRGBError':corrected_mae}
report={'schemaVersion':1,'status':'pass','actualFourCorrectedJPEGsViewedWithViewImage':True,'rootCorrectionReceiptSHA256':sha(ARCHIVE/'figure-export-correction.json'),'scope':'Independent pixel calculations and complete JPEG/PNG receipt identity checks; four corrected installed JPEGs also actually viewed. Original Figure images and premature initial visual pass retained under before-jpeg-color-correction.','episodes':rows}
(OUT/'figure-color-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'pass','medianCorrectedDeltas':{k:v['correctedMedianJPEGMinusPNG'] for k,v in rows.items()}},indent=2))
