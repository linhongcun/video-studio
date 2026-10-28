#!/usr/bin/env node
/** Sample the redis-style entry without changing original frozen inputs.
 * Usage: node episodes-codex/_shared/redis-cache-video/qa.mjs server-cache \
 *   --out-dir work/redis-qa/redis-skiplist [--frames 0,100,200] [--scale 1]
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';

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
if(!['server-cache','cache-consistency'].includes(slug))throw new Error(`Unknown Redis slug: ${slug}`);
if(!options['--out-dir'])throw new Error('--out-dir is required');
const scale=Number(options['--scale']??.5);
if(!Number.isFinite(scale)||scale<=0||scale>1)throw new Error('--scale must be greater than 0 and at most 1');
const fontInputs=JSON.parse(execFileSync('python3',[path.join(here,'render.py'),slug,'--font-inputs'],{encoding:'utf8'}));
const style=JSON.parse(fs.readFileSync(path.join(here,'style-v1.json'),'utf8'));
const out=path.resolve(options['--out-dir']);
const episode=path.resolve(repo,'episodes-codex',slug);
const remotion=path.join(episode,'remotion');
const entry=path.join(remotion,'src/redis-style/index.ts');
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
const closureBridge=String.raw`import importlib.util,json,sys
from pathlib import Path
from types import SimpleNamespace
path=Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('cache_qa_actual_inputs',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
ctx=module.context(SimpleNamespace(episode=sys.argv[2],revision='redis-style',baseline=None,entry='src/redis-style/index.ts',composition='Main'))
print(json.dumps([str(p.relative_to(module.ROOT)) for p in module.production_inputs(ctx,module.adapter_module())]))
`;
// Use the renderer's actual closure, including reused identity modules and the
// new navigation palette, rather than maintaining a partial shared-file list.
const closure=JSON.parse(execFileSync('python3',['-c',closureBridge,path.join(here,'render.py'),slug],{encoding:'utf8'}));
const sourceFiles=[...new Set([
  ...closure.map(file=>path.join(repo,file)),
  input,covers,...filesIn(path.join(remotion,'src')),
  path.join(remotion,'remotion.config.ts'),path.join(remotion,'package.json'),path.join(remotion,'package-lock.json'),
  path.join(here,'Frame.tsx'),path.join(here,'theme.ts'),path.join(here,'render.py'),fileURLToPath(import.meta.url),
  path.join(here,'style-v1.json'),
])];
const sources=Object.fromEntries(sourceFiles.sort().map(file=>[path.relative(repo,file),hash(file)]));
fs.mkdirSync(out,{recursive:true});
const inputProps={hideSubtitles:false,showSubtitles:true};
const report={schemaVersion:1,status:'running',slug,entry:path.relative(repo,entry),
  startedAt:new Date().toISOString(),inputProps,scale,requestedFrames:frames,fontInputs,
  selection:options['--frames']===undefined?{mode:'per-shot',fractions}:{mode:'explicit'},
  bodyFrames:total,auditMethod:'Renderer Page.close evaluates actual DOM after capture; no production hooks',sourceSHA256:sources,samples:[],audits:[],violations:[],missingAudits:[],
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
  const diagnostics={apply(compiler){compiler.hooks.done.tap('RedisQADiagnostics',stats=>{
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
  // Use the renderer's own documented Page.evaluate/close API. The still is
  // already captured when the page closes, so these are final-frame DOM boxes;
  // no production component, animation state or browser global is modified.
  const newPage=browser.newPage.bind(browser);
  browser.newPage=async creationOptions=>{
    const page=await newPage(creationOptions);
    const close=page.close.bind(page);
    page.close=async closeOptions=>{
      let auditError;
      try{
        if(Number.isInteger(renderFrame)&&!page.closed){
          const audit=await page.evaluate(async ({frame,fontStacks})=>{
            await document.fonts.ready;
            const calibration=document.querySelector('[data-redis-canvas]')
              ??document.querySelector('#remotion-canvas')??document.body;
            const base=calibration.getBoundingClientRect();
            if(base.width<=0||base.height<=0)return {skipped:true,frame,reason:'empty calibration'};
            const sx=base.width/1920,sy=base.height/1080;
            const box=r=>({x:(r.x-base.x)/sx,y:(r.y-base.y)/sy,w:r.width/sx,h:r.height/sy});
            const visible=element=>{
              let alpha=1,node=element;
              while(node){const style=getComputedStyle(node);
                if(style.display==='none'||style.visibility==='hidden')return false;
                alpha*=Number(style.opacity);node=node.parentElement;}
              return alpha>.03;
            };
            const subtitle=document.querySelector('[data-subtitle]');
            const subtitleBox=subtitle&&visible(subtitle)?box(subtitle.getBoundingClientRect()):null;
            const texts=[];const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
            while(walker.nextNode()){
              const node=walker.currentNode,element=node.parentElement,text=(node.textContent??'').trim();
              if(!text||!element||element.closest('script,style,noscript')||!visible(element))continue;
              const range=document.createRange();range.selectNodeContents(node);
              for(const rect of range.getClientRects()){
                if(rect.width<=.05||rect.height<=.05)continue;
                texts.push({text,...box(rect),tag:element.tagName,
                  subtitle:!!element.closest('[data-subtitle]'),fontFamily:getComputedStyle(element).fontFamily,fontSize:getComputedStyle(element).fontSize,fontWeight:getComputedStyle(element).fontWeight});
              }
            }
            if(texts.length===0)return {skipped:true,frame,reason:'no rendered text'};
            const region={left:35,right:1885,top:20,bottom:1055};
            const violations=[];
            if(document.fonts.status!=='loaded')violations.push({type:'fonts-not-ready',status:document.fonts.status});
            const fontChecks=Object.fromEntries(Object.entries(fontStacks).map(([role,stack])=>[role,document.fonts.check(`32px ${stack}`,role==='mono'?'def solution(nums):':'Redis缓存 IT小村')]));
            if(Object.values(fontChecks).some(value=>value!==true))violations.push({type:'required-font-unavailable',checks:fontChecks});
            for(const text of texts){
              if(text.x<region.left-.5||text.x+text.w>region.right+.5||
                  text.y<region.top-.5||text.y+text.h>region.bottom+.5){
                violations.push({type:'text-outside-safe-region',text,region});}
              if(!text.subtitle&&subtitleBox&&text.y+text.h>subtitleBox.y-6&&
                  text.y<subtitleBox.y+subtitleBox.h&&text.x<subtitleBox.x+subtitleBox.w&&
                  text.x+text.w>subtitleBox.x){
                violations.push({type:'scene-text-subtitle-overlap',text,subtitle:subtitleBox});}
            }
            return {kind:'main',frame,width:1920,height:1080,
              calibration:calibration.getAttribute('data-redis-canvas')!==null?'data-redis-canvas':calibration.id||calibration.tagName,
              region,texts,subtitle:subtitleBox,fonts:{status:document.fonts.status,checks:fontChecks},violations};
          },{frame:renderFrame,fontStacks:style.fonts});
          if(!audit.skipped)report.audits.push({prefix:'REDIS_LAYOUT_AUDIT',requestedFrame:renderFrame,...audit});
          else report.auditParseErrors.push({requestedFrame:renderFrame,message:audit.reason});
        }
      }catch(error){auditError=error;}
      await close(closeOptions);
      if(auditError)throw auditError;
    };
    return page;
  };

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
