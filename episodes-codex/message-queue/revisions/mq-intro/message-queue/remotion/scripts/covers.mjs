import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
import {execFileSync} from 'node:child_process';
const copyfit=[];const onBrowserLog=(q)=>{if(q.text.includes('COPYFIT')){copyfit.push(q.text);console.error(q.text)}};
const input=fs.existsSync('../storyboard.json')?path.resolve('../storyboard.json'):path.resolve('src/placeholders/storyboard.json');
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':path.resolve('../covers.json')},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
for(const size of ['16x9','4x3','3x4']){
 const id='Cover'+size;
 const composition=await selectComposition({serveUrl,id,browserExecutable:'/usr/bin/chromium'});
 await renderStill({composition,serveUrl,output:path.resolve('../cover-'+size+'.png'),browserExecutable:'/usr/bin/chromium',onBrowserLog,imageFormat:'png'});
 execFileSync('ffmpeg',['-y','-v','error','-i',path.resolve('../cover-'+size+'.png'),'-q:v','2',path.resolve('../cover-'+size+'.jpg')]);
 console.log(id+' PNG/JPG rendered');
}

fs.writeFileSync('../cover-copyfit.json',JSON.stringify(copyfit,null,2)+'\n');if(copyfit.length)throw new Error('COPYFIT failure');

fs.copyFileSync('../cover-3x4.jpg','../poster.jpg');
