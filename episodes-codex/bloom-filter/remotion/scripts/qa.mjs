import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition,renderMedia,openBrowser} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import webpack from 'webpack';
const root=path.resolve('..'),repo=path.resolve('../../..'),out=path.resolve(process.argv[2]??'out/preflight');fs.mkdirSync(out,{recursive:true});
const input=process.env.QA_STORYBOARD?path.resolve(process.env.QA_STORYBOARD):(fs.existsSync(root+'/storyboard.json')?root+'/storyboard.json':path.resolve('src/placeholders/storyboard.json'));
let from=0;const shots=JSON.parse(fs.readFileSync(input)).scenes.flatMap(x=>x.shots).map(s=>{const v={...s,from};from+=s.durationInFrames;return v;});
const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(x=>x.isDirectory()?walk(path.join(dir,x.name)):[path.join(dir,x.name)]);
const sourceFiles=[input,root+'/covers.json',root+'/model.json',...walk(path.resolve('src')).filter(p=>!p.includes('/placeholders/')),...walk(path.resolve('scripts')),path.resolve('remotion.config.ts'),path.resolve('tsconfig.json'),path.resolve('package.json'),path.resolve('package-lock.json'),repo+'/episodes/_shared/theme/pageTheme.ts'];
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),sourceSHA=Object.fromEntries(sourceFiles.map(p=>[path.relative(repo,p),hash(p)]));
const wanted=new Set((process.env.QA_SHOTS??'').split(',').filter(Boolean)),fractions=(process.env.QA_FRACTIONS??'.1,.5,.9').split(',').map(Number),explicit=(process.env.QA_FRAMES??'').split(',').filter(Boolean).map(Number);
const frames=explicit.length?explicit:shots.filter(s=>!wanted.size||wanted.has(String(s.id).slice(0,2))).flatMap(s=>fractions.map(p=>s.from+Math.min(s.durationInFrames-1,Math.round(s.durationInFrames*p))));
const inputProps={hideSubtitles:process.env.QA_HIDE_SUBTITLES==='1',auditLayout:true};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browserExecutable='/usr/bin/chromium',browser=await openBrowser('chrome',{browserExecutable}),audits=[],samples=[],clips=[];
const onBrowserLog=log=>{if(log.text?.startsWith('BLOOM_LAYOUT_AUDIT '))audits.push(JSON.parse(log.text.slice('BLOOM_LAYOUT_AUDIT '.length)));};
try{
 const selected=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps}),composition={...selected,props:{...selected.props,...inputProps}};
 for(const frame of frames){const s=shots.find(s=>frame>=s.from&&frame<s.from+s.durationInFrames),local=frame-s.from,file=out+'/'+String(s.id).slice(0,2)+'-local'+String(local).padStart(3,'0')+'.png';await renderStill({composition,serveUrl,frame,output:file,browserExecutable,puppeteerInstance:browser,imageFormat:'png',scale:Number(process.env.QA_SCALE??.5),inputProps,onBrowserLog});samples.push({shot:s.id,visualType:s.visualType,frame,local,file,sha256:hash(file)});console.log(path.basename(file));}
 for(const clip of JSON.parse(process.env.QA_CLIPS??'[]')){
  const first=shots.find(s=>String(s.id).startsWith(clip.from)),last=shots.find(s=>String(s.id).startsWith(clip.to)),range=clip.range??[first.from,last.from+last.durationInFrames-1],file=out+'/'+clip.name+'.mp4',clipProps={hideSubtitles:true,auditLayout:false};
  const selectedClip=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps:clipProps}),clipComposition={...selectedClip,props:{...selectedClip.props,...clipProps}};
  await renderMedia({composition:clipComposition,serveUrl,codec:'h264',crf:22,scale:.5,frameRange:range,outputLocation:file,browserExecutable,puppeteerInstance:browser,concurrency:2,inputProps:clipProps});
  const middle=Math.floor((range[1]-range[0])/2),decoded=out+'/'+clip.name+'-decoded-mid.png';
  execFileSync('ffmpeg',['-v','error','-y','-i',file,'-vf',`select=eq(n\\,${middle})`,'-frames:v','1',decoded]);
  const strip=execFileSync('ffmpeg',['-v','error','-i',file,'-vf',`select=eq(n\\,${middle}),crop=iw:40:0:ih-50`,'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']);let nonBackground=0;
  for(let i=0;i<strip.length;i+=3)if(Math.max(Math.abs(strip[i]-15),Math.abs(strip[i+1]-23),Math.abs(strip[i+2]-42))>24)nonBackground++;
  if(nonBackground)throw Error('Actual no-subtitle output contains foreground in subtitle-only band');
  clips.push({name:clip.name,file,sha256:hash(file),range,inputProps:clipProps,compositionProps:clipComposition.props,decodedRepresentative:{file:decoded,localFrame:middle,sha256:hash(decoded),subtitleBandNonBackgroundPixels:nonBackground}});fs.writeFileSync(out+'/samples-progress.json',JSON.stringify({status:'more clips pending; completed clip entries are actual outputs',input,sourceSHA,inputProps,samples,clips},null,2));console.log('clip '+clip.name);
 }
}finally{await browser.close({silent:true});}
for(const [p,v]of Object.entries(sourceSHA))if(hash(path.join(repo,p))!==v)throw Error('QA source changed: '+p);
const latest=Object.fromEntries(audits.map(x=>[x.frame,x])),violations=Object.values(latest).flatMap(x=>x.violations.map(v=>({frame:x.frame,...v}))),report={input,sourceSHA,inputProps,samples,clips,audits:Object.values(latest),violations};
fs.writeFileSync(out+'/samples.json',JSON.stringify(report,null,2));fs.writeFileSync(out+'/layout-audit.json',JSON.stringify({method:'Actual Chromium SVG/DOM bounds after fonts load',audits:report.audits,violations},null,2));
console.log('actual layout frames '+report.audits.length+', violations '+violations.length);if(report.audits.length!==samples.length||violations.length)process.exitCode=1;
