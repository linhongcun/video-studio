// Actual-timing stills and optional continuous previews for this revision only.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const REM=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..'),D=path.dirname(REM);
const require=createRequire(path.join(REM,'package.json'));
const {bundle}=require('@remotion/bundler');
const {openBrowser,selectComposition,renderStill,renderMedia}=require('@remotion/renderer');
const webpack=require('webpack');
const args=process.argv.slice(2),get=k=>args.find(v=>v.startsWith(k+'='))?.slice(k.length+1);
const name=get('--name')??'simple-preview-v1';
const OUT=path.resolve(get('--out')??path.join(D,'qa',name));
fs.mkdirSync(OUT,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const storyboard=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));
const shots=storyboard.scenes.flatMap(s=>s.shots);
const explicit=(get('--frames')??'').split(',').filter(Boolean).map(Number);
let frames=explicit.length?explicit:shots.flatMap(s=>[s.from,s.from+Math.round(s.durationInFrames*.65),s.from+s.durationInFrames-1]);
const only=(get('--shots')??'').split(',').filter(Boolean).map(Number);
if(only.length)frames=frames.filter(f=>shots.some(s=>only.includes(Number(s.id))&&f>=s.from&&f<s.from+s.durationInFrames));
frames=[...new Set(frames)].sort((a,b)=>a-b);
const props={hideSubtitles:get('--subtitles')!=='true',auditLayout:true};
const sourceFiles=['script.md','storyboard.json','model-data.json','remotion/src/Main.tsx','remotion/src/motion.ts','remotion/scripts/preview.mjs'];
const sourceHashes=Object.fromEntries(sourceFiles.map(p=>[p,sha(path.join(D,p))]));
const report={createdAt:new Date().toISOString(),executor:'Codex animation author',props,sourceHashes,samples:[],clips:[],browserLogs:[],passed:false,visualReviewed:false,limitations:['This records actual rendered samples and optional clips, not a full realtime watch.','No word-level alignment, speech recognition or semantic listening claim.']};
const save=()=>fs.writeFileSync(path.join(OUT,'report.json'),JSON.stringify(report,null,2)+'\n');save();
const serveUrl=await bundle({entryPoint:path.join(REM,'src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(REM,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
let metrics=null;
const newPage=browser.newPage.bind(browser);
browser.newPage=async options=>{
  const page=await newPage(options),close=page.close.bind(page);
  page.close=async options=>{
    metrics=await page.evaluate(()=>{
      const visible=el=>{let alpha=1;for(let n=el;n;n=n.parentElement){const s=getComputedStyle(n);if(s.visibility==='hidden'||s.display==='none')return false;alpha*=Number(s.opacity);}return alpha>.1;};
      const texts=[...document.querySelectorAll('svg text')].filter(visible).map(el=>{const r=document.createRange();r.selectNodeContents(el);const b=r.getBoundingClientRect();return {text:el.textContent,bounds:b.toJSON()};});
      const balls=[...document.querySelectorAll('svg [data-ball]')].filter(visible).map(el=>{const b=el.querySelector('circle').getBoundingClientRect();return {id:Number(el.dataset.ball),status:el.dataset.ballStatus,candidates:el.dataset.candidateCases,cx:b.x+b.width/2,cy:b.y+b.height/2,radius:b.width/2};});
      const collisions=[];for(let i=0;i<balls.length;i++)for(let j=i+1;j<balls.length;j++){const a=balls[i],b=balls[j],gap=Math.hypot(a.cx-b.cx,a.cy-b.cy)-a.radius-b.radius;if(gap<-.5)collisions.push({a:a.id,b:b.id,gap});}
      const duplicateIds=balls.map(b=>b.id).filter((id,i,a)=>a.indexOf(id)!==i);
      const caption=document.querySelector('[data-subtitle]');
      return {texts,balls,collisions,duplicateIds,subtitle:caption?{text:caption.textContent,bounds:caption.getBoundingClientRect().toJSON()}:null};
    });
    return close(options);
  };
  return page;
};
try{
  const composition=await selectComposition({serveUrl,id:'TwelveBalls',inputProps:props,puppeteerInstance:browser,logLevel:'error'});
  composition.props={...composition.props,...props};
  for(const frame of frames){
    metrics=null;const file=path.join(OUT,`frame-${String(frame).padStart(5,'0')}.png`);
    await renderStill({serveUrl,composition,frame,output:file,imageFormat:'png',inputProps:props,puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{if(/COPYFIT|error/i.test(l.text))report.browserLogs.push({frame,text:l.text});}});
    if(!metrics)throw Error('Actual rendered DOM metrics missing');
    const boundsErrors=metrics.texts.filter(t=>t.bounds.x<-.5||t.bounds.y<-.5||t.bounds.right>1920.5||t.bounds.bottom>889);
    const subtitleErrors=metrics.subtitle&&metrics.subtitle.bounds.bottom>1070?[metrics.subtitle]:[];
    report.samples.push({frame,shot:shots.find(s=>frame>=s.from&&frame<s.from+s.durationInFrames)?.id,file:path.relative(D,file),sha256:sha(file),metrics,boundsErrors,subtitleErrors});save();
    console.log('frame',frame);
  }
  for(const range of(get('--clips')??'').split(',').filter(Boolean)){
    const [from,to]=range.split(':').map(Number),file=path.join(OUT,`no-subtitles-${from}-${to}.mp4`);
    await renderMedia({serveUrl,composition,codec:'h264',outputLocation:file,inputProps:props,frameRange:[from,to],crf:23,concurrency:2,scale:.5,puppeteerInstance:browser,logLevel:'error'});
    const {execFileSync}=await import('node:child_process');
    const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames,width,height','-of','json',file],{encoding:'utf8'}));
    execFileSync('ffmpeg',['-v','error','-i',file,'-f','null','-'],{stdio:'pipe'});
    const actualFrames=Number(probe.streams[0].nb_read_frames),expectedFrames=to-from+1;
    if(actualFrames!==expectedFrames)throw Error('Preview frame count differs');
    report.clips.push({from,to,file:path.relative(D,file),sha256:sha(file),actualFrames,expectedFrames,fullDecode:true});save();
  }
  report.sourceUnchanged=Object.entries(sourceHashes).every(([p,h])=>sha(path.join(D,p))===h);
  report.passed=report.sourceUnchanged&&!report.browserLogs.length&&report.samples.every(s=>!s.boundsErrors.length&&!s.subtitleErrors.length&&!s.metrics.collisions.length&&!s.metrics.duplicateIds.length);
  save();console.log(JSON.stringify({passed:report.passed,samples:report.samples.length,clips:report.clips.length,report:path.join(OUT,'report.json'),browserLogs:report.browserLogs}));
}finally{await browser.close({silent:true});}
