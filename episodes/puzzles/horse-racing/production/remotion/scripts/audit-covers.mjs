import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition,openBrowser} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';
import webpack from 'webpack';

const root=path.resolve('..'),out=path.resolve(process.argv[2]??'out/covers-audit');fs.mkdirSync(out,{recursive:true});
const input=fs.existsSync('../storyboard.json')?path.resolve('../storyboard.json'):path.resolve('src/placeholders/storyboard.json');
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':path.resolve('../covers.json')},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browserExecutable='/usr/bin/chromium',browser=await openBrowser('chrome',{browserExecutable});
const audits=[],images=[];
const onBrowserLog=log=>{if(log.text?.startsWith('HORSE_LAYOUT_AUDIT ')){try{audits.push(JSON.parse(log.text.slice(19)));}catch{}}};
try{
 for(const size of ['16x9','4x3','3x4']){
  const id='Cover'+size,inputProps={size,auditLayout:true};
  const selected=await selectComposition({serveUrl,id,browserExecutable,puppeteerInstance:browser,inputProps});
  const composition={...selected,props:{...selected.props,...inputProps}};
  for(const format of ['png','jpeg']){
   const file=path.join(root,'cover-'+size+(format==='png'?'.png':'.jpg'));
   await renderStill({composition,serveUrl,output:file,browserExecutable,puppeteerInstance:browser,imageFormat:format,jpegQuality:format==='jpeg'?94:undefined,inputProps,onBrowserLog});
   images.push({size,format,file,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')});
  }
 }
}finally{await browser.close({silent:true});}
const latest=Object.fromEntries(audits.map(x=>[x.kind,x]));
const report={method:'Actual Chromium DOM/SVG bounding client rectangles after document.fonts.ready; scaled to composition pixels',checkedSizes:Object.keys(latest),audits:Object.values(latest),violations:Object.values(latest).flatMap(x=>x.violations.map(v=>({size:x.kind,...v}))),images};
fs.writeFileSync(path.join(out,'covers-layout-audit.json'),JSON.stringify(report,null,2));
console.log('cover audit: '+report.checkedSizes.length+' sizes, '+report.violations.length+' violations');
if(report.checkedSizes.length!==3||report.violations.length)process.exitCode=1;
