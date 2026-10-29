from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib,json,subprocess,shutil,re,gzip

ROOT=Path.cwd().resolve()
W=ROOT/'work/peak-video-style'
A=ROOT/'docs/archive/2026-10/peak-video-style'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def frame(video,n,p):
    second,offset=divmod(n,30)
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(second),'-i',str(video),'-vf',f'select=eq(n\\,{offset})'+(',scale=in_range=tv:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt601,format=yuvj420p' if p.suffix=='.jpg' else ''),'-frames:v','1','-fps_mode','vfr',*(['-q:v','2']if p.suffix=='.jpg'else[]),str(p)],check=True)

reports=[]
for slug in ['rate-limit','idempotency','circuit-breaker','degradation']:
    src=ROOT/'episodes-codex'/slug
    rev=src/'revisions/peak-style'
    pub=ROOT/'episodes'/slug
    result=read(rev/'render-result.json')
    old=read(rev/'baseline-publication.json')
    receipt=read(rev/'reference-appendix.json')
    check=read(rev/'reference-appendix-media-check.json')
    color=read(rev/'color-encoding-check.json')
    video=rev/'video.mp4'
    assert result['visualRevision']=='peak-style-v1'
    assert sha(video)==result['sha256']==receipt['outputSHA256']==check['outputSHA256']
    assert check['passed'] and color['passed']
    assert all(check[k] for k in ['bodyDecodedFramesAndTimestampsEqual','outputVideoTimelineContinuous','audioPacketsAndTimingEqual'])
    assert color['allOriginalPublishedPresentationTimesEqual']
    assert result['frames']==old['publishedMetadata']['finalVideoFrames']
    assert result['bodyFrames']==old['publishedMetadata']['referenceAppendix']['from']
    assert result['frames']-result['bodyFrames']==150
    assert result['newProductionManifestSHA256']==sha(rev/'source-sha256.json')
    assert read(pub/'meta.json')==old['publishedMetadata']
    assert (pub/'article.mdx').read_bytes()==(rev/'article.mdx').read_bytes()
    sb=read(src/'storyboard.json')
    mid=[];t=0
    for scene in sb['scenes']:
        for shot in scene['shots']:
            mid.append(t+(shot['durationInFrames']+1)//2);t+=shot['durationInFrames']
    article=(pub/'article.mdx').read_text()
    match=re.search(r'<Figure\s+src="([^"]+)"[^>]*seekTo=\{([0-9.]+)\}',article,re.S)
    assert match,slug
    figure=pub/('article/'+match.group(1).rsplit('/',1)[-1])
    seek=float(match.group(2));figure_frame=round(seek*30)
    dest=A/'final'/slug;dest.mkdir(parents=True,exist_ok=True)
    frames=sorted(set([0,*mid,figure_frame,t-1,t,t+75,result['frames']-1]))
    samples=[]
    for n in frames:
        p=dest/f'frame-{n:06d}.png';frame(video,n,p)
        samples.append({'frame':n,'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
    previous_figure=hashlib.sha256(subprocess.check_output(['git','show',old['baselineCommit']+':'+str(figure.relative_to(ROOT))])).hexdigest()
    figure.parent.mkdir(parents=True,exist_ok=True);frame(video,figure_frame,figure)
    before_meta=sha(pub/'meta.json');meta=read(pub/'meta.json')
    meta.update(result['publicationMetadata'])
    meta['updatedAt']=datetime.fromisoformat(result['createdAtUTC']).astimezone(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    meta['burnedInCaptions']=True
    changed={k for k in set(meta)|set(old['publishedMetadata'])if meta.get(k)!=old['publishedMetadata'].get(k)}
    assert changed<={'updatedAt','burnedInCaptions'}|set(result['publicationMetadata'])
    write(pub/'meta.json',meta)
    for name in ['video.mp4','reference-appendix.json','reference-appendix-media-check.json','render-result.json']:
        shutil.copyfile(rev/name,pub/name);assert sha(pub/name)==sha(rev/name)
    report={'slug':slug,'status':'installed-media-verified','sha256':sha(video),'bytes':video.stat().st_size,'frames':result['frames'],'bodyFrames':t,'referenceFrames':150,'samples':samples,'completeBaselineAudio':result['baselineAudioPreserved'],'colorEncoding':result['colorEncoding'],'allOriginalPublishedPresentationTimesEqual':True,'normalizedBodyDecodedFramesAndPTSAllPreservedInAppend':True,'metadata':{'beforeSHA256':before_meta,'afterSHA256':sha(pub/'meta.json'),'changedFields':sorted(changed),'sourcePathPreserved':True,'applicationScenarioPreserved':True},'article':{'mdxBytesPreserved':True,'sha256':sha(pub/'article.mdx'),'figureSeconds':seek,'figureFrame':figure_frame,'figureBeforeSHA256':previous_figure,'figureSHA256':sha(figure)},'stillsMethod':'Integer-second input seek plus exact relative CFR frame select, previously verified; no extra full decode solely for screenshots.'}
    write(dest/'final-media-check.json',report);reports.append(report)
    print(json.dumps({'slug':slug,'status':report['status'],'sha256':report['sha256'],'samples':len(samples)}),flush=True)
write(A/'final-media-summary.json',reports)
for name in [f'{stage}-{slug}' for stage in ['preflight','freeze','render'] for slug in ['rate-limit','idempotency','circuit-breaker','degradation']]:
    p=W/(name+'.log')
    if p.exists():(A/(name+'.log.gz')).write_bytes(gzip.compress(p.read_bytes(),mtime=0))
for slug in ['rate-limit','idempotency','circuit-breaker','degradation']:
    source=W/'preflight'/slug;dest=A/'preflight'/slug;dest.mkdir(parents=True,exist_ok=True)
    for p in source.iterdir():
        if p.suffix=='.png':shutil.copyfile(p,dest/p.name)
        elif p.suffix=='.json':(dest/(p.name+'.gz')).write_bytes(gzip.compress(p.read_bytes(),mtime=0))
