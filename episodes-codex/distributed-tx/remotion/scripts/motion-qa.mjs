// Inspect semantic motion in multiple phases, without leaning on subtitles/audio.
// node scripts/motion-qa.mjs /tmp/ep21-motion --shots=03,05,08,09,10,11,12 --clips
import {bundle} from '@remotion/bundler';
import {openBrowser, renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import webpack from 'webpack';

const args=process.argv.slice(2);
const output=path.resolve(args.find(a=>!a.startsWith('--'))??'/tmp/ep21-motion');
const ids=(args.find(a=>a.startsWith('--shots='))?.slice(8)??'03,05,08,09,10,11,12').split(',');
const clips=args.includes('--clips');
const flow=args.find(a=>a.startsWith('--flow='))?.slice(7).split('-');
const root=path.resolve('..');
const storyboard=JSON.parse(fs.readFileSync(root+'/storyboard.json','utf8'));
const selected=storyboard.scenes.flatMap(s=>s.shots).filter(s=>ids.includes(s.id));
if(selected.length!==ids.length)throw new Error('Unknown shot selection');
fs.mkdirSync(output,{recursive:true});
const inputProps={hideSubtitles:true};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,
 webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,
 '@storyboard':root+'/storyboard.json','@covers':root+'/covers.json'},
 modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),
 new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
const records=[];
try{
 const composition=await selectComposition({serveUrl,id:'Main',inputProps,puppeteerInstance:browser,logLevel:'error'});
 for(const shot of selected){
  for(const [i,phase] of [0,.18,.38,.58,.8,.97].entries()){
   const frame=shot.from+Math.min(shot.durationInFrames-1,Math.round(shot.durationInFrames*phase));
   const file=path.join(output,`${shot.id}-${i}.png`);
   await renderStill({composition,serveUrl,inputProps,frame,output:file,
    puppeteerInstance:browser,imageFormat:'png',scale:.5,logLevel:'error'});
   records.push({shot:shot.id,phase,frame,file});
  }
  if(clips){
   await renderMedia({composition,serveUrl,inputProps,codec:'h264',
    outputLocation:path.join(output,`${shot.id}-silent.mp4`),
    frameRange:[shot.from,shot.from+shot.durationInFrames-1],
    puppeteerInstance:browser,scale:.5,concurrency:2,crf:22,muted:true,logLevel:'error'});
  }
  console.log(`Motion QA ${shot.id}: 6 phases${clips?' and silent clip':''}`);
 }
 if(flow){
  const all=storyboard.scenes.flatMap(s=>s.shots);
  const first=all.find(s=>s.id===flow[0]),last=all.find(s=>s.id===flow[1]);
  if(!first||!last||first.from>last.from)throw new Error('Unknown flow range');
  await renderMedia({composition,serveUrl,inputProps,codec:'h264',
   outputLocation:path.join(output,`flow-${flow.join('-')}-silent.mp4`),
   frameRange:[first.from,last.from+last.durationInFrames-1],
   puppeteerInstance:browser,scale:.5,concurrency:2,crf:22,muted:true,logLevel:'error'});
  console.log(`Motion QA flow ${flow.join('-')} ready`);
 }
 fs.writeFileSync(path.join(output,'frames.json'),JSON.stringify(records,null,2)+'\n');
}finally{await browser.close({silent:true});}
