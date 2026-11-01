import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const require=createRequire(path.resolve('package.json'));
const {bundle}=require('@remotion/bundler');
const {openBrowser,renderStill,selectComposition}=require('@remotion/renderer');
const webpack=require('webpack');
const root=path.resolve('..'),out=path.join(root,'qa-methods-preflight');
const sb=JSON.parse(fs.readFileSync(path.join(root,'storyboard.json'),'utf8'));
const shots=sb.scenes.flatMap(s=>s.shots);
const selected=[
 ...[0,160,187,212,225,239,274,300,335,371].map(local=>({id:'16',local})),
 ...[0,15,28,38,55,70,81,95,106,130,240,285,335,368].map(local=>({id:'17',local})),
 ...[{id:'06',local:shots.find(s=>s.id==='06').durationInFrames-1},{id:'07',local:0},{id:'07',local:25}],
];
fs.mkdirSync(out,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,
 webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':root+'/storyboard.json','@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
const records=[],logs=[];
try{
 const compositions={}; for(const captions of [false,true]) compositions[String(captions)]=await selectComposition({serveUrl,id:'Main',inputProps:{showSubtitles:true,hideSubtitles:!captions},puppeteerInstance:browser,logLevel:'error'});
 for(const record of [...selected,...[{id:'16',local:160},{id:'16',local:335},{id:'17',local:55},{id:'17',local:240},{id:'17',local:335}].map(s=>({...s,captions:true}))]){
  const shot=shots.find(s=>s.id===record.id),frame=shot.from+record.local;
  const name=`${record.id}-f${String(record.local).padStart(3,'0')}${record.captions?'-sub':''}.png`;
  const file=path.join(out,name);
  await renderStill({composition:compositions[String(!!record.captions)],serveUrl,inputProps:{showSubtitles:true,hideSubtitles:!record.captions},frame,output:file,puppeteerInstance:browser,imageFormat:'png',scale:.5,logLevel:'error',onBrowserLog:l=>{if(/error|copyfit/i.test(l.text))logs.push(l.text)}});
  records.push({...record,frame,file});
 }
 fs.writeFileSync(path.join(out,'frames.json'),JSON.stringify({records,logs},null,2)+'\n');
 console.log(JSON.stringify({output:out,frames:records.length,browserErrorLogs:logs},null,2));
}finally{await browser.close({silent:true})}
