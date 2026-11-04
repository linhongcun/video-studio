#!/usr/bin/env python3
"""Audit actual P06 final media; never renders or changes production inputs."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw
import soundfile as sf

D = Path(__file__).resolve().parents[1]
ROOT = next(p for p in D.parents if (p/'AGENTS.md').is_file())
EXPECTED_MANIFEST = None
COLOR = {'pix_fmt':'yuv420p','color_range':'tv','color_space':'bt709',
         'color_transfer':'bt709','color_primaries':'bt709'}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def digest_json(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def read(path):return json.loads(path.read_text())


def run(args):
    result = subprocess.run([str(a) for a in args],capture_output=True)
    if result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}): {args!r}\n'+result.stderr.decode(errors='replace')[-8000:])
    return result.stdout


def probe(path):
    return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',path]))


def video(info):return next(s for s in info['streams'] if s['codec_type']=='video')
def audio(info):return next(s for s in info['streams'] if s['codec_type']=='audio')


def packets(path,kind):
    data = json.loads(run(['ffprobe','-v','error','-select_streams',kind,
        '-show_packets','-show_data_hash','sha256','-show_entries',
        'packet=pts,dts,duration,data_hash','-of','json',path]))['packets']
    return [{key:p.get(key) for key in ['pts','dts','duration','data_hash']} for p in data]


def pcm_hash(path):
    return run(['ffmpeg','-v','error','-i',path,'-map','0:a:0','-c:a','pcm_s16le',
                '-f','hash','-hash','sha256','-']).decode().strip()


def frame_md5(path,frames):
    return [line for line in run(['ffmpeg','-v','error','-i',path,'-map','0:v:0',
        '-frames:v',frames,'-f','framemd5','-']).decode().splitlines() if line and not line.startswith('#')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-name',default='independent-media-v1')
    parser.add_argument('--manifest-sha256',required=True)
    parser.add_argument('--previews',default='independent-preflight-v1',help='Comma-separated real visually reviewed no-subtitles preview reports')
    args=parser.parse_args()
    assert re.fullmatch(r'[a-zA-Z0-9_-]+',args.out_name)
    global EXPECTED_MANIFEST
    EXPECTED_MANIFEST=args.manifest_sha256
    assert re.fullmatch(r'[a-f0-9]{64}',EXPECTED_MANIFEST)
    out=D/'qa'/args.out_name
    if out.exists() or (D/'qa'/f'{args.out_name}.json').exists():raise ValueError('Preserve an earlier audit; choose a fresh --out-name')
    source=D/'video.mp4';body=D/'remotion/out/body.mp4';manifest=D/'source-sha256.json'
    assert source.is_file() and body.is_file() and (D/'render-result.json').is_file(), 'Wait for final render and receipts'
    assert sha(manifest)==EXPECTED_MANIFEST
    frozen=read(manifest)
    assert all(sha((D/name).resolve())==value for name,value in frozen.items())
    frozen_paths={(D/name).resolve():value for name,value in frozen.items()}
    receipts=read(D/'reference-appendix.json');result=read(D/'render-result.json');refs=read(D/'references.json')
    board=read(D/'storyboard.json');words=read(D/'words.json');frames=words['durationFrames'];fps=Fraction(board['meta']['fps'])
    assert frames>0 and fps==30 and len(words['shots'])==15 and len(read(D/'voice/build.json')['sentences'])==30
    total=frames+150
    assert receipts['bodyFrames']==frames and receipts['finalVideoFrames']==total
    assert result['frames']==total and sha(source)==receipts['outputSHA256']==result['sha256']
    assert receipts['presentation']=='title-author' and receipts['inputs']['secondsPerPage']==5
    assert receipts['layout']['renderedFields']==['title','credit'] and receipts['layout']['quotesRendered'] is False
    assert receipts['layout']['maxItemsPerPage']==4 and len(receipts['appendix']['pages'])==1
    assert receipts['appendix']['durationInFrames']==150 and receipts['appendix']['from']==frames
    bibliography=[{'id':r['id'],'title':r['title'],'credit':r.get('author') or r['organization']} for r in refs['sources']]
    assert len(bibliography)==2 and receipts['bibliography']==bibliography
    assert 'twelve-balls production manifest' in receipts['bodyProductionInputs'] and 'pirate-gold' not in receipts['bodyProductionInputs']
    out.mkdir(parents=True)
    report={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'executor':'Codex independent final-media QA',
        'status':'running','manifestSHA256':EXPECTED_MANIFEST,'videoSHA256':sha(source),
        'bodySHA256':sha(body),'bodyFrames':frames,'finalFrames':total,'fps':30,
        'visualReviewed':False,'notPerformed':['word ASR','full realtime playback','full semantic listening','physical-phone test','site or online review']}
    report_file=D/'qa'/f'{args.out_name}.json'
    def save():report_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    save()
    info=probe(source);v=video(info);a=audio(info)
    assert (v['codec_name'],int(v['width']),int(v['height']),Fraction(v['r_frame_rate']),int(v['nb_frames']))==('h264',1920,1080,fps,total)
    assert a['codec_name']=='aac' and int(a['sample_rate'])==48000
    assert all(v.get(key)==value for key,value in COLOR.items())
    decoded=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_frames',
        '-show_entries','frame=pts,best_effort_timestamp,pkt_duration,color_range,color_space,color_transfer,color_primaries,pix_fmt',
        '-of','json',source]))['frames']
    timebase=Fraction(v['time_base']);assert len(decoded)==total
    for index,frame in enumerate(decoded):
        assert Fraction(frame['pts'])*timebase==Fraction(index,1)/fps,(index,frame)
        assert frame.get('best_effort_timestamp',frame['pts'])==frame['pts']
        assert all(frame.get(key)==value for key,value in COLOR.items()),(index,frame)
    vp=packets(source,'v:0');assert len(vp)==total
    assert sorted(Fraction(p['pts'])*timebase for p in vp)==[Fraction(i,1)/fps for i in range(total)]
    assert all(Fraction(p['duration'])*timebase==1/fps for p in vp)
    assert all(Fraction(b['dts']-a['dts'])*timebase==1/fps for a,b in zip(vp,vp[1:]))
    report['timeline']={'everyDecodedFramePTSExact':True,'everyVideoPacketPTSCoveredExactlyOnce':True,
        'everyVideoPacketDTSConsecutive':True,'allDecodedFramesLimitedBT709':True,
        'decodedFramesSHA256':digest_json(decoded),'videoPacketsSHA256':digest_json(vp),
        'boundaryPTS':[{'frame':i,'pts':decoded[i]['pts']} for i in [frames-1,frames,frames+1,total-1]],'timeBase':v['time_base']}
    run(['ffmpeg','-v','error','-i',source,'-f','null','-'])
    left,right=frame_md5(body,frames),frame_md5(source,frames)
    assert len(left)==len(right)==frames and left==right
    report['fullDecode']={'passed':True,'bodyDecodedFramesAndPTSIdentical':True,
        'allBodyFrameMD5RowsSHA256':digest_json(left)}
    left,right=packets(body,'a:0'),packets(source,'a:0');assert left==right
    pcm_left,pcm_right=pcm_hash(body),pcm_hash(source);assert pcm_left==pcm_right
    before,after=packets(D/'remotion/out/voice.mp4','a:0'),packets(D/'remotion/out/voice-bt709.mp4','a:0');assert before==after
    report['audioPreservation']={'bodyAndFinalAACPacketsAndPTSDTSDurationEqual':True,
        'aacPacketCount':len(left),'aacPacketSequenceSHA256':digest_json(left),
        'bodyAndFinalDecodedPCMEqual':True,'decodedPCMHash':pcm_left,
        'colorNormalizationAACPacketsPreserved':True}
    loud=subprocess.run(['ffmpeg','-hide_banner','-i',str(source),'-map','0:a:0',
        '-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,check=True)
    text=loud.stderr.decode();loudness=json.loads(text[text.rfind('{'):text.rfind('}')+1])
    report['independentLoudness']={'inputLUFS':float(loudness['input_i']),'inputTruePeakDBTP':float(loudness['input_tp']),
        'pass':abs(float(loudness['input_i'])+16)<=.3 and float(loudness['input_tp'])<=-2.0}
    assert report['independentLoudness']['pass'],loudness
    original,sr=sf.read(D/'voice.wav');assert sr==48000
    rendered=np.frombuffer(run(['ffmpeg','-v','error','-i',D/'remotion/out/voice.mp4','-map','0:a:0','-ar','48000','-ac','1','-f','f32le','-']),dtype='<f4')
    builds=read(D/'voice/build.json');correlations=[]
    for row in builds['sentences']:
        start,end=row['startSample'],row['endSample'];x=original[start:end].astype(np.float64);y=rendered[start:end].astype(np.float64)
        assert len(x)==len(y)
        correlation=float(np.dot(x,y)/np.sqrt(np.dot(x,x)*np.dot(y,y)))
        correlations.append({'id':row['id'],'correlation':correlation,'above098':correlation>=.98})
    report['voiceSource']={'selectedVoiceSHA256':sha(D/'voice.wav'),'renderedAACDecodedSampleCount':len(rendered),
        'all30UnmixedAACSentenceCorrelationsAbove098':all(r['above098'] for r in correlations),'sentences':correlations,
        'scope':'Correlation to frozen selected voice before music mixing; compression/source identity check, not speech recognition.'}
    assert report['voiceSource']['all30UnmixedAACSentenceCorrelationsAbove098']
    report['referencePage']={'bibliography':bibliography,'from':frames,'durationInFrames':150,
        'oneFiveSecondTitleAuthorPage':True,'noRenderedQuotations':True,'visualReviewPending':True}
    save();print('Full timeline, decode, AAC/PCM, loudness and source-voice checks passed.',flush=True)
    previews=[read(D/'qa'/f'{name}.json') for name in args.previews.split(',')]
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
            assert Image.open(image).size==(1920,1080), 'Same-frame QA requires full1920 preview input'
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
        # P06 subtitle box begins at original y=835. Exclude original y>=824.
        # Full-resolution RGB is independently reduced by the same Pillow operation.
        whole=diff[:412];core=diff[125:412,50:910]
        mae=float(core.mean());outside=float((core.max(axis=2)>30).mean())
        tiles=[core[y:y+112,x:x+144].mean() for y in range(0,287,112) for x in range(0,860,144)]
        max_tile=float(max(tiles));good=float(whole.mean())<=3 and mae<=3 and outside<=.015 and max_tile<=8
        differences.append({'frame':frame,'shot':item['shot'],'preview':item['file'],'decoded':str(actual[frame].relative_to(D)),
            'meanAbsoluteErrorAboveSubtitleMask':float(whole.mean()),'coreMeanAbsoluteError':mae,
            'corePixelsWithMaxChannelErrorOver30Fraction':outside,'maximumCoreTileMAE':max_tile,'withinFixedBounds':bool(good)})
    report['sameFramePreviewComparison']={'source':'Actual independently rendered P06 no-subtitles PNGs; same frozen Main source',
        'decodedFullResolution':[1920,1080],'sameResampler':'Pillow Lanczos on both full-resolution RGB images','rgbDecoder':'zscale limited709 to full-range GBR then RGB24','grid':[960,540],'maskOriginalYAtOrBelow':824,'coreOriginalXYXY':[100,250,1820,824],
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
        if int(shot['id']) not in range(1,16):continue
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


if __name__=='__main__':
    name=next((sys.argv[i+1] for i,v in enumerate(sys.argv[:-1]) if v=='--out-name'),'independent-media-v1')
    previous=(D/'qa'/f'{name}.json').exists()
    try:main()
    except Exception as error:
        if not previous and re.fullmatch(r'[a-zA-Z0-9_-]+',name):
            target=D/'qa'/f'{name}.json'
            failure=read(target) if target.exists() else {'executor':'Codex independent final-media QA'}
            failure.update(status='failed',passed=False,errorType=type(error).__name__,error=str(error),failedAtUTC=datetime.now(timezone.utc).isoformat())
            target.write_text(json.dumps(failure,ensure_ascii=False,indent=2)+'\n')
        raise
