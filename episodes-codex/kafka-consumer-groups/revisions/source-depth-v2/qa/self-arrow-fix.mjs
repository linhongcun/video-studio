import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {createRequire} from 'node:module';import {fileURLToPath} from 'node:url';
const D=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),R=path.join(D,'remotion'),q=createRequire(path.join(R,'package.json'));
const {bundle}=q('@remotion/bundler'),{openBrowser,selectComposition,renderStill,renderMedia}=q('@remotion/renderer'),webpack=q('webpack');
const out=path.join(D,'qa/self-preview/arrow-fix');fs.mkdirSync(path.join(out,'images'),{recursive:true});
const board=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8')),shots=board.scenes.flatMap(s=>s.shots),inputProps={showSubtitles:false,hideSubtitles:true};
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const source={main:sha(path.join(R,'src/Main.tsx')),storyboard:sha(path.join(D,'storyboard.json')),model:sha(path.join(D,'model.json')),voice:sha(path.join(D,'voice.wav'))};
const url=await bundle({entryPoint:path.join(R,'src/index.ts'),publicDir:path.join(R,'public'),outDir:path.join(out,'bundle'),webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...(c.resolve?.alias||{}),'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(R,'node_modules'),'node_modules']},plugins:[...(c.plugins||[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:'true'})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',chromiumOptions:{disableWebSecurity:false}}),composition=await selectComposition({serveUrl:url,id:'Main',puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',inputProps});
const logs=[],images=[];let from=0;
for(const s of shots){
 if(s.id!=='03'){from+=s.durationInFrames;continue;}
 const locs=[Math.max(0,Math.floor(s.voice[0].localEnd-12)),Math.max(0,Math.floor(s.voice[1].localStart+35)),s.durationInFrames-20];
 for(const local of [...new Set(locs)]){
  const frame=from+Math.min(local,s.durationInFrames-1),name=`s${s.id}-f${frame}.png`,output=path.join(out,'images',name);
  await renderStill({serveUrl:url,composition,inputProps,frame,output,puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',onBrowserLog:log=>{if(log.text.includes('COPYFIT'))logs.push({frame,text:log.text});}});
  images.push({shot:s.id,frame,local,filename:name,sha256:sha(output)});
 }
 from+=s.durationInFrames;
}
const clipDefinitions=[];let clips=[];
for(const c of clipDefinitions){const s=shots[c.index],start=shots.slice(0,c.index).reduce((n,s)=>n+s.durationInFrames,0),end=start+s.durationInFrames-1,output=path.join(out,c.name+'.mp4');await renderMedia({serveUrl:url,composition,inputProps,frameRange:[start,end],outputLocation:output,codec:'h264',crf:24,muted:true,concurrency:2,puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',onBrowserLog:log=>{if(log.text.includes('COPYFIT'))logs.push({clip:c.name,text:log.text});}});clips.push({name:c.name,start,end,filename:path.relative(D,output),sha256:sha(output)});}
await browser.close({silent:true});fs.writeFileSync(path.join(out,'render-report.json'),JSON.stringify({source,images,clips,copyfit:logs,scope:'Self-review actual full-resolution muted no-subtitle frames and bounded preview clips. Not formal encoded publication or independent QA.'},null,2)+'\n');console.log(JSON.stringify({source,imageCount:images.length,clips,copyfit:logs}));
