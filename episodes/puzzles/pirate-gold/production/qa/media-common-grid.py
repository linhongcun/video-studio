#!/usr/bin/env python3
"""Resume only actual-frame extraction/comparison after preserved PNG QA failure."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,re
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parents[1]
ROOT=next(p for p in D.parents if (p/'AGENTS.md').is_file())
spec=importlib.util.spec_from_file_location('p09_media_qa_tools',D/'qa/media-independent.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha,read,run=m.sha,m.read,m.run
EXPECTED_MANIFEST=m.EXPECTED_MANIFEST

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-name',default='media-common-grid-v2')
    args=parser.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9_-]+',args.out_name)
    source=D/'video.mp4';body=D/'remotion/out/body.mp4';manifest=D/'source-sha256.json'
    assert sha(manifest)==EXPECTED_MANIFEST
    frozen=read(manifest);frozen_paths={(D/name).resolve():value for name,value in frozen.items()}
    assert all(sha(path)==digest for path,digest in frozen_paths.items())
    report_file=D/'qa'/f'{args.out_name}.json';report=read(D/'qa/media-independent-v1-metrics-checkpoint.json')
    assert not report_file.exists(), 'Preserve an earlier common-grid result'
    assert report['videoSHA256']==sha(source)=='3b41d2bb007fa235a48357a272c2e22f8b5cee9d5efd4eb19e5d3a106e0d310d'
    assert report['bodySHA256']==sha(body)
    assert report['timeline']['everyDecodedFramePTSExact'] and report['timeline']['all4951DecodedFramesLimitedBT709']
    assert report['fullDecode']['passed'] and report['audioPreservation']['bodyAndFinalDecodedPCMEqual']
    assert report['independentLoudness']['pass'] and report['voiceSource']['all28UnmixedAACSentenceCorrelationsAbove098']
    checkpoint=D/'qa/media-independent-v1-metrics-checkpoint.json'
    report['metricsReusedFromCheckpointSHA256']=sha(checkpoint)
    report['imageStageResumedAtUTC']=datetime.now(timezone.utc).isoformat()
    report['supersededImageComparison']='qa/media-independent-v1.json'
    report['imageStageCorrection']='Decode all selected frames at full1920x1080 through explicit limited709 to full-range GBR, then pack RGB and apply exactly the same Pillow Lanczos960x540 resampler to actual and preview PNGs. The original fixed bounds and media are unchanged.'
    report['rgbDecoder']='zscale=matrixin=709:rangein=limited:matrix=gbr:range=full,format=gbrp,format=rgb24'
    report['imageAttemptFailures']=['qa/media-independent-v1-attempt1-failure.json','qa/media-independent-v1-attempt2-failure.json']
    def save():report_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    out=D/'qa'/args.out_name;out.mkdir();frames=4801;total=4951;board=read(D/'storyboard.json')
    previews=[read(D/'qa/preflight-v3.json'),read(D/'qa/preflight-v3-navigation.json')]
    samples={}
    for preview in previews:
        assert preview['pass'] and preview['visualReviewed'] and preview['props']['hideSubtitles']
        assert preview['sourceHashes']['remotion/src/Main.tsx']==sha(D/'remotion/src/Main.tsx')
        for name,expected in preview['sourceHashes'].items():
            path=(D/name).resolve()
            if path in frozen_paths:
                assert expected==frozen_paths[path],f'Preview did not use the same final frozen production source: {name}'
        for item in preview['samples']:
            image=D/item['file'];assert sha(image)==item['sha256']
            samples[item['frame']]=item
    frame_numbers=sorted(set(samples)|{frames-1,frames,frames+1,frames+75,total-1})
    image_dir=out/'decoded';image_dir.mkdir(exist_ok=True)
    assert not list(image_dir.glob('*.png')), 'Preserve previous extraction outputs before another image attempt'
    images=[];batches=[]
    for batch_number,start_index in enumerate(range(0,len(frame_numbers),40)):
        selected=frame_numbers[start_index:start_index+40]
        terms=['eq(n'+chr(92)+f',{i})' for i in selected]
        # Bound expression size and depth without changing selected frames.
        while len(terms)>1:
            terms=[('('+terms[i]+'+'+terms[i+1]+')') if i+1<len(terms) else terms[i] for i in range(0,len(terms),2)]
        prefix=f'batch-{batch_number:02d}-'
        run(['ffmpeg','-v','error','-threads','2','-filter_threads','1','-i',source,'-vf',
            f'select={terms[0]},zscale=matrixin=709:rangein=limited:matrix=gbr:range=full,format=gbrp,format=rgb24',
            '-fps_mode','passthrough','-threads','1',image_dir/(prefix+'%04d.png')])
        produced=sorted(image_dir.glob(prefix+'*.png'))
        assert len(produced)==len(selected)
        images.extend(produced)
        batches.append({'batch':batch_number,'frames':selected,'images':len(produced)})
        print(f'Extracted image batch {batch_number+1}: {len(produced)} exact frames.',flush=True)
    assert len(images)==len(frame_numbers) and len(set(frame_numbers))==len(frame_numbers)
    report['imageExtractionBatches']=batches
    report['imageExtractionFrameSetHasNoDropsOrDuplicates']=True
    actual={frame:image for frame,image in zip(frame_numbers,images)}
    differences=[]
    for frame,item in sorted(samples.items()):
        expected=np.asarray(Image.open(D/item['file']).convert('RGB').resize((960,540),Image.Resampling.LANCZOS),dtype=np.float32)
        measured=np.asarray(Image.open(actual[frame]).convert('RGB').resize((960,540),Image.Resampling.LANCZOS),dtype=np.float32)
        diff=np.abs(measured-expected)
        # Subtitle box begins at original y=931. Mask every pixel from y=920,
        # leaving a safety margin. Mechanism ROI is original x100..1820,y250..920.
        whole=diff[:460];core=diff[125:460,50:910]
        mae=float(core.mean());outside=float((core.max(axis=2)>30).mean())
        tiles=[core[y:y+112,x:x+144].mean() for y in range(0,335,112) for x in range(0,860,144)]
        max_tile=float(max(tiles));good=float(whole.mean())<=3 and mae<=3 and outside<=.015 and max_tile<=8
        differences.append({'frame':frame,'shot':item['shot'],'preview':item['file'],'decoded':str(actual[frame].relative_to(D)),
            'meanAbsoluteErrorAboveSubtitleMask':float(whole.mean()),'coreMeanAbsoluteError':mae,
            'corePixelsWithMaxChannelErrorOver30Fraction':outside,'maximumCoreTileMAE':max_tile,'withinFixedBounds':bool(good)})
    report['sameFramePreviewComparison']={'source':'Actual independent no-subtitles PNGs from preflight-v3 and navigation; same frozen Main source',
        'decodedFullResolution':[1920,1080],'sameResampler':'Pillow Lanczos on both full-resolution RGB images','grid':[960,540],'maskOriginalYAtOrBelow':920,'coreOriginalXYXY':[100,250,1820,920],
        'bounds':{'meanAbsoluteErrorMax':3,'coreMeanAbsoluteErrorMax':3,'fractionMaxChannelErrorOver30Max':.015,'maximumTileMAEMax':8},
        'frames':len(differences),'passed':all(r['withinFixedBounds'] for r in differences),'rows':differences,
        'scope':'Bounded lossy/color-conversion comparison supports picture/timing consistency; it is not a semantic correctness test.'}
    cards=[np.asarray(Image.open(actual[i]).convert('RGB'),dtype=np.float32) for i in [frames,frames+75,total-1]]
    static_diffs=[float(np.abs(cards[0]-other).mean()) for other in cards[1:]]
    report['referencePage']['sampledStaticPageMAE']=static_diffs
    report['referencePage']['sampledStaticPageWithin1']=all(v<=1 for v in static_diffs)
    assert report['referencePage']['sampledStaticPageWithin1']
    shots=[s for scene in board['scenes'] for s in scene['shots']]
    sheets=[]
    def sheet(name,selected):
        canvas=Image.new('RGB',(1920,575*((len(selected)+1)//2)),(23,19,38));draw=ImageDraw.Draw(canvas)
        for index,frame in enumerate(selected):
            x=(index%2)*960;y=(index//2)*575;canvas.paste(Image.open(actual[frame]).convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(x,y+35))
            draw.text((x+12,y+9),f'{name} | frame {frame} | {frame/30:.3f}s',fill=(244,238,249))
        target=out/f'{name}.jpg';canvas.save(target,quality=94);sheets.append(str(target.relative_to(D)))
    for shot in shots:
        if int(shot['id']) not in [5,7,9,11,12,13,14]:continue
        available=sorted(f for f,item in samples.items() if item['shot']==shot['id'])
        targets=[shot['from'],shot['from']+shot['durationInFrames']*.4,shot['from']+shot['durationInFrames']*.7,shot['from']+shot['durationInFrames']-1]
        selected=list(dict.fromkeys(min(available,key=lambda f:abs(f-target)) for target in targets))
        sheet(f'shot-{shot["id"]}',selected)
    sheet('body-reference-boundary',[frames-1,frames,frames+75,total-1])
    report['actualDecodeSheetsForVisualReview']=sheets
    report['actualFrameMap']={str(frame):str(path.relative_to(D)) for frame,path in actual.items()}
    report['status']='automatic-checks-passed-awaiting-visual-review' if report['sameFramePreviewComparison']['passed'] else 'same-frame-comparison-flags-require-review'
    assert sha(manifest)==EXPECTED_MANIFEST and all(sha((D/name).resolve())==value for name,value in frozen.items())
    report['frozenInputsUnchangedBeforeAndAfter']=True
    save()
    print(json.dumps({'status':report['status'],'frames':total,'comparisons':len(differences),
        'comparisonFlags':[r['frame'] for r in differences if not r['withinFixedBounds']],
        'maximumCoreMAE':max(r['coreMeanAbsoluteError'] for r in differences),
        'loudness':report['independentLoudness'],'report':str(report_file.relative_to(ROOT))},ensure_ascii=False))


if __name__=='__main__':main()
