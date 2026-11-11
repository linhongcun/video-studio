#!/usr/bin/env node
// Local Chromium checks for the staged P06/P10 revisions. Default is plan-only.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const R='/workspace/video-studio',OUTROOT=__dirname;
const args=process.argv.slice(2),arg=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const BASE=arg('--base','http://127.0.0.1:4173/video-studio/');
const RUN=arg('--run','browser-local-v1');
if(!/^[a-zA-Z0-9_-]+$/.test(RUN))throw Error('Use a simple unique run name');
const SLUGS=arg('--slugs','twelve-balls,prisoners-light').split(',');
const CONFIG={
  'twelve-balls':{chapter:'balanced-branch',shots:['12']},
  'prisoners-light':{chapter:'protocol',shots:['03','04']},
};
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const assert=(b,m)=>{if(!b)throw Error(m);};
if(!args.includes('--execute')){
  console.log(JSON.stringify({status:'prepared-not-executed',base:BASE,run:RUN,slugs:SLUGS,
    prerequisites:['New publication meta.sourcePath contains revisions/logic-20261111',
      'Staged MP4 matches the actual new revision render-result SHA',
      'Site build and preview served at the selected base'],
    checks:['desktop/light and phone-touch-viewport/dark',
      'new duration, native controls and burned-in-caption track default',
      'all chapter data and changed chapter click with real playback',
      'requestVideoFrameCallback at a new-explanation frame',
      'keyboard play/pause and both article figure returns',
      'trusted-click native desktop fullscreen enter/exit',
      'time deep link and horizontal bounds'],
    browser:'Global Playwright, /usr/bin/chromium; no install needed'},null,2));
  process.exit(0);
}
const reportFile=path.join(OUTROOT,RUN+'.json');
assert(!fs.existsSync(reportFile),'Preserve prior reports; select a new --run name');
const OUT=path.join(OUTROOT,RUN);fs.mkdirSync(OUT,{recursive:true});
const report={status:'running',startedAt:new Date().toISOString(),base:BASE,
  executor:'Codex batch_browser_qa; actual automated Chromium/Playwright',
  actions:[],pageErrors:[],mediaFailures:[],screenshots:[],episodes:[],
  limitations:[
    'Local built website only; online HTTP identity is verified separately by the parent task.',
    'Desktop and touch/mobile viewport emulation in headless Chromium; no physical phone or other browser engine test.',
    'Fullscreen uses a trusted click on a temporary QA button calling native video.requestFullscreen; native shadow-control geometry is not asserted.',
    'Screenshots preserve native controls and any transient seek spinner. Functional success is not an all-controls-state caption-legibility claim.',
    'No full real-time viewing, semantic listening or ASR claim.'
  ]};
