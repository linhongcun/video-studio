#!/usr/bin/env node
'use strict';
// QA is read-only with respect to production/publication; report paths are unique.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
let ROOT=__dirname;while(!fs.existsSync(path.join(ROOT,'AGENTS.md')))ROOT=path.dirname(ROOT);
const D=path.resolve(__dirname,'../..'),P=path.join(path.dirname(D),'publication'),SLUG='top-k-frequent-elements';
const args=process.argv.slice(2),arg=(n,d)=>args.includes(n)?args[args.indexOf(n)+1]:d;
const BASE=arg('--base','http://127.0.0.1:4173/video-studio/'),RUN=arg('--run','local-v1');
assert.match(RUN,/^[a-zA-Z0-9_-]+$/);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=b=>crypto.createHash('sha256').update(b).digest('hex'),fileSha=p=>sha(fs.readFileSync(p));
if(!args.includes('--execute')){console.log(JSON.stringify({status:'prepared-not-executed',base:BASE,run:RUN,
  prerequisites:['Exact checked final MP4/bibliography/article staged in publication','Built site preview served at --base'],
  checks:['1440/390 viewports in light and dark','All chapter playback and presented-frame seeks','Native keyboard play/pause and fullscreen','Caption exact text and code/reference boundaries','SourceQuote hover/click/touch/Enter/Escape and source links','Figure exact image SHA, returns, original-image open','Article directory and horizontal bounds'],
  limits:['Chromium touch viewport emulation; no physical phone','Muted playback; no semantic listening or ASR','Local website QA; online identity is separate']},null,2));process.exit(0);}
const OUT=path.join(D,'qa','browser',RUN),REPORT=path.join(D,'qa','browser',RUN+'.json');
assert.ok(!fs.existsSync(REPORT),'Use a unique --run; previous attempts must be retained');fs.mkdirSync(OUT,{recursive:true});
const report={status:'running',startedAt:new Date().toISOString(),base:BASE,executor:'Codex cover/browser child agent; actual Playwright Chromium',
  checks:[],screenshots:[],pageErrors:[],limits:['Local build only; online complete SHA is checked separately.','Headless Chromium desktop and touch/mobile viewport emulation; no physical devices or second engine.','Fullscreen is native API entered through a trusted click on a temporary QA button; native shadow-control geometry is not asserted.','Muted playback and presented-frame checks; no full realtime viewing, semantic listening, ASR, user acceptance or learning-effect claim.']};
