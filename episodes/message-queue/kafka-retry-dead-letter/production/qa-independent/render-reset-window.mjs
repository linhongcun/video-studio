// Independent continuous source window, executed only after the author stops production writes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const D=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const Q=path.join(D,'qa-independent'), OUT=path.join(Q,'reset-window');
if(fs.existsSync(OUT))throw Error('Preserve earlier attempt; choose a new explicit output before rerunning.');
fs.mkdirSync(OUT,{recursive:true});
const req=createRequire(path.join(D,'remotion/package.json'));
const {bundle}=req('@remotion/bundler');
const {openBrowser,selectComposition,renderMedia}=req('@remotion/renderer');
const webpack=req('webpack');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const inputs=['remotion/src/Main.tsx','model.json','storyboard.json','voice.wav','script.md','article.mdx','plan.json','article-figure-plan.json','remotion/public/audio/voice.wav'];
const hashes=Object.fromEntries(inputs.map(p=>[p,sha(path.join(D,p))]));
if(hashes['voice.wav']!==hashes['remotion/public/audio/voice.wav'])throw Error('Actual public voice must match final voice.');
const props={showSubtitles:false,hideSubtitles:true};
const report={startedAtUTC:new Date().toISOString(),kind:'independent-actual-final-timing-source-window',frameRange:[2676,3455],expectedFrames:780,expectedSeconds:26,sourceHashes:hashes,props,hasActualVoice:true,domChecks:[],console:[],pass:false,visualReviewed:false};
const save=()=>fs.writeFileSync(path.join(OUT,'report.json'),JSON.stringify(report,null,2)+'\n');
save();
const serveUrl=await bundle({entryPoint:path.join(D,'remotion/src/index.ts'),publicDir:path.join(D,'remotion/public'),outDir:path.join(Q,'reset-window-bundle'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(D,'remotion/node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:true})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});
const newPage=browser.newPage.bind(browser);
browser.newPage=async opts=>{const p=await newPage(opts),close=p.close.bind(p);p.close=async arg=>{try{const m=await p.evaluate(()=>({subtitles:document.querySelectorAll('[data-subtitle]').length,modelState:document.querySelector('[data-model-state]')?.getAttribute('data-model-state')??null}));if(m.modelState){report.domChecks.push(m);save();}}catch(e){report.domChecks.push({measurementError:String(e)});save();}return close(arg);};return p;};
try{
 const composition=await selectComposition({serveUrl,id:'Main',inputProps:props,puppeteerInstance:browser,logLevel:'error'});
 composition.props={...composition.props,...props};
 report.resolvedProps=composition.props;save();
 await renderMedia({serveUrl,composition,inputProps:props,puppeteerInstance:browser,codec:'h264',audioCodec:'aac',crf:24,scale:.5,concurrency:2,frameRange:report.frameRange,outputLocation:path.join(OUT,'success-to-exhausted-and-permanent-resets.mp4'),logLevel:'error',onBrowserLog:l=>{if(/COPYFIT|error/i.test(l.text)){report.console.push(l);save();}}});
 report.sourceUnchanged=Object.entries(hashes).every(([p,h])=>sha(path.join(D,p))===h);
 report.videoSHA256=sha(path.join(OUT,'success-to-exhausted-and-permanent-resets.mp4'));
 report.pass=report.sourceUnchanged&&!report.console.length&&report.domChecks.some(x=>x.modelState)&&report.domChecks.every(x=>!x.measurementError&&x.subtitles===0);
 report.finishedAtUTC=new Date().toISOString();save();
 console.log(JSON.stringify({pass:report.pass,path:OUT}));
}catch(e){report.failure={name:e.name,message:e.message,stack:e.stack};save();throw e;}finally{await browser.close({silent:true});}
