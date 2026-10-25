import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import crypto from 'node:crypto';
const ep='/workspace/video-studio/episodes-codex/http-request';
const rem=ep+'/remotion',require=createRequire(rem+'/package.json');
const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,renderMedia}=require('@remotion/renderer');
const webpack=require('webpack');
const board=JSON.parse(fs.readFileSync(ep+'/storyboard.json','utf8'));
const shots=board.scenes.flatMap(s=>s.shots),out=process.env.HTTP_PREVIEW_OUT??'/tmp/http-depth-preview';
fs.mkdirSync(out,{recursive:true});
fs.mkdirSync(out+'/source',{recursive:true});
const srcPaths=['src/Scenes.tsx','src/Main.tsx','src/Primitives.tsx'];
fs.writeFileSync(out+'/source/sha256.json',JSON.stringify(Object.fromEntries(srcPaths.map(p=>{const b=fs.readFileSync(rem+'/'+p);fs.writeFileSync(out+'/source/'+path.basename(p),b);return [p,crypto.createHash('sha256').update(b).digest('hex')];})),null,2));
const inputProps={hideSubtitles:true};
const serveUrl=await bundle({entryPoint:rem+'/src/index.ts',enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':ep+'/storyboard.json','@covers':ep+'/covers.json'},modules:[rem+'/node_modules','node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const composition=await selectComposition({serveUrl,id:'Main',browserExecutable:'/usr/bin/chromium',inputProps});
const log=[],onBrowserLog=(l)=>{if(l.type==='error'||l.text.includes('COPYFIT'))log.push(l);};
const plan=[],only16=process.argv.includes('--only16'),finalCues=process.argv.includes('--final-cues');
for(const s of shots){
 if(only16&&s.id!=='16')continue;
 if(finalCues&&!['07','16'].includes(s.id))continue;
 const b=s.cueFrames?.sentences?.[1]??s.durationInFrames*.5;
 const key=s.id==='07'?'synackLabel':'http3Label';
 const locals=new Set((finalCues?[0,(s.cueFrames[key]??b)-1,s.cueFrames[key]??b,(s.cueFrames[key]??b)+2,24,Math.round(b),s.durationInFrames-1]:only16?[0,(s.cueFrames.http3Label??b)-1,s.cueFrames.http3Label??b,(s.cueFrames.http3Label??b)+2,s.durationInFrames-1]:[0,24,Math.round(b*.5),Math.round(b)-1,Math.round(b)+1,Math.round(b)+30,Math.round(b)+60,s.durationInFrames-1]).map(f=>Math.max(0,Math.min(s.durationInFrames-1,f))));
 for(const local of [...locals].sort((a,b)=>a-b))plan.push({shot:s.id,local,frame:s.from+local,name:`s${s.id}-f${String(local).padStart(4,'0')}`});
}
fs.writeFileSync(out+'/frameplan.json',JSON.stringify(plan,null,2));
if(!process.argv.includes('--video-only'))for(const f of plan){await renderStill({composition,serveUrl,frame:f.frame,output:out+'/'+f.name+'.png',browserExecutable:'/usr/bin/chromium',imageFormat:'png',scale:.5,inputProps,onBrowserLog});}
if(process.argv.includes('--video')||process.argv.includes('--video-only'))for(const [first,last] of (finalCues?[[7,7],[16,16]]:only16?[[16,16]]:[[6,9],[10,13],[14,16]])){
 const a=shots[first-1],b=shots[last-1],range=[a.from,b.from+b.durationInFrames-1];
 await renderMedia({composition,serveUrl,codec:'h264',outputLocation:out+`/shots-${first}-${last}-no-subtitles.mp4`,frameRange:range,browserExecutable:'/usr/bin/chromium',scale:.5,crf:23,concurrency:2,inputProps,onBrowserLog});
 console.log(`preview ${first}-${last} frames ${range}`);
}
fs.writeFileSync(out+'/browser-errors.json',JSON.stringify(log,null,2));
console.log(JSON.stringify({out,frames:plan.length,browserErrors:log.length}));
