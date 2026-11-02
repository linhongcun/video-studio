import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const D=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const R=path.join(D,'remotion');const require=createRequire(path.join(R,'package.json'));
const {bundle}=require('@remotion/bundler');const {openBrowser,selectComposition,renderStill,renderMedia}=require('@remotion/renderer');
const board=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json')));const timings=JSON.parse(fs.readFileSync(path.join(D,'model-timing.json')));
const out=path.join(D,process.argv.includes('--motion-only')?'qa-self/motion-current':process.argv.includes('--ping-fix')?'qa-self/ping-after':'qa-self');fs.mkdirSync(out,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const requested=process.argv.find(a=>a.startsWith('--frames='));
const frames=process.argv.includes('--motion-only')?[]:requested?requested.slice(9).split(',').map(Number):[...new Set([0,...Object.values(timings.shots).flatMap(windows=>windows.flatMap(w=>[Math.min(w.globalTo-1,w.globalFrom+Math.round((w.to-w.from)*.3)),w.globalTo-1]))])].sort((a,b)=>a-b);
const sourcePaths=['remotion/scripts/qa.mjs','remotion/package.json','remotion/package-lock.json','remotion/src/Main.tsx','remotion/src/Root.tsx','model.json','model-timing.json','storyboard.json'];const sources=Object.fromEntries(sourcePaths.map(p=>[p,sha(path.join(D,p))]));
const report={status:'running',scope:'Author actual still/DOM review, separate from independent QA and final media',sourceSHA256:sources,frames,samples:[],dom:[],browserErrors:[]};
const serveUrl=await bundle({entryPoint:path.join(R,'src/index.ts'),publicDir:path.join(R,'public'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,modules:[path.join(R,'node_modules'),'node_modules']}})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});let currentFrame;
const newPage=browser.newPage.bind(browser);browser.newPage=async options=>{
 const page=await newPage(options),close=page.close.bind(page);page.close=async options=>{
  if(Number.isInteger(currentFrame)&&!page.closed){
   const snapshot=await page.evaluate(async()=>{
    await document.fonts.ready;const svg=document.querySelector('[data-canvas]');if(!svg)return null;
    const base=svg.getBoundingClientRect(),sx=1920/base.width,sy=1080/base.height;
    const visible=e=>{let a=1;for(let n=e;n;n=n.parentElement){const c=getComputedStyle(n);a*=Number(c.opacity);if(c.display==='none'||c.visibility==='hidden')return false;}return a>.03;};
    const texts=[...svg.querySelectorAll('[data-text]')].filter(visible).map(e=>{const b=e.getBoundingClientRect();return{text:e.textContent,x:(b.x-base.x)*sx,y:(b.y-base.y)*sy,w:b.width*sx,h:b.height*sy,subtitle:!!e.closest('[data-subtitle]')};});
    const violations=texts.filter(t=>t.x<35||t.y<15||t.x+t.w>1885||t.y+t.h>1074).map(t=>({kind:'outside',text:t}));
    for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){const a=texts[i],b=texts[j];if(Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>2&&Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>2)violations.push({kind:'text-overlap',a,b});}
    return{state:svg.getAttribute('data-model-state'),phase:svg.getAttribute('data-state-phase'),visualState:JSON.parse(svg.getAttribute('data-visual-state')),texts,violations};
   });if(snapshot)report.dom.push({frame:currentFrame,...snapshot});
  }return close(options);
 };return page;
};
try{
 const inputProps={hideCaptions:false};const composition=await selectComposition({serveUrl,id:'Main',browserExecutable:'/usr/bin/chromium',puppeteerInstance:browser,inputProps,logLevel:'error'});
 for(const frame of frames){currentFrame=frame;const file=path.join(out,`frame-${String(frame).padStart(6,'0')}.png`);await renderStill({composition,serveUrl,frame,output:file,scale:.5,imageFormat:'png',browserExecutable:'/usr/bin/chromium',puppeteerInstance:browser,inputProps,logLevel:'error',onBrowserLog:e=>{if(e.type==='error')report.browserErrors.push(e);}});report.samples.push({frame,file:path.relative(D,file),sha256:sha(file)});}
 currentFrame=null;
 if(process.argv.includes('--motion')||process.argv.includes('--motion-promotion')){
  const noCaptionProps={hideCaptions:true};
  const noCaptionComposition=await selectComposition({serveUrl,id:'Main',browserExecutable:'/usr/bin/chromium',puppeteerInstance:browser,inputProps:noCaptionProps,logLevel:'error'});
  noCaptionComposition.props={...noCaptionComposition.props,...noCaptionProps};
  if(noCaptionComposition.props.hideCaptions!==true)throw Error('No-caption resolved props were not true');
  currentFrame=2351;
  await renderStill({composition:noCaptionComposition,serveUrl,frame:2351,output:path.join(out,'no-caption-proof.png'),scale:.5,imageFormat:'png',browserExecutable:'/usr/bin/chromium',puppeteerInstance:browser,inputProps:noCaptionProps,logLevel:'error'});
  const proof=report.dom[report.dom.length-1];if(!proof||proof.texts.some(t=>t.subtitle))throw Error('Actual no-caption proof still contains subtitle text');
  report.noCaptionProof={frame:2351,resolvedCompositionProps:noCaptionComposition.props,visibleSubtitles:proof.texts.filter(t=>t.subtitle).length,file:'no-caption-proof.png'};currentFrame=null;
  const shots=board.scenes.flatMap(s=>s.shots);
  for(const [a,b,name]of[['06','08','authorization'],['09','11','promotion']]){
   if(process.argv.includes('--motion-promotion')&&name!=='promotion')continue;
   const first=shots.find(s=>s.id===a),last=shots.find(s=>s.id===b);const file=path.join(out,`motion-${name}.mp4`);
   await renderMedia({composition:noCaptionComposition,serveUrl,codec:'h264',outputLocation:file,scale:.5,frameRange:[first.from,last.from+last.durationInFrames-1],concurrency:1,crf:24,browserExecutable:'/usr/bin/chromium',puppeteerInstance:browser,inputProps:{hideCaptions:true},logLevel:'error'});
   report[name]={file:path.relative(D,file),from:first.from,to:last.from+last.durationInFrames-1,sha256:sha(file)};
  }
 }
 for(const [p,h]of Object.entries(sources))if(sha(path.join(D,p))!==h)throw Error('Input changed during author QA: '+p);
 report.status=report.dom.every(d=>d.violations.length===0)&&report.browserErrors.length===0?'passed':'needs-review';
}catch(error){report.status='failed';report.error=String(error);throw error;}
finally{fs.writeFileSync(path.join(out,'render-report.json'),JSON.stringify(report,null,2)+'\n');await browser.close({silent:true});}
console.log(JSON.stringify({status:report.status,samples:report.samples.length,dom:report.dom.length,violations:report.dom.flatMap(d=>d.violations).length,browserErrors:report.browserErrors.length}));
