// Independent actual-timing stills and DOM state capture; no production writes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const EVIDENCE=path.dirname(fileURLToPath(import.meta.url));
const ROOT=path.resolve(EVIDENCE,'../../../../../');
const argv=process.argv.slice(2),get=k=>argv.find(v=>v.startsWith(k+'='))?.slice(k.length+1);
const slug=get('--slug');
if(!['twelve-balls','prisoners-light'].includes(slug))throw Error('Choose one authorized episode');
const D=path.join(ROOT,'episodes/puzzles',slug,'production/revisions/logic-20261111',slug);
const REM=path.join(D,'remotion');
const NAME=get('--name')??'preflight-v1';
const OUT=path.join(EVIDENCE,slug,NAME),REPORT=path.join(OUT,'report.json');
fs.mkdirSync(OUT,{recursive:true});
if(fs.existsSync(REPORT))throw Error('Use a fresh evidence run name');
const require=createRequire(path.join(REM,'package.json'));
const {bundle}=require('@remotion/bundler');
const {openBrowser,selectComposition,renderStill}=require('@remotion/renderer');
const webpack=require('webpack');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sb=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));
const shots=sb.scenes.flatMap(s=>s.shots);
const frames=[...new Set((get('--frames')??'').split(',').filter(Boolean).map(Number))].sort((a,b)=>a-b);
if(!frames.length)throw Error('Explicit affected/boundary frame list required');
const props={hideSubtitles:get('--subtitles')!=='true',auditLayout:true};
const files=['storyboard.json','script.md','voice.wav','model-data.json','remotion/package.json','remotion/package-lock.json',
 ...fs.readdirSync(path.join(REM,'src')).filter(x=>/\.(ts|tsx)$/.test(x)).map(x=>'remotion/src/'+x)];
const hashes=Object.fromEntries(files.map(p=>[p,sha(path.join(D,p))]));
const backups=[];
for(const rel of files.filter(p=>p.startsWith('remotion/src/')||p==='model-data.json'||p==='storyboard.json')){
 const target=path.join(OUT,'sources',rel+'.txt');
 fs.mkdirSync(path.dirname(target),{recursive:true});
 fs.writeFileSync(target,fs.readFileSync(path.join(D,rel)));
 backups.push({source:rel,backup:path.relative(ROOT,target),sha256:sha(target)});
}
const report={createdAt:new Date().toISOString(),executor:'Codex independent motion QA',episode:slug,
 revision:path.relative(ROOT,D),props,sourceHashes:hashes,sourceBackups:backups,samples:[],browserLogs:[],
 pass:false,visualReviewed:false,
 scope:'Actual storyboard timing and rendered DOM/stills, affected and boundary frames only. No full realtime viewing, ASR or semantic listening claim.'};
const save=()=>fs.writeFileSync(REPORT,JSON.stringify(report,null,2)+'\n');
save();
const url=await bundle({entryPoint:path.join(REM,'src/index.ts'),enableCaching:false,
 webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,
 '@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},
 modules:[path.join(REM,'node_modules'),'node_modules']},
 plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
let current=null,metrics=null;
const newPage=browser.newPage.bind(browser);
browser.newPage=async o=>{
 const page=await newPage(o),close=page.close.bind(page);
 page.close=async a=>{
  if(current)metrics=await page.evaluate(()=>{
   const visible=e=>{let opacity=1;for(let n=e;n;n=n.parentElement){const s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden')return false;opacity*=Number(s.opacity);}return opacity>.1;};
   const texts=[...document.querySelectorAll('svg text')].filter(visible).map(e=>{
    const range=document.createRange();range.selectNodeContents(e);const r=range.getBoundingClientRect();
    return{text:e.textContent,x:r.x,y:r.y,w:r.width,h:r.height,maxWidth:Number(e.getAttribute('data-max-width')||0)};
   });
   const states=[...document.querySelectorAll('svg *')].filter(e=>visible(e)&&[...e.attributes].some(a=>a.name.startsWith('data-'))).map(e=>{
    const r=e.getBoundingClientRect();return{tag:e.tagName,
     attrs:Object.fromEntries([...e.attributes].filter(a=>a.name.startsWith('data-')).map(a=>[a.name,a.value])),
     text:e.textContent,bounds:r.toJSON()};
   });
   const caption=document.querySelector('[data-subtitle]');
   return{texts,states,subtitles:document.querySelectorAll('[data-subtitle]').length,
    caption:caption?{text:caption.textContent,box:caption.getBoundingClientRect().toJSON()}:null};
  });
  return close(a);
 };
 return page;
};
try{
 const composition=await selectComposition({serveUrl:url,id:slug==='twelve-balls'?'TwelveBalls':'PrisonersLight',
  inputProps:props,puppeteerInstance:browser,logLevel:'error'});
 composition.props={...composition.props,...props};
 for(const frame of frames){
  const shot=shots.find(s=>frame>=s.from&&frame<s.from+s.durationInFrames);
  if(!shot)throw Error('Requested frame outside actual body storyboard: '+frame);
  current={frame,shot:shot.id,local:frame-shot.from};metrics=null;
  const file=path.join(OUT,`s${shot.id}-f${String(frame).padStart(5,'0')}.png`);
  await renderStill({serveUrl:url,composition,frame,output:file,imageFormat:'png',inputProps:props,
   puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{
    if(/COPYFIT|error/i.test(l.text))report.browserLogs.push({frame,text:l.text});
   }});
  if(!metrics)throw Error('Missing actual rendered DOM metrics');
  const violations=metrics.texts.filter(t=>t.w>0&&(t.x<-.5||t.y<-.5||t.x+t.w>1920.5||t.y+t.h>835.5||t.maxWidth&&t.w>t.maxWidth+2));
  if(metrics.caption){const b=metrics.caption.box;if(b.x<0||b.y<835||b.right>1920||b.bottom>1080)violations.push({captionBox:b});}
  report.samples.push({...current,file:path.relative(ROOT,file),sha256:sha(file),metrics,violations});
  save();
 }
 current=null;
 report.sourceUnchanged=Object.entries(hashes).every(([p,h])=>sha(path.join(D,p))===h);
 report.pass=report.sourceUnchanged&&!report.browserLogs.length&&report.samples.every(s=>!s.violations.length&&s.metrics.subtitles===(props.hideSubtitles?0:1));
 save();
 console.log(JSON.stringify({pass:report.pass,sourceUnchanged:report.sourceUnchanged,samples:report.samples.length,
  browserLogs:report.browserLogs,violations:report.samples.filter(s=>s.violations.length).map(s=>({frame:s.frame,violations:s.violations})),
  report:path.relative(ROOT,REPORT)}));
}finally{await browser.close({silent:true});}
