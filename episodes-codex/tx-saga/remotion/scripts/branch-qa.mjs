// Saga range selection only. Rendering/camera sampling remain in the shared QA.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const dir=path.resolve(project,'..'),shared=path.resolve(dir,'../_shared/branch-map/qa.mjs');
const args=process.argv.slice(2),out=path.resolve(args.find(a=>!a.startsWith('--'))??'/workspace/.video-studio-branch-qa/tx-saga');
const clipsOnly=args.includes('--clips-only'),stillsOnly=args.includes('--stills-only');
const ranges=[
 {name:'01-outline-to-detail',range:[0,225],purpose:'开头整图、相机中间态、聚焦库存冲突'},
 {name:'05-07-success-to-shortage',range:[1090,1550],purpose:'库存成功后缩回，再从1000/库存0重置并聚焦'},
 {name:'11-13-refund-to-recovery',range:[2585,3177],purpose:'安全重放后回图，从800待退款重置并保留恢复进度'},
 {name:'14-summary-return',range:[3178,3477],purpose:'保留读到800动作，再缩回全图总结'},
];
fs.mkdirSync(out,{recursive:true});
const env={...process.env,TMPDIR:process.env.TMPDIR??'/workspace/.video-studio-tmp'};
const run=(folder,extra=[])=>{
 execFileSync(process.execPath,[shared,`--dir=${dir}`,`--out=${folder}`,...extra],{cwd:project,env,stdio:'inherit'});
 return JSON.parse(fs.readFileSync(path.join(folder,'frames.json'),'utf8'));
};
const outputs=[];
if(!clipsOnly)outputs.push({kind:'captioned-states',folder:path.join(out,'stills'),manifest:run(path.join(out,'stills'))});
if(!stillsOnly)for(const r of ranges){
 const folder=path.join(out,r.name);outputs.push({...r,kind:'silent-cross-shot',folder,manifest:run(folder,[`--range=${r.range[0]}:${r.range[1]}`,'--no-captions'])});
}
const current=outputs[0]?.manifest.sourceSha256;
for(const row of outputs)if(JSON.stringify(row.manifest.sourceSha256)!==JSON.stringify(current))throw Error('Inputs changed between QA runs; do not combine these outputs');
fs.writeFileSync(path.join(out,clipsOnly?'clip-index.json':stillsOnly?'still-index.json':'index.json'),JSON.stringify({scope:'Saga selections of shared branch-navigation QA; not final movie',outputs},null,2)+'\n');
