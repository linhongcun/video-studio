import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, renderMedia, selectComposition} from '@remotion/renderer';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import webpack from 'webpack';

// QA-only entry. Actual production scenes are rendered without modification.
const remotion=process.cwd(),episode=path.resolve(remotion,'..');
let repo=episode;
while(!fs.existsSync(path.join(repo,'AGENTS.md'))){const parent=path.dirname(repo);if(parent===repo)throw Error('Repository root missing');repo=parent;}
const out=path.resolve(process.argv[2]??'out/preflight'),smoke=false;
const planPath=path.resolve(episode,'qa-clear-parts-plan.json'),storyPath=path.resolve(episode,'storyboard.json');
const plan=JSON.parse(fs.readFileSync(planPath)),sb=JSON.parse(fs.readFileSync(storyPath));
fs.mkdirSync(out,{recursive:true});
const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
const files=[storyPath,path.join(episode,'model.json'),path.join(episode,'covers.json'),
 ...walk(path.join(remotion,'src')).filter(p=>!p.includes('/placeholders/')),
 ...walk(path.join(remotion,'scripts')).filter(p=>/\.(mjs|ts|tsx|js)$/.test(p)),
 ...['package.json','package-lock.json','remotion.config.ts','tsconfig.json'].map(p=>path.join(remotion,p)),
 path.join(repo,'episodes/_shared/theme/pageTheme.ts')];
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const sourceSHA=Object.fromEntries([...new Set(files)].map(p=>[path.relative(repo,p),hash(p)]));
const sourcesUnchanged=()=>{for(const[p,v]of Object.entries(sourceSHA))if(hash(path.join(repo,p))!==v)throw Error('QA source changed during rendering: '+p);};
let total=0;
const shots=sb.scenes.flatMap(s=>s.shots).map(s=>{const result={...s,id:String(s.id).padStart(2,'0'),from:total};total+=s.durationInFrames;return result;});
if(total!==plan.bodyFrames)throw Error('Plan/storyboard duration mismatch');
const frames=[...new Set(smoke?plan.smokeFrames:plan.frames)].sort((a,b)=>a-b);
if(!frames.length||frames.some(f=>!Number.isInteger(f)||f<0||f>=total))throw Error('Invalid actual-frame plan');
const inputProps={hideSubtitles:false,auditLayout:true};
const audits=new Map(),samples=[],clips=[];
const report={status:'in-progress',scope:'Actual bounded clear-parts transition PNG/DOM matrix and two short silent no-subtitle clips.',
 startedAtUTC:new Date().toISOString(),input:path.relative(repo,storyPath),sourceSHA,planSHA256:hash(planPath),inputProps,samples,clips,audits:[],violations:[]};
