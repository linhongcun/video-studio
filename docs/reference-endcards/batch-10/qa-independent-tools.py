"""Independent batch10 read-only checks and short-tail PNG collection; no product writes."""
from pathlib import Path
import argparse, datetime, hashlib, json, math, re, subprocess
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).resolve().parent
BASE='4213a233c4c242b04453b8c1215031dc421c2398'
PUBLICATION_BASE='486f042a01a9e69aa10eb390f75b51c03a3f2a47'
SLUGS=['container-most-water','longest-substring','number-of-islands','permutations','trapping-rain-water']
REPORT=BATCH/'qa-independent.json'
CACHE={}

def require(value, message):
    if not value: raise AssertionError(message)

def read(p): return json.loads(p.read_text())
def digest(p):
    p=p.resolve()
    if p not in CACHE:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        CACHE[p]=h.hexdigest()
    return CACHE[p]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(path, commit=BASE):return subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=ROOT)
def relative(p):return str(p.relative_to(ROOT))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(report): REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

NOTES={
 'container-most-water': '24日实际中文官方题面原题/机构，1项真实核心来源，不重复中英文题面凑数。英文交叉/2018旧答复/未读editorial不入片尾。面积与短边整组排除、O(n)为独立推导；旧执行不是本轮重跑。',
 'longest-substring': '24日题面、集合语义和平均复杂度实读；26日仅本地复用第9批固定CPython原响应核全题/PSF。集合无序与平均常数/碰撞最坏边界保留；原Time Complexity简称已据真正H1补全，未虚构本片editorial访问结果。',
 'number-of-islands': '25日官方题面、Using Lists as Stacks与集合语义实读。26日固定官方3.13 RST仅补Set Types完整章节原题；未把新raw SHA充作25日响应。四邻连通、显式栈/去重有对应，DFS证明/访问顺序为独立工作，不声称读过editorial。',
 'permutations': '25日source-access真实记录的46. Permutations完整原题与Built-in Types。26日本地复用官方固定原响应补题名/PSF，不冒称fresh GET或重读技术。copy浅副本与pop末项对应，回溯/唯一性/输出复杂度为本片独立工作；整数元素边界明确。',
 'trapping-rain-water': 'SELF-SOURCE：本代理整理，须另人交叉。25日官方题面原读取记录；26日新GET固定functions/copyright并实际读len/max/min，为新增技术补核，绝不追记成25日已读。原题functions小写；水位/前后缀/复杂度为独立工作，不声称读过editorial。'
}

