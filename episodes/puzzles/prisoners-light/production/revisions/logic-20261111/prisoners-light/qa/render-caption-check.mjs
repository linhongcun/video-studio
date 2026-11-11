import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const D=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..'),REM=path.join(D,'remotion'),require=createRequire(path.join(REM,'package.json'));
const {bundle}=require('@remotion/bundler'),{openBrowser,selectComposition,renderStill}=require('@remotion/renderer'),webpack=require('webpack');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const out=path.join(D,'qa/caption-v1');fs.mkdirSync(out,{recursive:true});
const report={scope:'Producer actual long-sentence subtitle sample generation; visual review is separate.',source:{Main:sha(path.join(REM,'src/Main.tsx')),storyboard:sha(path.join(D,'storyboard.json'))},props:{hideSubtitles:false,auditLayout:true},samples:[],logs:[]};
const serveUrl=await bundle({entryPoint:path.join(REM,'src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(REM,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
try{const composition=await selectComposition({serveUrl,id:'PrisonersLight',inputProps:report.props,puppeteerInstance:browser,logLevel:'error'});
 for(const frame of [1085,1600,1900]){const output=path.join(out,`f${frame}.png`);await renderStill({serveUrl,composition,frame,output,imageFormat:'png',inputProps:report.props,puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{if(/COPYFIT|error/i.test(l.text))report.logs.push({frame,text:l.text});}});report.samples.push({frame,file:path.relative(D,output),sha256:sha(output)});}
 fs.writeFileSync(path.join(D,'qa/caption-v1.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{await browser.close({silent:true});}
