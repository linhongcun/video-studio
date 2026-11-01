import {bundle} from '@remotion/bundler';
import {openBrowser,renderStill,selectComposition,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import webpack from 'webpack';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const root=path.resolve('..'),args=process.argv.slice(2);
const out=path.resolve(args.find(a=>!a.startsWith('--'))??'out/qa');
const wanted=args.find(a=>a.startsWith('--shots='))?.slice(8).split(',');
const motion=args.includes('--motion'),hideSubtitles=args.includes('--no-captions');
const ranges=(args.find(a=>a.startsWith('--ranges='))?.slice(9)??'').split(',').filter(Boolean).map(v=>v.split(':'));
const exact=(args.find(a=>a.startsWith('--frames='))?.slice(9)??'').split(',').filter(Boolean).map(v=>v.split(':'));
const input=fs.existsSync(root+'/storyboard.json')?root+'/storyboard.json':path.resolve('src/placeholders/storyboard.json');
const data=JSON.parse(fs.readFileSync(input,'utf8')),shots=data.scenes.flatMap(s=>s.shots);
let offset=0;for(const s of shots){s.from=offset;offset+=s.durationInFrames;}
const {events}=await import(pathToFileURL(path.resolve('src/motion.ts')).href);
const sourceSha256=Object.fromEntries(['../storyboard.json','../covers.json','src/Main.tsx','src/motion.ts','src/data.ts','src/objects.tsx','src/primitives.tsx','src/theme.ts','src/Cover.tsx','src/java-card.json'].filter(p=>fs.existsSync(p)).map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')]));
fs.mkdirSync(out,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'}),samples=[],clips=[],copyfit=[];
const onBrowserLog=log=>{if(log.text?.includes('COPYFIT')){copyfit.push(log.text);console.error(log.text);}};
const inputProps={hideSubtitles,showSubtitles:!hideSubtitles};
try{
 const selected=await selectComposition({serveUrl,id:'Main',puppeteerInstance:browser,inputProps,logLevel:'error'});
 const composition={...selected,props:{...selected.props,...inputProps}};
 for(const shot of shots.filter(s=>!wanted||wanted.includes(s.id))){
  const frames=new Map();
  for(const ratio of [0,.24,.53,.83,.98]){const local=Math.min(shot.durationInFrames-1,Math.round(shot.durationInFrames*ratio));frames.set(local,{phase:ratio});}
  for(const [event,local] of events(shot))for(const delta of [-1,0])frames.set(local+delta,{event,state:delta<0?'before':'after'});
  for(const [local,details]of frames){
   if(local<0||local>=shot.durationInFrames)continue;
   const file=path.join(out,`${shot.id}-${local}.png`),frame=shot.from+local;
   await renderStill({composition,serveUrl,frame,output:file,puppeteerInstance:browser,inputProps,scale:.5,imageFormat:'png',logLevel:'error',onBrowserLog});
   samples.push({shot:shot.id,visualType:shot.visualType,local,frame,file,...details});
  }
  if(motion){
   const file=path.join(out,`${shot.id}-motion.mp4`);
   await renderMedia({composition,serveUrl,codec:'h264',outputLocation:file,frameRange:[shot.from,shot.from+shot.durationInFrames-1],inputProps,scale:.5,crf:22,concurrency:2,puppeteerInstance:browser,logLevel:'error',onBrowserLog});
   clips.push({shot:shot.id,visualType:shot.visualType,file,frameRange:[shot.from,shot.from+shot.durationInFrames-1],hideSubtitles,voice:false});
  }
  console.log(`QA ${shot.id} ${shot.visualType}: ${frames.size} states${motion?' + continuous clip':''}`);
 }
 for(const [id,localText] of exact){
  const shot=shots.find(s=>s.id===id),local=Number(localText);if(!shot||!Number.isInteger(local)||local<0||local>=shot.durationInFrames)throw new Error('Invalid exact frame '+id+':'+localText);
  const file=path.join(out,`${shot.id}-${local}.png`),frame=shot.from+local;
  await renderStill({composition,serveUrl,frame,output:file,puppeteerInstance:browser,inputProps,scale:.5,imageFormat:'png',logLevel:'error',onBrowserLog});
  samples.push({shot:shot.id,visualType:shot.visualType,local,frame,file,sameSourceControl:true});
 }
 for(const [start,end] of ranges){
  const first=shots.find(s=>s.id===start),last=shots.find(s=>s.id===end);if(!first||!last||first.from>last.from)throw new Error('Invalid cross-shot range '+start+':'+end);
  const file=path.join(out,`${start}-${end}-continuous.mp4`),frameRange=[first.from,last.from+last.durationInFrames-1];
  await renderMedia({composition,serveUrl,codec:'h264',outputLocation:file,frameRange,inputProps,scale:.5,crf:22,concurrency:2,puppeteerInstance:browser,logLevel:'error',onBrowserLog});
  clips.push({shot:start+'-'+end,file,frameRange,hideSubtitles,voice:false,crossShot:true});
  console.log(`QA continuous ${start}-${end}`);
 }
 fs.writeFileSync(path.join(out,'frames.json'),JSON.stringify({provisional:!!data.meta.provisionalTiming,javaEndCard:data.meta.javaEndCard??null,source:input,sourceSha256,hideSubtitles,effectiveProps:composition.props,voice:false,copyfit,samples,clips},null,2)+'\n');
 if(copyfit.length)throw new Error('COPYFIT overflow detected');
}finally{await browser.close({silent:true});}
