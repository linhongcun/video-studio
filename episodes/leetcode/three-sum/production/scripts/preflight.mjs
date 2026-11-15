/** LC15 actual Remotion DOM COPYFIT, subtitle and complete-code-card audit.
 * Based on the shared LeetCode QA's Page.close audit, using this episode entry.
 * Does not drive the site or replace independent continuous-video review.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
const ep=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const repo=path.resolve(ep,'../../../..'),remotion=path.join(ep,'remotion');
const require=createRequire(path.join(remotion,'package.json'));
const {bundle}=require('@remotion/bundler'),{renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
const webpack=require('webpack');
const sb=JSON.parse(fs.readFileSync(path.join(ep,'storyboard.json')));
const shots=sb.scenes.flatMap(s=>s.shots),card=sb.meta.unvoicedEndCard;
const code=JSON.parse(fs.readFileSync(path.join(ep,'solution.json'))).lines;
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const out=path.join(ep,'qa/preflight');fs.mkdirSync(out,{recursive:true});
const frames=[...new Set(shots.flatMap(s=>[s.from,s.from+Math.floor(s.durationInFrames/2),s.from+s.durationInFrames-1,
  ...s.subtitles.map(c=>s.from+Math.floor((c.from+c.to)/2))]).concat([card.from-1,card.from,card.from+75,card.from+149]))].sort((a,b)=>a-b);
const report={status:'running',startedAt:new Date().toISOString(),storyboardSHA256:sha(path.join(ep,'storyboard.json')),
  frames,audits:[],warnings:[],errors:[],fontFiles:[],limitation:'Sampled final-frame geometry; continuous action and sound reviewed separately.'};
for(const family of ['Noto Sans CJK SC','JetBrains Mono']){
  const p=execFileSync('fc-match',['-f','%{file}',family],{encoding:'utf8'}).trim();
  report.fontFiles.push({family,path:p,sha256:sha(p)});
}
let browser,frame=null;
try{
  const serveUrl=await bundle({entryPoint:path.join(remotion,'src/index.ts'),enableCaching:false,
    publicDir:path.join(remotion,'public'),webpackOverride:c=>({...c,
      resolve:{...c.resolve,alias:{...c.resolve?.alias,'@storyboard':path.join(ep,'storyboard.json')}},
      plugins:[...(c.plugins??[]),new webpack.DefinePlugin({__HAS_VOICE_AUDIO__:false})]})});
  const executable=process.env.CHROME_BIN??'/usr/bin/chromium';
  browser=await openBrowser('chrome',{browserExecutable:executable,logLevel:'error'});
  const newPage=browser.newPage.bind(browser);
  browser.newPage=async options=>{
    const page=await newPage(options),close=page.close.bind(page);
    page.close=async options=>{
      if(Number.isInteger(frame)&&!page.closed){
        const audit=await page.evaluate(async ({frame,cardFrom,code})=>{
          await document.fonts.ready;
          const base=(document.querySelector('[data-leetcode-canvas]')??document.querySelector('svg')).getBoundingClientRect();
          const box=r=>({x:(r.x-base.x)*1920/base.width,y:(r.y-base.y)*1080/base.height,w:r.width*1920/base.width,h:r.height*1080/base.height});
          const visible=e=>{let a=1;while(e){const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden')return false;a*=Number(s.opacity);e=e.parentElement;}return a>.03;};
          const sub=document.querySelector('[data-subtitle]'),subtitle=sub&&visible(sub)?box(sub.getBoundingClientRect()):null;
          const texts=[...document.querySelectorAll('svg text,[data-leetcode-header] div')].filter(e=>e.textContent.trim()&&visible(e)&&(!e.children.length||e.tagName==='text')).map(e=>({text:e.textContent,subtitle:!!e.closest('[data-subtitle]'),...box(e.getBoundingClientRect())}));
          const violations=[];
          for(const t of texts){
            if(t.x<35||t.y<20||t.x+t.w>1885||t.y+t.h>1055)violations.push({type:'COPYFIT',text:t});
            if(!t.subtitle&&subtitle&&t.y+t.h>subtitle.y-6&&t.y<subtitle.y+subtitle.h&&t.x<subtitle.x+subtitle.w&&t.x+t.w>subtitle.x)violations.push({type:'subtitle-overlap',text:t});
          }
          const card=document.querySelector('[data-code-card="complete-python-solution"]');
          const lines=card?[...card.querySelectorAll('[data-code-line]')].map(e=>e.textContent):[];
          if((frame>=cardFrom)!==!!card)violations.push({type:'code-boundary'});
          if(card&&(subtitle||JSON.stringify(lines)!==JSON.stringify(code)))violations.push({type:'code-card-content-or-subtitle'});
          return {frame,texts,subtitle,codeVisible:!!card,codeLines:lines.length,violations};
        },{frame,cardFrom:card.from,code});
        report.audits.push(audit);
      }
      await close(options);
    };return page;
  };
  const onBrowserLog=log=>{if(['warn','warning'].includes(log.type))report.warnings.push(log);if(['error','assert'].includes(log.type))report.errors.push(log);};
  const composition=await selectComposition({serveUrl,id:'Main',puppeteerInstance:browser,browserExecutable:executable,onBrowserLog,logLevel:'error'});
  for(const f of frames){
    frame=f;
    await renderStill({serveUrl,composition,frame:f,puppeteerInstance:browser,browserExecutable:executable,
      output:path.join(out,`frame-${String(f).padStart(6,'0')}.png`),scale:.65,onBrowserLog,logLevel:'error'});
  }
  report.violations=report.audits.flatMap(a=>a.violations.map(v=>({frame:a.frame,...v})));
  if(!report.audits.find(a=>a.frame===0)?.texts.some(t=>t.text.includes('三数之和')))
    report.violations.push({frame:0,type:'opening-problem-title-missing'});
  if(!report.audits.some(a=>a.texts.some(t=>t.text==='两端已相遇，右指针不再移动')))
    report.violations.push({type:'second-hit-stationary-right-caption-not-observed'});
  report.status=report.errors.length||report.violations.length||report.audits.length!==frames.length?'failed':'passed';
}catch(e){report.status='failed';report.failure=String(e);console.error(e);}
finally{if(browser)await browser.close({silent:true});report.completedAt=new Date().toISOString();fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');}
console.log(report.status,report.audits.length,'frames',report.violations?.length??0,'layout violations');
if(report.status!=='passed')process.exitCode=1;
