import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
import crypto from 'node:crypto';
const input=fs.existsSync('../storyboard.json')?path.resolve('../storyboard.json'):path.resolve('src/placeholders/storyboard.json');
const copyfit=[];
const onBrowserLog=log=>{if(log.text?.includes('COPYFIT')){copyfit.push(log.text);console.error(log.text);}};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':path.resolve('../covers.json')},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
for(const size of ['16x9','4x3','3x4']){
 const composition=await selectComposition({serveUrl,id:'Cover'+size,browserExecutable:'/usr/bin/chromium'});
 for(const [extension,imageFormat]of [['png','png'],['jpg','jpeg']])await renderStill({composition,serveUrl,output:path.resolve('../cover-'+size+'.'+extension),browserExecutable:'/usr/bin/chromium',imageFormat,jpegQuality:imageFormat==='jpeg'?94:undefined,onBrowserLog});
 console.log('Cover'+size+' rendered (PNG + JPG)');
}
fs.copyFileSync(path.resolve('../cover-3x4.jpg'),path.resolve('../poster.jpg'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const files=Object.fromEntries(['16x9','4x3','3x4'].map(size=>[size,Object.fromEntries(['png','jpg'].map(ext=>{const p=path.resolve('../cover-'+size+'.'+ext);return[ext,{sha256:hash(p),bytes:fs.statSync(p).size}]}))]));
const sourceSha256=Object.fromEntries(['../covers.json','src/Cover.tsx','src/objects.tsx','src/theme.ts'].map(p=>[p,hash(p)]));
fs.writeFileSync(path.resolve('../cover-copyfit.json'),JSON.stringify({copyfit,passed:copyfit.length===0,sourceSha256,files,poster:{sameAs:'3x4.jpg',sha256:hash('../poster.jpg')}},null,2)+'\n');
if(copyfit.length)throw new Error('Cover COPYFIT overflow detected');
