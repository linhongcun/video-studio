import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition,openBrowser} from '@remotion/renderer';
import path from 'node:path';import fs from 'node:fs';import crypto from 'node:crypto';import webpack from 'webpack';
const root=path.resolve('..'),out=path.resolve('out/covers-audit');fs.mkdirSync(out,{recursive:true});
const input=fs.existsSync(root+'/storyboard.json')?root+'/storyboard.json':path.resolve('src/placeholders/storyboard.json');
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browserExecutable='/usr/bin/chromium',browser=await openBrowser('chrome',{browserExecutable}),audits=[],images=[],onBrowserLog=log=>{if(log.text?.startsWith('EGG_LAYOUT_AUDIT '))audits.push(JSON.parse(log.text.slice('EGG_LAYOUT_AUDIT '.length)));};
try{for(const size of ['16x9','4x3','3x4']){const inputProps={size,auditLayout:true},selected=await selectComposition({serveUrl,id:'Cover'+size,browserExecutable,puppeteerInstance:browser,inputProps}),composition={...selected,props:{...selected.props,...inputProps}};for(const format of ['png','jpeg']){const file=root+'/cover-'+size+(format==='png'?'.png':'.jpg');await renderStill({composition,serveUrl,output:file,browserExecutable,puppeteerInstance:browser,inputProps,onBrowserLog,imageFormat:format,jpegQuality:format==='jpeg'?94:undefined});images.push({size,format,file,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')});}}}finally{await browser.close({silent:true});}
const latest=Object.fromEntries(audits.map(x=>[x.kind,x])),violations=Object.values(latest).flatMap(x=>x.violations);
const boundsPassed=Object.keys(latest).length===3&&violations.length===0&&images.length===6;
const report={status:boundsPassed?'bounds-passed-awaiting-visual-review':'failed',checkedAtUTC:new Date().toISOString(),method:'Actual Chromium SVG/DOM bounds after fonts load',audits:Object.values(latest),images,violations,visualReview:{status:'pending',scope:'Each actual PNG and JPG must be opened before covers are final.'}};
fs.writeFileSync(out+'/covers-layout-audit.json',JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(root+'/qa-covers.json',JSON.stringify(report,null,2)+'\n');
console.log('covers: '+Object.keys(latest).length+' sizes, '+violations.length+' violations, '+images.length+' actual image files');
if(!boundsPassed)process.exitCode=1;
