// Silent continuous previews. All frame ranges come from this episode's real voice storyboard.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const D=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..'),REM=path.join(D,'remotion');
const require=createRequire(path.join(REM,'package.json'));
const {bundle}=require('@remotion/bundler'),{openBrowser,selectComposition,renderMedia}=require('@remotion/renderer'),webpack=require('webpack');
const get=k=>process.argv.slice(2).find(s=>s.startsWith(k+'='))?.slice(k.length+1);
const name=get('--name')??'animation-dynamic-v1',out=path.join(D,'qa/out',name);fs.mkdirSync(out,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sb=JSON.parse(fs.readFileSync(path.join(D,'storyboard.json'))),shots=sb.scenes.flatMap(s=>s.shots);let offset=0;
for(const s of shots){if(s.voice?.length!==2)throw Error('Actual voice timing required');s.from=offset;offset+=s.durationInFrames;}
const sourceFiles=['storyboard.json','model-data.json','remotion/package.json','remotion/package-lock.json','remotion/remotion.config.ts',...fs.readdirSync(path.join(REM,'src')).filter(p=>/\.(ts|tsx)$/.test(p)).map(p=>'remotion/src/'+p),'../../../_shared/puzzles-video/Frame.tsx','../../../_shared/puzzles-video/theme.ts','../../../_shared/puzzles-covers/catalog.json'];
const hashes=Object.fromEntries(sourceFiles.map(p=>[p,sha(path.join(D,p))]));
const groups=(get('--shots')??'03,05-07,08,09,11,12,14').split(',').map(item=>item.split('-').map(Number));
const props={hideSubtitles:true,auditLayout:false};
const report={createdAt:new Date().toISOString(),executor:'Codex animation producer',props,sourceHashes:hashes,clips:[],rendered:false,visualReviewed:false,limitations:['Silent preview renders; semantic narration audition and full realtime viewing are separate checks.']};
const save=()=>fs.writeFileSync(path.join(D,'qa',name+'.json'),JSON.stringify(report,null,2)+'\n');save();
const url=await bundle({entryPoint:path.join(REM,'src/index.ts'),enableCaching:false,publicDir:path.join(REM,'public'),webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json')},modules:[path.join(REM,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
try{
  const composition=await selectComposition({serveUrl:url,id:'TwelveBalls',inputProps:props,puppeteerInstance:browser,logLevel:'error'});
  for(const [first,last=first] of groups){const selected=shots.filter(s=>Number(s.id)>=first&&Number(s.id)<=last);if(!selected.length)throw Error('No actual shots selected '+first);const frameRange=[selected[0].from,selected.at(-1).from+selected.at(-1).durationInFrames-1],file=path.join(out,`shots-${first}-${last}.mp4`);
    await renderMedia({serveUrl:url,composition,frameRange,outputLocation:file,codec:'h264',crf:25,scale:.5,concurrency:2,inputProps:props,puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{if(/COPYFIT/.test(l.text))throw Error(l.text);}});
    report.clips.push({first,last,frameRange,seconds:(frameRange[1]-frameRange[0]+1)/composition.fps,file:path.relative(D,file),sha256:sha(file)});save();console.log('Rendered silent actual-time shots '+first+'-'+last);
  }
  report.sourceUnchanged=Object.entries(hashes).every(([p,h])=>sha(path.join(D,p))===h);report.rendered=report.sourceUnchanged;save();
}finally{await browser.close({silent:true});}