const save=()=>fs.writeFileSync(reportFile,JSON.stringify(report,null,2)+'\n');
const add=(episode,viewport,kind,data={})=>{report.actions.push({episode,viewport,kind,...data});save();};
async function shot(page,slug,name,videoOnly=false){
  const p=path.join(OUT,slug+'-'+name+'.png');
  if(videoOnly)await page.locator('video').screenshot({path:p});else await page.screenshot({path:p});
  report.screenshots.push({episode:slug,path:path.relative(OUTROOT,p),sha256:sha(p)});save();
}
async function frame(page,time){
  const result=await page.locator('video').evaluate((v,t)=>new Promise((resolve,reject)=>{
    v.pause();const timer=setTimeout(()=>reject(Error('seek/video-frame timeout')),15000);
    const cb=(now,m)=>{
      if(Math.abs(m.mediaTime-t)<=1/30+.005){clearTimeout(timer);resolve({targetTime:t,mediaTime:m.mediaTime,currentTime:v.currentTime,readyState:v.readyState,width:v.videoWidth,height:v.videoHeight,seeking:v.seeking});}
      else v.requestVideoFrameCallback(cb);
    };
    v.requestVideoFrameCallback(cb);v.currentTime=t;
  }),time);
  assert(Math.abs(result.mediaTime-time)<=1/30+.005,'Seek presented frame mismatch: '+JSON.stringify(result));
  await page.waitForFunction(()=>{const v=document.querySelector('video');return !v.seeking&&v.readyState>=2;});
  return result;
}
async function loadSpec(slug){
  assert(CONFIG[slug],'Unsupported episode '+slug);
  const P=path.join(R,'episodes/puzzles',slug,'publication');
  const meta=read(path.join(P,'meta.json'));
  assert(meta.sourcePath.includes('/revisions/logic-20261111/'),'New staged revision is required: '+slug);
  let D=path.join(R,meta.sourcePath);if(!fs.existsSync(path.join(D,'render-result.json')))D=path.dirname(D);
  const result=read(path.join(D,'render-result.json')),sb=read(path.join(P,'storyboard.json'));
  const videoSHA=sha(path.join(P,'video.mp4'));
  assert(result.sha256===videoSHA&&sha(path.join(D,'video.mp4'))===videoSHA,'Publication/new-render media differs: '+slug);
  assert(meta.finalVideoFrames===result.frames,'New frame count differs: '+slug);
  assert(meta.burnedInCaptions===true,'Burned-in captions not declared: '+slug);
  const chapters=sb.scenes.map(c=>({id:c.id,title:c.title,start:c.from/30}));
  const shots=sb.scenes.flatMap(c=>c.shots),focus=CONFIG[slug];
  const frameTargets=focus.shots.map(id=>{
    const s=shots.find(x=>String(x.id).padStart(2,'0')===id);assert(s,'Missing new explanation shot '+slug+'/'+id);
    const n=s.from+Math.floor(s.durationInFrames*.72);
    return {shotId:id,from:s.from,durationInFrames:s.durationInFrames,frame:n,time:n/30};
  });
  const article=fs.readFileSync(path.join(P,'article.mdx'),'utf8');
  const figures=[...article.matchAll(/<Figure\s+[^>]*?seekTo=\{([0-9.]+)\}[^>]*>/g)].map(x=>Number(x[1]));
  assert(figures.length===2&&new Set(figures).size===2,'Expected two distinct actual figure return times: '+slug);
  const sourceLinkFragment=meta.sourcePath;
  const spec={slug,P,D,meta,result,chapters,frameTargets,figures,sourceLinkFragment,
    url:new URL('episodes/'+slug+'/',BASE).href};
  report.episodes.push({slug,sourcePath:meta.sourcePath,videoSHA256:videoSHA,frames:result.frames,
    seconds:result.frames/30,storyboardSHA256:sha(path.join(P,'storyboard.json')),
    articleSHA256:sha(path.join(P,'article.mdx')),chapters,frameTargets,figureSeconds:figures});save();
  return spec;
}
(async()=>{
  const specs=[];for(const slug of SLUGS)specs.push(await loadSpec(slug));
  const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  report.chromiumVersion=browser.version();save();
  try{
    for(const spec of specs){
      const {slug,meta,result,chapters,frameTargets,figures,url}=spec;
      const focusChapter=chapters.find(x=>x.id===CONFIG[slug].chapter);assert(focusChapter,'Missing focus chapter');
      for(const [view,settings] of [
        ['desktop',{viewport:{width:1280,height:900},colorScheme:'light'}],
        ['phone',{viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1,colorScheme:'dark'}]
      ]){
        const context=await browser.newContext({...settings,reducedMotion:'reduce'}),page=await context.newPage();
        page.on('pageerror',e=>{report.pageErrors.push({episode:slug,viewport:view,message:e.message});save();});
        page.on('requestfailed',r=>{if(/\/(video\.mp4|captions\.vtt)(?:$|\?)/.test(r.url())){report.mediaFailures.push({episode:slug,viewport:view,url:r.url(),error:r.failure()?.errorText});save();}});
        const response=await page.goto(url,{waitUntil:'domcontentloaded'});assert(response.status()===200,'Page HTTP '+slug);
        await page.waitForFunction(()=>{const v=document.querySelector('video');return v&&v.readyState>=2&&Number.isFinite(v.duration);});
        const media=await page.locator('video').evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,
          controls:v.controls,playsInline:v.playsInline,tracks:[...v.textTracks].map(t=>({kind:t.kind,mode:t.mode})),source:v.currentSrc,error:v.error?.code??null}));
        assert(Math.abs(media.duration-result.frames/30)<.04&&media.width===1920&&media.height===1080&&media.controls&&media.playsInline&&!media.error,'Media metadata '+slug);
        assert(media.source===new URL('video.mp4',url).href,'Actual video source '+slug);
        assert(media.tracks.length===1&&media.tracks[0].kind==='captions'&&media.tracks[0].mode==='disabled','Native captions default '+slug);
        add(slug,view,'media-metadata',media);
        const actualChapters=await page.locator('.vp').evaluate(e=>JSON.parse(e.dataset.chapters));
        assert(actualChapters.length===chapters.length&&actualChapters.every((c,i)=>c.id===chapters[i].id&&c.title===chapters[i].title&&Math.abs(c.start-chapters[i].start)<.034),'New chapter timeline '+slug);
        add(slug,view,'all-chapters', {chapters:actualChapters});
        const sources=await page.locator('a[href*="github.com"]').evaluateAll(as=>as.map(a=>a.href));
        assert(sources.some(h=>h.endsWith('/'+meta.sourcePath)),'Current source revision link '+slug);add(slug,view,'source-link',{sourcePath:meta.sourcePath});
        await page.locator('video').evaluate(v=>{v.muted=true;});
        await page.locator((view==='desktop'?'.ch':'.chip')+'[data-id="'+focusChapter.id+'"]').click();
        await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.paused&&v.currentTime>=t&&v.currentTime<t+2;},focusChapter.start);
        await page.locator('video').evaluate(v=>v.pause());add(slug,view,'changed-chapter-click-and-playing',{chapter:focusChapter.id,start:focusChapter.start});
        for(const target of frameTargets){
          add(slug,view,'explanation-presented-frame',{shotId:target.shotId,frame:target.frame,...await frame(page,target.time)});
          await shot(page,slug,view+'-shot-'+target.shotId,true);
        }
        await page.evaluate(()=>document.activeElement?.blur());
        const before=await page.locator('video').evaluate(v=>v.currentTime);
        await page.keyboard.press('k');await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.paused&&v.currentTime>t+.08;},before);
        await page.keyboard.press('k');await page.waitForFunction(()=>document.querySelector('video').paused);add(slug,view,'keyboard-play-pause',{startedFrom:before});
        const actualFigureTimes=await page.locator('[data-seek-time]').evaluateAll(es=>es.map(e=>Number(e.dataset.seekTime)));
        assert(actualFigureTimes.length===figures.length&&actualFigureTimes.every((t,i)=>t===figures[i]),'Figure HTML times '+slug);
        for(const t of figures){
          await page.locator(`[data-seek-time="${t}"]`).click();
          await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.paused&&v.currentTime>=t&&v.currentTime<t+2;},t);
          await page.locator('video').evaluate(v=>v.pause());add(slug,view,'figure-return',{target:t,actual:await page.locator('video').evaluate(v=>v.currentTime)});
        }
        if(view==='desktop'){
          const target=frameTargets.at(-1);await frame(page,Math.min(target.time+.5,(result.frames-150)/30-.1));
          await page.evaluate(()=>{const b=document.createElement('button');b.id='qa-native-fullscreen';b.textContent='QA fullscreen gesture';b.style='position:fixed;top:0;right:0;z-index:2147483647';b.onclick=()=>document.querySelector('video').requestFullscreen();document.body.append(b);});
          await page.locator('#qa-native-fullscreen').click();await page.waitForFunction(()=>document.fullscreenElement===document.querySelector('video'));
          await shot(page,slug,'desktop-fullscreen');await page.evaluate(()=>document.exitFullscreen());await page.waitForFunction(()=>!document.fullscreenElement);
          await page.locator('#qa-native-fullscreen').evaluate(e=>e.remove());add(slug,view,'native-fullscreen-enter-exit',{method:'trusted click, native API'});
        }
        const deepTime=frameTargets[0].time,deepUrl=new URL(url);deepUrl.searchParams.set('t',String(deepTime));deepUrl.hash='player';
        await page.goto(deepUrl.href,{waitUntil:'domcontentloaded'});
        await page.waitForFunction(t=>{const v=document.querySelector('video');return Math.abs(v.currentTime-t)<.04&&v.readyState>=2&&!v.seeking;},deepTime);
        add(slug,view,'time-deep-link',{target:deepTime,actual:await page.locator('video').evaluate(v=>v.currentTime)});
        const dims=await page.evaluate(()=>({viewportWidth:innerWidth,documentScrollWidth:document.documentElement.scrollWidth}));
        assert(dims.documentScrollWidth<=dims.viewportWidth+1,'Horizontal overflow '+slug);add(slug,view,'horizontal-bounds',dims);
        await shot(page,slug,view+'-page');await context.close();
      }
    }
    assert(report.pageErrors.length===0,'Browser page errors');
    // Range requests may be aborted normally after seek; retain them as evidence,
    // while the actual ready/playing/frame assertions and video.error check decide playback.
    report.status='passed-functional-actions';report.finishedAt=new Date().toISOString();save();
    console.log(JSON.stringify({status:report.status,episodes:specs.length,actions:report.actions.length,screenshots:report.screenshots.length,mediaRequestFailuresRetained:report.mediaFailures.length}));
  }catch(e){report.status='failed';report.failure=e.stack;report.finishedAt=new Date().toISOString();save();throw e;}
  finally{await browser.close();}
})().catch(e=>{if(report.status!=='failed'){report.status='failed-before-browser';report.failure=e.stack;save();}console.error(e.stack);process.exit(1);});
