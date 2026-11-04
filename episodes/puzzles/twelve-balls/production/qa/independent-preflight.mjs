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
const NAME=get('--name')??'independent-preflight-v1',OUT=path.join(D,'qa/out',NAME),REPORT=path.join(D,'qa',NAME+'.json');
if(fs.existsSync(REPORT))throw Error('Preserve earlier QA report; choose a new --name');
fs.mkdirSync(OUT,{recursive:true});
const sb=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));
const shots=sb.scenes.flatMap(s=>s.shots),samples=new Map();
function add(s,local,why){local=Math.min(s.durationInFrames-1,Math.max(0,Math.round(local)));const f=s.from+local;const r=samples.get(f)??{shot:s.id,local,frame:f,reasons:[]};r.reasons.push(why);samples.set(f,r);}
for(const s of shots){
  add(s,0,'first');add(s,s.durationInFrames/2,'middle');add(s,s.durationInFrames-1,'last');
  for(const v of s.voice??[])for(const t of[v.localStart,v.localEnd])add(s,t,'speech-boundary');
  if(get('--dense')!=='false'&&[3,4,5,6,7,8,9,10,11,12,13,14].includes(Number(s.id)))for(let f=30;f<s.durationInFrames;f+=90)add(s,f,'mechanism-3s-grid');
}

