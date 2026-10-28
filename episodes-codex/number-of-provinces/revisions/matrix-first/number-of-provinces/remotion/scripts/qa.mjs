#!/usr/bin/env node
/** Sample the leetcode-style entry without changing original frozen inputs.
 * Usage: node episodes-codex/_shared/leetcode-video/qa.mjs two-sum \
 *   --out-dir work/leetcode-qa/two-sum [--frames 0,100,200] [--scale 1]
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';

// Local path adapter for the current nested revision; the layout audit is the
// current shared LeetCode QA implementation, without production hooks.
let repo=path.dirname(fileURLToPath(import.meta.url));
while(!fs.existsSync(path.join(repo,'AGENTS.md'))){const up=path.dirname(repo);if(up===repo)throw new Error('Repository root not found');repo=up;}
const here=path.join(repo,'episodes-codex/_shared/leetcode-video');
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
const catalog=JSON.parse(fs.readFileSync(path.join(here,'identities-v1.json'),'utf8'));
if(!catalog.episodes.some(ep=>ep.slug===slug))throw new Error(`Unknown LeetCode slug: ${slug}`);
if(!options['--out-dir'])throw new Error('--out-dir is required');
const scale=Number(options['--scale']??.5);
if(!Number.isFinite(scale)||scale<=0||scale>1)throw new Error('--scale must be greater than 0 and at most 1');
const fontInputs=JSON.parse(execFileSync('python3',[path.join(here,'render.py'),slug,'--font-inputs'],{encoding:'utf8'}));
const style=JSON.parse(fs.readFileSync(path.join(here,'style-v1.json'),'utf8'));
const out=path.resolve(options['--out-dir']);
const episode=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const remotion=path.join(episode,'remotion');
const entry=path.join(remotion,'src/leetcode-style/index.ts');
const input=path.join(episode,'storyboard.json');
const covers=path.join(episode,'covers.json');
const storyboard=JSON.parse(fs.readFileSync(input,'utf8'));
let total=0;
const shots=storyboard.scenes.flatMap(scene=>scene.shots).map(shot=>{
  const item={...shot,from:total};
  total+=shot.durationInFrames;
  return item;
});
const codeIntervals=shots.filter(shot=>Number.isInteger(shot.codeCardFrom)).map(shot=>({shot:shot.id,from:shot.from+shot.codeCardFrom,durationInFrames:shot.durationInFrames-shot.codeCardFrom}));
const card=storyboard.meta?.unvoicedEndCard;
if(codeIntervals.length!==1||!card||card.durationInFrames!==150||card.from!==codeIntervals[0].from||card.from+150!==total)throw new Error('Original complete Python card must occupy the final 150 body frames');
const displayFile=path.join(episode,card.displaySource);
const solution=JSON.parse(fs.readFileSync(displayFile,'utf8'));
const codeLines=solution.lines;
if(!Array.isArray(codeLines)||codeLines.some(line=>typeof line!=='string'))throw new Error('Original Python display source has no complete line array');
const fractions=[0,.5,.98];
let frames;
if(options['--frames']!==undefined){
  if(!/^\d+(,\d+)*$/.test(options['--frames']))throw new Error('--frames must be comma-separated nonnegative integers');
  frames=options['--frames'].split(',').map(Number);
}else{
  frames=[0,...shots.flatMap(shot=>fractions.map(fraction=>shot.from+Math.min(shot.durationInFrames-1,Math.round(shot.durationInFrames*fraction)))),...codeIntervals.flatMap(card=>[card.from-1,card.from,card.from+Math.floor(card.durationInFrames/2),card.from+card.durationInFrames-1])];
}
frames=[...new Set(frames)].sort((a,b)=>a-b);
if(frames.some(frame=>!Number.isSafeInteger(frame)||frame<0||frame>=total))throw new Error(`Every frame must be in 0..${total-1}`);
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const filesIn=directory=>fs.readdirSync(directory,{withFileTypes:true}).flatMap(item=>{
  const file=path.join(directory,item.name);
  return item.isDirectory()?filesIn(file):item.isFile()&&/\.(?:ts|tsx|mjs|json)$/.test(item.name)?[file]:[];
});
const sourceFiles=[...new Set([
  input,covers,displayFile,path.join(episode,card.codeSource),...filesIn(path.join(remotion,'src')),
  path.join(remotion,'remotion.config.ts'),path.join(remotion,'package.json'),path.join(remotion,'package-lock.json'),
  path.join(here,'Frame.tsx'),path.join(here,'theme.ts'),path.join(here,'render.py'),fileURLToPath(import.meta.url),
  path.join(here,'style-v1.json'),path.join(here,'identities-v1.json'),
])];
const sources=Object.fromEntries(sourceFiles.sort().map(file=>[path.relative(repo,file),hash(file)]));
fs.mkdirSync(out,{recursive:true});
const inputProps={hideSubtitles:false,showSubtitles:true};
const report={schemaVersion:1,status:'running',slug,entry:path.relative(repo,entry),
  startedAt:new Date().toISOString(),inputProps,scale,requestedFrames:frames,fontInputs,
  selection:options['--frames']===undefined?{mode:'per-shot-and-code-boundary',fractions,codeIntervals}:{mode:'explicit',codeIntervals},
  bodyFrames:total,codeIntervals,expectedCodeLineCount:codeLines.length,auditMethod:'Renderer Page.close evaluates actual DOM after capture; no production hooks',sourceSHA256:sources,samples:[],audits:[],violations:[],missingAudits:[],
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
  const {renderStill,selectComposition,openBrowser,renderMedia}=require('@remotion/renderer');
  const webpack=require('webpack');
  const diagnostics={apply(compiler){compiler.hooks.done.tap('LeetCodeQADiagnostics',stats=>{
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
          const audit=await page.evaluate(async ({frame,codeFrom,expectedCodeLines,fontStacks})=>{
            await document.fonts.ready;
            const calibration=document.querySelector('[data-leetcode-canvas]')
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
            const codeCards=[...document.querySelectorAll('[data-code-card="complete-python-solution"],[data-code-card="full-python-static-150-frames"]')].filter(visible);
            const codeCard=codeCards[0]??null;
            const markedCode=codeCard?[...codeCard.querySelectorAll('[data-code-line]')].filter(visible):[];
            const codeNodes=markedCode.length?markedCode:codeCard?[...codeCard.querySelectorAll('text')].filter(node=>visible(node)&&node.getAttribute('xml:space')==='preserve'):[];
            // Retain empty lines and every leading space. The alternate marker
            // is the original LC547/739 card; production markup is unchanged.
            const computedCode=codeNodes.map(node=>node.textContent??'');
            const codeVisible=Boolean(codeCard);
            const inCode=frame>=codeFrom;
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
            const fontChecks=Object.fromEntries(Object.entries(fontStacks).map(([role,stack])=>[role,document.fonts.check(`32px ${stack}`,role==='mono'?'def solution(nums):':'算法题完整代码 IT小村')]));
            if(Object.values(fontChecks).some(value=>value!==true))violations.push({type:'required-font-unavailable',checks:fontChecks});
            if(inCode&&!codeVisible)violations.push({type:'complete-python-card-missing'});
            if(inCode&&codeCards.length>1)violations.push({type:'multiple-complete-python-cards',count:codeCards.length});
            if(!inCode&&codeVisible)violations.push({type:'python-card-before-boundary'});
            if(inCode&&JSON.stringify(computedCode)!==JSON.stringify(expectedCodeLines))violations.push({type:'python-lines-differ',expected:expectedCodeLines,actual:computedCode});
            if(inCode&&subtitleBox)violations.push({type:'subtitle-on-python-card',subtitle:subtitleBox});
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
              calibration:calibration.getAttribute('data-leetcode-canvas')!==null?'data-leetcode-canvas':calibration.id||calibration.tagName,
              region,texts,subtitle:subtitleBox,fonts:{status:document.fonts.status,checks:fontChecks},code:{expected:inCode,visible:codeVisible,marker:codeCard?.getAttribute('data-code-card')??null,lineSource:markedCode.length?'data-code-line':'xml:space-preserve',lineCount:computedCode.length,linesMatch:inCode?JSON.stringify(computedCode)===JSON.stringify(expectedCodeLines):null},violations};
          },{frame:renderFrame,codeFrom:card.from,expectedCodeLines:codeLines,fontStacks:style.fonts});
          if(!audit.skipped)report.audits.push({prefix:'LEETCODE_LAYOUT_AUDIT',requestedFrame:renderFrame,...audit});
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
      file,sha256:hash(file),codeCard:frame>=card.from,auditCount:matching.length});
    console.log(`${slug}: frame ${frame}, audits ${matching.length}`);
  }
  if(process.env.QA_CLIP==='1'){
    renderFrame=null;
    const range=[shots[0].from,shots[2].from+shots[2].durationInFrames-1];
    const file=path.join(out,'opening-motion.mp4');
    const motionProps={hideSubtitles:true};
    const motionComposition=await selectComposition({serveUrl,id:'Main',browserExecutable,puppeteerInstance:browser,inputProps:motionProps,logLevel:'error'});
    await renderMedia({composition:motionComposition,serveUrl,codec:'h264',crf:22,scale:.5,frameRange:range,outputLocation:file,browserExecutable,puppeteerInstance:browser,concurrency:2,inputProps:motionProps,logLevel:'error'});
    report.clips=[{file,frameRange:range,hideSubtitles:true,scale:.5,sha256:hash(file)}];
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
