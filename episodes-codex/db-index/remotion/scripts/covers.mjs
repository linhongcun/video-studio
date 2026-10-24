import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.resolve('../storyboard.json'),'@covers':path.resolve('../covers.json')},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
for(const size of ['16x9','4x3','3x4']){
 const id='Cover'+size;
 const composition=await selectComposition({serveUrl,id,browserExecutable:'/usr/bin/chromium'});
 await renderStill({composition,serveUrl,output:path.resolve('../cover-'+size+'.png'),browserExecutable:'/usr/bin/chromium',imageFormat:'png'});
 console.log(id+' rendered');
}
