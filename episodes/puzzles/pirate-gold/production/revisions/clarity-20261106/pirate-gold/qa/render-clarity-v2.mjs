// Independent actual-timing preview. Does not mutate production inputs.
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
const argv=process.argv.slice(2),get=k=>argv.find(v=>v.startsWith(k+'='))?.slice(k.length+1);
const NAME=get('--name')??'clarity-preflight-v1',OUT=path.join(D,'qa',NAME),REPORT=path.join(D,'qa',NAME+'.json');
fs.mkdirSync(OUT,{recursive:true});
const sb=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));
const shots=sb.scenes.flatMap(s=>s.shots),samples=new Map();
function add(s,local,why){local=Math.min(s.durationInFrames-1,Math.max(0,Math.round(local)));const f=s.from+local;const r=samples.get(f)??{shot:s.id,local,frame:f,reasons:[]};r.reasons.push(why);samples.set(f,r);}
for(const s of shots){
  add(s,0,'first');add(s,s.durationInFrames/2,'middle');add(s,s.durationInFrames-1,'last');
  for(const v of s.voice??[])for(const t of[v.localStart,v.localEnd])add(s,t,'speech-boundary');
  if([5,7,9,11,12,13].includes(Number(s.id)))for(let f=15;f<s.durationInFrames;f+=30)add(s,f,'proposal-vote-1s-grid');
}
for(const f of(get('--frames')??'').split(',').filter(Boolean).map(Number)){const s=shots.find(s=>f>=s.from&&f<s.from+s.durationInFrames);if(s)add(s,f-s.from,'extra');}
const only=get('--only')?.split(',').map(Number);if(only)for(const[f,s]of samples)if(!only.includes(Number(s.shot)))samples.delete(f);
if(get('--explicit-only')==='true'){for(const[f,s]of samples)if(!s.reasons.includes('extra'))samples.delete(f);}
const props={hideSubtitles:get('--subtitles')!=='true',auditLayout:true};
const files=['storyboard.json','script.md','voice.wav','plan.json','episode-config.json','model-data.json','qa/render-clarity-v2.mjs','remotion/package.json','remotion/package-lock.json','remotion/remotion.config.ts','remotion/tsconfig.json','../../../../../../_shared/puzzles-video/Frame.tsx','../../../../../../_shared/puzzles-video/theme.ts','../../../../../../_shared/puzzles-covers/catalog.json',...fs.readdirSync(path.join(REM,'src')).filter(x=>/\.(ts|tsx)$/.test(x)).map(x=>'remotion/src/'+x)];
const hashes=Object.fromEntries(files.map(p=>[p,sha(path.join(D,p))]));
// Preserve exact dynamic source bytes before this independent run.
const backups=[];for(const rel of files.filter(p=>p.startsWith('remotion/src/')||p==='model-data.json')){const target=path.join(D,'qa/revisions',NAME,rel+'.txt');fs.mkdirSync(path.dirname(target),{recursive:true});if(fs.existsSync(target)&&sha(target)!==hashes[rel])throw Error('Use a new QA run name; original source snapshot differs: '+rel);fs.writeFileSync(target,fs.readFileSync(path.join(D,rel)));backups.push({source:rel,backup:path.relative(D,target),sha256:sha(target)});}
const report={createdAt:new Date().toISOString(),executor:'Codex independent QA',props,sourceHashes:hashes,sourceBackups:backups,samples:[],clips:[],browserLogs:[],pass:false,visualReviewed:false,limitations:['Frames and continuous encoded previews reviewed through sampled sequences, not full realtime playback.','No speech-recognition or full-track semantic audition.']};
const save=()=>fs.writeFileSync(REPORT,JSON.stringify(report,null,2)+'\n');save();
const url=await bundle({entryPoint:path.join(REM,'src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(REM,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
let current=null,metrics=null;
const newPage=browser.newPage.bind(browser);browser.newPage=async o=>{const p=await newPage(o),close=p.close.bind(p);p.close=async a=>{if(current)metrics=await p.evaluate(()=>{
  const visible=e=>{let opacity=1;for(let n=e;n;n=n.parentElement){const s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden')return false;opacity*=Number(s.opacity);}return opacity>.1;};
  const nodes=[...document.querySelectorAll('svg text,[data-text]')].filter(visible);
  const texts=nodes.map(e=>{const range=document.createRange();range.selectNodeContents(e);const r=range.getBoundingClientRect();return{text:e.textContent,x:r.x,y:r.y,w:r.width,h:r.height};});
  const checked=[...document.querySelectorAll('[data-check]')].filter(visible).map(e=>({tag:e.tagName,key:e.getAttribute('data-check'),text:e.textContent,attrs:Object.fromEntries([...e.attributes].filter(a=>a.name.startsWith('data-')).map(a=>[a.name,a.value]))}));
  const states=[...document.querySelectorAll('svg [data-round],svg [data-phase],svg [data-pirate],svg [data-coin-count],svg [data-quota],svg [data-vote],svg [data-proposal-status],svg [data-votes-yes]')].filter(visible).map(e=>({tag:e.tagName,attrs:Object.fromEntries([...e.attributes].filter(a=>a.name.startsWith('data-')).map(a=>[a.name,a.value])),text:e.textContent}));
  return {texts,checked,states,subtitles:document.querySelectorAll('[data-subtitle]').length,caption:document.querySelector('[data-subtitle]')?{text:document.querySelector('[data-subtitle]').textContent,box:document.querySelector('[data-subtitle]').getBoundingClientRect().toJSON()}:null};
});return close(a);};return p;};
try{
  const composition=await selectComposition({serveUrl:url,id:'PirateGold',inputProps:props,puppeteerInstance:browser,logLevel:'error'});composition.props={...composition.props,...props};
  for(const sample of[...samples.values()].sort((a,b)=>a.frame-b.frame)){
    current=sample;metrics=null;const file=path.join(OUT,`s${sample.shot}-f${String(sample.frame).padStart(5,'0')}.png`);
    await renderStill({serveUrl:url,composition,frame:sample.frame,output:file,imageFormat:'png',inputProps:props,puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{if(/COPYFIT|error/i.test(l.text))report.browserLogs.push({frame:sample.frame,text:l.text});}});
    if(!metrics)throw Error('Missing actual rendered DOM metrics');
    const violations=metrics.texts.filter(t=>t.w>0&&(t.x<-.5||t.y<-.5||t.x+t.w>1920.5||t.y+t.h>960));
    report.samples.push({...sample,file:path.relative(D,file),sha256:sha(file),metrics,violations});save();
    if(report.samples.length%20===0)console.log('samples',report.samples.length);
  }
  current=null;
  for(const spec of(get('--clips')??'').split(',').filter(Boolean)){
    const[from,to]=spec.split(':').map(Number),file=path.join(OUT,`no-subtitles-${from}-${to}.mp4`);
    await renderMedia({serveUrl:url,composition,codec:'h264',outputLocation:file,inputProps:props,frameRange:[from,to],crf:23,concurrency:2,scale:.5,puppeteerInstance:browser,logLevel:'error'});
    const {execFileSync}=await import('node:child_process');const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames,nb_frames,avg_frame_rate,width,height','-of','json',file],{encoding:'utf8'}));const stream=probe.streams[0],actualFrames=Number(stream.nb_read_frames??stream.nb_frames),expectedFrames=to-from+1;if(actualFrames!==expectedFrames)throw Error('Encoded preview frame mismatch '+actualFrames+' != '+expectedFrames);execFileSync('ffmpeg',['-v','error','-i',file,'-f','null','-'],{stdio:'pipe'});report.clips.push({file:path.relative(D,file),from,to,sha256:sha(file),props,expectedFrames,actualFrames,fullDecodePassed:true,stream});save();console.log('clip',from,to);
  }
  report.sourceUnchanged=Object.entries(hashes).every(([p,h])=>sha(path.join(D,p))===h);
  report.pass=report.sourceUnchanged&&report.samples.every(s=>!s.violations.length&&s.metrics.subtitles===(props.hideSubtitles?0:1))&&!report.browserLogs.length;
  save();console.log(JSON.stringify({pass:report.pass,samples:report.samples.length,clips:report.clips.length,violations:report.samples.filter(s=>s.violations.length).map(s=>({frame:s.frame,violations:s.violations})),browserLogs:report.browserLogs,report:REPORT}));
}finally{await browser.close({silent:true});}
