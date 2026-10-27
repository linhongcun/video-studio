import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition,openBrowser} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
const input=fs.existsSync('../storyboard.json')?path.resolve('../storyboard.json'):path.resolve('src/placeholders/storyboard.json');
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':path.resolve('../covers.json')},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browserExecutable='/usr/bin/chromium',browser=await openBrowser('chrome',{browserExecutable});
try {
 for(const size of ['16x9','4x3','3x4']){
  const id='Cover'+size;
  const composition=await selectComposition({serveUrl,id,browserExecutable,puppeteerInstance:browser});
  await renderStill({composition,serveUrl,output:path.resolve('../cover-'+size+'.png'),browserExecutable,puppeteerInstance:browser,imageFormat:'png'});
  await renderStill({composition,serveUrl,output:path.resolve('../cover-'+size+'.jpg'),browserExecutable,puppeteerInstance:browser,imageFormat:'jpeg',jpegQuality:94});
  console.log(id+' rendered (PNG + JPG)');
 }
 fs.copyFileSync(path.resolve('../cover-3x4.jpg'),path.resolve('../poster.jpg'));
} finally {await browser.close({silent:true});}
