const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const R='/workspace/video-studio',D=path.join(R,'episodes/puzzles/pirate-gold/production/revisions/motivation-20261107/pirate-gold');
const BASE=process.env.PIRATE_QA_BASE_URL||'http://127.0.0.1:4173/video-studio/episodes/pirate-gold/';
const RUN=process.env.PIRATE_QA_RUN_NAME||'browser-local-v1';const OUT=path.join(D,'qa',RUN);fs.mkdirSync(OUT,{recursive:true});
const sb=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'))),expected=sb.scenes.map(x=>({id:x.id,start:x.from/30,title:x.title}));
const report={status:'running',startedAt:new Date().toISOString(),url:BASE,executor:'Codex primary, actual Chromium/Playwright',actions:[],errors:[],screenshots:[],limitations:['Desktop and touch/mobile viewport emulation in headless Chromium; no physical phone or other browser engines.','Fullscreen is checked with an actual trusted click invoking the native video requestFullscreen API; native shadow-control geometry is not asserted.']};
const file=path.join(D,'qa',RUN+'.json');const save=()=>fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n');
const add=(kind,data)=>{report.actions.push({kind,...data});save();};const assert=(b,m)=>{if(!b)throw Error(m);};
const shot=async(page,name,videoOnly=false)=>{const p=path.join(OUT,name+'.png');if(videoOnly)await page.locator('video').screenshot({path:p});else await page.screenshot({path:p});report.screenshots.push({path:path.relative(D,p),sha256:crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')});save();};
async function frame(page,time){
 const result=await page.locator('video').evaluate((v,t)=>new Promise((resolve,reject)=>{
  v.pause();const timer=setTimeout(()=>reject(Error('seek/video-frame timeout')),12000);
  v.requestVideoFrameCallback((now,m)=>{clearTimeout(timer);resolve({mediaTime:m.mediaTime,currentTime:v.currentTime,readyState:v.readyState,width:v.videoWidth,height:v.videoHeight});});v.currentTime=t;
 }),time);
 assert(Math.abs(result.mediaTime-time)<=1/30+.005,'Exact seek frame differs: '+JSON.stringify(result));return result;
}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});report.chromiumVersion=browser.version();save();
 try{
  for(const [name,settings] of [['desktop',{viewport:{width:1280,height:900},colorScheme:'light'}],['phone',{viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1,colorScheme:'dark'}]]){
   const context=await browser.newContext({...settings,reducedMotion:'reduce'}),page=await context.newPage();
   page.on('pageerror',e=>{report.errors.push({viewport:name,message:e.message});save();});
   const response=await page.goto(BASE,{waitUntil:'domcontentloaded'});assert(response.status()===200,'page HTTP');
   await page.waitForFunction(()=>{const v=document.querySelector('video');return v&&v.readyState>=2&&Number.isFinite(v.duration);});
   const meta=await page.locator('video').evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,controls:v.controls,playsInline:v.playsInline,tracks:[...v.textTracks].map(t=>({kind:t.kind,mode:t.mode})),source:v.currentSrc,error:v.error?.code??null}));
   assert(Math.abs(meta.duration-5377/30)<.04&&meta.width===1920&&meta.height===1080&&meta.controls&&meta.playsInline&&!meta.error,'media metadata');
   assert(meta.tracks.length===1&&meta.tracks[0].mode==='disabled','burned-in captions default');add('metadata',{viewport:name,...meta});
   const chapters=await page.locator('.vp').evaluate(e=>JSON.parse(e.dataset.chapters));
   assert(chapters.length===4&&chapters.every((c,i)=>c.id===expected[i].id&&Math.abs(c.start-expected[i].start)<.034),'chapter timeline');assert(chapters[1].title.includes('为什么'),'motivation chapter label');add('chapters',{viewport:name,chapters});
   await page.locator('video').evaluate(v=>{v.muted=true;});
   await page.locator((name==='desktop'?'.ch':'.chip')+'[data-id="backwards"]').click();
   await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.paused&&v.currentTime>=t&&v.currentTime<t+2;},expected[1].start);
   await page.locator('video').evaluate(v=>v.pause());add('chapter-click-and-playing',{viewport:name,start:expected[1].start});
   const exact=await frame(page,(1077+590)/30);add('motivation-exact-frame',{viewport:name,...exact});await shot(page,name+'-motivation',true);
   await page.evaluate(()=>document.activeElement?.blur());const before=await page.locator('video').evaluate(v=>v.currentTime);await page.keyboard.press('k');await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.paused&&v.currentTime>t+.08;},before);await page.keyboard.press('k');await page.waitForFunction(()=>document.querySelector('video').paused);add('play-pause-keyboard',{viewport:name});
   for(const t of [114,159.5]){
    await page.locator(`[data-seek-time="${t}"]`).click();await page.waitForFunction(t=>document.querySelector('video').currentTime>=t&&document.querySelector('video').currentTime<t+2,t);await page.locator('video').evaluate(v=>v.pause());add('figure-return',{viewport:name,target:t,actual:await page.locator('video').evaluate(v=>v.currentTime)});
   }
   if(name==='desktop'){
    await frame(page,(1077+640)/30);
    await page.evaluate(()=>{const b=document.createElement('button');b.id='qa-native-fullscreen';b.textContent='QA fullscreen gesture';b.style='position:fixed;top:0;right:0;z-index:2147483647';b.onclick=()=>document.querySelector('video').requestFullscreen();document.body.append(b);});
    await page.locator('#qa-native-fullscreen').click();await page.waitForFunction(()=>document.fullscreenElement===document.querySelector('video'));await shot(page,'desktop-fullscreen');await page.evaluate(()=>document.exitFullscreen());await page.waitForFunction(()=>!document.fullscreenElement);await page.locator('#qa-native-fullscreen').evaluate(e=>e.remove());add('native-fullscreen-enter-exit',{viewport:name});
   }
   await page.goto(BASE+'?t=55.5#player',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>{const v=document.querySelector('video');return Math.abs(v.currentTime-55.5)<.04&&v.readyState>=2&&!v.seeking;});add('time-deep-link',{viewport:name,time:55.5});
   const dims=await page.evaluate(()=>({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth}));assert(dims.scrollWidth<=dims.viewport+1,'page horizontal overflow');add('horizontal-bounds',{viewport:name,...dims});await shot(page,name+'-page');await context.close();
  }
  assert(report.errors.length===0,'browser page errors');report.status='passed';report.finishedAt=new Date().toISOString();save();console.log(JSON.stringify({status:report.status,actions:report.actions.length,screenshots:report.screenshots.length}));
 }catch(e){report.status='failed';report.failure=e.stack;save();throw e;}finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1);});
