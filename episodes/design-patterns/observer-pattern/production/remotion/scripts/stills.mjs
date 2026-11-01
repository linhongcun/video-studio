import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
import webpack from 'webpack';
const root=path.resolve('..');
const input=fs.existsSync(root+'/storyboard.json')?root+'/storyboard.json':path.resolve('src/placeholders/storyboard.json');
const data=JSON.parse(fs.readFileSync(input,'utf8'));
const shots=data.scenes.flatMap(s=>s.shots);let from=0;
const frames=shots.map((s,i)=>{const frame=from+Math.min(s.durationInFrames-1,Math.round(s.durationInFrames*.65));from+=s.durationInFrames;return {name:String(i+1).padStart(2,'0'),frame};});
const wanted=new Set((process.env.QA_SHOTS??'').split(',').filter(Boolean));
const hideSubtitles=process.env.QA_HIDE_SUBTITLES==='1';
const inputProps={hideSubtitles,showSubtitles:!hideSubtitles};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':input,'@covers':root+'/covers.json'},modules:[path.resolve('node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const selected=await selectComposition({serveUrl,id:'Main',browserExecutable:'/usr/bin/chromium',inputProps});
const composition={...selected,props:{...selected.props,...inputProps}};
const out=process.argv[2]??'out/stills';fs.mkdirSync(out,{recursive:true});
for(const f of [{name:'first',frame:0},...frames.filter(f=>wanted.size===0||wanted.has(f.name))]){
 await renderStill({composition,serveUrl,frame:f.frame,output:out+'/'+f.name+'.png',browserExecutable:'/usr/bin/chromium',imageFormat:'png',scale:.5,inputProps});console.log(f.name+' '+f.frame);
}
