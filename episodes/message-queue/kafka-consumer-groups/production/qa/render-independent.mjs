// Independent read-only source rendering. No production or frozen input is changed.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const D=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const REM=path.join(D,'remotion');
const require=createRequire(path.join(REM,'package.json'));
const {bundle}=require('@remotion/bundler');
const {openBrowser,selectComposition,renderStill,renderMedia}=require('@remotion/renderer');
const webpack=require('webpack');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const OUT=path.resolve(process.argv[2]??path.join(D,'qa/preflight-independent'));
fs.mkdirSync(OUT,{recursive:true});
const sb=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));
const shots=sb.scenes.flatMap(s=>s.shots);
const args=process.argv.slice(3);
const get=k=>args.find(s=>s.startsWith(k+'='))?.slice(k.length+1);
const picked=(get('--shots')??shots.map(s=>s.id).join(',')).split(',').map(Number);
let frame=0;const samples=[];
for(const s of shots){
 const start=frame;frame+=s.durationInFrames;
 if(!picked.includes(Number(s.id)))continue;
 const locals=new Set([0,1,Math.floor(s.durationInFrames/4),Math.floor(s.durationInFrames/2),Math.floor(s.durationInFrames*3/4),s.durationInFrames-2,s.durationInFrames-1]);
 for(let f=0;f<s.durationInFrames;f+=20)locals.add(f);
 for(const v of s.voice??[])for(const n of [v.localStart,v.localEnd])for(const a of [-1,0,1])locals.add(Math.max(0,Math.min(s.durationInFrames-1,Math.ceil(n)+a)));
 for(const f of [...locals].sort((a,b)=>a-b))samples.push({shot:s.id,local:f,frame:start+f});
}
for(const raw of (get('--frames')??'').split(',').filter(Boolean)){const n=Number(raw);let a=0;for(const s of shots){if(n>=a&&n<a+s.durationInFrames)samples.push({shot:s.id,local:n-a,frame:n,reason:'explicit-article-or-boundary'});a+=s.durationInFrames;}}
const files=['remotion/src/Main.tsx','remotion/src/data.ts','remotion/src/theme.ts','storyboard.json','words.json','script.md','plan.json','model.json'].filter(p=>fs.existsSync(path.join(D,p)));
const identities=Object.fromEntries(files.map(p=>[p,sha(path.join(D,p))]));
const props={showSubtitles:false,hideSubtitles:true};
const report={createdAt:new Date().toISOString(),executor:'Codex independent QA agent',props,sourceHashes:identities,samples:[],browserLogs:[],renderedClips:[],pass:false,visualReviewed:false};
const save=()=>fs.writeFileSync(path.join(OUT,'report.json'),JSON.stringify(report,null,2)+'\n');
save();
const serveUrl=await bundle({entryPoint:path.join(REM,'src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(REM,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
let metrics=null,cur=null;
const newPage=browser.newPage.bind(browser);
browser.newPage=async(opts)=>{const p=await newPage(opts);const close=p.close.bind(p);p.close=async(args)=>{
 if(cur)metrics=await p.evaluate(()=>{
  const visible=e=>{let q=e,o=1;while(q){const c=getComputedStyle(q);if(c.display==='none'||c.visibility==='hidden')return false;o*=Number(c.opacity);q=q.parentElement;}return o>.1};
  const texts=[...document.querySelectorAll('[data-copyfit]')].filter(visible).map(e=>{const b=e.getBoundingClientRect();const r=document.createRange();r.selectNodeContents(e);const ink=r.getBoundingClientRect();return {text:e.textContent,tag:e.tagName,x:b.x,y:b.y,w:b.width,h:b.height,ink:{x:ink.x,y:ink.y,w:ink.width,h:ink.height},scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,moving:!!e.closest('[data-moving-record]')};});
  const moving=[...document.querySelectorAll('[data-moving-record]')].filter(visible).map(e=>{const r=e.getBoundingClientRect();return {id:e.getAttribute('data-moving-record'),x:r.x,y:r.y,w:r.width,h:r.height};});
  const collisions=[];for(const b of moving)for(const e of texts.filter(e=>!e.moving)){const r=e.ink,w=Math.min(b.x+b.w,r.x+r.w)-Math.max(b.x,r.x),h=Math.min(b.y+b.h,r.y+r.h)-Math.max(b.y,r.y);if(w>1&&h>1)collisions.push({moving:b.id,text:e.text,w,h});}
  return {texts,moving,collisions,subtitleCount:document.querySelectorAll('[data-subtitle]').length,logIds:[...document.querySelectorAll('[data-log-record]')].filter(visible).map(e=>e.getAttribute('data-log-record')),bodyText:document.body.innerText};
 });return close(args);};return p;};
try{
 const composition=await selectComposition({serveUrl,id:'Main',inputProps:props,puppeteerInstance:browser,logLevel:'error'});
 composition.props={...composition.props,...props};
 for(const s of samples){cur=s;metrics=null;const name=`s${String(s.shot).padStart(2,'0')}-l${String(s.local).padStart(4,'0')}-f${String(s.frame).padStart(5,'0')}.png`;await renderStill({serveUrl,composition,frame:s.frame,output:path.join(OUT,name),imageFormat:'png',inputProps:props,puppeteerInstance:browser,logLevel:'error',onBrowserLog:e=>{if(/COPYFIT|error/i.test(e.text))report.browserLogs.push({frame:s.frame,text:e.text});}});if(!metrics)throw Error('No DOM metrics captured');const violations=metrics.texts.filter(e=>e.x<-.5||e.y<-.5||e.x+e.w>1920.5||e.y+e.h>926||e.scrollWidth>e.clientWidth+2);report.samples.push({...s,file:name,sha256:sha(path.join(OUT,name)),metrics,violations});if(report.samples.length%25===0)console.log('sampled',report.samples.length);save();}
 cur=null;
 const range=get('--clip');
 if(range){const [a,b]=range.split(':').map(Number);const out=path.join(OUT,`true-no-subtitles-${a}-${b}.mp4`);await renderMedia({serveUrl,composition,codec:'h264',outputLocation:out,inputProps:props,frameRange:[a,b],crf:23,concurrency:2,puppeteerInstance:browser,logLevel:'error'});report.renderedClips.push({file:path.basename(out),from:a,to:b,props,sha256:sha(out)});}
 report.sourceUnchanged=Object.entries(identities).every(([p,h])=>sha(path.join(D,p))===h);
 report.pass=report.sourceUnchanged&&!report.browserLogs.some(e=>/COPYFIT/.test(e.text))&&report.samples.every(s=>!s.violations.length&&!s.metrics.collisions.length&&s.metrics.subtitleCount===0);
 save();console.log(JSON.stringify({pass:report.pass,samples:report.samples.length,violating:report.samples.filter(s=>s.violations.length||s.metrics.collisions.length||s.metrics.subtitleCount).map(s=>({frame:s.frame,violations:s.violations,collisions:s.metrics.collisions,subtitles:s.metrics.subtitleCount})),output:OUT}));
}finally{await browser.close({silent:true});}
