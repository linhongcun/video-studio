import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition,renderMedia,openBrowser} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';
import webpack from 'webpack';
const root=path.resolve('..');
const out=path.join(root,'remotion/out/qa-push-recheck');fs.mkdirSync(out,{recursive:true});
const input=path.join(root,'storyboard.json'),frozenPath=path.join(root,'source-sha256.json');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const frozen=JSON.parse(fs.readFileSync(frozenPath,'utf8'));
const verify=()=>{for(const [rel,sha] of Object.entries(frozen))if(hash(path.resolve(root,rel))!==sha)throw new Error('Frozen input changed: '+rel);};
verify();
const ranges=[[1648,1664],[1814,1829],[1916,1932],[1987,2003],[2063,2079],[2418,2434],[2745,2761],[2867,2883],[3194,3210],[3356,3364]];
const frames=[...new Set([...ranges.flatMap(([a,b])=>[a,Math.floor((a+b)/2),b]),2753,2754])].sort((a,b)=>a-b);
const captionFrames=[2473,2567,2676,2780,2753,2754].sort((a,b)=>a-b);
const sourceSHA={...frozen,'source-sha256.json':hash(frozenPath),'revisions/push-label-results-after/recheck.mjs':hash(path.join(root,'revisions/push-label-results-after/recheck.mjs'))};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browserExecutable='/usr/bin/chromium',browser=await openBrowser('chrome',{browserExecutable});
const outputs=[];
try{
 const composition=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps:{hideSubtitles:true}});
 for(const frame of frames){
  const file=path.join(out,`silent-${frame}.png`);
  await renderStill({composition,serveUrl,frame,output:file,browserExecutable,puppeteerInstance:browser,imageFormat:'png',scale:.5,inputProps:{hideSubtitles:true}});
  outputs.push({file,frame,hideSubtitles:true,sha256:hash(file)});
 }
 const captioned=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps:{hideSubtitles:false}});
 for(const frame of captionFrames){
  const file=path.join(out,`captioned-${frame}.png`);
  await renderStill({composition:captioned,serveUrl,frame,output:file,browserExecutable,puppeteerInstance:browser,imageFormat:'png',scale:.5,inputProps:{hideSubtitles:false}});
  outputs.push({file,frame,hideSubtitles:false,sha256:hash(file)});
 }
 for(let i=0;i<ranges.length;i++){
  const range=ranges[i],file=path.join(out,`push-${String(i+1).padStart(2,'0')}-${range[0]}-${range[1]}.mp4`);
  await renderMedia({composition,serveUrl,codec:'h264',crf:22,scale:.5,frameRange:range,outputLocation:file,browserExecutable,puppeteerInstance:browser,concurrency:2,inputProps:{hideSubtitles:true}});
  outputs.push({file,frameRange:range,hideSubtitles:true,sha256:hash(file)});console.log('push window '+range.join('..'));
 }
 verify();
 const manifest={scope:'Targeted recheck of all ten animated push windows; no full-shot or full-video encoding',reviewRequest:'derive_container exact frame ranges',sourceSHA,frozenEntries:Object.keys(frozen).length,provisionalTiming:false,pendingAudio:false,stillFrames:frames,captionedFrames:captionFrames,clipRanges:ranges,outputs};
 fs.writeFileSync(path.join(out,'samples.json'),JSON.stringify(manifest,null,2)+'\n');
 fs.writeFileSync(path.join(root,'revisions/push-label-results-after/recheck-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 console.log('Targeted recheck complete: '+frames.length+' silent frames, '+captionFrames.length+' captioned frames, '+ranges.length+' short windows.');
}finally{await browser.close({silent:true});}