// Use actual voice boundaries to sample the causal transitions independently.
for(const s of shots){
  const [v,w]=s.voice??[];if(!v||!w)throw Error('Wait for actual two-sentence voice timing: '+s.id);
  const a=v.localStart,b=v.localEnd,c=w.localStart,e=w.localEnd,q=Number(s.id),at=p=>a+(e-a)*p;
  let points=[];
  if(q===3){const end=a+133;points=[end-1,end,end+1,c-1,c,c+(e-c)*.48-1,c+(e-c)*.48,e-17,e-16,e-15];for(let f=0;f<=134;f+=8)points.push(a+f);}
  if(q===4){const t=a+(b-a)*.21;points=[t-1,t,t+1,c-1,c];}
  if(q===5){for(let f=0;f<=116;f+=6)points.push(a+f);for(let f=0;f<=56;f+=6)points.push(c+f);}
  if(q===6)for(const t of[a+(b-a)*.16,a+(b-a)*.34,a+(b-a)*.54,c+(e-c)*.40,c+(e-c)*.60])for(const d of[-1,0,5,11,17,22,23])points.push(t+d);
  if(q===7){const x=a+(b-a)*.3,y=a+(b-a)*.6;points=[x-1,x,(x+y)/2,y-1,y,y+1];}
  const span=(x,y)=>{points.push(x-1,x,x+1,y-1,y,y+1);for(let k=1;k<12;k++)points.push(x+(y-x)*k/12);};
  if(q===8){const t=a+(b-a)*.23,move=t+20,end=b-2,result=c+(e-c)*.73;points=[t-1,t,t+1,c,result-1,result,result+1];span(move,end);}
  if([9,10,13].includes(q)){const select=at(.15),move=select+18,end=c+(e-c)*.28;points.push(a+23,a+24,a+25,select-1,select,select+1);span(move,end);for(const t of[end+8,end+8+(e-end-16)/3,end+8+2*(e-end-16)/3])points.push(t-1,t,t+1);}
  if(q===11){const focus=a+(b-a)*.22,one=60,oneEnd=c+12,two=c+(e-c)*.15,twoEnd=c+(e-c)*.69,result=c+(e-c)*.78;points=[focus-1,focus,focus+1,result-1,result,result+1];span(one,oneEnd);span(two,twoEnd);}
  if(q===12){const focus=a+(b-a)*.21,move=a+(b-a)*.45,end=e-28;points=[focus-1,focus,focus+1];span(move,end);}
  if(q===14){const select=a+(b-a)*.44,move=a+(b-a)*.56,end=c+(e-c)*.28,result=c+(e-c)*.8;points=[select-1,select,select+1,c,result-1,result,result+1];span(move,end);}
  for(const f of points)add(s,f,'causal-transition');
}
for(const f of(get('--frames')??'').split(',').filter(Boolean).map(Number)){const s=shots.find(s=>f>=s.from&&f<s.from+s.durationInFrames);if(s)add(s,f-s.from,'extra');}
const only=get('--only')?.split(',').map(Number);if(only)for(const[f,s]of samples)if(!only.includes(Number(s.shot)))samples.delete(f);
if(get('--explicit-only')==='true'){for(const[f,s]of samples)if(!s.reasons.includes('extra'))samples.delete(f);}
const props={hideSubtitles:true,auditLayout:true};
const files=['storyboard.json','script.md','voice.wav','plan.json','model-data.json','qa/independent-preflight.mjs','remotion/package.json','remotion/package-lock.json','remotion/remotion.config.ts','remotion/tsconfig.json','../../../_shared/puzzles-video/Frame.tsx','../../../_shared/puzzles-video/theme.ts','../../../_shared/puzzles-covers/catalog.json',...fs.readdirSync(path.join(REM,'src')).filter(x=>/\.(ts|tsx)$/.test(x)).map(x=>'remotion/src/'+x)];
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
  const states=[...document.querySelectorAll('svg [data-ball],svg [data-navigation-prefix],svg [data-left-balls],svg [data-current-candidates],svg [data-results-for-prefix],svg [data-outcome],svg [data-global-map]')].filter(visible).map(e=>{const r=e.getBoundingClientRect(),circle=e.querySelector('circle')?.getBoundingClientRect();return{tag:e.tagName,attrs:Object.fromEntries([...e.attributes].filter(a=>a.name.startsWith('data-')).map(a=>[a.name,a.value])),text:e.textContent,bounds:{x:r.x,y:r.y,w:r.width,h:r.height},circle:circle?{x:circle.x,y:circle.y,w:circle.width,h:circle.height}:null}});
  const overlapCandidates=[];for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){const a=texts[i],b=texts[j],w=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),h=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);if(w>2&&h>2)overlapCandidates.push({a:a.text,b:b.text,intersection:{w,h}});}return {texts,checked,states,overlapCandidates,subtitles:document.querySelectorAll('[data-subtitle]').length};
});return close(a);};return p;};
try{
  const composition=await selectComposition({serveUrl:url,id:'TwelveBalls',inputProps:props,puppeteerInstance:browser,logLevel:'error'});composition.props={...composition.props,...props};
  for(const sample of[...samples.values()].sort((a,b)=>a.frame-b.frame)){
    current=sample;metrics=null;const file=path.join(OUT,`s${sample.shot}-f${String(sample.frame).padStart(5,'0')}.png`);
    await renderStill({serveUrl:url,composition,frame:sample.frame,output:file,imageFormat:'png',inputProps:props,puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{if(/COPYFIT|error/i.test(l.text))report.browserLogs.push({frame:sample.frame,text:l.text});}});
    if(!metrics)throw Error('Missing actual rendered DOM metrics');
    const violations=metrics.texts.filter(t=>t.w>0&&(t.x<-.5||t.y<-.5||t.x+t.w>1920.5||t.y+t.h>820));
    const balls=metrics.states.filter(s=>s.attrs['data-ball']);if(balls.length&&(balls.length!==12||new Set(balls.map(s=>s.attrs['data-ball'])).size!==12))violations.push({physicalBalls:'expected precisely twelve unique physical identities'});
    for(let i=0;i<balls.length;i++)for(let j=i+1;j<balls.length;j++){const a=balls[i].circle,b=balls[j].circle;if(a&&b){const distance=Math.hypot(a.x+a.w/2-b.x-b.w/2,a.y+a.h/2-b.y-b.h/2);if(distance<(a.w+b.w)/2-1)violations.push({ballCircleOverlap:[balls[i].attrs['data-ball'],balls[j].attrs['data-ball']],distance});}}
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
  report.pass=report.sourceUnchanged&&report.samples.every(s=>!s.violations.length&&s.metrics.subtitles===0)&&!report.browserLogs.length;
  save();console.log(JSON.stringify({pass:report.pass,samples:report.samples.length,clips:report.clips.length,violations:report.samples.filter(s=>s.violations.length).map(s=>({frame:s.frame,violations:s.violations})),browserLogs:report.browserLogs,report:REPORT}));
}finally{await browser.close({silent:true});}
