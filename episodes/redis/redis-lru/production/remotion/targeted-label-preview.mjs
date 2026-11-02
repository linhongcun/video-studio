import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const R=path.dirname(fileURLToPath(import.meta.url)),D=path.dirname(R);
const require=createRequire(path.join(R,'package.json'));
const {bundle}=require('@remotion/bundler');
const {renderStill,selectComposition,openBrowser,renderMedia}=require('@remotion/renderer');
const webpack=require('webpack');
const board=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'))),shots=board.scenes.flatMap(s=>s.shots);
const noCaptions=process.argv.includes('--no-captions');const inputProps={hideSubtitles:noCaptions,showSubtitles:!noCaptions};
const out=path.join(D,'qa-self/independent-pressure-label-fix',noCaptions?'no-captions':'captions');fs.mkdirSync(out,{recursive:true});
const clips=process.argv.includes('--clips');
const selected=process.argv.find(a=>a.startsWith('--frames='));
const specific={
 '01':[0,180,300],'02':[40,190,330],'03':[60,160,280,400],'04':[100,250,380],
 '05':[40,100,160,210,270],'06':[45,100,155,210,250,310],
 '07':[45,110,170,230,285],'08':[50,115,180,245,340],
 '09':[60,120,195,250,375],'10':[70,170,225,310],'11':[100,260,400],'12':[60,200,330,415],
};
const frames=selected?selected.split('=')[1].split(',').map(Number):shots.flatMap(s=>(specific[s.id]??[0,s.durationInFrames/2]).map(l=>s.from+Math.min(Math.floor(l),s.durationInFrames-1)));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const before={main:hash(path.join(R,'src/Main.tsx')),board:hash(path.join(D,'storyboard.json')),model:hash(path.join(D,'model.json')),voice:hash(path.join(D,'voice.wav'))};
const report={kind:'author-targeted-pressure-label-fix-preview',actualTiming:true,actualAudio:clips,sourceSHA256:before,frames:[],dom:[],clips:[],violations:[],reviewLimits:'Author inspection, not independent review, encoded final media or ASR/listening.'};
const url=await bundle({entryPoint:path.join(R,'src/index.ts'),publicDir:path.join(R,'public'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json')},modules:[path.join(R,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:true})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
let current=null;
const original=browser.newPage.bind(browser);
browser.newPage=async opts=>{const page=await original(opts),close=page.close.bind(page);page.close=async closeOpts=>{
 if(current!==null&&!page.closed){
  const r=await page.evaluate(async()=>{await document.fonts.ready;const svg=document.querySelector('svg[data-frame]');if(!svg)return null;const base=svg.getBoundingClientRect(),sx=base.width/1920,sy=base.height/1080;const texts=[];const visible=e=>{let n=e,a=1;while(n){const s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden')return false;a*=Number(s.opacity);n=n.parentElement;}return a>.05;};
   for(const e of svg.querySelectorAll('text')){if(!visible(e)||!e.textContent?.trim())continue;const q=e.getBoundingClientRect();texts.push({text:e.textContent,x:(q.x-base.x)/sx,y:(q.y-base.y)/sy,w:q.width/sx,h:q.height/sy,subtitle:!!e.closest('[data-subtitle]')});}
   const movers=[...svg.querySelectorAll('[data-moving-body]')].filter(visible).map(e=>{const q=e.getBoundingClientRect();return{x:(q.x-base.x)/sx,y:(q.y-base.y)/sy,w:q.width/sx,h:q.height/sy};});
   const state=svg.querySelector('[data-model-state]')?.getAttribute('data-model-state');const violations=texts.filter(t=>t.x<30||t.x+t.w>1890||t.y<15||t.y+t.h>1058).map(t=>({kind:'outside',...t}));
   const subtitle=svg.querySelector('[data-subtitle]');if(subtitle){const b=subtitle.getBoundingClientRect();const top=(b.y-base.y)/sy;violations.push(...texts.filter(t=>!t.subtitle&&t.y+t.h>top-6).map(t=>({kind:'subtitleOverlap',...t})));}
   const pressure=texts.filter(t=>t.text.replace(/\s/g,'').startsWith('写入J'));for(const b of movers)for(const t of pressure){const w=Math.min(b.x+b.w,t.x+t.w)-Math.max(b.x,t.x),h=Math.min(b.y+b.h,t.y+t.h)-Math.max(b.y,t.y);if(w>1&&h>1)violations.push({kind:'moving-sample-pressure-text-overlap',w,h});}
   return {state,texts,movers,violations,fontsLoaded:document.fonts.status==='loaded'};
  });if(r){report.dom.push({frame:current,...r});report.violations.push(...r.violations.map(v=>({frame:current,...v})));}
 }await close(closeOpts);};return page;};
try{
 const composition=await selectComposition({serveUrl:url,id:'Main',inputProps,puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',logLevel:'error'});
 if(!clips){for(const frame of frames){current=frame;const file=path.join(out,`frame-${String(frame).padStart(6,'0')}.png`);await renderStill({composition,serveUrl:url,inputProps,frame,output:file,scale:.5,imageFormat:'png',puppeteerInstance:browser,logLevel:'error'});report.frames.push({frame,file,sha256:hash(file)});console.log(frame);}}
 else{
  for(const [name,a,b] of [['pool-to-eviction',1775+140,2102+230],['retained-to-D',2399+90,2752+270],['ghost-existence',3144+30,3470]]){
   current=null;const file=path.join(out,name+'.mp4');await renderMedia({composition,serveUrl:url,codec:'h264',outputLocation:file,frameRange:[a,b],scale:.5,concurrency:1,crf:22,puppeteerInstance:browser,logLevel:'error'});report.clips.push({name,file,from:a,to:b,sha256:hash(file)});console.log(name);
  }
 }
 report.passed=report.violations.length===0;
 for(const [k,p] of Object.entries({main:path.join(R,'src/Main.tsx'),board:path.join(D,'storyboard.json'),model:path.join(D,'model.json'),voice:path.join(D,'voice.wav')})){if(hash(p)!==before[k])throw Error('Source changed during self preview: '+k);}
}catch(error){report.passed=false;report.failure=String(error);throw error;}finally{await browser.close({silent:true});fs.writeFileSync(path.join(out,clips?'clips-report.json':'preview-report.json'),JSON.stringify(report,null,2)+'\n');}
