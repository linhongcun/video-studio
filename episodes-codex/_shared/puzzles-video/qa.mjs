#!/usr/bin/env node
/** Sample the cover-continuity entry without changing original frozen inputs.
 * Usage: node episodes-codex/_shared/puzzles-video/qa.mjs water-jug \
 *   --out-dir work/puzzles-qa/water-jug [--frames 0,100,200] [--scale 1]
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';

const here=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(here,'../../..');
const args=process.argv.slice(2);
const slug=args.shift();
const options={};
for(let i=0;i<args.length;i+=2){
  if(!['--out-dir','--frames','--scale'].includes(args[i])||args[i+1]===undefined){
    throw new Error('Usage: qa.mjs SLUG --out-dir PATH [--frames 0,100] [--scale 1]');
  }
  if(Object.hasOwn(options,args[i]))throw new Error(`Duplicate option: ${args[i]}`);
  options[args[i]]=args[i+1];
}
const catalog=JSON.parse(fs.readFileSync(path.resolve(here,'../puzzles-covers/catalog.json'),'utf8'));
if(!catalog.episodes.some(ep=>ep.slug===slug))throw new Error(`Unknown puzzle slug: ${slug}`);
if(!options['--out-dir'])throw new Error('--out-dir is required');
const scale=Number(options['--scale']??.5);
if(!Number.isFinite(scale)||scale<=0||scale>1)throw new Error('--scale must be greater than 0 and at most 1');
const out=path.resolve(options['--out-dir']);
const episode=path.resolve(repo,'episodes-codex',slug);
const remotion=path.join(episode,'remotion');
const entry=path.join(remotion,'src/cover-continuity/index.ts');
const input=path.join(episode,'storyboard.json');
const covers=path.join(episode,'covers.json');
const storyboard=JSON.parse(fs.readFileSync(input,'utf8'));
let total=0;
const shots=storyboard.scenes.flatMap(scene=>scene.shots).map(shot=>{
  const item={...shot,from:total};
  total+=shot.durationInFrames;
  return item;
});
const fractions=[0,.5,.98];
let frames;
if(options['--frames']!==undefined){
  if(!/^\d+(,\d+)*$/.test(options['--frames']))throw new Error('--frames must be comma-separated nonnegative integers');
  frames=options['--frames'].split(',').map(Number);
}else{
  frames=[0,...shots.flatMap(shot=>fractions.map(fraction=>shot.from+Math.min(shot.durationInFrames-1,Math.round(shot.durationInFrames*fraction))))];
}
frames=[...new Set(frames)].sort((a,b)=>a-b);
if(frames.some(frame=>!Number.isSafeInteger(frame)||frame<0||frame>=total))throw new Error(`Every frame must be in 0..${total-1}`);
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const filesIn=directory=>fs.readdirSync(directory,{withFileTypes:true}).flatMap(item=>{
  const file=path.join(directory,item.name);
  return item.isDirectory()?filesIn(file):item.isFile()&&/\.(?:ts|tsx|mjs|json)$/.test(item.name)?[file]:[];
});
const sourceFiles=[...new Set([
  input,covers,...filesIn(path.join(remotion,'src')),
  path.join(remotion,'remotion.config.ts'),path.join(remotion,'package.json'),path.join(remotion,'package-lock.json'),
  path.join(here,'Frame.tsx'),path.join(here,'theme.ts'),fileURLToPath(import.meta.url),
  path.resolve(here,'../puzzles-covers/catalog.json'),
])];
const sources=Object.fromEntries(sourceFiles.sort().map(file=>[path.relative(repo,file),hash(file)]));
fs.mkdirSync(out,{recursive:true});
const inputProps={auditLayout:true,hideSubtitles:false};
const report={schemaVersion:1,status:'running',slug,entry:path.relative(repo,entry),
  startedAt:new Date().toISOString(),inputProps,scale,requestedFrames:frames,
  selection:options['--frames']===undefined?{mode:'per-shot',fractions}:{mode:'explicit'},
  bodyFrames:total,sourceSHA256:sources,samples:[],audits:[],violations:[],missingAudits:[],
  browserWarnings:[],browserErrors:[],bundleWarnings:[],bundleErrors:[],auditParseErrors:[]};
let browser;
let renderFrame=null;
const onBrowserLog=log=>{
  const match=/^([A-Z0-9_]+_LAYOUT_AUDIT)\s+(\{.*\})$/s.exec(log.text??'');
  if(match){
    try{report.audits.push({prefix:match[1],requestedFrame:renderFrame,...JSON.parse(match[2])});}
    catch(error){report.auditParseErrors.push({requestedFrame:renderFrame,text:log.text,error:String(error)});}
  }else if(['warning','warn','error','assert'].includes(log.type)){
    const item={requestedFrame:renderFrame,...log};
    (['error','assert'].includes(log.type)?report.browserErrors:report.browserWarnings).push(item);
  }
};
try{
  const require=createRequire(path.join(remotion,'package.json'));
  const {bundle}=require('@remotion/bundler');
  const {renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
  const webpack=require('webpack');
  const diagnostics={apply(compiler){compiler.hooks.done.tap('PuzzleQADiagnostics',stats=>{
    const info=stats.toJson({all:false,warnings:true,errors:true});
    report.bundleWarnings.push(...(info.warnings??[]).map(item=>typeof item==='string'?item:item.message));
    report.bundleErrors.push(...(info.errors??[]).map(item=>typeof item==='string'?item:item.message));
  });}};
  const serveUrl=await bundle({entryPoint:entry,enableCaching:false,publicDir:path.join(remotion,'public'),
    webpackOverride:config=>({...config,resolve:{...config.resolve,
      alias:{...config.resolve?.alias,'@storyboard':input,'@covers':covers},
      modules:[path.join(remotion,'node_modules'),'node_modules']},
      plugins:[...(config.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false}),diagnostics]})});
  const browserExecutable='/usr/bin/chromium';
  browser=await openBrowser('chrome',{browserExecutable,logLevel:'error'});
  const composition=await selectComposition({serveUrl,id:'Main',browserExecutable,
    puppeteerInstance:browser,inputProps,onBrowserLog,logLevel:'error'});
  report.video={width:composition.width,height:composition.height,fps:composition.fps,durationInFrames:composition.durationInFrames};
  if(composition.durationInFrames!==total)throw new Error(`Composition duration differs: ${composition.durationInFrames} != ${total}`);
  for(const frame of frames){
    renderFrame=frame;
    const file=path.join(out,`frame-${String(frame).padStart(6,'0')}.png`);
    const auditStart=report.audits.length;
    await renderStill({composition,serveUrl,frame,output:file,browserExecutable,
      puppeteerInstance:browser,imageFormat:'png',scale,inputProps,onBrowserLog,logLevel:'error'});
    const shot=shots.find(item=>frame>=item.from&&frame<item.from+item.durationInFrames);
    const matching=report.audits.slice(auditStart).filter(audit=>audit.frame===frame);
    if(matching.length===0)report.missingAudits.push(frame);
    report.samples.push({frame,shot:shot.id,visualType:shot.visualType,localFrame:frame-shot.from,
      file,sha256:hash(file),auditCount:matching.length});
    console.log(`${slug}: frame ${frame}, audits ${matching.length}`);
  }
  for(const [relative,expected] of Object.entries(sources)){
    if(hash(path.resolve(repo,relative))!==expected)throw new Error(`QA input changed during sampling: ${relative}`);
  }
  // Some renderers emit initial frame logs as well; retain the raw records but
  // count only each requested frame's own final audit once in the result.
  const finalAudits=new Map();
  for(const audit of report.audits){
    if(audit.requestedFrame===audit.frame&&frames.includes(audit.frame)){
      finalAudits.set(`${audit.prefix}:${audit.kind}:${audit.frame}`,audit);
    }
  }
  report.finalAudits=[...finalAudits.values()];
  report.violations=report.finalAudits.flatMap(audit=>(audit.violations??[]).map(violation=>({frame:audit.frame,prefix:audit.prefix,...violation})));
  report.status=report.violations.length||report.missingAudits.length||report.browserErrors.length||report.bundleErrors.length||report.auditParseErrors.length?'failed':'passed';
}catch(error){
  report.status='failed';
  report.failure={message:String(error),stack:error?.stack};
  console.error(error?.stack??error);
}finally{
  if(browser)await browser.close({silent:true});
  report.completedAt=new Date().toISOString();
  fs.writeFileSync(path.join(out,'qa-report.json'),JSON.stringify(report,null,2)+'\n');
  fs.writeFileSync(path.join(out,'layout-audit.json'),JSON.stringify({slug,checkedFrames:report.samples.map(sample=>sample.frame),audits:report.finalAudits??[],violations:report.violations,missingAudits:report.missingAudits},null,2)+'\n');
}
console.log(`${slug}: ${report.status}; ${report.samples.length} frames, ${report.violations.length} violations, ${report.browserWarnings.length} warnings, ${report.browserErrors.length} errors`);
if(report.status!=='passed')process.exitCode=1;
