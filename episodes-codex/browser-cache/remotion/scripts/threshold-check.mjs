import {bundle} from '@remotion/bundler';
import {openBrowser,renderStill,selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import webpack from 'webpack';
const root=path.resolve('..'),sb=JSON.parse(fs.readFileSync(root+'/storyboard.json','utf8'));
const hook=process.argv.includes('--hook');
const shot=sb.scenes.flatMap(s=>s.shots).find(s=>s.id===(hook?'01':'09'));
const output=hook?'/tmp/ep07-hook-final':'/tmp/ep07-threshold-final';fs.mkdirSync(output,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':root+'/storyboard.json','@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
try{
 const inputProps={hideSubtitles:true};const composition=await selectComposition({serveUrl,id:'Main',inputProps,puppeteerInstance:browser});
 for(const local of (hook?[0,45,60]:[81,82])){
  await renderStill({composition,serveUrl,inputProps,frame:shot.from+local,output:output+`/${shot.id}-${local}.png`,puppeteerInstance:browser,imageFormat:'png',scale:.5,onBrowserLog:log=>{if(log.text.includes('COPYFIT'))throw new Error(log.text)}});
  console.log('threshold local',local,'absolute',shot.from+local);
 }
}finally{await browser.close({silent:true});}
