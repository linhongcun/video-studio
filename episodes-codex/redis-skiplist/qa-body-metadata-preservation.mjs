// Independent small witness render after the reference-mode metadata rebuild.
// The original 231-sample report stays bound to its original storyboard.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const episode=path.dirname(fileURLToPath(import.meta.url));
const remotion=path.join(episode,'remotion');
const require=createRequire(path.join(remotion,'package.json'));
const {bundle}=require('@remotion/bundler');
const {openBrowser,renderStill,selectComposition}=require('@remotion/renderer');
const webpack=require('webpack');
const repo=path.resolve(episode,'../..');
const old=JSON.parse(fs.readFileSync(path.join(episode,'qa-preflight-evidence/samples.json')));
const out=path.join(remotion,'out/body-metadata-preservation');
fs.mkdirSync(out,{recursive:true});
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const storyboard=path.join(episode,'storyboard.json');
const sources=Object.fromEntries(Object.keys(old.sourceSHA).map(p=>[p,hash(path.join(repo,p))]));
const stable=()=>{for(const [p,h] of Object.entries(sources))if(hash(path.join(repo,p))!==h)throw Error('Witness source mutated: '+p);};
for(const [p,h] of Object.entries(old.sourceSHA))if(p!=='episodes-codex/redis-skiplist/storyboard.json'&&sources[p]!==h)throw Error('A body dependency changed: '+p);
const inputProps={hideSubtitles:false,auditLayout:true};
const audits=new Map();
const onBrowserLog=e=>{const prefix='SKIPLIST_LAYOUT_AUDIT ';if(e.text?.startsWith(prefix)){const a=JSON.parse(e.text.slice(prefix.length));if(a.kind==='main')audits.set(a.frame,a);}};
const serveUrl=await bundle({entryPoint:path.join(remotion,'src/index.ts'),enableCaching:false,
 webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':storyboard,'@covers':path.join(episode,'covers.json')},modules:[path.join(remotion,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const executable='/usr/bin/chromium';
const browser=await openBrowser('chrome',{browserExecutable:executable});
const report={status:'running',scope:'Three actual body PNG byte-reproduction witnesses; supplements separate complete dependency preservation proof.',sourceSHA:sources,oldSamplesSHA256:hash(path.join(episode,'qa-preflight-evidence/samples.json')),inputProps,frames:[]};
try{
 const selected=await selectComposition({serveUrl,id:'Main',browserExecutable:executable,puppeteerInstance:browser,inputProps});
 const composition={...selected,props:{...selected.props,...inputProps}};
 if(composition.durationInFrames!==4482||composition.width!==1920||composition.height!==1080||composition.fps!==30)throw Error('Body metadata changed');
 for(const frame of [2072,3134,3798]){
  const previous=old.samples.find(s=>s.frame===frame);if(!previous)throw Error('Original sample missing');
  const file=path.join(out,path.basename(previous.file));
  await renderStill({composition,serveUrl,frame,output:file,imageFormat:'png',scale:1,browserExecutable:executable,puppeteerInstance:browser,inputProps,onBrowserLog});
  const audit=audits.get(frame);if(!audit||audit.violations?.length)throw Error('Actual witness DOM missing/invalid');
  const same=hash(file)===previous.sha256;
  report.frames.push({frame,file,sha256:hash(file),oldSHA256:previous.sha256,byteIdenticalToOriginalFinalPreflight:same,actualDOMViolations:audit.violations.length});
  if(!same)throw Error('Witness PNG changed at '+frame);
  stable();
 }
 stable();report.status='passed';report.completedAtUTC=new Date().toISOString();report.audits=[...audits.values()];
}catch(e){report.status='failed';report.error=String(e);throw e;}
finally{fs.writeFileSync(path.join(out,'witness.json'),JSON.stringify(report,null,2));await browser.close({silent:true});}
console.log(JSON.stringify({status:report.status,witnesses:report.frames.length,allByteIdentical:report.frames.every(r=>r.byteIdenticalToOriginalFinalPreflight)}));
