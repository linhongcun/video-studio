import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition,renderMedia,openBrowser} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';
import webpack from 'webpack';
const root=path.resolve('..'),repo=path.resolve('../../..');
const input=process.env.QA_STORYBOARD?path.resolve(process.env.QA_STORYBOARD):(fs.existsSync(root+'/storyboard.json')?root+'/storyboard.json':path.resolve('src/placeholders/storyboard.json'));
const data=JSON.parse(fs.readFileSync(input,'utf8'));
let from=0;const shots=data.scenes.flatMap(s=>s.shots).map(s=>{const x={...s,from};from+=s.durationInFrames;return x;});
const out=path.resolve(process.argv[2]??'/tmp/container-stills');fs.mkdirSync(out,{recursive:true});
const proof=process.argv.includes('--proof');
const wanted=new Set((process.env.QA_SHOTS??(proof?'08,09,10,11':'')).split(',').filter(Boolean));
const fractions=(process.env.QA_FRACTIONS??(proof?'0,0.2,0.4,0.6,0.8,0.98':'0.65')).split(',').map(Number);
const explicit=(process.env.QA_FRAMES??'').split(',').filter(Boolean).map(Number);
const additional=(process.env.QA_EXTRA_FRAMES??'').split(',').filter(Boolean).map(Number);
const inputProps={hideSubtitles:process.env.QA_HIDE_SUBTITLES==='1'||proof};
const sourceFiles=[input,root+'/covers.json',root+'/solution.py',root+'/solution.json',...['Main.tsx','CodeCard.tsx','Cover.tsx','Root.tsx','theme.ts','data.ts','index.ts'].map(x=>path.resolve('src',x)),...['qa.mjs','covers.mjs'].map(x=>path.resolve('scripts',x)),path.resolve('remotion.config.ts'),path.resolve('package.json'),path.resolve('package-lock.json'),repo+'/episodes/_shared/theme/pageTheme.ts'];
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sourceSHA=Object.fromEntries(sourceFiles.map(p=>[path.relative(repo,p),hash(p)]));
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browserExecutable='/usr/bin/chromium',browser=await openBrowser('chrome',{browserExecutable});
try {
 const composition=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps});
 const frames=explicit.length?explicit.map(frame=>({name:String(frame),frame})):[{name:'first',frame:0},...shots.filter(s=>wanted.size===0||wanted.has(String(s.id).slice(0,2))).flatMap(s=>fractions.map(frac=>({name:String(s.id).slice(0,2)+'-'+String(frac).replace('.','_'),frame:s.from+Math.min(s.durationInFrames-1,Math.round(s.durationInFrames*frac))})))];
 frames.push(...additional.map(frame=>({name:'cue-'+String(frame),frame})));
 const samples=[];
 for(const f of frames){
  const file=out+'/'+f.name+'.png',s=shots.find(s=>f.frame>=s.from&&f.frame<s.from+s.durationInFrames),local=f.frame-s.from,caption=(s.subtitles??[]).find(x=>local>=x.from&&local<(x.to!==undefined?x.to+1:x.from+(x.duration??0)));
  await renderStill({composition,serveUrl,frame:f.frame,output:file,browserExecutable,puppeteerInstance:browser,imageFormat:'png',scale:Number(process.env.QA_SCALE??.5),inputProps});
  samples.push({shot:s.id,visualType:s.visualType,local,frame:f.frame,file,captionState:{hidden:inputProps.hideSubtitles,text:caption?.text??null}});console.log(f.name+' '+f.frame);
 }
 const manifest={input,sourceSHA,hideSubtitles:inputProps.hideSubtitles,inputProps,scale:Number(process.env.QA_SCALE??.5),frames,samples};
 fs.writeFileSync(out+'/samples.json',JSON.stringify(manifest,null,2));
 fs.writeFileSync(out+'/qa-motion-samples.json',JSON.stringify(manifest,null,2));
 if(process.env.QA_MANIFEST)fs.writeFileSync(path.resolve(process.env.QA_MANIFEST),JSON.stringify(manifest,null,2));
 const clips=process.env.QA_CLIPS?JSON.parse(process.env.QA_CLIPS):(proof||process.env.QA_CLIP?[{name:'motion',from:'08',to:'11'}]:[]);
 manifest.clips=[];
 for(const clip of clips){
  const first=shots.find(s=>String(s.id).startsWith(clip.from)),last=shots.find(s=>String(s.id).startsWith(clip.to));
  const range=process.env.QA_RANGE?process.env.QA_RANGE.split(',').map(Number):[first.from,last.from+last.durationInFrames-1],file=out+'/'+clip.name+'.mp4';
  const clipInputProps={...inputProps,hideSubtitles:true};
  const selected=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps:clipInputProps});
  const clipComposition={...selected,props:{...selected.props,hideSubtitles:true}};
  await renderMedia({composition:clipComposition,serveUrl,codec:'h264',crf:22,scale:.5,frameRange:range,outputLocation:file,browserExecutable,puppeteerInstance:browser,concurrency:2,inputProps:clipInputProps});
  manifest.clips.push({name:clip.name,frameRange:range,file,hideSubtitles:true});console.log('clip '+clip.name+' '+range.join('..'));
 }
 fs.writeFileSync(out+'/samples.json',JSON.stringify(manifest,null,2));
 fs.writeFileSync(out+'/qa-motion-samples.json',JSON.stringify(manifest,null,2));
 if(process.env.QA_MANIFEST)fs.writeFileSync(path.resolve(process.env.QA_MANIFEST),JSON.stringify(manifest,null,2));
 for(const [p,v] of Object.entries(sourceSHA))if(hash(path.resolve(repo,p))!==v)throw new Error('QA source changed during sampling: '+p);
} finally {await browser.close({silent:true});}