const persist=name=>{report.audits=[...audits.values()].sort((a,b)=>a.frame-b.frame);report.violations=report.audits.flatMap(a=>(a.violations??[]).map(v=>({frame:a.frame,...v})));fs.writeFileSync(path.join(out,name),JSON.stringify(report,null,2));};
const onBrowserLog=entry=>{const prefix='SKIPLIST_LAYOUT_AUDIT ';if(entry.text?.startsWith(prefix)){const a=JSON.parse(entry.text.slice(prefix.length));if(a.kind==='main')audits.set(a.frame,a);}};
const serveUrl=await bundle({entryPoint:path.join(remotion,'src/index.ts'),enableCaching:false,
 webpackOverride:c=>({...c,resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':storyPath,'@covers':path.join(episode,'covers.json')},modules:[path.join(remotion,'node_modules'),'node_modules']},
 plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
const browserExecutable='/usr/bin/chromium',browser=await openBrowser('chrome',{browserExecutable});
try{
 const selected=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps});
 const composition={...selected,props:{...selected.props,...inputProps}};
 if(composition.width!==sb.meta.width||composition.height!==sb.meta.height||composition.fps!==sb.meta.fps||composition.durationInFrames!==total)throw Error('Real composition metadata mismatch');
 report.composition={width:composition.width,height:composition.height,fps:composition.fps,durationInFrames:composition.durationInFrames};
 for(const frame of frames){
  const shot=shots.find(s=>frame>=s.from&&frame<s.from+s.durationInFrames),local=frame-shot.from;
  const file=path.join(out,`${shot.id}-local${String(local).padStart(3,'0')}.png`);
  await renderStill({composition,serveUrl,frame,output:file,imageFormat:'png',scale:1,browserExecutable,puppeteerInstance:browser,inputProps,onBrowserLog});
  const audit=audits.get(frame);if(!audit)throw Error('No real DOM audit at frame '+frame);
  samples.push({shot:shot.id,visualType:shot.visualType,frame,local,file,sha256:hash(file)});
  sourcesUnchanged();persist('samples-progress.json');
  console.log(path.basename(file));
  if(audit.violations?.length)throw Error('Actual DOM/layout violations at frame '+frame);
 }
 if(!smoke){
  const clipProps={hideSubtitles:true,auditLayout:false};
  const chosen=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps:clipProps});
  const clipComposition={...chosen,props:{...chosen.props,...clipProps}};
  for(const clip of plan.clips){
   const range=clip.range,file=path.join(out,clip.name+'.mp4');
   await renderMedia({composition:clipComposition,serveUrl,codec:'h264',crf:21,scale:.5,frameRange:range,outputLocation:file,browserExecutable,puppeteerInstance:browser,concurrency:2,inputProps:clipProps});
   const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file],{encoding:'utf8'}));
   if(probe.streams.some(s=>s.codec_type==='audio'))throw Error('A planned silent clip unexpectedly contains audio');
   const actualFrameCount=Number(probe.streams.find(s=>s.codec_type==='video').nb_frames);
   if(actualFrameCount!==range[1]-range[0]+1)throw Error('Actual continuous clip frame count mismatch');
   const reviewFrames=[...new Set(clip.reviewFrames)].filter(f=>f>=range[0]&&f<=range[1]).sort((a,b)=>a-b),decoded=[];
   for(const globalFrame of reviewFrames){
    const localFrame=globalFrame-range[0],png=path.join(out,`${clip.name}-f${String(globalFrame).padStart(5,'0')}.png`);
    execFileSync('ffmpeg',['-v','error','-y','-i',file,'-vf',`select=eq(n\\,${localFrame})`,'-frames:v','1',png]);
    const band=execFileSync('ffmpeg',['-v','error','-i',file,'-vf',`select=eq(n\\,${localFrame}),crop=iw:35:0:ih-45`,'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']);
    let foreground=0;for(let i=0;i<band.length;i+=3)if(Math.max(Math.abs(band[i]-15),Math.abs(band[i+1]-23),Math.abs(band[i+2]-42))>24)foreground++;
    if(foreground)throw Error('No-subtitle clip has foreground in subtitle-only band: '+clip.name+' frame '+globalFrame);
    decoded.push({globalFrame,localFrame,file:png,sha256:hash(png),subtitleBandForegroundPixels:foreground});
   }
   clips.push({name:clip.name,range,file,sha256:hash(file),inputProps:clipProps,compositionProps:clipComposition.props,
    actualVideoFrames:Number(probe.streams.find(s=>s.codec_type==='video').nb_frames),actualDuration:probe.format.duration,
    decodedReviewFrames:decoded,reviewStatus:'Actual images created; independent visual inspection is reported separately.'});
   sourcesUnchanged();persist('samples-progress.json');console.log('clip '+clip.name);
  }
 }
 sourcesUnchanged();
 if(audits.size!==frames.length)throw Error('Actual DOM/sample count mismatch');
 report.status=smoke?'smoke-completed-awaiting-full-preflight':'completed';report.completedAtUTC=new Date().toISOString();
 persist('samples.json');
 console.log(JSON.stringify({status:report.status,samples:samples.length,audits:audits.size,clips:clips.length,violations:report.violations.length}));
}catch(error){
 report.status='stopped-before-completion';report.error=String(error);report.stoppedAtUTC=new Date().toISOString();persist('failure.json');throw error;
}finally{await browser.close({silent:true});}
