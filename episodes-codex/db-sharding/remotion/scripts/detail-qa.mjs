// Dense source-frame sampling around extraction and query-return transitions.
import {bundle} from '@remotion/bundler';
import {openBrowser,renderStill,selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
const root=path.resolve('..'),out=process.argv[2]??'/tmp/ep19-detail';
fs.mkdirSync(out,{recursive:true});
const inputProps={hideSubtitles:true};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':root+'/storyboard.json','@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
try{
 const composition=await selectComposition({serveUrl,id:'Main',inputProps,puppeteerInstance:browser,logLevel:'error'});
 const frames=[...[0,6,12,18,24,36,100,120,140,160,200].map(f=>({name:`07-${f}`,frame:1580+f})),...[0,130,145,146,156,166,176,186,201,211,220,260].map(f=>({name:`11-${f}`,frame:2607+f}))];
 for(const f of frames){await renderStill({composition,serveUrl,inputProps,frame:f.frame,output:path.join(out,f.name+'.png'),puppeteerInstance:browser,imageFormat:'png',scale:.5,logLevel:'error'});}
 fs.writeFileSync(path.join(out,'frames.json'),JSON.stringify(frames,null,2)+'\n');
 console.log(`Dense QA ${frames.length} frames`);
}finally{await browser.close({silent:true});}
