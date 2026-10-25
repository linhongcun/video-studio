import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const require=createRequire(path.resolve('package.json'));
const {bundle}=require('@remotion/bundler');
const {openBrowser,renderStill,selectComposition}=require('@remotion/renderer');
const webpack=require('webpack');
const root=path.resolve('..'),out=path.join(root,'qa-tradeoffs-preflight');
const sb=JSON.parse(fs.readFileSync(path.join(root,'storyboard.json'),'utf8'));
const shots=sb.scenes.flatMap(s=>s.shots);
const selected=[
 ...[8,65,110,145,180,215,255,290,330,375,397,435].map(local=>({id:'16',local})),
 ...[30,65,125,165,200,250,286,340,365,455,500,550,640,730].map(local=>({id:'17',local})),
 {id:'06',local:shots.find(s=>s.id==='06').durationInFrames-1},
 {id:'16',local:452},{id:'17',local:0},{id:'17',local:773},{id:'07',local:0},{id:'07',local:25},
 ...[{id:'16',local:145},{id:'16',local:290},{id:'16',local:435},{id:'17',local:165},{id:'17',local:340},{id:'17',local:500},{id:'17',local:640},{id:'17',local:730}].map(r=>({...r,captions:true})),
];
fs.mkdirSync(out,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,
 webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':root+'/storyboard.json','@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
const records=[],logs=[];
try{
 const compositions={};for(const captions of [false,true])compositions[String(captions)]=await selectComposition({serveUrl,id:'Main',inputProps:{showSubtitles:true,hideSubtitles:!captions},puppeteerInstance:browser,logLevel:'error'});
 for(const record of selected.filter(r=>r.id==='16'&&r.local>=321)){
  const shot=shots.find(s=>s.id===record.id),frame=shot.from+record.local;
  const name=`${record.id}-f${String(record.local).padStart(3,'0')}${record.captions?'-sub':''}.png`;
  const file=path.join(out,name);
  await renderStill({composition:compositions[String(!!record.captions)],serveUrl,inputProps:{showSubtitles:true,hideSubtitles:!record.captions},frame,output:file,puppeteerInstance:browser,imageFormat:'png',scale:.5,logLevel:'error',onBrowserLog:l=>{if(/error|copyfit/i.test(l.text))logs.push(l.text)}});
  records.push({...record,frame,file});
 }
 const previous=JSON.parse(fs.readFileSync(path.join(out,'frames.json'),'utf8')); for(const record of records){const i=previous.records.findIndex(r=>r.id===record.id&&r.local===record.local&&!!r.captions===!!record.captions);if(i>=0)previous.records[i]=record;else previous.records.push(record);}previous.logs.push(...logs);fs.writeFileSync(path.join(out,'frames.json'),JSON.stringify(previous,null,2)+'\n');
 console.log(JSON.stringify({output:out,frames:records.length,browserErrorLogs:logs},null,2));
}finally{await browser.close({silent:true})}
