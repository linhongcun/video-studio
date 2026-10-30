// Bounded independent MQ06 preview clips; never invokes the formal body pipeline.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {createRequire} from 'node:module';
const get=k=>process.argv.slice(2).find(x=>x.startsWith(k+'='))?.slice(k.length+1);
const D=path.resolve(get('--dir')),SPEC=JSON.parse(fs.readFileSync(get('--spec'),'utf8')),REM=path.join(D,'remotion'),req=createRequire(path.join(REM,'package.json'));
const {bundle}=req('@remotion/bundler'),{openBrowser,selectComposition,renderMedia,renderStill}=req('@remotion/renderer'),webpack=req('webpack');
const NAME=get('--name')??'continuous-independent-v1',Q=path.join(D,'qa-independent'),OUT=path.join(Q,NAME),REPORT=path.join(Q,NAME+'.json');fs.mkdirSync(OUT,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const inputs=['model.json','storyboard.json','script.md','voice.wav','remotion/public/audio/voice.wav','remotion/public/series-background.png','remotion/package-lock.json',...fs.readdirSync(path.join(REM,'src')).filter(x=>/\.(tsx?|json)$/.test(x)).map(x=>'remotion/src/'+x)];
for(const n of ['article.mdx','article-figure-plan.json'])if(fs.existsSync(path.join(D,n)))inputs.push(n);
const hashes=Object.fromEntries(inputs.map(n=>[n,sha(path.join(D,n))]));
if(hashes['voice.wav']!==hashes['remotion/public/audio/voice.wav'])throw Error('Actual public voice bytes differ');
if(fs.lstatSync(path.join(REM,'public/audio/voice.wav')).isSymbolicLink())throw Error('Public audio must be an entity');
const props={showSubtitles:false,hideSubtitles:true};
const report={createdAt:new Date().toISOString(),kind:'independent-bounded-continuous-source-preview',sourceHashes:hashes,props,clips:[],actualDOMClosures:[],console:[],machinePass:false,visualReviewed:false,scope:'Short continuous Remotion preflights, not frozen or formally encoded MP4. Voice is actual selected voice.wav; no subtitle or BGM replacement.'};
const save=()=>fs.writeFileSync(REPORT,JSON.stringify(report,null,2)+'\n');save();
const url=await bundle({entryPoint:path.join(REM,'src/index.ts'),publicDir:path.join(REM,'public'),outDir:path.join(Q,NAME+'-bundle'),enableCaching:false,webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(D,'storyboard.json'),'@covers':path.join(D,'covers.json')},modules:[path.join(REM,'node_modules'),'node_modules']},plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:'true'})]})});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/chromium',logLevel:'error'});let active=null;
const newPage=browser.newPage.bind(browser);browser.newPage=async options=>{const p=await newPage(options),close=p.close.bind(p);p.close=async args=>{if(active){const actual=await p.evaluate(()=>({subtitles:document.querySelectorAll('[data-subtitle]').length,modelState:document.querySelector('[data-model-state]')?.getAttribute('data-model-state')??null,projection:document.querySelector('[data-projection]')?.getAttribute('data-projection')??null}));report.actualDOMClosures.push({clip:active.name,...actual});save();if(actual.subtitles!==0)throw Error('Actual preview DOM contains subtitles');}return close(args)};return p;};
try{
 const comp=await selectComposition({serveUrl:url,id:'Main',inputProps:props,puppeteerInstance:browser,logLevel:'error'});comp.props={...comp.props,...props};report.resolvedProps=comp.props;report.bodyFrames=comp.durationInFrames;
 let frames=0;for(const s of SPEC.clips){if(!Number.isInteger(s.from)||!Number.isInteger(s.to)||s.to<s.from||s.from<0||s.to>=comp.durationInFrames||s.to-s.from+1>500)throw Error('Invalid or unbounded clip '+s.name);frames+=s.to-s.from+1;}if(frames>=comp.durationInFrames/2)throw Error('Preview scope exceeds half the body');
 for(const s of SPEC.clips){active=s;const png=path.join(OUT,s.name+'-no-subtitles.png');await renderStill({serveUrl:url,composition:comp,frame:Math.floor((s.from+s.to)/2),output:png,imageFormat:'png',inputProps:props,puppeteerInstance:browser,logLevel:'error'});
  const output=path.join(OUT,s.name+'-no-subtitles.mp4');await renderMedia({serveUrl:url,composition:comp,codec:'h264',outputLocation:output,inputProps:props,frameRange:[s.from,s.to],scale:.5,crf:24,concurrency:2,puppeteerInstance:browser,logLevel:'error',onBrowserLog:l=>{if(/COPYFIT|error/i.test(l.text))report.console.push({clip:s.name,text:l.text})}});
  report.clips.push({...s,frames:s.to-s.from+1,file:path.relative(D,output),sha256:sha(output),midpointPNG:path.relative(D,png),midpointPNGSHA256:sha(png)});save();console.log('completed',s.name);
 }
 report.sourceUnchanged=Object.entries(hashes).every(([n,h])=>sha(path.join(D,n))===h);report.machinePass=report.sourceUnchanged&&!report.console.length&&report.clips.length===SPEC.clips.length&&report.actualDOMClosures.length>=SPEC.clips.length&&report.actualDOMClosures.every(x=>x.subtitles===0);save();console.log(JSON.stringify({machinePass:report.machinePass,clips:report.clips.length,actualNoSubtitleDOMChecks:report.actualDOMClosures.length,report:REPORT}));
}finally{await browser.close({silent:true})}
