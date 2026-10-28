"""Exact-candidate Redis cache lessons: local full HTTP + actual browser review."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urljoin, quote
from html.parser import HTMLParser
import argparse, atexit, base64, hashlib, json, subprocess, sys
from playwright.sync_api import sync_playwright
from PIL import Image
import helpers

p=argparse.ArgumentParser()
p.add_argument('--root',default='/workspace/work/video-studio-sitecheck')
p.add_argument('--candidate',required=True)
p.add_argument('--baseline',default='9dd0abf0')
p.add_argument('--base',default='http://127.0.0.1:4326/video-studio')
p.add_argument('--out',required=True)
p.add_argument('--reuse-http-from')
p.add_argument('--widths',default='1440,390')
args=p.parse_args(); root=Path(args.root); out=Path(args.out); out.mkdir(parents=True,exist_ok=True); helpers.root=root
prior_http=json.loads(Path(args.reuse_http_from).read_text()) if args.reuse_http_from else None
if prior_http: assert prior_http['candidate']==args.candidate and prior_http['base']==args.base
SLUGS=['server-cache','cache-consistency']; MEMBERS=[*SLUGS,'redis-skiplist']; BG=[238,241,245]; ROI=[1880,1040]
report={'status':'running','candidate':args.candidate,'baseline':args.baseline,'base':args.base,'startedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),'scope':SLUGS,'httpMedia':[],'views':[],'screenshots':[],'errors':[]}
atexit.register(lambda:(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'))
def ex(kind,value,tb): report['status']='failed'; report['errors'].append(str(value)); sys.__excepthook__(kind,value,tb)
sys.excepthook=ex
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==args.candidate
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root,text=True).strip()
def gitbytes(ref,path): return subprocess.check_output(['git','show',ref+':'+path],cwd=root)
def tree(ref,*paths):
    return subprocess.check_output(['git','ls-tree','-r',ref,*paths],cwd=root,text=True).splitlines()
skip_paths=['episodes/redis-skiplist','episodes-codex/redis-skiplist']
oldskip=tree(args.baseline,*skip_paths); newskip=tree(args.candidate,*skip_paths); assert oldskip==newskip
report['skiplistPreservation']={'trackedFiles':len(oldskip),'allGitBlobSHAAndModesUnchanged':True}
old_style=json.loads((root/'episodes-codex/_shared/redis-video/style-v1.json').read_text())
new_style=json.loads((root/'episodes-codex/_shared/redis-cache-video/style-v1.json').read_text())
assert new_style['palette']==old_style['palette']; report['paletteEqualsSkiplist']=new_style['palette']

def exact_still(video,frame,path):
    second,offset=divmod(frame,30)
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(second),'-i',str(video),'-vf',f'select=eq(n\\,{offset})','-frames:v','1',str(path)],check=True)
def ffprobe(video):
    value=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,pix_fmt,color_range,color_space,color_transfer,color_primaries,nb_frames','-of','json',str(video)],text=True))['streams'][0]
    assert value['width']==1920 and value['height']==1080
    assert value['pix_fmt']=='yuv420p' and value['color_range']=='tv'
    assert value['color_space']==value['color_transfer']==value['color_primaries']=='bt709',value
    return value
class Tracks(HTMLParser):
    def __init__(self): super().__init__(); self.tracks=[]
    def handle_starttag(self,tag,attrs):
        if tag=='track': self.tracks.append(dict(attrs))
episodes={}
for slug in SLUGS:
    directory=root/'episodes'/slug; meta=json.loads((directory/'meta.json').read_text()); original=json.loads(gitbytes(args.baseline,f'episodes/{slug}/meta.json'))
    assert meta['series']=='redis' and meta['burnedInCaptions'] is True
    assert meta['sourcePath']==f'episodes-codex/{slug}/remotion'
    allowed={'updatedAt','burnedInCaptions','finalVideoFrames','referenceAppendix'}
    changes=[key for key in set(meta)|set(original) if meta.get(key)!=original.get(key)]; assert set(changes)<=allowed,changes
    article_path=directory/'article.mdx'; assert article_path.read_bytes()==gitbytes(args.baseline,f'episodes/{slug}/article.mdx')
    assert (directory/'storyboard.json').read_bytes()==gitbytes(args.baseline,f'episodes/{slug}/storyboard.json')
    article=helpers.article_data(article_path.read_text()); receipt=json.loads((directory/'reference-appendix.json').read_text()); result=json.loads((directory/'render-result.json').read_text())
    assert result['sha256']==receipt['outputSHA256']==helpers.sha_file(directory/'video.mp4')
    assert meta['finalVideoFrames']==result['frames']==receipt['finalVideoFrames']; body=meta['referenceAppendix']['from']
    assert result['bodyFrames']==body and result['frames']==body+150
    style=json.loads((directory/'cover-style.json').read_text()); assert style['ep']==meta['ep']
    coverchecks={}
    for ratio,dimensions in [('16x9',[1920,1080]),('3x4',[1080,1440]),('4x3',[1440,1080])]:
        cover=directory/f'cover-{ratio}.jpg'; sha=helpers.sha_file(cover); assert sha==style['covers'][ratio]['jpgSha256']; assert list(Image.open(cover).size)==dimensions
        coverchecks[ratio]={'sha256':sha,'dimensions':dimensions,'changedFromOldCover':helpers.git_blob(args.baseline,str(cover.relative_to(root)))!=helpers.git_blob(args.candidate,str(cover.relative_to(root)))}
        assert coverchecks[ratio]['changedFromOldCover']
    assert helpers.sha_file(directory/'poster.jpg')==coverchecks['3x4']['sha256']
    data={'meta':meta,'article':article,'body':body,'frames':result['frames'],'covers':coverchecks,'metadataChangedFields':changes,'colourTags':ffprobe(directory/'video.mp4')}
    packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time','-of','json',str(directory/'video.mp4')],text=True)); data['pts']=sorted(float(x['pts_time']) for x in packets['packets']); assert len(data['pts'])==result['frames']
    storyboard=json.loads((directory/'storyboard.json').read_text()); data['subtitleTexts']=[s['text'] for sc in storyboard['scenes'] for shot in sc['shots'] for s in shot.get('subtitles',[])]; assert len(data['subtitleTexts'])==24
    for f in ['video.mp4',meta['poster'],*[v['src'].split('/episodes/'+slug+'/')[1] for v in article['figures']],'captions.vtt']:
        url=args.base+'/episodes/'+slug+'/'+f
        response=next(x for x in prior_http['httpMedia'] if x['url']==url) if prior_http else helpers.full_http_sha(url)
        expected=root/'site/dist/episodes'/slug/f if f=='captions.vtt' else directory/f
        assert response['sha256']==helpers.sha_file(expected); report['httpMedia'].append(response)
    data['colourExpected']={}
    for kind,frame in [('body',round(article['figures'][0]['seek']*30)),('references',body+75)]:
        path=out/f'{slug}-ffmpeg-{kind}.png'; exact_still(directory/'video.mp4',frame,path); pixel=Image.open(path).convert('RGB').getpixel(tuple(ROI)); assert max(abs(pixel[i]-BG[i]) for i in range(3))<=6,(slug,kind,pixel)
        data['colourExpected'][kind]={'frame':frame,'pixel':pixel,'file':str(path),'sha256':helpers.sha_file(path)}
    parser=Tracks(); parser.feed((root/f'site/dist/episodes/{slug}/index.html').read_text()); assert len(parser.tracks)==1 and 'default' not in parser.tracks[0]; data['nativeTrackStatic']=parser.tracks[0]
    episodes[slug]=data
report['episodes']={s:{k:v for k,v in d.items() if k not in ['pts','subtitleTexts']} for s,d in episodes.items()}

def snap(page,name):
    helpers.overflow(page); path=out/name; page.screenshot(path=str(path)); report['screenshots'].append({'file':str(path),'sha256':helpers.sha_file(path)})
def seek(page,data,seconds):
    frame=round(float(seconds)*30); target=data['pts'][frame]; state=helpers.seek_paused(page,target)
    assert round(state['presentedFrame']['mediaTime']*30)==frame,(seconds,target,state)
    state.update(requestedSeconds=seconds,targetFrame=frame); return state
UI_ARM="""()=>{const v=document.querySelector('video');v.pause();const trace={frames:[],events:[]};window.__qaUIClick=new Promise((resolve,reject)=>{let sought=false,paint=null,done=false;const timer=setTimeout(()=>{done=true;reject(new Error('UI seek paint timeout '+JSON.stringify({trace,time:v.currentTime})))},12000);const finish=()=>{if(done||!sought||!paint)return;done=true;clearTimeout(timer);requestAnimationFrame(()=>requestAnimationFrame(()=>resolve({currentTime:v.currentTime,paused:v.paused,hash:location.hash,painted:paint,trace})))};const callback=(now,m)=>{paint={mediaTime:m.mediaTime,presentedFrames:m.presentedFrames,afterSeeked:sought};trace.frames.push({...paint,time:v.currentTime,afterSeeked:sought});finish();if(!done)v.requestVideoFrameCallback(callback)};v.requestVideoFrameCallback(callback);v.addEventListener('seeking',()=>trace.events.push({event:'seeking',time:v.currentTime}),{once:true});v.addEventListener('seeked',()=>{v.pause();sought=true;trace.events.push({event:'seeked',time:v.currentTime});finish()},{once:true})});return true}"""
def click_seek(page,data,link,seconds):
    seek(page,data,2 if seconds>5 else 10); link.scroll_into_view_if_needed(); page.evaluate(UI_ARM); link.click(); trace=page.evaluate('()=>window.__qaUIClick')
    assert abs(trace['currentTime']-seconds)<.05,(seconds,trace)
    # JS number formatting differs from Python's long decimal representation; compare numeric hash.
    assert trace['hash'].startswith('#t=') and abs(float(trace['hash'][3:])-seconds)<1e-9
    trace.update(requestedNominalSeconds=seconds,nominalExpectedFrame=round(seconds*30),paintedFrame=round(trace['painted']['mediaTime']*30)); trace['nominalClickPresentedExactFrame']=trace['nominalExpectedFrame']==trace['paintedFrame']; return trace
def canvas(page,data,kind,name):
    current=page.locator('video').evaluate('''(v,p)=>{let c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;let x=c.getContext('2d');x.drawImage(v,0,0);return {pixel:[...x.getImageData(p[0],p[1],1,1).data],png:c.toDataURL('image/png')}}''',ROI)
    path=out/name; path.write_bytes(base64.b64decode(current.pop('png').split(',',1)[1])); expected=data['colourExpected'][kind]['pixel']; delta=max(abs(current['pixel'][i]-expected[i]) for i in range(3)); assert delta<=3,(kind,current,expected)
    assert max(abs(current['pixel'][i]-BG[i]) for i in range(3))<=6
    return {**current,'file':str(path),'sha256':helpers.sha_file(path),'maximumChannelDifferenceFromFFmpeg':delta}
def theme(page,value):
    page.locator('.theme-trigger').click(); page.locator(f'[data-theme-opt="{value}"]').click(); assert page.locator('html').get_attribute('data-theme')==value
def taxonomy(page,width):
    response=page.goto(args.base+'/series/redis/',wait_until='networkidle'); assert response.status==200 and page.locator('h1').inner_text().strip()=='Redis 系列'
    lessons=page.locator('ol.lesson-list a.lesson'); paths=[a.rsplit('/',2)[1] for a in helpers.links(lessons)]; assert paths==MEMBERS,paths
    for slug in SLUGS:
        entry=lessons.filter(has=page.get_by_role('heading',name=episodes[slug]['meta']['title'],exact=True)); assert entry.count()==1
        assert '应用场景 · '+episodes[slug]['meta']['applicationScenario'] in entry.inner_text(); assert f"EP.{episodes[slug]['meta']['ep']:02}" in entry.inner_text()
        image=entry.locator('img'); assert image.get_attribute('src').endswith('/'+slug+'/'+episodes[slug]['meta']['poster'])
        if width>=768: image.evaluate('async i=>i.decode()')
        else: assert not image.is_visible()  # The responsive series layout intentionally hides thumbnails.
    snap(page,f'series-{width}.png')
    page.goto(args.base+'/learn/#redis',wait_until='networkidle'); track=page.locator('section#redis.series-card'); assert track.locator('h2').inner_text().replace('↗','').strip()=='Redis 系列'
    assert [a.rsplit('/',2)[1] for a in helpers.links(track.locator('ol.series-lessons a'))]==MEMBERS
    for slug in SLUGS: assert track.get_by_text('应用场景 · '+episodes[slug]['meta']['applicationScenario'],exact=True).count()==1
    track.scroll_into_view_if_needed(); snap(page,f'learn-{width}.png')
    page.goto(args.base+'/library/?series=redis',wait_until='networkidle'); assert page.locator('select[name="series"]').input_value()=='redis'; visible=page.locator('#library-grid > ul > li:not([hidden]) a.card'); assert set(a.rsplit('/',2)[1] for a in helpers.links(visible))==set(MEMBERS)
    for card in visible.all():
        card.scroll_into_view_if_needed(); card.locator('img').evaluate('async i=>i.decode()')
        if width<768: snap(page,'library-'+card.get_attribute('href').rsplit('/',2)[1]+f'-{width}.png')
    snap(page,f'library-{width}.png'); return {'members':MEMBERS,'applicationScenarios':[episodes[s]['meta']['applicationScenario']for s in SLUGS],'overflow':helpers.overflow(page)}

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']); report['chromiumVersion']=browser.version
    for width in [int(v)for v in args.widths.split(',')]:
        assert width in [1440,390]; height=1000 if width==1440 else 844
        context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce'); page=context.new_page(); errors=[]
        page.on('pageerror',lambda e:errors.append(str(e))); page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        view={'width':width,'height':height,'taxonomy':taxonomy(page,width),'episodes':[]}; report['views'].append(view)
        for slug in SLUGS:
            data=episodes[slug]; meta=data['meta']; article=data['article']; response=page.goto(args.base+'/episodes/'+slug+'/',wait_until='networkidle'); assert response.status==200
            row={'slug':slug}; view['episodes'].append(row)
            assert page.locator('header.eh h1').inner_text().strip()==meta['title']; assert page.locator('header.eh .eyebrow').inner_text().strip()=='Redis 应用场景 · '+meta['applicationScenario']
            assert page.locator('nav[aria-label="面包屑"]').get_by_role('link',name='Redis 系列',exact=True).count()==1
            assert page.locator('.episode-version time').get_attribute('datetime')==meta['updatedAt']
            source=page.locator('.source-links a').evaluate_all('(as)=>as.map(a=>a.href)'); assert len(source)==3 and all(args.candidate in u for u in source); assert source[-1].endswith(quote(meta['sourcePath'],safe='/')); row['sourceLinks']=source
            pager=[a.rsplit('/',2)[1]for a in helpers.links(page.locator('nav.pager a'))]
            expected_neighbors=[MEMBERS[i]for i in [MEMBERS.index(slug)-1,MEMBERS.index(slug)+1]if 0<=i<len(MEMBERS)]
            assert pager==expected_neighbors,(slug,pager,expected_neighbors); row['withinRedisPager']=pager
            assert [a.rsplit('/',2)[1]for a in helpers.links(page.locator('#course-directory nav a'))]==MEMBERS
            row['related']=[]
            for href in helpers.links(page.locator('aside.rel a.rc')):
                r=page.request.get(urljoin(args.base+'/',href)); assert r.status==200; row['related'].append({'href':href,'status':200}); r.dispose()
            video=page.locator('video'); page.wait_for_function('()=>{const v=document.querySelector("video");return v&&v.readyState>=1&&v.textTracks.length===1}')
            state=video.evaluate('(v)=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,trackDefault:v.querySelector("track").default,mode:v.textTracks[0].mode})'); assert state['width']==1920 and state['height']==1080 and abs(state['duration']-data['frames']/30)<.034; assert state['trackDefault'] is False and state['mode']=='disabled'; row['initialPlayer']=state
            row['defaultBody']=seek(page,data,2); assert not row['defaultBody']['active']
            video.evaluate('(v)=>{v.muted=true;return v.play()}'); page.wait_for_function('document.querySelector("video").currentTime>2.2&&!document.querySelector("video").paused'); page.keyboard.press('k'); page.wait_for_function('document.querySelector("video").paused'); row['playbackKeyboardPause']=True
            body_time=article['figures'][0]['seek']; seek(page,data,body_time); row['bodyColour']=canvas(page,data,'body',f'{slug}-body-canvas-{width}.png')
            page.evaluate('()=>{let b=document.createElement("button");b.id="qa-fullscreen";b.style="position:fixed;top:0;left:0;z-index:99999";b.textContent="Fullscreen QA";b.onclick=()=>document.querySelector("video").requestFullscreen();document.body.appendChild(b)}'); page.locator('#qa-fullscreen').click(); page.wait_for_function('document.fullscreenElement===document.querySelector("video")'); seek(page,data,body_time); snap(page,f'{slug}-fullscreen-{width}.png'); page.evaluate('()=>document.exitFullscreen()'); page.wait_for_function('()=>!document.fullscreenElement'); page.locator('#qa-fullscreen').evaluate('(b)=>b.remove()'); row['fullscreen']={'entered':True,'exited':True}
            chapters=json.loads(page.locator('#player').get_attribute('data-chapters'))
            assert [c['id']for c in chapters]==({'server-cache':['repeated','cache','lifecycle'],'cache-consistency':['stale','invalidate','order']}[slug])
            article_chapters={c['id']:c['title']for c in article['frontmatter']['chapters']}
            assert {c['id']:c['title']for c in chapters if c['id']in article_chapters}==article_chapters
            row['videoOnlyChapters']=[c['id']for c in chapters if c['id']not in article_chapters]
            row['chapterSeeks']=[]; row['articleChapterSeeks']=[]
            for i,c in enumerate(chapters):
                selector='.vp .side a.ch' if width>=768 else '.vp .chips a.chip'; trace=click_seek(page,data,page.locator(selector+f'[data-index="{i}"]'),c['start']); row['chapterSeeks'].append({**c,'uiClick':trace,'exactPacketPTSProbe':seek(page,data,c['start'])})
                button=page.locator('article.article-body [data-seek="'+c['id']+'"]')
                if c['id']in article_chapters:
                    assert button.count()==1; trace=click_seek(page,data,button,c['start']); row['articleChapterSeeks'].append({'id':c['id'],'uiClick':trace,'exactPacketPTSProbe':seek(page,data,c['start'])})
                else: assert button.count()==0
            for h in article['headings']: assert page.locator('article.article-body [id="'+h['id']+'"]').count()==1
            row['articleAnchors']=[h['id']for h in article['headings']]; row['figureThemes']=[]
            for appearance in ['light','dark']:
                theme(page,appearance)
                for f in article['figures']:
                    figure=page.locator('figure.fig').filter(has=page.locator('img[src="'+f['src']+'"]')); figure.scroll_into_view_if_needed(); figure.locator('img').evaluate('async i=>{await i.decode();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}'); snap(page,f'{slug}-figure-{appearance}-{width}.png')
                    row['figureThemes'].append({'appearance':appearance,'uiClick':click_seek(page,data,figure.locator('[data-seek-time]'),f['seek']),'exactPacketPTSProbe':seek(page,data,f['seek'])})
            row['sourceQuotes']=[]
            for i in range(page.locator('[data-source-trigger]').count()):
                trigger=page.locator('[data-source-trigger]').nth(i); ident=trigger.get_attribute('data-source-trigger'); trigger.scroll_into_view_if_needed(); page.mouse.move(0,0); page.wait_for_timeout(120); trigger.focus(); page.keyboard.press('Enter'); panel=page.locator('[data-source-panel="'+ident+'"]'); panel.wait_for(state='visible'); assert panel.locator('blockquote').inner_text().strip(); identity=panel.locator('.source-identity').inner_text(); snap(page,f'{slug}-source-{i+1}-{width}.png'); page.keyboard.press('Escape'); panel.wait_for(state='hidden'); row['sourceQuotes'].append({'sourceId':ident,'keyboardOpened':True,'escapedClosed':True,'identity':identity})
            video.evaluate('(v)=>v.textTracks[0].mode="showing"'); page.wait_for_function('document.querySelector("video").textTracks[0].cues?.length>0'); cues=video.evaluate('(v)=>[...v.textTracks[0].cues].map(c=>({start:c.startTime,end:c.endTime,text:c.text}))'); assert [c['text']for c in cues]==data['subtitleTexts']; assert cues[-1]['end']<=data['body']/30
            t=(cues[0]['start']+cues[0]['end'])/2; active=seek(page,data,t); assert active['active']==[cues[0]['text']]
            refs=seek(page,data,(data['body']+75)/30); assert not refs['active']; row['referenceColour']=canvas(page,data,'references',f'{slug}-references-canvas-{width}.png'); snap(page,f'{slug}-references-{width}.png'); restored=seek(page,data,t); assert restored['active']==active['active']; video.evaluate('(v)=>v.textTracks[0].mode="disabled"'); disabled=seek(page,data,t); assert not disabled['active']
            row['nativeCaptions']={'cueCount':len(cues),'lastEnd':cues[-1]['end'],'explicitEnabled':active,'referencesEmpty':refs,'restored':restored,'explicitDisabled':disabled}; row['overflow']=helpers.overflow(page)
            print(json.dumps({'slug':slug,'width':width,'status':'passed'}),flush=True)
        assert not errors,errors; view['errors']=errors; context.close()
    browser.close()
report['status']='passed'; report['finishedAt']=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'); report['limits']=['Complete local HTTP responses and exact committed media hashes; canonical online checks are separate.','Mobile viewport simulation and native Fullscreen API, not physical-device tests.','Nominal fractional UI requests and their paint traces are recorded separately from exact packet-PTS paused probes; no adjacent-frame tolerance is used in direct probes.','No full-film listening, ASR or new user viewing approval.']
print('Redis cache lessons site QA passed',flush=True)
