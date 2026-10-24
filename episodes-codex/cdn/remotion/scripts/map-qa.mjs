// Actual progressive map/refresh preview with an explicit no-subtitle composition.
import {bundle} from '@remotion/bundler';
import {openBrowser,getCompositions,renderStill,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import webpack from 'webpack';

const out=path.resolve(process.argv[2]??'out/map-motion');
const clips=process.argv.includes('--clips');
const root=path.resolve('..');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)]);
const files=[...walk(path.resolve('src')),...walk(path.resolve('scripts')),...walk(root+'/assets'),...['script.md','storyboard.json','words.json','voice.wav','covers.json','visual-direction.md','knoll-props.md'].map(p=>root+'/'+p)];
const snapshot=()=>Object.fromEntries(files.sort().map(p=>[path.relative(root,p),sha(p)]));
const before=snapshot();
const sb=JSON.parse(fs.readFileSync(root+'/storyboard.json','utf8'));
const shots=sb.scenes.flatMap(s=>s.shots),get=id=>shots.find(s=>s.id===id);
fs.mkdirSync(out,{recursive:true});
const inputProps={hideSubtitles:true,showSubtitles:false};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':root+'/storyboard.json','@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
const records=[],media=[],warnings=[];
const onBrowserLog=q=>{if(q.text?.includes('COPYFIT'))warnings.push(q.text)};
try{
 const base=(await getCompositions(serveUrl,{inputProps,puppeteerInstance:browser,logLevel:'error'})).find(c=>c.id==='Main');
 if(!base)throw new Error('Main composition missing');
 const composition={...base,props:{...base.props,...inputProps}};
 if(!composition.props.hideSubtitles||composition.props.showSubtitles!==false)throw new Error('Subtitle props did not resolve');
 for(const id of ['03','04','05','06','07','08','09','12']){
  const s=get(id),s1=s.cueFrames.sentences[1];
  let local=[0,Math.round(s.durationInFrames*.18),Math.round(s.durationInFrames*.38),Math.round(s.durationInFrames*.58),Math.round(s.durationInFrames*.8),s.durationInFrames-1];
  if(id==='03')local.push(s.cueFrames.cdnLabel,35,80,s1+58);
  if(id==='04')local.push(s.cueFrames.edgeLabel,62,63);
  if(id==='05')local.push(s.cueFrames.originLabel-1,s.cueFrames.originLabel);
  if(id==='06')local.push(69,70,119,120,Math.max(125,s1+15)+39,Math.max(125,s1+15)+40);
  if(id==='07')local.push(62,63,s1+57,s1+58);
  if(id==='09')local.push(57,58,64,65,s1+102,s1+103,s1+108,s1+132,s1+152,s1+153);
  if(id==='12')local.push(s.durationInFrames-76,s.durationInFrames-64,s.durationInFrames-50,s.durationInFrames-38);
  local=[...new Set(local.filter(f=>f>=0&&f<s.durationInFrames))].sort((a,b)=>a-b);
  for(const frame of local){
   const file=path.join(out,`${id}-${frame}.png`);
   await renderStill({composition,serveUrl,inputProps,frame:s.from+frame,output:file,puppeteerInstance:browser,imageFormat:'png',scale:.5,logLevel:'error',onBrowserLog});
   records.push({shot:id,local:frame,frame:s.from+frame,file,sha256:sha(file),subtitles:false});
  }
  console.log('Stages ready',id,local.join(','));
 }
 fs.writeFileSync(out+'/frames.json',JSON.stringify(records,null,2)+'\n');
 if(clips){
  for(const [name,first,last] of [['map-03-07',get('03').from,get('07').from+get('07').durationInFrames-1],['refresh-09',get('09').from,get('09').from+get('09').durationInFrames-1],['recap-12',get('12').from,get('12').from+get('12').durationInFrames-1]]){
   const file=path.join(out,name+'-silent.mp4');
   await renderMedia({composition,serveUrl,inputProps,codec:'h264',outputLocation:file,frameRange:[first,last],puppeteerInstance:browser,scale:.5,concurrency:2,crf:22,muted:true,logLevel:'error',onBrowserLog});
   media.push({name,file,sha256:sha(file),first,last,frames:last-first+1,subtitles:false,muted:true,props:composition.props});
   console.log('Silent encoded preview ready',name,first,last);
  }
 }
 const after=snapshot();
 if(JSON.stringify(before)!==JSON.stringify(after))throw new Error('Production inputs changed during QA preview');
 fs.writeFileSync(out+'/evidence.json',JSON.stringify({inputs:before,unchangedAfterPreview:true,resolvedProps:composition.props,stills:records.length,media,warnings},null,2)+'\n');
 if(warnings.length)throw new Error('COPYFIT warnings in actual preview: '+warnings.join('; '));
}finally{await browser.close({silent:true});}