def precheck():
    entry=read(BATCH/'production-entry-check.json'); rows={x['slug']:x for x in entry['episodes']}
    report={'schemaVersion':1,'task':'batch10-independent-source-input-and-final-tail-review',
       'baselineCommit':BASE,'publicationBaselineCommit':PUBLICATION_BASE,'executor':'Codex reference_gate',
       'checkedAtUTC':now(),'status':'pending-final-media-and-publication','passed':False,
       'inventoryContext':{'fixedOriginalBacklog':47,'beforeCompleted':33,'afterThisBatch':38,
           'currentSitePublished':48,'afterSiteWithReferences':39,'newRedisEpisodeIsBacklog':False},
       'sourceIdentityReview':[],'productionInputIdentityReview':[],'codeCardAndCaptionReview':[],
       'finalMediaReview':[],'blockingFindings':[],
       'limitations':['接雨水为self-source，另人独立交叉；本报告不将自审冒称独立来源复核。',
         'No fresh canonical/source GET by this QA task; old reading and documented supplement identities are inspected locally.',
         'No body render/mix/TTS/ASR/algorithm rerun/full-movie decode or listening; only actual short-tail PNGs after ready.',
         'Publication checks remain pending until root integration; old public movie differences are not early blockers.']}
    for slug in SLUGS:
        ep=ROOT/'episodes-codex'/slug; rev=ep/'revisions/reference-endcards'; baseline=read(rev/'baseline.json')
        refs=read(ep/'references.json'); evidence=ROOT/f'docs/reference-endcards/batch-10/sources-{slug}.json'
        record=read(evidence); current=read(ep/'source-sha256.json'); old_raw=git(f'episodes-codex/{slug}/source-sha256.json')
        old=json.loads(old_raw); require((rev/'before-source-sha256.json').read_bytes()==old_raw,slug+' old manifest bytes')
        current_proofs=[]
        for key,wanted in current.items():
            p=ep/key; require(p.is_file(),f'{slug} current missing {key}'); actual=digest(p)
            require(actual==wanted,f'{slug} current hash mismatch {key}')
            current_proofs.append({'key':key,'sha256':actual})
        historical=[];missing={}
        for key,wanted in old.items():
            p=ROOT/rows[slug]['historicalMapping'][key] if key in rows[slug]['historicalMapping'] else ep/key
            if not p.is_file():missing[key]=wanted;continue
            require(digest(p)==wanted,f'{slug} old identity mismatch {key}')
            historical.append({'key':key,'verifiedVia':relative(p.resolve()),'sha256':wanted})
        require(missing==rows[slug]['missingHistoricalInputs'],slug+' missing historical classification')
        preserved={}
        for name in ['article.mdx','research.md']:
            before=git(f'episodes-codex/{slug}/{name}'); current_bytes=(ep/name).read_bytes()
            require((rev/('before-'+name)).read_bytes()==before,slug+' before snapshot '+name)
            require(current_bytes.startswith(before),slug+' original prefix '+name)
            require(re.findall(rb'^#{1,6} .+$',before,re.M)==re.findall(rb'^#{1,6} .+$',current_bytes[:len(before)],re.M),slug+' old headings')
            if name=='article.mdx': require(re.findall(rb'```python\n.*?```',before,re.S)==re.findall(rb'```python\n.*?```',current_bytes,re.S),slug+' Python article block')
            preserved[name]={'originalBytes':len(before),'originalSHA256':sha(before),'currentSHA256':sha(current_bytes),'completeOriginalPrefixPreserved':True}
        sb=read(ep/'storyboard.json'); old_sb=json.loads(git(f'episodes-codex/{slug}/storyboard.json'))
        card=baseline['existingCodeCard']; require(sb['meta']['unvoicedEndCard']==old_sb['meta']['unvoicedEndCard']==card,slug+' Python card metadata')
        require(card['from']+card['durationInFrames']==baseline['bodyFrames'] and card['durationInFrames']==150,slug+' original150frame Python card')
        codes={}
        for name,key in [('solution.py','codeSourceSha256'),('solution.json','displaySourceSha256')]:
            before=git(f'episodes-codex/{slug}/{name}'); actual=(ep/name).read_bytes()
            require(before==actual and sha(actual)==card[key],slug+' original '+name)
            codes[name]=sha(actual)
        require((ep/'storyboard.json').read_bytes()==git(f'episodes-codex/{slug}/storyboard.json'),slug+' whole original storyboard')
        fps=sb['meta']['fps']; offset=0; cues=[]
        for scene in sb['scenes']:
            for shot in scene['shots']:
                for sub in shot.get('subtitles',[]):
                    end_frame=offset+sub['to']+1
                    end_ms=round(Fraction(end_frame*1000,fps))
                    if end_frame==card['from']:end_ms=math.ceil(Fraction(end_frame*1000,fps))-1
                    cues.append({'text':sub['text'],'from':offset+sub['from'],'endMs':end_ms})
                offset+=shot['durationInFrames']
        require(cues and max(c['endMs'] for c in cues)*fps<card['from']*1000,slug+' captions enter Python card')
        article=(ep/'article.mdx').read_text()
        for source in refs['sources']:
            require(source['verification']['status']=='verified' and source['titleEvidence']['locator'],slug+' verified/evidence')
            require(source['title'] in (ROOT/source['titleEvidence']['evidence']).read_text(),slug+' title evidence')
            require('author' not in source,slug+' unexpected personal author')
            require(source['url'] in article and source['verification']['sourceUrl'] in article,slug+' article links')
        report['sourceIdentityReview'].append({'slug':slug,'status':'self-source-awaiting-cross-review' if slug=='trapping-rain-water' else 'passed',
            'evidence':relative(evidence),'evidenceSHA256':digest(evidence),'referencesSHA256':digest(ep/'references.json'),
            'review':NOTES[slug],'sourceCount':len(refs['sources']),'sources':[{'id':s['id'],'title':s['title'],'credit':s.get('author',s['organization']),'technicalReadDate':s['verification']['checkedAt'],'supports':s['supports']} for s in refs['sources']],
            'preservedPrefixes':preserved})
        report['productionInputIdentityReview'].append({'slug':slug,'passed':True,'manifestSHA256':digest(ep/'source-sha256.json'),
            'currentActualInputs':len(current),'currentActualHashProofs':current_proofs,'historicalDeclaredKeys':len(old),
            'historicalDeclaredManifestSHA256':sha(old_raw),'historicalPresentVerified':len(historical),'historicalPresentProofs':historical,
            'historicalMissingDeclaredNotVerified':len(missing),'historicalMissingOriginalKeyAndSHA':missing,
            'absentHistoricalFilesCountedVerified':False,'bodySHA256':digest(ROOT/baseline['bodyPath']),
            'bodyExpectedSHA256':baseline['originalBodySHA256'],'productionVideoInitiallyPresent':baseline['productionVideoInitiallyPresent']})
        require(report['productionInputIdentityReview'][-1]['bodySHA256']==baseline['originalBodySHA256'],slug+' immutable body')
        report['codeCardAndCaptionReview'].append({'slug':slug,'passed':True,'originalWholeStoryboardSHA256':digest(ep/'storyboard.json'),
            'originalCodeCard':card,'originalCodeFilesSHA256':codes,'subtitleCueCount':len(cues),'lastSubtitleEndMs':max(c['endMs'] for c in cues),
            'subtitlesEndStrictlyBeforeOriginalPythonCard':True,'finalBuiltVTTBinding':'pending-final-build'})
    totals={key:sum(x[key] for x in report['productionInputIdentityReview']) for key in ['currentActualInputs','historicalDeclaredKeys','historicalPresentVerified','historicalMissingDeclaredNotVerified']}
    require(list(totals.values())==[900,842,813,29],'Batch counts changed')
    report['productionInputTotals']=totals
    save(report);print('Precheck PASS',totals,'5original prefixes/code cards; sources4 independent +rain self-source')


