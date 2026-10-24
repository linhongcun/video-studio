// Episode selections only. Camera sampling and Remotion rendering use the shared implementation.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const dir=path.resolve(project,'..'),shared=path.resolve(dir,'../_shared/branch-map/qa.mjs');
const args=process.argv.slice(2),out=path.resolve(args.find(a=>!a.startsWith('--'))??'/workspace/.video-studio-flow-audit/intro-remake');
const pilot=args.includes('--pilot'),clipsOnly=args.includes('--clips-only'),stillsOnly=args.includes('--stills-only');
const frames=pilot?[441,456,471,482,532,549,566,739]:[
 0,441,456,471,482,532,549,566,738,739,801,
 1128,1129,1268,1375,1376,1625,1637,1649,
 1708,1725,1742,1747,1748,1769,1790,1847,1848,
 1912,1913,1957,1958,2051,2117,2118,2180,
 2612,2626,2640,2651,2687,2702,2717,2723,2738,2752,2753,2757,2774,2790,2791,2818,
 3020,3021,3289,3340,3341,3410,3429,3441,3453,
 3497,3511,3525,3536,3537,3620,3664,3802,3869,
 4058,4082,4107,4144,4204,4262,4263,4325,4358,4403,4450,
 4789,4804,4819,4832,5154,
];
const ranges=[
 {name:'07-09-scope-comparison',range:[1570,1968],purpose:'同笔范围回图→明确架构重置→独立边界完整拆开→部分成功'},
 {name:'11-12-timeout-unknown',range:[2580,2947],purpose:'回问题大纲→新超时情景→请求抵达/保存→回复丢失→调用方未知'},
 {name:'14-15-recovery-reset',range:[3385,3712],purpose:'错误反向修改落点→回大纲→正确库存4重置→库存/进度共同保存与恢复查证'},
 {name:'19-20-summary-return',range:[4740,4980],purpose:'业务规则局部→缩回概念全图→独立机制短片引导'},
];
fs.mkdirSync(out,{recursive:true});
const env={...process.env,TMPDIR:process.env.TMPDIR??'/workspace/.video-studio-tmp'};
const run=(folder,extra)=>{
 execFileSync(process.execPath,[shared,`--dir=${dir}`,`--out=${folder}`,...extra],{cwd:project,env,stdio:'inherit'});
 return JSON.parse(fs.readFileSync(path.join(folder,'frames.json'),'utf8'));
};
const outputs=[];
if(!clipsOnly)outputs.push({kind:'captioned-states',manifest:run(path.join(out,pilot?'pilot':'stills'),[`--frames=${frames.join(',')}`])});
if(!pilot&&!stillsOnly)for(const r of ranges)outputs.push({...r,kind:'silent-cross-shot',manifest:run(path.join(out,r.name),[`--range=${r.range.join(':')}`,'--no-captions'])});
const source=JSON.stringify(outputs[0]?.manifest.sourceSha256);
for(const r of outputs)if(JSON.stringify(r.manifest.sourceSha256)!==source)throw Error('Source changed between preview runs');
fs.writeFileSync(path.join(out,pilot?'pilot-index.json':clipsOnly?'clip-index.json':stillsOnly?'still-index.json':'index.json'),JSON.stringify({scope:'Intro concept navigation sampled QA; not final narrated movie',outputs},null,2)+'\n');
