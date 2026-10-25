import {bundle} from '@remotion/bundler';
import {openBrowser,renderStill,selectComposition,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import webpack from 'webpack';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const root=path.resolve('..'),args=process.argv.slice(2),out=path.resolve(args.find(a=>!a.startsWith('--'))??'out/qa');
const wanted=args.find(a=>a.startsWith('--shots='))?.slice(8).split(','),hideSubtitles=args.includes('--no-captions'),motion=args.includes('--motion');
const input=path.join(root,'storyboard.json');
if(!fs.existsSync(input))throw new Error('Real voice-timed storyboard is required; no provisional preview is accepted.');
const data=JSON.parse(fs.readFileSync(input,'utf8'));
if(data.meta.provisionalTiming)throw new Error('Storyboard is provisional.');
const shots=data.scenes.flatMap(s=>s.shots);let total=0;for(const s of shots){s.from=total;total+=s.durationInFrames;}
const {events}=await import(pathToFileURL(path.resolve('src/motion.ts')).href);
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sourceFiles=['../storyboard.json','../covers.json',...fs.readdirSync('src').filter(p=>/\.(tsx?|json)$/.test(p)).map(p=>'src/'+p),'scripts/qa.mjs'];
const sourceSha256=Object.fromEntries(sourceFiles.map(p=>[p,hash(p)]));
fs.mkdirSync(out,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'}),samples=[],clips=[],copyfit=[];
const onBrowserLog=log=>{if(log.text?.includes('COPYFIT')){copyfit.push(log.text);console.error(log.text);}};
const inputProps={hideSubtitles};
try{
 const composition=await selectComposition({serveUrl,id:'Main',puppeteerInstance:browser,inputProps,logLevel:'error'});composition.props={...composition.props,...inputProps};
 for(const shot of shots.filter(s=>!wanted||wanted.includes(s.id))){
  const frames=new Map();
  for(const ratio of [0,.25,.53,.83,.98])frames.set(Math.min(shot.durationInFrames-1,Math.round(shot.durationInFrames*ratio)),{phase:ratio});
  for(const [event,local]of events(shot))for(const delta of [-1,0,1])frames.set(local+delta,{event,state:delta<0?'before':delta>0?'after':'boundary'});
  for(const [local,details]of frames){if(local<0||local>=shot.durationInFrames)continue;const file=path.join(out,`${shot.id}-${local}.png`),frame=shot.from+local;await renderStill({composition,serveUrl,frame,output:file,puppeteerInstance:browser,inputProps,scale:.5,imageFormat:'png',logLevel:'error',onBrowserLog});samples.push({shot:shot.id,visualType:shot.visualType,local,frame,file,...details});}
  console.log(`QA ${shot.id}: ${frames.size} states`);
 }
 const gateFrames=[0,24,54,60,120,150,shots[1].from-1,shots[1].from,shots[2].from,shots[7].from,shots[8].from,shots[9].from];
 for(const frame of gateFrames){const existing=samples.find(s=>s.frame===frame);if(existing){existing.openingGate=true;continue;}const shot=shots.find(s=>frame>=s.from&&frame<s.from+s.durationInFrames);const file=path.join(out,`gate-${frame}.png`);await renderStill({composition,serveUrl,frame,output:file,puppeteerInstance:browser,inputProps,scale:.5,imageFormat:'png',logLevel:'error',onBrowserLog});samples.push({shot:shot.id,visualType:shot.visualType,local:frame-shot.from,frame,file,openingGate:true});}
 if(motion){
  const groups=[['opening','01','03'],['execution','04','07'],['denied','08','10']];
  for(const [name,start,end]of groups){if(wanted&&!wanted.includes(start))continue;const a=shots.find(s=>s.id===start),b=shots.find(s=>s.id===end),file=path.join(out,`${name}-motion.mp4`),frameRange=[a.from,b.from+b.durationInFrames-1];await renderMedia({composition,serveUrl,codec:'h264',outputLocation:file,frameRange,inputProps,scale:.5,crf:22,concurrency:2,puppeteerInstance:browser,logLevel:'error',onBrowserLog});clips.push({name,file,frameRange,hideSubtitles,voice:false,sourceSha256});console.log('Motion '+name);}
 }
 fs.writeFileSync(path.join(out,'frames.json'),JSON.stringify({provisional:false,source:input,sourceSha256,hideSubtitles,voice:false,copyfit,gateFrames,samples,clips},null,2)+'\n');
 if(copyfit.length)throw new Error('COPYFIT overflow detected');
 for(const [p,sha]of Object.entries(sourceSha256))if(hash(p)!==sha)throw new Error('Input changed during QA: '+p);
}finally{await browser.close({silent:true});}
