const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
(async()=>{
 const base=process.argv[2]||'http://127.0.0.1:4321';
 const out=process.argv[3]||'/workspace/work/twelve-balls-review/site-local';
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const report={base,viewports:[],limitations:['Desktop Chromium with simulated mobile viewport; no physical phone or semantic audio listening.']};
 for(const mode of [{id:'desktop',viewport:{width:1440,height:1000},colorScheme:'dark'},{id:'mobile',viewport:{width:390,height:844},colorScheme:'light',isMobile:true,hasTouch:true}]){
  const {id,...settings}=mode; const context=await browser.newContext({...settings,reducedMotion:'reduce'});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/video-studio/episodes/twelve-balls/',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>{const v=document.querySelector('video');return v&&v.readyState>=2&&Number.isFinite(v.duration)});
  const details=await page.evaluate(()=>({duration:document.querySelector('video').duration,chapters:JSON.parse(document.querySelector('.vp').dataset.chapters),captionMode:[...document.querySelector('video').textTracks].map(t=>t.mode),figures:document.querySelectorAll('figure.fig').length,quotes:document.querySelectorAll('.source-trigger').length,overflow:document.documentElement.scrollWidth>innerWidth+1}));
  if(Math.abs(details.duration-160.633333)>0.08||details.chapters.length!==5||details.figures!==2||details.quotes!==2||details.overflow||details.captionMode.some(m=>m==='showing'))throw Error(JSON.stringify(details));
  const checks=[];
  for(const c of details.chapters){
   const target=page.locator(`${mode.id==='mobile'?'.chip':'.ch'}[data-id="${c.id}"]`);
   await target.click();await page.locator('video').evaluate(v=>v.pause());
   await page.waitForFunction(t=>Math.abs(document.querySelector('video').currentTime-t)<.4,c.start);
   checks.push({chapter:c.id,currentTime:await page.locator('video').evaluate(v=>v.currentTime)});
  }
  for(const t of [46,71]){
   await page.locator(`a[data-seek-time="${t}"]`).click();await page.locator('video').evaluate(v=>v.pause());
   await page.waitForFunction(t=>Math.abs(document.querySelector('video').currentTime-t)<.4,t);
   checks.push({figureSeek:t,currentTime:await page.locator('video').evaluate(v=>v.currentTime)});
  }
  if(mode.id==='desktop'){ await page.locator('button[data-source-trigger="R1"]').hover(); await page.waitForFunction(()=>document.querySelector('[data-source-panel="R1"]').matches(':popover-open')); await page.screenshot({path:path.join(out,'desktop-hover-R1.png')}); await page.keyboard.press('Escape'); await page.mouse.move(0,0); }
  for(const id of ['R1','R2']){
   await page.locator(`button[data-source-trigger="${id}"]`).click();
   await page.waitForFunction(id=>document.querySelector(`[data-source-panel="${id}"]`).matches(':popover-open'),id);
   const bounds=await page.locator(`[data-source-panel="${id}"]`).boundingBox();
   if(!bounds||bounds.x<0||bounds.x+bounds.width>mode.viewport.width+1)throw Error('Citation overflow');
   await page.screenshot({path:path.join(out,mode.id+'-'+id+'.png')});
   await page.keyboard.press('Escape');
  }
  await page.locator('button[data-source-trigger="R1"]').focus();await page.keyboard.press('Enter');
  await page.waitForFunction(()=>document.querySelector('[data-source-panel="R1"]').matches(':popover-open'));await page.keyboard.press('Escape');
  for(const t of [46,71,140,157]){
   await page.locator('video').evaluate((v,t)=>{v.pause();v.currentTime=t},t);
   await page.waitForFunction(t=>{const v=document.querySelector('video');return !v.seeking&&Math.abs(v.currentTime-t)<.06},t);
   await page.locator('video').scrollIntoViewIfNeeded();
   await page.locator('video').screenshot({path:path.join(out,mode.id+'-video-'+t+'.png')});
  }
  for(const img of await page.locator('figure.fig img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode())} await page.locator('figure.fig').first().scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>[...document.querySelectorAll('figure.fig img')].every(i=>i.complete&&i.naturalWidth>0));
  await page.screenshot({path:path.join(out,mode.id+'-article.png')});
  if(mode.id==='mobile')await page.setViewportSize({width:844,height:390}); await page.locator('video').scrollIntoViewIfNeeded();await page.locator('video').click();await page.locator('video').evaluate(v=>{v.pause();v.currentTime=157;return v.requestFullscreen()});
  await page.waitForFunction(()=>document.fullscreenElement?.tagName==='VIDEO'); await page.waitForFunction(()=>{const v=document.querySelector('video');return !v.seeking&&v.readyState>=2&&Math.abs(v.currentTime-157)<.06});
  await page.screenshot({path:path.join(out,mode.id+'-fullscreen-reference.png')});await page.evaluate(()=>document.exitFullscreen());
  report.viewports.push({id:mode.id,details,checks,pageErrors:errors});if(errors.length)throw Error(errors.join('\n'));
  await context.close();
 }
 await browser.close();fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exit(1)});