def extract(slug):
    report=read(REPORT);ep=ROOT/'episodes-codex'/slug;rev=ep/'revisions/reference-endcards'
    receipt=read(rev/'reference-appendix.json');media=read(rev/'reference-appendix-media-check.json')
    require(receipt.get('presentation')=='title-author' and media.get('passed') is True,slug+' not actual ready')
    baseline=read(rev/'baseline.json');body=baseline['bodyFrames'];video=ep/'video.mp4'
    require(receipt['outputSHA256']==digest(video),slug+' receipt movie SHA')
    folder=BATCH/'evidence'/slug;folder.mkdir(parents=True,exist_ok=True)
    frames=[body-1,body,body+75,body+149];start=(body-1)//30
    expression='+'.join(f'eq(n,{frame-start*30})' for frame in frames)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(start),'-i',str(video),'-an','-vf',f"select='{expression}'",
        '-fps_mode','vfr','-frames:v','4',str(folder/'sample-%02d.png')],check=True)
    samples=[]
    for i,(label,frame) in enumerate(zip(['original-python-last','reference-first','reference-middle','reference-last'],frames),1):
        temp=folder/f'sample-{i:02d}.png';path=folder/f'{label}-frame-{frame:06d}.png';require(temp.is_file(),slug+' missing extracted frame');temp.rename(path)
        samples.append({'label':label,'globalFrame':frame,'path':relative(path),'sha256':digest(path),'actuallyViewed':False})
    row={'slug':slug,'status':'actual-pngs-awaiting-view','actualProductionVideoSHA256':digest(video),'receiptSHA256':digest(rev/'reference-appendix.json'),
         'producerMediaReportSHA256':digest(rev/'reference-appendix-media-check.json'),'producerFullMediaPreservationPassed':True,'samples':samples,
         'extraction':{'inputSeekWholeSeconds':start,'selectedGlobalFrames':frames,'shortTailOnly':True,'fullMovieDecodeByThisReviewer':False}}
    report['finalMediaReview']=[x for x in report['finalMediaReview'] if x['slug']!=slug]+[row]
    save(report);print(slug,'4 actual short-tail PNGs ready')


