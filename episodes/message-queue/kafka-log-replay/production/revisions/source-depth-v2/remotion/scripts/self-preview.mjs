import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
const R=process.cwd(),D=path.resolve(R,'..'),O=path.join(D,'qa/self-preview');fs.mkdirSync(O,{recursive:true});
const sb=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'),'utf8'));
const shots=sb.scenes.flatMap(s=>s.shots),logs=[];
const url=await bundle({entryPoint:path.join(R,'src/index.ts'),publicDir:path.join(R,'public'),outDir:path.join(R,'out/self-bundle'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...(c.resolve?.alias??{}),'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(R,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:'true'})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium'});
const composition=await selectComposition({serveUrl:url,id:'Main',puppeteerInstance:browser,browserExecutable:"/usr/bin/chromium",inputProps:{showSubtitles:true}});
const selected=[];for(const s of shots){for(const p of [.15,.54,.88])selected.push({shot:s.id,frame:Math.min(s.from+s.durationInFrames-1,s.from+Math.round(s.durationInFrames*p))});}
for(const item of selected){const output=path.join(O,`shot-${item.shot}-f${item.frame}.png`);await renderStill({serveUrl:url,composition,frame:item.frame,output,puppeteerInstance:browser,browserExecutable:"/usr/bin/chromium",inputProps:{showSubtitles:true},onBrowserLog:x=>logs.push(x)});}
const plainComposition=await selectComposition({serveUrl:url,id:'Main',puppeteerInstance:browser,browserExecutable:'/usr/bin/chromium',inputProps:{showSubtitles:false,hideSubtitles:true}});
for(const [name,ids]of [['restore-fetch',['06','07','08','09']],['read-restart',['03','04','05','06']],['counter-retention',['10','11']]]){const rows=shots.filter(s=>ids.includes(s.id));const first=rows[0].from,last=rows.at(-1).from+rows.at(-1).durationInFrames-1;await renderMedia({serveUrl:url,composition:plainComposition,codec:'h264',outputLocation:path.join(O,`${name}-no-subtitles.mp4`),puppeteerInstance:browser,browserExecutable:"/usr/bin/chromium",inputProps:{showSubtitles:false,hideSubtitles:true},frameRange:[first,last],scale:.5,crf:28,concurrency:2,onBrowserLog:x=>logs.push(x)});}
fs.writeFileSync(path.join(O,'report.json'),JSON.stringify({status:'generated-awaiting-human-visual-review',selected,clips:['restore-fetch','read-restart','counter-retention'],logs,bodyFrames:composition.durationInFrames,scope:'Actual Remotion PNG/short clips, not frozen or formal final-body encoding.'},null,2)+'\n');await browser.close({silent:true});console.log(JSON.stringify({png:selected.length,clips:3,output:O}));