const save=()=>fs.writeFileSync(REPORT,JSON.stringify(report,null,2)+'\n');
const record=(view,kind,data)=>{report.checks.push({view,kind,...data});save();};
async function screenshot(page,name){const p=path.join(OUT,name+'.png');await page.screenshot({path:p});report.screenshots.push({path:path.relative(D,p),sha256:fileSha(p)});save();}
async function presented(page,t){
 const result=await page.locator('video').evaluate((v,t)=>new Promise((resolve,reject)=>{v.pause();const timer=setTimeout(()=>reject(Error('presented frame timeout')),15000);const cb=(_,m)=>{if(Math.abs(m.mediaTime-t)<=1/30+.005){clearTimeout(timer);resolve({targetTime:t,mediaTime:m.mediaTime,currentTime:v.currentTime});}else v.requestVideoFrameCallback(cb);};v.requestVideoFrameCallback(cb);v.currentTime=t;}),t);
 await page.waitForFunction(()=>{const v=document.querySelector('video');return !v.seeking&&v.readyState>=2;});return result;
}
async function seek(page,t){await page.locator('video').evaluate((v,t)=>{v.pause();v.currentTime=t;},t);await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.seeking&&v.readyState>=2&&Math.abs(v.currentTime-t)<.025;},t);}
async function main(){
 const meta=read(path.join(P,'meta.json')),result=read(path.join(D,'render-result.json')),sb=read(path.join(P,'storyboard.json'));
 const videoSHA=fileSha(path.join(P,'video.mp4'));assert.equal(videoSHA,fileSha(path.join(D,'video.mp4')));assert.equal(videoSHA,result.sha256??result.videoSha256);assert.equal(meta.finalVideoFrames,result.frames);assert.equal(meta.burnedInCaptions,true);
 const fps=sb.meta.fps,card=sb.meta.unvoicedEndCard,appendix=meta.referenceAppendix;assert.ok(card&&appendix);
 const chapters=sb.scenes.map(s=>({id:s.chapterId??s.id,title:s.title,start:s.from/fps}));
 const expectedTexts=sb.scenes.flatMap(s=>s.shots.flatMap(sh=>sh.subtitles.map(c=>c.text)));
 const references=[...read(path.join(P,'references.json')).sources,...(fs.existsSync(path.join(P,'article-sources.json'))?read(path.join(P,'article-sources.json')).sources:[])];
 const article=fs.readFileSync(path.join(P,'article.mdx'),'utf8');assert.equal(fileSha(path.join(P,'article.mdx')),fileSha(path.join(D,'article.mdx')));
 report.identity={slug:SLUG,frames:result.frames,videoSha256:videoSHA,storyboardSha256:fileSha(path.join(P,'storyboard.json')),articleSha256:fileSha(path.join(P,'article.mdx')),sourcePath:meta.sourcePath,chapters};save();
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});report.chromium=browser.version();
 try{for(const width of [1440,390])for(const theme of ['light','dark']){
  const view=`${width}-${theme}`,context=await browser.newContext({viewport:{width,height:900},colorScheme:theme,isMobile:width<768,hasTouch:width<768,reducedMotion:'reduce'});
  await context.addInitScript(t=>localStorage.setItem('vs:theme',t),theme);const page=await context.newPage();page.setDefaultTimeout(15000);
  page.on('pageerror',e=>{report.pageErrors.push({view,message:e.message});save();});
  const url=new URL(`episodes/${SLUG}/`,BASE).href;assert.equal((await page.goto(url,{waitUntil:'load'})).status(),200);
  await page.waitForFunction(()=>document.querySelector('video')?.readyState>=2);const video=page.locator('video');await video.evaluate(v=>{v.muted=true;});
  assert.equal((await page.locator('h1').textContent()).trim(),meta.title);
  const media=await video.evaluate(v=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,controls:v.controls,playsInline:v.playsInline,source:v.currentSrc,tracks:[...v.textTracks].map(t=>({kind:t.kind,mode:t.mode}))}));
  assert.deepEqual([media.width,media.height],[1920,1080]);assert.ok(media.controls&&media.playsInline&&Math.abs(media.duration-result.frames/fps)<.04);assert.equal(media.source,new URL('video.mp4',url).href);assert.deepEqual(media.tracks,[{kind:'captions',mode:'disabled'}]);record(view,'media',media);
  const data=await page.locator('#player').evaluate(e=>JSON.parse(e.dataset.chapters));assert.equal(data.length,chapters.length);data.forEach((c,i)=>{assert.equal(c.id,chapters[i].id);assert.ok(Math.abs(c.start-chapters[i].start)<.034);});
  for(const c of chapters){const link=page.locator(`.${width<768?'chip':'ch'}[data-id="${c.id}"]`);await link.click();await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.paused&&v.currentTime>=t&&v.currentTime<t+2;},c.start);await video.evaluate(v=>v.pause());record(view,'chapter-playing',{id:c.id,start:c.start,actual:await video.evaluate(v=>v.currentTime)});}
  const key=Math.min(card.from-1,Math.floor((chapters[Math.min(2,chapters.length-1)].start+1)*fps));record(view,'presented-explanation-frame',await presented(page,key/fps));
  await page.evaluate(()=>document.activeElement?.blur());const before=await video.evaluate(v=>v.currentTime);await page.keyboard.press('k');await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.paused&&v.currentTime>t+.08;},before);await page.keyboard.press('k');await page.waitForFunction(()=>document.querySelector('video').paused);record(view,'keyboard-play-pause',{startedFrom:before});
  await video.evaluate(v=>{v.textTracks[0].mode='showing';});await page.waitForFunction(()=>document.querySelector('video').textTracks[0].cues?.length>0);
  const cues=await video.evaluate(v=>[...v.textTracks[0].cues].map(c=>({text:c.text,start:c.startTime,end:c.endTime})));assert.deepEqual(cues.map(c=>c.text),expectedTexts);assert.ok(cues.every(c=>c.end<card.from/fps));
  for(const t of [card.from/fps-.001,card.from/fps,card.from/fps+.001,(card.from+75)/fps,appendix.from/fps,(appendix.from+75)/fps,(result.frames-1)/fps]){await seek(page,t);const active=await video.evaluate(v=>[...v.textTracks[0].activeCues].map(c=>c.text));assert.deepEqual(active,cues.filter(c=>c.start<=t&&t<c.end).map(c=>c.text));if(t>=card.from/fps)assert.deepEqual(active,[]);record(view,'caption-boundary',{time:t,active});}
  await video.evaluate(v=>{v.textTracks[0].mode='disabled';});
  for(const [name,t]of [['python',(card.from+75)/fps],['references',(appendix.from+75)/fps]]){record(view,'presented-'+name,await presented(page,t));await screenshot(page,view+'-'+name);}
  await page.evaluate(()=>{const b=document.createElement('button');b.id='qa-native-fullscreen';b.textContent='QA fullscreen';b.style='position:fixed;top:0;right:0;z-index:2147483647';b.onclick=()=>document.querySelector('video').requestFullscreen();document.body.append(b);});await page.locator('#qa-native-fullscreen').click();await page.waitForFunction(()=>document.fullscreenElement===document.querySelector('video'));await screenshot(page,view+'-native-fullscreen');await page.evaluate(()=>document.exitFullscreen());await page.waitForFunction(()=>!document.fullscreenElement);await page.locator('#qa-native-fullscreen').evaluate(e=>e.remove());record(view,'native-fullscreen',{enteredAndExited:true});
  const triggers=page.locator('[data-source-trigger]');assert.ok(await triggers.count()>0);
  for(let i=0;i<await triggers.count();i++){
   const trigger=triggers.nth(i),id=await trigger.getAttribute('data-source-trigger'),source=references.find(s=>s.id===id),panel=page.locator(`aside[data-source-panel="${id}"]`);assert.ok(source?.quotation?.text);await trigger.scrollIntoViewIfNeeded();
   if(width>=768){await trigger.hover();await page.waitForFunction(id=>document.querySelector(`aside[data-source-panel="${id}"]`).matches(':popover-open'),id);await trigger.click();}else await trigger.tap();
   await page.waitForFunction(id=>document.querySelector(`aside[data-source-panel="${id}"]`).matches(':popover-open'),id);assert.equal((await panel.locator('blockquote').textContent()).trim(),source.quotation.text.trim());assert.equal(await panel.locator('cite a').getAttribute('href'),source.url);
   const bounds=await panel.boundingBox();assert.ok(bounds.x>=3&&bounds.y>=3&&bounds.x+bounds.width<=width-3&&bounds.y+bounds.height<=897);if(i===0)await screenshot(page,view+'-quote');
   await page.keyboard.press('Escape');await page.waitForFunction(id=>!document.querySelector(`aside[data-source-panel="${id}"]`).matches(':popover-open'),id);await page.mouse.move(0,0);await trigger.focus();await page.keyboard.press('Enter');await page.waitForFunction(id=>document.querySelector(`aside[data-source-panel="${id}"]`).matches(':popover-open'),id);await panel.locator('cite a').focus();assert.ok(await panel.locator('cite a').evaluate(e=>e===document.activeElement));await panel.getByRole('button',{name:'关闭原文与出处'}).click();await page.waitForFunction(id=>!document.querySelector(`aside[data-source-panel="${id}"]`).matches(':popover-open'),id);record(view,'sourcequote',{id,hover:width>=768,touch:width<768,keyboardOpenEscapeClose:true,bounds,sourceUrl:source.url});
  }
  const figures=page.locator('figure.fig');assert.ok(await figures.count()>0);
  for(let i=0;i<await figures.count();i++){
   const figure=figures.nth(i),img=figure.locator('img'),src=await img.getAttribute('src');await figure.scrollIntoViewIfNeeded();await img.evaluate(n=>n.decode());const local=path.join(P,src.split(`/episodes/${SLUG}/`)[1]);const response=await context.request.get(new URL(src,BASE).href);assert.equal(response.status(),200);assert.equal(sha(await response.body()),fileSha(local));const link=figure.locator('[data-seek-time]'),time=Number(await link.getAttribute('data-seek-time'));assert.ok(time>=0&&time<card.from/fps);await link.click();await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.paused&&v.currentTime>=t&&v.currentTime<t+2;},time);await video.evaluate(v=>v.pause());record(view,'figure-return',{index:i,src,time,actual:await video.evaluate(v=>v.currentTime),sha256:fileSha(local)});if(i===0)await screenshot(page,view+'-figure-return');
  }
  const original=page.locator('figure.fig .fig-image-link').first(),originalUrl=new URL(await original.getAttribute('href'),BASE).href;await original.click();await page.waitForURL(originalUrl);assert.ok(await page.locator('img').first().evaluate(n=>n.complete&&n.naturalWidth>0));await page.goBack({waitUntil:'load'});record(view,'original-image',{url:originalUrl,opened:true});
  const toc=page.locator('.toc');if(!await toc.evaluate(e=>e.open))await toc.locator('summary').click();const entries=await page.locator('[data-toc]').evaluateAll(es=>es.map(e=>({id:e.dataset.toc,text:e.textContent})));assert.ok(entries.length>0);for(const e of entries)assert.ok(await page.locator(`[id="${e.id}"]`).count()>0);const last=entries.at(-1);await page.locator(`[data-toc="${last.id}"]`).click();assert.equal(decodeURIComponent(new URL(page.url()).hash),'#'+last.id);record(view,'article-directory',{entries,lastClicked:last.id});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);assert.ok(overflow<=1);record(view,'horizontal-bounds',{overflow});await screenshot(page,view+'-article');await context.close();
 }
 assert.deepEqual(report.pageErrors,[]);report.status='passed-functional-actions';report.finishedAt=new Date().toISOString();report.actualScreenshotReviewPending=true;save();console.log(JSON.stringify({status:report.status,checks:report.checks.length,screenshots:report.screenshots.length}));
 }finally{await browser.close();}
}
main().catch(e=>{report.status='failed';report.failure=e.stack;report.finishedAt=new Date().toISOString();save();console.error(e.stack);process.exitCode=1;});
