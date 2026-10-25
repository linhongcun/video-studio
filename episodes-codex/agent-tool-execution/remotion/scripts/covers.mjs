import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
const input=fs.existsSync('../storyboard.json')?path.resolve('../storyboard.json'):path.resolve('src/placeholders/storyboard.json');
const copyfit=[];
const onBrowserLog=log=>{if(log.text?.includes('COPYFIT')){copyfit.push(log.text);console.error(log.text);}};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':path.resolve('../covers.json')},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
for(const size of ['16x9','4x3','3x4']){
 const id='Cover'+size;
 const composition=await selectComposition({serveUrl,id,browserExecutable:'/usr/bin/chromium'});
 await renderStill({composition,serveUrl,output:path.resolve('../cover-'+size+'.png'),browserExecutable:'/usr/bin/chromium',imageFormat:'png',onBrowserLog});
 execFileSync('ffmpeg',['-v','error','-y','-i',path.resolve('../cover-'+size+'.png'),'-q:v','2',path.resolve('../cover-'+size+'.jpg')]);
 console.log(id+' rendered');
}
fs.copyFileSync(path.resolve('../cover-3x4.jpg'),path.resolve('../poster.jpg'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const files=Object.fromEntries(['16x9','4x3','3x4'].map(size=>{const p=path.resolve('../cover-'+size+'.png');return [size,{sha256:hash(p),bytes:fs.statSync(p).size}];}));
const sourceSha256=Object.fromEntries(['../covers.json','src/Cover.tsx','src/objects.tsx','src/theme.ts'].map(p=>[p,hash(p)]));
fs.writeFileSync(path.resolve('../cover-copyfit.json'),JSON.stringify({copyfit,passed:copyfit.length===0,sourceSha256,files},null,2)+'\n');
if(copyfit.length)throw new Error('Cover COPYFIT overflow detected');