def final_bindings():
    report=read(REPORT);proofs=[]
    for slug in SLUGS:
        ep=ROOT/'episodes-codex'/slug;pub=ROOT/'episodes'/slug;rev=ep/'revisions/reference-endcards'
        baseline=read(rev/'baseline.json');receipt=read(rev/'reference-appendix.json');media=read(rev/'reference-appendix-media-check.json')
        refs=read(ep/'references.json');actual=digest(ep/'video.mp4');body=baseline['bodyFrames']
        require(media['passed'] is True and receipt['outputSHA256']==media['outputSHA256']==actual,slug+' actual media/receipts')
        require(receipt['inputs']['bodySHA256']==media['bodySHA256']==baseline['originalBodySHA256'],slug+' immutable body receipt')
        require(receipt['inputs']['referencesSHA256']==digest(ep/'references.json'),slug+' refs receipt')
        require(receipt['bodyFrames']==media['bodyFrames']==body and receipt['finalVideoFrames']==media['finalFrames']==body+150,slug+' final frames')
        require(receipt['appendix']['from']==body and receipt['appendix']['durationInFrames']==receipt['appendix']['framesPerPage']==150,slug+' appendix interval')
        require(receipt['inputs']['secondsPerPage']==5 and len(receipt['appendix']['pages'])==1,slug+' five second page')
        expected=[{'id':s['id'],'title':s['title'],'credit':s.get('author',s['organization'])} for s in refs['sources']]
        require(receipt['bibliography']==expected,slug+' rendered bibliography identity')
        require(receipt['sourceTitles']==[{'id':s['id'],'title':s['title']} for s in refs['sources']],slug+' source titles receipt')
        require(receipt['quotations']==[],slug+' unexpected research quotation identity')
        require(receipt['presentation']=='title-author' and receipt['layout']=={'kind':'title-author-single-column','maxItemsPerPage':4,'renderedFields':['title','credit'],'quotesRendered':False},slug+' list-only presentation')
        require(receipt['inputs']['generatorSHA256']==digest(ROOT/'episodes-codex/_shared/append_references_bibliography.py'),slug+' renderer')
        for path_key,sha_key in [('oldEngine','oldEngineSHA256'),('originalRenderer','originalRendererSHA256')]:
            require(receipt['dependencies'][sha_key]==digest(ROOT/receipt['dependencies'][path_key]),slug+' frozen renderer dependency')
        require(media['bodyDecodedFramesAndTimestampsEqual'] and media['audioPacketsAndTimingEqual'] and media['outputVideoTimelineContinuous'],slug+' producer preservation proof')
        bindings={}
        for name,src in [('video.mp4',ep/'video.mp4'),('references.json',ep/'references.json'),('source-sha256.json',ep/'source-sha256.json'),
                         ('reference-appendix.json',rev/'reference-appendix.json'),('reference-appendix-media-check.json',rev/'reference-appendix-media-check.json'),
                         ('storyboard.json',ep/'storyboard.json'),('solution.py',ep/'solution.py'),('solution.json',ep/'solution.json'),('render-result.json',ep/'render-result.json')]:
            if name in ['solution.py','solution.json'] and not (pub/name).exists():
                existed=subprocess.run(['git','cat-file','-e',f'{PUBLICATION_BASE}:episodes/{slug}/{name}'],cwd=ROOT,capture_output=True).returncode==0
                require(not existed,slug+' removed existing public code file '+name)
                bindings[name]={'sourceSHA256':digest(src),'publicationFileWasAbsentAndRemainsAbsent':True}
                continue
            require(digest(pub/name)==digest(src),slug+' publication copy '+name)
            bindings[name]=digest(src)
        source_row=next(x for x in report['sourceIdentityReview'] if x['slug']==slug)
        input_row=next(x for x in report['productionInputIdentityReview'] if x['slug']==slug)
        require(digest(ep/'source-sha256.json')==input_row['manifestSHA256'],slug+' final manifest changed')
        require(digest(ep/'references.json')==source_row['referencesSHA256'],slug+' source refs changed')
        require(digest(ROOT/source_row['evidence'])==source_row['evidenceSHA256'],slug+' evidence changed')
        for name in ['article.mdx','research.md']:
            require(digest(ep/name)==source_row['preservedPrefixes'][name]['currentSHA256'],slug+' final source prefix binding '+name)
        old_publication=git(f'episodes/{slug}/article.mdx',PUBLICATION_BASE)
        current_publication=(pub/'article.mdx').read_bytes()
        require(current_publication.startswith(old_publication),slug+' preserve upstream SourceQuote/Figure article prefix')
        # The source and publication articles deliberately have different preserved prefixes.
        for s in refs['sources']:
            require(s['title'].encode() in current_publication and s['organization'].encode() in current_publication and s['url'].encode() in current_publication,slug+' public reference entry')
        meta=read(pub/'meta.json');old_meta=json.loads(git(f'episodes/{slug}/meta.json',PUBLICATION_BASE))
        for key in ['createdAt','publishedAt','firstRelease']:
            require(meta.get(key)==old_meta.get(key),slug+' original publication date '+key)
        require(meta['finalVideoFrames']==body+150 and meta['referenceAppendix']['from']==body and meta['referenceAppendix']['durationInFrames']==150,slug+' published metadata appendix')
        result=read(ep/'render-result.json');require(result['sha256']==actual and result['finalVideoFrames']==body+150,slug+' result binding')
        visuals=next(x for x in report['finalMediaReview'] if x['slug']==slug)
        require(len(visuals['samples'])==4 and all(x['actuallyViewed'] and digest(ROOT/x['path'])==x['sha256'] for x in visuals['samples']),slug+' actual image review required')
        # Native VTT is generated from the unchanged whole original storyboard.
        sb=read(ep/'storyboard.json');offset=0;wanted=[];card=baseline['existingCodeCard'];fps=30
        for scene in sb['scenes']:
            for shot in scene['shots']:
                for sub in shot.get('subtitles',[]):
                    end_frame=offset+sub['to']+1
                    end_ms=round(Fraction(end_frame*1000,fps))
                    if end_frame==card['from']:end_ms=math.ceil(Fraction(end_frame*1000,fps))-1
                    wanted.append((round(Fraction((offset+sub['from'])*1000,fps)),end_ms,sub['text']))
                offset+=shot['durationInFrames']
        caption=ROOT/'site/dist/episodes'/slug/'captions.vtt';native=caption.read_text().replace('\r\n','\n');actual_cues=[]
        def millis(t):
            h,m,s=t.split(':');return int(h)*3600000+int(m)*60000+round(float(s)*1000)
        for block in re.split(r'\n\s*\n',native.strip())[1:]:
            line,sep,text=block.partition('\n');match=re.fullmatch(r'(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)',line)
            require(match and sep,slug+' malformed VTT');actual_cues.append((millis(match[1]),millis(match[2]),text))
        require(actual_cues==wanted,slug+' complete VTT differs from frozen original text/timing')
        require(max(c[1] for c in actual_cues)*30<card['from']*1000,slug+' VTT overlaps original code card')
        caption_row=next(x for x in report['codeCardAndCaptionReview'] if x['slug']==slug)
        caption_row.update(finalBuiltVTTBinding='passed-all-frozen-cue-text-and-timing',builtVTTPath=relative(caption),builtVTTSHA256=digest(caption),
            nativeCueCount=len(actual_cues),nativeLastEndMs=max(c[1] for c in actual_cues))
        proofs.append({'slug':slug,'passed':True,'bodyFrames':body,'finalFrames':body+150,'productionPublicationReceiptSHA256':actual,
            'bindingsSHA256':bindings,'currentMetadataSHA256':digest(pub/'meta.json'),'contentUpdatedAt':meta['updatedAt'],
            'currentSourceArticleSHA256':digest(ep/'article.mdx'),'currentSourceResearchSHA256':digest(ep/'research.md'),
            'currentPublicationArticleSHA256':digest(pub/'article.mdx'),'preservedPublicationBaseline':PUBLICATION_BASE,
            'originalFullPublicationArticleBytes':len(old_publication),'originalFullPublicationArticleSHA256':sha(old_publication),
            'completeUpstreamSourceQuoteFigurePrefixPreserved':True,'firstRelease':meta['firstRelease'],
            'producerFullPreservationReportInspected':True,'producerFullDecodeNotRepeated':True,
            'bodyFrameMD5RowsSHA256':media['bodyFrameMD5RowsSHA256'],'audioPacketPayloadAndTimingSHA256':media['audioPacketPayloadAndTimingSHA256'],
            'decodedAudioPCMProof':media['decodedAudioPCM']})
    report['finalPublicationBindings']=proofs
    report['status']='passed';report['passed']=True;report['completedAtUTC']=now()
    report['actualTailImagesViewed']=20;report['referenceItems']=11;report['referencePages']=5
    report['limitations'][-1]='Publication copies, current manifests/meta, latest unified SourceQuote/Figure article prefixes and full native VTT text/timing bound after integration; browser playback and online deployment remain separate root checks.'
    save(report);print('Final independent QA PASS:5source/prod/pub bindings,20actually viewed PNGs,900inputs, full original Python cards and frozen native cues')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--precheck',action='store_true');parser.add_argument('--extract',choices=SLUGS);parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    if args.precheck:precheck()
    if args.extract:extract(args.extract)
    if args.final:final_bindings()
