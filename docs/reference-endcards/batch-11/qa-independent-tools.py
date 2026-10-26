"""Batch11 independent read-only source/input checks and short-tail PNG collection."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,re,subprocess
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).resolve().parent
BASE='a1a9821845c83a61a57fbb3f0e10461ef4c55238'
SLUGS=['horse-racing','bridge-torch','water-jug','monty-hall']
REPORT=BATCH/'qa-independent.json'
CACHE={}

def need(ok,message):
    if not ok:raise AssertionError(message)
def read(path):return json.loads(path.read_text())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(path):
    path=path.resolve()
    if path not in CACHE:
        h=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
        CACHE[path]=h.hexdigest()
    return CACHE[path]
def git(path):return subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT)
def rel(path):return str(path.resolve().relative_to(ROOT))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(report):REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def parse_vtt(raw):
    text=raw.decode().replace('\r\n','\n');need(text.startswith('WEBVTT'),'nativeVTT header')
    def ms(t):
        h,m,s=t.split(':');return int(h)*3600000+int(m)*60000+round(float(s)*1000)
    cues=[]
    for block in re.split(r'\n\s*\n',text.strip())[1:]:
        timing,sep,body=block.partition('\n');match=re.fullmatch(r'(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)',timing)
        need(match and sep,'nativeVTT cue format');cues.append((ms(match[1]),ms(match[2]),body))
    return cues

def expected_cues(sb,body,strict=False):
    offset=0;fps=sb['meta']['fps'];cues=[]
    for scene in sb['scenes']:
        for shot in scene['shots']:
            for sub in shot.get('subtitles',[]):
                end_frame=offset+sub['to']+1;end_ms=round(Fraction(end_frame*1000,fps))
                if strict and end_frame==body:end_ms=min(end_ms,math.ceil(Fraction(body*1000,fps))-1)
                cues.append((round(Fraction((offset+sub['from'])*1000,fps)),end_ms,sub['text']))
            offset+=shot['durationInFrames']
    return cues

NOTES={
 'horse-racing':'25日实际mathspp题面与七场构造；26日官方网站固定仓库元数据明确原题与Rodrigo Girão Serrão署名。第七场A2/A3/B1/B2/C1可交叉；原文第115行仅去TeX定界符得到原已读可见短引。六场下界原文未证，不以此为通用最优性背书，视频未新增下界。',
 'bridge-torch':'25日OEIS四人17分钟路径与公开README规则/19对17实读；26日复用既有OEIS%N完整原题/%A Peter Kagey身份，另只补固定README Setext标题Lantern & Bridge与byline核查。2018OEIS仅参考；README项目发布名非个人作者猜测；六人/15分钟电量与剪枝实现不作本片全最短性证明，外链论文未读不列。',
 'water-jug':'25日实际doocs固定第三方镜像读取，26日相同文件SHA/Git blob身份及Doocs组织metadata核验。明确非官方原站，镜像合计4升与本片大壶单独4升/终态(3,4)总7升不同；仅共享操作与前六步构造，最少性/GCD/外链不冒称已读/入片。',
 'monty-hall':'SELF-SOURCE：本代理整理，需references_audit交叉。两份大学资料25日实际全文读，26日零新GET。Stanford原Lecture题名与站名分列；Misra明确作者/2011旧资料仅参考。公平二选一为本期显式模型，整体2/3不要求fair；精确后验和盲开1/2为独立推导。'
}

def precheck():
    entry=read(BATCH/'production-entry-check.json');entries={x['slug']:x for x in entry['episodes']}
    old_report=read(REPORT) if REPORT.exists() else {}
    report={'schemaVersion':1,'task':'batch11-independent-source-input-ending-and-actual-tail-review','baselineCommit':BASE,
      'executor':'Codex reference_gate','checkedAtUTC':now(),'status':'pending-source-freeze-and-final-media','passed':False,
      'scope':'Four puzzles; retain complete original bodies/endings, no original or newly introduced code cards.',
      'inventoryContext':{'fixedOriginalBacklog':47,'beforeCompleted':38,'afterThisBatch':42,'currentSitePublished':48,'afterSiteWithReferences':43},
      'sourceIdentityReview':[],'productionInputIdentityReview':[],'originalEndingAndCaptionReview':[],
      'finalMediaReview':old_report.get('finalMediaReview',[]),'blockingFindings':[],
      'limitations':['Monty source was prepared by this reviewer; independent cross-review is separately attributed, never self-certified as independent.',
       'No new source GET, probability/algorithm rerun, body render/mix/TTS/ASR or full-movie/audio decode by this QA task.',
       'Full preservation producer reports are inspected and cryptographically bound; their full decode is not repeated.',
       'Actual images and publication/VTT remain pending until ready and root integration/build.']}
    for slug in SLUGS:
        ep=ROOT/'episodes-codex'/slug;rev=ep/'revisions/reference-endcards';baseline=read(rev/'baseline.json')
        raw_old=git(f'episodes-codex/{slug}/source-sha256.json');old=json.loads(raw_old)
        need((rev/'before-source-sha256.json').read_bytes()==raw_old,slug+' old manifest bytes')
        history=[];missing={}
        for key,wanted in old.items():
            path=ROOT/entries[slug]['historicalMapping'][key] if key in entries[slug]['historicalMapping'] else ep/key
            if not path.is_file():missing[key]=wanted;continue
            need(digest(path)==wanted,slug+' historical hash '+key);history.append({'key':key,'verifiedVia':rel(path),'sha256':wanted})
        need(missing==entries[slug]['missingHistoricalInputs'],slug+' missing historical classification')
        preserved={}
        for name in ['article.mdx','research.md']:
            original=git(f'episodes-codex/{slug}/{name}');current=(ep/name).read_bytes()
            need(current.startswith(original),slug+' original prefix '+name)
            need(re.findall(rb'^\[\^[^\]]+\]:.*$',original,re.M)==re.findall(rb'^\[\^[^\]]+\]:.*$',current,re.M),slug+' original footnotes')
            preserved[name]={'originalBytes':len(original),'originalSHA256':sha(original),'currentSHA256':sha(current),'completeOriginalPrefixPreserved':True}
        preserved_core={}
        for name in ['storyboard.json','words.json','voice.wav','research-math.md','verify_math.py','qa-math.json']:
            path=ep/name
            if path.exists():
                before=git(rel(path));need(digest(path)==sha(before),slug+' original core '+name);preserved_core[name]=sha(before)
        sb=read(ep/'storyboard.json');need(not baseline['existingCodeCard'] and not sb['meta'].get('unvoicedEndCard') and not sb['meta'].get('javaEndCard'),slug+' original no-code-card scope')
        before_vtt=rev/'before-captions.vtt';old_cues=parse_vtt(before_vtt.read_bytes());wanted_old=expected_cues(sb,baseline['bodyFrames']);need(old_cues==wanted_old,slug+' baselineVTT all cues')
        wanted_new=expected_cues(sb,baseline['bodyFrames'],True);changes=[{'cueIndex':i,'beforeEndMs':a[1],'strictEndMs':b[1],'text':a[2]} for i,(a,b) in enumerate(zip(old_cues,wanted_new)) if a!=b]
        need(all(x['beforeEndMs']-x['strictEndMs']==1 for x in changes),slug+' only final1ms clip allowed')
        need(max(c[1] for c in wanted_new)*sb['meta']['fps']<baseline['bodyFrames']*1000,slug+' expectedVTT reaches appended card')
        report['originalEndingAndCaptionReview'].append({'slug':slug,'passed':True,'originalCodeCard':None,'originalCoreFileSHA256':preserved_core,
          'bodyFrames':baseline['bodyFrames'],'beforeVTTSHA256':digest(before_vtt),'originalCueCount':len(old_cues),'originalVTTLastEndMs':max(x[1] for x in old_cues),
          'expectedStrictVTTLastEndMs':max(x[1] for x in wanted_new),'derivedLastCueOnlyChanges':changes,'sourceStoryboardUnchanged':True,'finalBuiltVTTBinding':'pending'})
        current=read(ep/'source-sha256.json');current_proofs=[]
        ready=entry.get('complete') is True and entry.get('passed') is True
        if ready:
            for key,wanted in current.items():
                path=ep/key;need(path.is_file() and digest(path)==wanted,slug+' current frozen '+key)
                current_proofs.append({'key':key,'sha256':wanted})
        report['productionInputIdentityReview'].append({'slug':slug,'historicalDeclaredKeys':len(old),'historicalDeclaredManifestSHA256':sha(raw_old),
            'historicalPresentVerified':len(history),'historicalPresentProofs':history,'historicalMissingDeclaredNotVerified':len(missing),'historicalMissingOriginalKeys':missing,
            'currentActualInputsVerified':ready,'currentActualInputs':len(current) if ready else None,'manifestSHA256':digest(ep/'source-sha256.json') if ready else None,
            'currentActualHashProofs':current_proofs,'immutableBodySHA256':digest(ROOT/baseline['bodyPath']),
            'productionVideoInitiallyPresent':baseline['productionVideoInitiallyPresent']})
        need(report['productionInputIdentityReview'][-1]['immutableBodySHA256']==baseline['originalBodySHA256'],slug+' immutable body')
        refs_path=ep/'references.json'
        if not refs_path.exists():
            report['sourceIdentityReview'].append({'slug':slug,'status':'pending-source-agent','preservedPrefixes':preserved});continue
        refs=read(refs_path);evidence=BATCH/f'sources-{slug}.json';need(evidence.exists(),slug+' source evidence')
        article=(ep/'article.mdx').read_text()
        for source in refs['sources']:
            need(source['title'] in (ROOT/source['titleEvidence']['evidence']).read_text(),slug+' title evidence')
            need(source['url'] in article and source['verification']['sourceUrl'] in article,slug+' complete links')
            need(source['verification']['checkedAt']=='2026-10-25',slug+' old technical read date')
        row={'slug':slug,'status':'self-source-awaiting-cross-review' if slug=='monty-hall' else 'passed',
          'sourceCount':len(refs['sources']),'review':NOTES[slug],'referencesSHA256':digest(refs_path),'evidence':rel(evidence),'evidenceSHA256':digest(evidence),
          'sources':[{'id':x['id'],'title':x['title'],'credit':x.get('author',x['organization']),'technicalReadDate':x['verification']['checkedAt'],'supports':x['supports']} for x in refs['sources']],
          'preservedPrefixes':preserved}
        old_row=next((x for x in old_report.get('sourceIdentityReview',[]) if x['slug']==slug),{})
        for key in ['sourceCrossReview','officialRawProofs','titleBylineAndQuotationCheck','actualReadForQA']:
            if key in old_row:row[key]=old_row[key]
        if old_row.get('sourceCrossReview'):row['status']='passed-by-independent-cross-review'
        report['sourceIdentityReview'].append(row)
    totals={key:sum(x[key] for x in report['productionInputIdentityReview']) for key in ['historicalDeclaredKeys','historicalPresentVerified','historicalMissingDeclaredNotVerified']}
    need(list(totals.values())==[606,606,0],'Historical606 count boundary')
    totals['currentActualInputs']=sum(x['currentActualInputs'] or 0 for x in report['productionInputIdentityReview']) if entry.get('complete') else None
    report['productionInputTotals']=totals;save(report);print('Precheck:',totals,'current ready',entry.get('complete'))


def extract(slug):
    report=read(REPORT);ep=ROOT/'episodes-codex'/slug;rev=ep/'revisions/reference-endcards'
    receipt=read(rev/'reference-appendix.json');media=read(rev/'reference-appendix-media-check.json');baseline=read(rev/'baseline.json')
    need(receipt.get('presentation')=='title-author' and media.get('passed') is True,slug+' actual media not ready')
    video=ep/'video.mp4';need(receipt['outputSHA256']==media['outputSHA256']==digest(video),slug+' actual video receipts')
    pages=len(receipt['appendix']['pages']);body=baseline['bodyFrames'];frames=[body-1]
    for i in range(pages):frames += [body+i*150,body+i*150+75,body+i*150+149]
    start=(body-1)//30;selection='+'.join(f'eq(n,{frame-start*30})' for frame in frames)
    folder=BATCH/'evidence'/slug;folder.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(start),'-i',str(video),'-an','-vf',f"select='{selection}'",'-fps_mode','vfr','-frames:v',str(len(frames)),str(folder/'sample-%02d.png')],check=True)
    samples=[];labels=['original-ending-last']+[f'reference-page-{i+1}-{label}' for i in range(pages) for label in ['first','middle','last']]
    for i,(label,frame) in enumerate(zip(labels,frames),1):
        temp=folder/f'sample-{i:02d}.png';path=folder/f'{label}-frame-{frame:06d}.png';need(temp.exists(),slug+' extractedPNG');temp.rename(path)
        samples.append({'label':label,'globalFrame':frame,'path':rel(path),'sha256':digest(path),'actuallyViewed':False})
    row={'slug':slug,'status':'actual-pngs-awaiting-view','actualProductionVideoSHA256':digest(video),'receiptSHA256':digest(rev/'reference-appendix.json'),
         'producerMediaReportSHA256':digest(rev/'reference-appendix-media-check.json'),'producerFullMediaPreservationPassed':True,'samples':samples,
         'extraction':{'inputSeekWholeSeconds':start,'selectedGlobalFrames':frames,'shortTailOnly':True,'fullMovieDecodeByThisReviewer':False}}
    report['finalMediaReview']=[x for x in report['finalMediaReview'] if x['slug']!=slug]+[row];save(report);print(slug,len(samples),'actual short-tail PNGs')


def final_bindings(include_vtt=True):
    report=read(REPORT);bindings=[]
    need(all(x['currentActualInputsVerified'] for x in report['productionInputIdentityReview']),'Final actual freeze precheck required')
    need(all(x['status'] in ['passed','passed-by-independent-cross-review'] for x in report['sourceIdentityReview']),'Independent sources incomplete')
    for slug in SLUGS:
        ep=ROOT/'episodes-codex'/slug;rev=ep/'revisions/reference-endcards';pub=ROOT/'episodes'/slug
        baseline=read(rev/'baseline.json');receipt=read(rev/'reference-appendix.json');media=read(rev/'reference-appendix-media-check.json')
        refs=read(ep/'references.json');body=baseline['bodyFrames'];actual=digest(ep/'video.mp4');pages=len(receipt['appendix']['pages'])
        need(receipt['presentation']=='title-author' and media['passed'] is True and receipt['outputSHA256']==media['outputSHA256']==actual,slug+' actual media receipt')
        need(receipt['inputs']['bodySHA256']==media['bodySHA256']==baseline['originalBodySHA256'],slug+' immutable body receipt')
        need(receipt['inputs']['referencesSHA256']==digest(ep/'references.json'),slug+' refs SHA receipt')
        need(receipt['bodyFrames']==media['bodyFrames']==body and receipt['finalVideoFrames']==media['finalFrames']==body+pages*150,slug+' final range')
        need(receipt['appendix']['from']==body and receipt['appendix']['durationInFrames']==pages*150 and receipt['appendix']['framesPerPage']==150 and receipt['inputs']['secondsPerPage']==5,slug+' exact reference interval')
        need(receipt['layout']=={'kind':'title-author-single-column','maxItemsPerPage':4,'renderedFields':['title','credit'],'quotesRendered':False},slug+' plain bibliography layout')
        need(receipt['bibliography']==[{'id':x['id'],'title':x['title'],'credit':x.get('author',x['organization'])} for x in refs['sources']],slug+' title/credit identity')
        need(receipt['sourceTitles']==[{'id':x['id'],'title':x['title']} for x in refs['sources']],slug+' original title identities')
        need(receipt['quotations']==[dict(id=x['id'],**x['quotation']) for x in refs['sources'] if x.get('quotation')],slug+' retained research quote identities')
        need(receipt['inputs']['generatorSHA256']==digest(ROOT/'episodes-codex/_shared/append_references_bibliography.py'),slug+' generator identity')
        for key,sha_key in [('oldEngine','oldEngineSHA256'),('originalRenderer','originalRendererSHA256')]:
            need(digest(ROOT/receipt['dependencies'][key])==receipt['dependencies'][sha_key],slug+' old renderer identity')
        need(media['bodyDecodedFramesAndTimestampsEqual'] and media['audioPacketsAndTimingEqual'] and media['outputVideoTimelineContinuous'],slug+' full producer preservation proof')
        proofs={}
        for name,source in [('video.mp4',ep/'video.mp4'),('references.json',ep/'references.json'),('source-sha256.json',ep/'source-sha256.json'),
             ('reference-appendix.json',rev/'reference-appendix.json'),('reference-appendix-media-check.json',rev/'reference-appendix-media-check.json'),
             ('storyboard.json',ep/'storyboard.json'),('words.json',ep/'words.json'),('render-result.json',ep/'render-result.json')]:
            need(digest(pub/name)==digest(source),slug+' public copy '+name);proofs[name]=digest(source)
        input_row=next(x for x in report['productionInputIdentityReview'] if x['slug']==slug)
        need(digest(ep/'source-sha256.json')==input_row['manifestSHA256'],slug+' final manifest drift')
        source_row=next(x for x in report['sourceIdentityReview'] if x['slug']==slug)
        need(digest(ep/'references.json')==source_row['referencesSHA256'] and digest(ROOT/source_row['evidence'])==source_row['evidenceSHA256'],slug+' final source identity drift')
        for name in ['article.mdx','research.md']:
            need(digest(ep/name)==source_row['preservedPrefixes'][name]['currentSHA256'],slug+' final source prefix identity '+name)
        original_pub=git(f'episodes/{slug}/article.mdx');article=(pub/'article.mdx').read_bytes()
        need(article.startswith(original_pub),slug+' whole original public SourceQuote/Figure article prefix')
        for source in refs['sources']:
            for text in [source['title'],source['organization'],source.get('author',''),source['url'],source['verification']['sourceUrl']]:
                need(text.encode() in article,slug+' public full source text/link')
        meta=read(pub/'meta.json');old_meta=json.loads(git(f'episodes/{slug}/meta.json'))
        for key in ['createdAt','publishedAt','firstRelease']:need(meta.get(key)==old_meta.get(key),slug+' first publication date '+key)
        need(meta['finalVideoFrames']==body+pages*150 and meta['referenceAppendix']['from']==body and meta['referenceAppendix']['durationInFrames']==pages*150,slug+' published appendix metadata')
        result=read(ep/'render-result.json');need(result['sha256']==actual and result['finalVideoFrames']==body+pages*150,slug+' render-result identity')
        visual=next(x for x in report['finalMediaReview'] if x['slug']==slug)
        need(len(visual['samples'])==1+3*pages and all(x['actuallyViewed'] and digest(ROOT/x['path'])==x['sha256'] for x in visual['samples']),slug+' actual image viewing required')
        if include_vtt:
            sb=read(ep/'storyboard.json');wanted=expected_cues(sb,body,True)
            vtt=ROOT/'site/dist/episodes'/slug/'captions.vtt';actual_cues=parse_vtt(vtt.read_bytes());need(actual_cues==wanted,slug+' full strict derived VTT text/timing')
            need(max(x[1] for x in actual_cues)*sb['meta']['fps']<body*1000,slug+' native captions enter reference card')
            before_vtt=rev/'before-captions.vtt';before=parse_vtt(before_vtt.read_bytes());differences=[]
            for index,(old,new) in enumerate(zip(before,actual_cues)):
                need(old[0]==new[0] and old[2]==new[2],slug+' original caption start/text changed')
                if old!=new:differences.append({'cueIndex':index,'beforeEndMs':old[1],'afterEndMs':new[1],'deltaMs':new[1]-old[1]})
            need(len(before)==len(actual_cues) and len(differences)<=1 and all(x['deltaMs']==-1 and x['cueIndex']==len(before)-1 for x in differences),slug+' unexpected VTT derived change')
            caption_row=next(x for x in report['originalEndingAndCaptionReview'] if x['slug']==slug)
            caption_row.update(finalBuiltVTTBinding='passed-all-original-text-starts-and-complete-derived-end-times',builtVTTPath=rel(vtt),builtVTTSHA256=digest(vtt),
                actualDerivedChanges=differences,unchangedByteForByteWithOriginalVTT=vtt.read_bytes()==before_vtt.read_bytes(),nativeSubtitlesEndStrictlyBeforeReferences=True)
        bindings.append({'slug':slug,'passed':True,'bodyFrames':body,'finalFrames':body+pages*150,'pages':pages,'productionPublicationReceiptSHA256':actual,
            'bindingsSHA256':proofs,'currentMetadataSHA256':digest(pub/'meta.json'),'contentUpdatedAt':meta['updatedAt'],'firstRelease':meta['firstRelease'],
            'currentSourceArticleSHA256':digest(ep/'article.mdx'),'currentSourceResearchSHA256':digest(ep/'research.md'),'currentPublicationArticleSHA256':digest(pub/'article.mdx'),
            'originalFullPublicationArticleBytes':len(original_pub),'originalFullPublicationArticleSHA256':sha(original_pub),
            'completeOriginalPublicationSourceQuoteFigurePrefixPreserved':True,'originalEndingNotReplacedWithCodeCard':True,
            'producerFullPreservationReportInspected':True,'producerFullDecodeNotRepeated':True,'bodyFrameMD5RowsSHA256':media['bodyFrameMD5RowsSHA256'],
            'audioPacketPayloadAndTimingSHA256':media['audioPacketPayloadAndTimingSHA256'],'decodedAudioPCMProof':media['decodedAudioPCM']})
    report['finalPublicationBindings']=bindings;report['status']='passed' if include_vtt else 'publication-bound-pending-final-vtt';report['passed']=include_vtt;report['completedAtUTC']=now() if include_vtt else None
    report['actualTailImagesViewed']=sum(len(x['samples']) for x in report['finalMediaReview']);report['referenceItems']=sum(x['sourceCount'] for x in report['sourceIdentityReview']);report['referencePages']=sum(x['pages'] for x in bindings)
    report['limitations'][-1]=('Final product/publication/source/receipt/meta/manifests and generated full VTT identities verified after root integration/build; browser/online release checks remain root-owned.' if include_vtt else 'Final product/publication/source/receipt/meta/manifests bound; generated final strict VTT waits for root build. Browser/online release checks remain root-owned.')
    save(report);print('IndependentQA',report['status'],':',report['actualTailImagesViewed'],'actualPNGviews,',report['productionInputTotals'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--precheck',action='store_true');p.add_argument('--extract',choices=SLUGS);p.add_argument('--final',action='store_true');p.add_argument('--bind-publication',action='store_true');a=p.parse_args()
    if a.precheck:precheck()
    if a.extract:extract(a.extract)
    if a.final:final_bindings()
    if a.bind_publication:final_bindings(include_vtt=False)
